from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Tuple

import redis
from sqlalchemy import select, insert, update
from sqlalchemy.engine import Engine

from .exceptions import (
	InvalidKeyError,
	KeyDeactivatedError,
	KeyExpiredError,
	RateLimitExceededError,
	ScopeDeniedError,
)
from .schema import keymaster_keys, keymaster_logs, keymaster_key_scope_map, keymaster_scopes
from .settings_service import SettingsService
from .utils import hash_key, parse_rate_limit
from .redis_limiter import RedisFixedWindowLimiter


_UNIT_SECONDS = {
	"second": 1,
	"sec": 1,
	"s": 1,
	"minute": 60,
	"min": 60,
	"m": 60,
	"hour": 3600,
	"h": 3600,
	"day": 86400,
	"d": 86400,
}


class _InMemoryFixedWindowLimiter:
	"""Development-only in-memory fixed window limiter keyed by (key_id)."""

	def __init__(self) -> None:
		self._counters: dict[Tuple[int, int], int] = {}

	def allow(self, key_id: int, limit: int, unit_seconds: int) -> bool:
		window_start = int(time.time()) // unit_seconds
		k = (key_id, window_start)
		count = self._counters.get(k, 0)
		if count >= limit:
			return False
		self._counters[k] = count + 1
		return True


class AuthService:
	def __init__(self, engine: Engine, settings: SettingsService, redis_client: Optional[redis.Redis] = None) -> None:
		self._engine = engine
		self._settings = settings
		if redis_client:
			self._limiter: RedisFixedWindowLimiter | _InMemoryFixedWindowLimiter = RedisFixedWindowLimiter(redis_client)
		else:
			self._limiter = _InMemoryFixedWindowLimiter()

	def _resolve_limit(self, per_key_rate: Optional[str]) -> Tuple[int, int]:
		value = per_key_rate or self._settings.default_rate_limit()
		limit, unit = parse_rate_limit(value)
		unit_seconds = _UNIT_SECONDS.get(unit)
		if not unit_seconds:
			raise ValueError("unsupported rate unit")
		return limit, unit_seconds

	def validate_key(
		self,
		key_string: str,
		request_id: Optional[str] = None,
		required_scope: Optional[str] = None,
		source_ip: Optional[str] = None,
		request_method: Optional[str] = None,
		request_path: Optional[str] = None,
	) -> None:
		"""Validate API key and enforce fixed-window rate limiting.

		Enforces required_scope if provided.
		"""
		key_id: Optional[int] = None
		was_success = False
		error_reason: Optional[str] = None
		try:
			hashval = hash_key(key_string)
			with self._engine.begin() as conn:
				row = conn.execute(
					select(
						keymaster_keys.c.id,
						keymaster_keys.c.is_active,
						keymaster_keys.c.expires_at,
						keymaster_keys.c.rate_limit,
					)
					.where(keymaster_keys.c.hashed_key == hashval)
				).fetchone()
				if row is None:
					error_reason = "invalid"
					raise InvalidKeyError("invalid api key")
				key_id = int(row[0])
				is_active = bool(row[1])
				expires_at = row[2]
				rate_limit_val = row[3]
				if not is_active:
					error_reason = "deactivated"
					raise KeyDeactivatedError("key deactivated")
				if expires_at is not None:
					now = datetime.now(timezone.utc)
					# sqlite may store naive; if so, compare naive to naive
					if expires_at.tzinfo is None:
						expires_cmp = expires_at
						now_cmp = now.replace(tzinfo=None)
					else:
						expires_cmp = expires_at
						now_cmp = now
					if now_cmp >= expires_cmp:
						error_reason = "expired"
						raise KeyExpiredError("key expired")

				limit, unit_seconds = self._resolve_limit(rate_limit_val)
				if not self._limiter.allow(key_id, limit, unit_seconds):
					error_reason = "limited"
					raise RateLimitExceededError("rate limit exceeded")

				# required scope check
				if required_scope:
					q = (
						select(keymaster_key_scope_map.c.key_id)
						.select_from(keymaster_key_scope_map.join(keymaster_scopes, keymaster_key_scope_map.c.scope_id == keymaster_scopes.c.id))
						.where((keymaster_key_scope_map.c.key_id == key_id) & (keymaster_scopes.c.name == required_scope))
					)
					row2 = conn.execute(q).fetchone()
					if row2 is None:
						error_reason = "scope_denied"
						raise ScopeDeniedError("required scope missing")

			was_success = True
		finally:
			# audit log (best-effort; errors in logging should not escape)
			try:
				with self._engine.begin() as conn:
					conn.execute(
						insert(keymaster_logs).values(
							key_id=key_id,
							request_id=request_id,
							source_ip=source_ip,
							request_method=request_method,
							request_path=request_path,
							was_success=was_success,
							error_reason=error_reason,
						)
					)
			except Exception:
				pass

		# re-raise if failed
		if not was_success:
			if key_id is None:
				raise InvalidKeyError("invalid api key")
