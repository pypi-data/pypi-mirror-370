from __future__ import annotations

import time
import json
from typing import Optional, Dict, Any, Set
from dataclasses import dataclass, asdict

import redis.asyncio as aioredis


@dataclass
class CachedAuthResult:
    """Cached authentication result with metadata."""
    key_id: int
    is_valid: bool
    scopes: Set[str]
    expires_at: Optional[float]  # Unix timestamp
    cached_at: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            'scopes': list(self.scopes)  # Convert set to list for JSON
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CachedAuthResult':
        data['scopes'] = set(data['scopes'])  # Convert list back to set
        return cls(**data)


class AsyncAuthCache:
    """Redis-based auth result cache with TTL."""
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None, ttl_seconds: int = 5) -> None:
        self._redis = redis_client
        self._ttl = ttl_seconds
        self._in_memory_cache: Dict[str, CachedAuthResult] = {}
        
    def _cache_key(self, key_hash: str) -> str:
        """Generate Redis cache key."""
        return f"auth_cache:{key_hash}"
    
    def _is_expired(self, result: CachedAuthResult) -> bool:
        """Check if cached result is expired."""
        now = time.time()
        
        # Check cache TTL
        if (now - result.cached_at) > self._ttl:
            return True
            
        # Check key expiration
        if result.expires_at and now >= result.expires_at:
            return True
            
        return False
    
    async def get(self, key_hash: str) -> Optional[CachedAuthResult]:
        """Get cached auth result."""
        cache_key = self._cache_key(key_hash)
        
        if self._redis:
            try:
                cached_data = await self._redis.get(cache_key)
                if cached_data:
                    data = json.loads(cached_data)
                    result = CachedAuthResult.from_dict(data)
                    
                    if not self._is_expired(result):
                        return result
                    else:
                        # Clean up expired cache
                        await self._redis.delete(cache_key)
                        
            except Exception:
                # Fail gracefully on Redis errors
                pass
        else:
            # Fallback to in-memory cache
            if key_hash in self._in_memory_cache:
                result = self._in_memory_cache[key_hash]
                if not self._is_expired(result):
                    return result
                else:
                    del self._in_memory_cache[key_hash]
        
        return None
    
    async def set(self, key_hash: str, result: CachedAuthResult) -> None:
        """Cache auth result."""
        cache_key = self._cache_key(key_hash)
        
        if self._redis:
            try:
                data = json.dumps(result.to_dict())
                await self._redis.setex(cache_key, self._ttl, data)
            except Exception:
                # Fail gracefully on Redis errors
                pass
        else:
            # Fallback to in-memory cache
            self._in_memory_cache[key_hash] = result
    
    async def invalidate(self, key_hash: str) -> None:
        """Invalidate cached result."""
        cache_key = self._cache_key(key_hash)
        
        if self._redis:
            try:
                await self._redis.delete(cache_key)
            except Exception:
                pass
        else:
            self._in_memory_cache.pop(key_hash, None)
    
    async def clear(self) -> None:
        """Clear all cached results."""
        if self._redis:
            try:
                # Delete all auth cache keys
                pattern = self._cache_key("*")
                async for key in self._redis.scan_iter(match=pattern):
                    await self._redis.delete(key)
            except Exception:
                pass
        else:
            self._in_memory_cache.clear()
