from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Tuple

import redis.asyncio as aioredis
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncEngine

from .exceptions import (
    InvalidKeyError,
    KeyDeactivatedError,
    KeyExpiredError,
    RateLimitExceededError,
    ScopeDeniedError,
)
from .schema import keymaster_keys, keymaster_logs, keymaster_key_scope_map, keymaster_scopes
from .async_settings_service import AsyncSettingsService
from .utils import hash_key, parse_rate_limit
from .async_redis_limiter import AsyncRedisFixedWindowLimiter, AsyncInMemoryFixedWindowLimiter
from .auth_cache import AsyncAuthCache, CachedAuthResult


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


class AsyncAuthService:
    def __init__(
        self, 
        engine: AsyncEngine, 
        settings: AsyncSettingsService, 
        redis_client: Optional[aioredis.Redis] = None
    ) -> None:
        self._engine = engine
        self._settings = settings
        if redis_client:
            self._limiter = AsyncRedisFixedWindowLimiter(redis_client)
        else:
            self._limiter = AsyncInMemoryFixedWindowLimiter()
        
        # Initialize auth cache
        self._cache = AsyncAuthCache(redis_client)

    async def _resolve_limit(self, per_key_rate: Optional[str]) -> Tuple[int, int]:
        default_rate = await self._settings.default_rate_limit()
        value = per_key_rate or default_rate
        limit, unit = parse_rate_limit(value)
        unit_seconds = _UNIT_SECONDS.get(unit)
        if not unit_seconds:
            raise ValueError("unsupported rate unit")
        return limit, unit_seconds

    async def validate_key(
        self,
        key_string: str,
        request_id: Optional[str] = None,
        required_scope: Optional[str] = None,
        source_ip: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
    ) -> None:
        """Async validate API key and enforce fixed-window rate limiting.

        Enforces required_scope if provided.
        """
        key_id: Optional[int] = None
        was_success = False
        error_reason: Optional[str] = None
        
        try:
            hashval = hash_key(key_string)
            
            # Try cache first
            cached_result = await self._cache.get(hashval)
            if cached_result and cached_result.is_valid:
                key_id = cached_result.key_id
                
                # Check scope from cache
                if required_scope and required_scope not in cached_result.scopes:
                    error_reason = "scope_denied"
                    raise ScopeDeniedError("required scope missing")
                
                # Still need to check rate limiting (can't cache this)
                limit, unit_seconds = await self._resolve_limit(None)  # Use default rate
                if not await self._limiter.allow(key_id, limit, unit_seconds):
                    error_reason = "limited"
                    raise RateLimitExceededError("rate limit exceeded")
                
                was_success = True
                return
            
            # Cache miss or invalid - do full validation
            async with self._engine.begin() as conn:
                result = await conn.execute(
                    select(
                        keymaster_keys.c.id,
                        keymaster_keys.c.is_active,
                        keymaster_keys.c.expires_at,
                        keymaster_keys.c.rate_limit,
                    )
                    .where(keymaster_keys.c.hashed_key == hashval)
                )
                row = result.fetchone()
                
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
                    # Handle timezone-naive datetimes
                    if expires_at.tzinfo is None:
                        expires_cmp = expires_at
                        now_cmp = now.replace(tzinfo=None)
                    else:
                        expires_cmp = expires_at
                        now_cmp = now
                    if now_cmp >= expires_cmp:
                        error_reason = "expired"
                        raise KeyExpiredError("key expired")

                # Rate limiting
                limit, unit_seconds = await self._resolve_limit(rate_limit_val)
                if not await self._limiter.allow(key_id, limit, unit_seconds):
                    error_reason = "limited"
                    raise RateLimitExceededError("rate limit exceeded")

                # Scope check
                if required_scope:
                    scope_result = await conn.execute(
                        select(keymaster_key_scope_map.c.key_id)
                        .select_from(
                            keymaster_key_scope_map.join(
                                keymaster_scopes, 
                                keymaster_key_scope_map.c.scope_id == keymaster_scopes.c.id
                            )
                        )
                        .where(
                            (keymaster_key_scope_map.c.key_id == key_id) & 
                            (keymaster_scopes.c.name == required_scope)
                        )
                    )
                    scope_row = scope_result.fetchone()
                    if scope_row is None:
                        error_reason = "scope_denied"
                        raise ScopeDeniedError("required scope missing")

                # Cache the successful validation result
                scopes_set = set()
                if key_id:
                    scope_result = await conn.execute(
                        select(keymaster_scopes.c.name)
                        .select_from(
                            keymaster_key_scope_map.join(
                                keymaster_scopes, 
                                keymaster_key_scope_map.c.scope_id == keymaster_scopes.c.id
                            )
                        )
                        .where(keymaster_key_scope_map.c.key_id == key_id)
                    )
                    scope_rows = scope_result.fetchall()
                    scopes_set = {row[0] for row in scope_rows}
                
                # Cache the result
                cache_result = CachedAuthResult(
                    key_id=key_id,
                    is_valid=True,
                    scopes=scopes_set,
                    expires_at=expires_at.timestamp() if expires_at else None,
                    cached_at=time.time()
                )
                await self._cache.set(hashval, cache_result)

            was_success = True
            
        finally:
            # Audit log (best-effort; errors in logging should not escape)
            try:
                async with self._engine.begin() as conn:
                    await conn.execute(
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

        # Re-raise if failed
        if not was_success:
            if key_id is None:
                raise InvalidKeyError("invalid api key")
