from __future__ import annotations

from typing import Any, Optional

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from .config_provider import ConfigProvider
from .async_db_init import build_async_mysql_url, init_db_async
from .async_settings_service import AsyncSettingsService, ensure_default_settings_async
from .async_keys_service import AsyncKeysService
from .async_auth_service import AsyncAuthService


class _AsyncKeysAPI:
    """Async facade to AsyncKeysService."""

    def __init__(self, master: "AsyncKeyMaster") -> None:
        self._m = master

    async def create(self, *args: Any, **kwargs: Any) -> Any:
        keys_service = await self._m._keys_service()
        return await keys_service.create(*args, **kwargs)

    async def deactivate(self, key_id: int) -> None:
        keys_service = await self._m._keys_service()
        await keys_service.deactivate(key_id)

    async def rotate(self, key_id: int, transition_period_hours: int = 24) -> Any:
        keys_service = await self._m._keys_service()
        return await keys_service.rotate(key_id=key_id, transition_period_hours=transition_period_hours)


class _AsyncAuthAPI:
    """Async auth facade to AsyncAuthService."""

    def __init__(self, master: "AsyncKeyMaster") -> None:
        self._m = master

    async def validate_key(
        self, 
        key_string: str, 
        request_id: Optional[str] = None, 
        required_scope: Optional[str] = None, 
        *, 
        source_ip: Optional[str] = None, 
        request_method: Optional[str] = None, 
        request_path: Optional[str] = None
    ) -> None:
        auth_service = await self._m._auth_service()
        return await auth_service.validate_key(
            key_string, 
            request_id=request_id, 
            required_scope=required_scope, 
            source_ip=source_ip, 
            request_method=request_method, 
            request_path=request_path
        )


class AsyncKeyMaster:
    """Async main orchestrator."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self._base_dir = base_dir
        self.keys = _AsyncKeysAPI(self)
        self.auth = _AsyncAuthAPI(self)
        self._engine: Optional[AsyncEngine] = None
        self._settings: Optional[AsyncSettingsService] = None
        self._keys: Optional[AsyncKeysService] = None
        self._auth: Optional[AsyncAuthService] = None
        self._redis: Optional[aioredis.Redis] = None

    async def _ensure_engine(self) -> AsyncEngine:
        if self._engine is None:
            provider = ConfigProvider(self._base_dir)
            mysql_cfg = provider.get_mysql_config()
            url = build_async_mysql_url(mysql_cfg)
            self._engine = create_async_engine(url, pool_pre_ping=True)
            # Ensure schema and defaults
            await init_db_async(self._base_dir)
            await ensure_default_settings_async(self._engine)
        return self._engine

    async def _ensure_redis(self) -> Optional[aioredis.Redis]:
        if self._redis is None:
            provider = ConfigProvider(self._base_dir)
            redis_cfg = provider.get_redis_config()
            if redis_cfg:
                self._redis = aioredis.Redis(
                    host=redis_cfg["host"],
                    port=int(redis_cfg["port"]),
                    password=redis_cfg["password"],
                    decode_responses=True,
                )
        return self._redis

    async def _settings_service(self) -> AsyncSettingsService:
        if self._settings is None:
            engine = await self._ensure_engine()
            self._settings = AsyncSettingsService(engine)
        return self._settings

    async def _keys_service(self) -> AsyncKeysService:
        if self._keys is None:
            engine = await self._ensure_engine()
            settings = await self._settings_service()
            self._keys = AsyncKeysService(engine, settings)
        return self._keys

    async def _auth_service(self) -> AsyncAuthService:
        if self._auth is None:
            engine = await self._ensure_engine()
            settings = await self._settings_service()
            redis_client = await self._ensure_redis()
            self._auth = AsyncAuthService(engine, settings, redis_client)
        return self._auth

    async def close(self) -> None:
        """Close all connections."""
        if self._engine:
            await self._engine.dispose()
        if self._redis:
            await self._redis.aclose()


def _build_async_master() -> AsyncKeyMaster:
    return AsyncKeyMaster()


async_master: AsyncKeyMaster = _build_async_master()
