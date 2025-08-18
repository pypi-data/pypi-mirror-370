from __future__ import annotations

import asyncio
from typing import Dict, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text

from .config_provider import MySQLConfig
from .schema import metadata


def build_async_mysql_url(config: MySQLConfig) -> str:
    """Build async MySQL connection URL from config."""
    return (
        f"mysql+aiomysql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )


async def create_all_async(engine: AsyncEngine) -> None:
    """Create all keymaster tables asynchronously and idempotently."""
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)


_init_lock = asyncio.Lock()
_initialized = False


async def init_db_async(base_dir: Optional[str] = None) -> None:
    """Initialize database asynchronously - idempotent and thread-safe."""
    global _initialized
    
    async with _init_lock:
        if _initialized:
            return
        
        from .config_provider import ConfigProvider
        from .async_settings_service import ensure_default_settings_async
        
        try:
            provider = ConfigProvider(base_dir)
            mysql_cfg = provider.get_mysql_config()
            url = build_async_mysql_url(mysql_cfg)
            
            engine = create_async_engine(url, pool_pre_ping=True)
            
            # Create tables
            await create_all_async(engine)
            
            # Ensure default settings
            await ensure_default_settings_async(engine)
            
            await engine.dispose()
            _initialized = True
            
        except Exception as e:
            from .exceptions import InitializationError
            raise InitializationError(f"Database initialization failed: {e}")
