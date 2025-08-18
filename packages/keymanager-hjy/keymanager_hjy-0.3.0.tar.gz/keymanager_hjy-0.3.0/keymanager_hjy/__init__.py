"""keymaster_hjy package public API.

This package provides both async-first and sync-compatible APIs for zero-config
API key authentication, rate limiting, and audit logging.
"""

# Async-first API (recommended for new applications)
from .async_master import AsyncKeyMaster, async_master

# Sync-compatible API (for backward compatibility and Flask/Django)
from .sync_wrapper import SyncKeyMaster, sync_master

# Legacy sync API (deprecated but maintained for compatibility)
from ._master import KeyMaster

# Default master object (sync for backward compatibility)
master = sync_master

__all__ = [
    # Async API (recommended)
    "AsyncKeyMaster",
    "async_master",
    
    # Sync API 
    "SyncKeyMaster", 
    "sync_master",
    
    # Legacy (deprecated)
    "KeyMaster",
    
    # Default (sync for compatibility)
    "master",
]
