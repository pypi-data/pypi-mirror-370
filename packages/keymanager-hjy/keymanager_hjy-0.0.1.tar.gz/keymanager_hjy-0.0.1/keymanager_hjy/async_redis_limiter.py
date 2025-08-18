from __future__ import annotations

import time
import asyncio
from typing import Optional, Tuple

import redis.asyncio as aioredis


class AsyncRedisFixedWindowLimiter:
    """Async Redis-backed fixed window rate limiter."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client

    async def allow(self, key_id: int, limit: int, unit_seconds: int) -> bool:
        """Check if request is within rate limit using fixed window algorithm."""
        window_start = int(time.time()) // unit_seconds
        redis_key = f"rate_limit:{key_id}:{window_start}"
        
        try:
            # Use pipeline for atomic operations
            async with self._redis.pipeline() as pipe:
                await pipe.incr(redis_key)
                await pipe.expire(redis_key, unit_seconds)
                results = await pipe.execute()
                
            current_count = results[0]
            return current_count <= limit
            
        except Exception:
            # Fail open on Redis errors
            return True


class AsyncInMemoryFixedWindowLimiter:
    """Development-only async in-memory fixed window limiter."""

    def __init__(self) -> None:
        self._counters: dict[Tuple[int, int], int] = {}
        self._lock = asyncio.Lock()

    async def allow(self, key_id: int, limit: int, unit_seconds: int) -> bool:
        window_start = int(time.time()) // unit_seconds
        k = (key_id, window_start)
        
        async with self._lock:
            count = self._counters.get(k, 0)
            if count >= limit:
                return False
            self._counters[k] = count + 1
            return True
