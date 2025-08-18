from __future__ import annotations

import time
from typing import Dict, Optional, Any

from sqlalchemy import select
from sqlalchemy.engine import Engine

from .schema import keymaster_settings


_DEFAULTS: Dict[str, str] = {
	"key_prefix": "lingchongtong",
	"default_rate_limit": "100/minute",
	"cache_ttl_seconds": "5",
	"rate_limit_strategy": "fixed-window",
	"config_refresh_seconds": "30",
}


def ensure_default_settings(engine: Engine) -> None:
	"""Insert default settings if missing, idempotently."""
	with engine.begin() as conn:
		for k, v in _DEFAULTS.items():
			row = conn.execute(select(keymaster_settings.c.value).where(keymaster_settings.c.key == k)).fetchone()
			if row is None:
				conn.execute(keymaster_settings.insert().values(key=k, value=v, description=None))


class SettingsService:
	"""Cached settings reader with manual refresh and auto-refresh by TTL."""

	def __init__(self, engine: Engine) -> None:
		self._engine = engine
		self._cache: Dict[str, str] = {}
		self._last_loaded: float = 0.0

	def _should_refresh(self) -> bool:
		if not self._cache:
			return True
		try:
			ttl = int(self._cache.get("config_refresh_seconds", _DEFAULTS["config_refresh_seconds"]))
		except ValueError:
			ttl = int(_DEFAULTS["config_refresh_seconds"])
		return (time.time() - self._last_loaded) >= ttl

	def refresh(self) -> None:
		with self._engine.begin() as conn:
			rows = conn.execute(select(keymaster_settings.c.key, keymaster_settings.c.value)).fetchall()
			self._cache = {k: v for k, v in rows}
			# ensure required defaults in memory even if not persisted
			for k, v in _DEFAULTS.items():
				self._cache.setdefault(k, v)
			self._last_loaded = time.time()

	def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
		if self._should_refresh():
			self.refresh()
		return self._cache.get(key, default)

	# Convenience accessors
	def key_prefix(self) -> str:
		return self.get("key_prefix", _DEFAULTS["key_prefix"]) or _DEFAULTS["key_prefix"]

	def default_rate_limit(self) -> str:
		return self.get("default_rate_limit", _DEFAULTS["default_rate_limit"]) or _DEFAULTS["default_rate_limit"]

	def cache_ttl_seconds(self) -> int:
		val = self.get("cache_ttl_seconds", _DEFAULTS["cache_ttl_seconds"]) or _DEFAULTS["cache_ttl_seconds"]
		try:
			return int(val)
		except ValueError:
			return int(_DEFAULTS["cache_ttl_seconds"])

	def rate_limit_strategy(self) -> str:
		return self.get("rate_limit_strategy", _DEFAULTS["rate_limit_strategy"]) or _DEFAULTS["rate_limit_strategy"]

	def config_refresh_seconds(self) -> int:
		val = self.get("config_refresh_seconds", _DEFAULTS["config_refresh_seconds"]) or _DEFAULTS["config_refresh_seconds"]
		try:
			return int(val)
		except ValueError:
			return int(_DEFAULTS["config_refresh_seconds"]) 
