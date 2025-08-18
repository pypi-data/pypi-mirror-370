from __future__ import annotations

import asyncio
import threading
from typing import Any, Optional
from functools import wraps

from .async_master import AsyncKeyMaster


def run_in_event_loop(coro):
    """Run coroutine in event loop, handling different scenarios."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_running_loop()
        # If we're already in an event loop, we need to run in a thread
        if loop.is_running():
            # Use a thread to run the coroutine
            result = None
            exception = None
            
            def run_in_thread():
                nonlocal result, exception
                try:
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()
                except Exception as e:
                    exception = e
            
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            if exception:
                raise exception
            return result
        else:
            # Event loop exists but not running, use it
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


def sync_wrapper(async_func):
    """Decorator to wrap async functions for sync usage."""
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        coro = async_func(*args, **kwargs)
        return run_in_event_loop(coro)
    return wrapper


class _SyncKeysAPI:
    """Sync wrapper for AsyncKeysAPI."""

    def __init__(self, async_master: AsyncKeyMaster) -> None:
        self._async_master = async_master

    @sync_wrapper
    async def create(self, *args: Any, **kwargs: Any) -> Any:
        return await self._async_master.keys.create(*args, **kwargs)

    @sync_wrapper
    async def deactivate(self, key_id: int) -> None:
        await self._async_master.keys.deactivate(key_id)

    @sync_wrapper
    async def rotate(self, key_id: int, transition_period_hours: int = 24) -> Any:
        return await self._async_master.keys.rotate(key_id, transition_period_hours)


class _SyncAuthAPI:
    """Sync wrapper for AsyncAuthAPI."""

    def __init__(self, async_master: AsyncKeyMaster) -> None:
        self._async_master = async_master

    @sync_wrapper
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
        await self._async_master.auth.validate_key(
            key_string, 
            request_id=request_id, 
            required_scope=required_scope, 
            source_ip=source_ip, 
            request_method=request_method, 
            request_path=request_path
        )


class SyncKeyMaster:
    """Sync wrapper for AsyncKeyMaster - maintains backward compatibility."""

    def __init__(self, base_dir: Optional[str] = None) -> None:
        self._async_master = AsyncKeyMaster(base_dir)
        self.keys = _SyncKeysAPI(self._async_master)
        self.auth = _SyncAuthAPI(self._async_master)

    def close(self) -> None:
        """Close all connections."""
        run_in_event_loop(self._async_master.close())


def _build_sync_master() -> SyncKeyMaster:
    return SyncKeyMaster()


# For backward compatibility, keep the old sync master as default
sync_master: SyncKeyMaster = _build_sync_master()
