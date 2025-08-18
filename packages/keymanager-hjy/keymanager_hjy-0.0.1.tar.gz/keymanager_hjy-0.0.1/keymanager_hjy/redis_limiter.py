from __future__ import annotations

import time
from typing import Optional

import redis  # type: ignore[import-untyped]


class RedisFixedWindowLimiter:
	"""Fixed window rate limiter using Redis."""

	def __init__(self, client: redis.Redis) -> None:
		self._client = client

	def allow(self, key_id: int, limit: int, unit_seconds: int) -> bool:
		key = f"rl:{key_id}:{int(time.time()) // unit_seconds}"
		# INCR is atomic
		count = self._client.incr(key)
		# on first hit, set expiry
		if count == 1:
			self._client.expire(key, unit_seconds)
		return count <= limit
