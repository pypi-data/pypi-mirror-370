from functools import wraps
from typing import Callable, Any, Optional

from ._master import master
from .exceptions import (
	InvalidKeyError,
	KeyDeactivatedError,

	KeyExpiredError,
	RateLimitExceededError,
	ScopeDeniedError,
)

# --- FastAPI integration ---

try:
	from fastapi import Request, Header, HTTPException
	from fastapi.params import Depends

	def fastapi_guard(required_scope: Optional[str] = None) -> Callable:
		async def _guard(
			request: Request,
			x_api_key: str | None = Header(default=None, alias="X-API-Key"),
			x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
		) -> None:
			if not x_api_key:
				raise HTTPException(status_code=401, detail="Missing API key")
			try:
				master.auth.validate_key(
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
	fastapi_guard = None


# --- Flask integration ---

try:
	from flask import request, jsonify

	def flask_guard(required_scope: Optional[str] = None) -> Callable:
		def deco(fn: Callable) -> Callable:
			@wraps(fn)
			def wrapper(*args: Any, **kwargs: Any) -> Any:
				key = request.headers.get("X-API-Key")
				if not key:
					return jsonify({"error": "Missing API key"}), 401
				try:
					master.auth.validate_key(
						key,
						request_id=request.headers.get("X-Request-ID"),
						required_scope=required_scope,
						source_ip=request.remote_addr,
						request_method=request.method,
						request_path=request.path,
					)
				except (InvalidKeyError, KeyDeactivatedError, KeyExpiredError):
					return jsonify({"error": "Invalid/Inactive/Expired key"}), 401
				except ScopeDeniedError:
					return jsonify({"error": "Scope denied"}), 403
				except RateLimitExceededError:
					return jsonify({"error": "Too Many Requests"}), 429
				return fn(*args, **kwargs)

			return wrapper

		return deco

except ImportError:
	flask_guard = None
