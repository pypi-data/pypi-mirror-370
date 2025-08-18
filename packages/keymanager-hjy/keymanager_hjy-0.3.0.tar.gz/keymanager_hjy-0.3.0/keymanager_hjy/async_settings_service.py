from __future__ import annotations

import time
from typing import Dict, Optional

from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncEngine

from .schema import keymaster_settings


_DEFAULTS: Dict[str, str] = {
    "key_prefix": "lingchongtong",
    "default_rate_limit": "100/minute",
    "cache_ttl_seconds": "5",
    "rate_limit_strategy": "fixed-window",
    "config_refresh_seconds": "30",
}


async def ensure_default_settings_async(engine: AsyncEngine) -> None:
    """Insert default settings if missing, idempotently."""
    async with engine.begin() as conn:
        for k, v in _DEFAULTS.items():
            result = await conn.execute(
                select(keymaster_settings.c.value).where(keymaster_settings.c.key == k)
            )
            row = result.fetchone()
            if row is None:
                await conn.execute(
                    insert(keymaster_settings).values(key=k, value=v, description=None)
                )


class AsyncSettingsService:
    """Async cached settings reader with manual refresh and auto-refresh by TTL."""

    def __init__(self, engine: AsyncEngine) -> None:
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

    async def refresh(self) -> None:
        async with self._engine.begin() as conn:
            result = await conn.execute(
                select(keymaster_settings.c.key, keymaster_settings.c.value)
            )
            rows = result.fetchall()
            self._cache = {k: v for k, v in rows}
            # ensure required defaults in memory even if not persisted
            for k, v in _DEFAULTS.items():
                self._cache.setdefault(k, v)
            self._last_loaded = time.time()

    async def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        if self._should_refresh():
            await self.refresh()
        return self._cache.get(key, default)

    # Convenience accessors
    async def key_prefix(self) -> str:
        value = await self.get("key_prefix", _DEFAULTS["key_prefix"])
        return value or _DEFAULTS["key_prefix"]

    async def default_rate_limit(self) -> str:
        value = await self.get("default_rate_limit", _DEFAULTS["default_rate_limit"])
        return value or _DEFAULTS["default_rate_limit"]

    async def cache_ttl_seconds(self) -> int:
        value = await self.get("cache_ttl_seconds", _DEFAULTS["cache_ttl_seconds"])
        value = value or _DEFAULTS["cache_ttl_seconds"]
        try:
            return int(value)
        except ValueError:
            return int(_DEFAULTS["cache_ttl_seconds"])

    async def rate_limit_strategy(self) -> str:
        value = await self.get("rate_limit_strategy", _DEFAULTS["rate_limit_strategy"])
        return value or _DEFAULTS["rate_limit_strategy"]

    async def config_refresh_seconds(self) -> int:
        value = await self.get("config_refresh_seconds", _DEFAULTS["config_refresh_seconds"])
        value = value or _DEFAULTS["config_refresh_seconds"]
        try:
            return int(value)
        except ValueError:
            return int(_DEFAULTS["config_refresh_seconds"])
