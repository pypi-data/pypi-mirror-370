from typing import Callable, Any, Optional

from .async_master import async_master
from .exceptions import (
    InvalidKeyError,
    KeyDeactivatedError,
    KeyExpiredError,
    RateLimitExceededError,
    ScopeDeniedError,
)

# --- FastAPI async integration ---

try:
    from fastapi import Request, Header, HTTPException
    from fastapi.params import Depends

    def async_fastapi_guard(required_scope: Optional[str] = None) -> Callable:
        """Async FastAPI guard using the async master."""
        async def _guard(
            request: Request,
            x_api_key: str | None = Header(default=None, alias="X-API-Key"),
            x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
        ) -> None:
            if not x_api_key:
                raise HTTPException(status_code=401, detail="Missing API key")
            try:
                await async_master.auth.validate_key(
                    x_api_key,
                    request_id=x_request_id,
                    required_scope=required_scope,
                    source_ip=request.client.host if request.client else None,
                    request_method=request.method,
                    request_path=request.url.path,
                )
            except (InvalidKeyError, KeyDeactivatedError, KeyExpiredError):
                raise HTTPException(status_code=401, detail="Invalid/Inactive/Expired key")
            except ScopeDeniedError:
                raise HTTPException(status_code=403, detail="Scope denied")
            except RateLimitExceededError:
                raise HTTPException(status_code=429, detail="Too Many Requests")

        return Depends(_guard)

except ImportError:
    async_fastapi_guard = None


# --- Starlette async integration ---

try:
    from starlette.requests import Request
    from starlette.responses import JSONResponse
    from starlette.middleware.base import BaseHTTPMiddleware

    class AsyncKeyMasterMiddleware(BaseHTTPMiddleware):
        """Async middleware for Starlette/FastAPI applications."""
        
        def __init__(self, app, required_scope: Optional[str] = None, skip_paths: Optional[list] = None):
            super().__init__(app)
            self.required_scope = required_scope
            self.skip_paths = skip_paths or []
        
        async def dispatch(self, request: Request, call_next):
            # Skip authentication for certain paths
            if request.url.path in self.skip_paths:
                return await call_next(request)
            
            api_key = request.headers.get("X-API-Key")
            if not api_key:
                return JSONResponse(
                    status_code=401, 
                    content={"error": "Missing API key"}
                )
            
            try:
                await async_master.auth.validate_key(
                    api_key,
                    request_id=request.headers.get("X-Request-ID"),
                    required_scope=self.required_scope,
                    source_ip=request.client.host if request.client else None,
                    request_method=request.method,
                    request_path=request.url.path,
                )
            except (InvalidKeyError, KeyDeactivatedError, KeyExpiredError):
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid/Inactive/Expired key"}
                )
            except ScopeDeniedError:
                return JSONResponse(
                    status_code=403,
                    content={"error": "Scope denied"}
                )
            except RateLimitExceededError:
                return JSONResponse(
                    status_code=429,
                    content={"error": "Too Many Requests"}
                )
            
            return await call_next(request)

except ImportError:
    AsyncKeyMasterMiddleware = None
