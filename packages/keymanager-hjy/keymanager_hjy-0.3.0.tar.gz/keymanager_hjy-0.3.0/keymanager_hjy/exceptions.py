"""
Keymaster HJY Exceptions

All exceptions provide detailed, actionable error messages to help developers
quickly understand and resolve issues.
"""

from typing import Optional, List, Dict, Any


class KeymasterError(Exception):
    """Base exception for all Keymaster HJY errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, 
                 details: Optional[Dict[str, Any]] = None, 
                 suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        """Return a detailed error message with suggestions."""
        msg = super().__str__()
        
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            msg += f" (Details: {detail_str})"
        
        if self.suggestions:
            suggestions_str = "; ".join(self.suggestions)
            msg += f" | Suggestions: {suggestions_str}"
        
        return msg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": self.error_code,
            "message": super().__str__(),
            "details": self.details,
            "suggestions": self.suggestions
        }


class InitializationError(KeymasterError, RuntimeError):
    """Raised when the library fails to initialize due to invalid or missing configuration."""
    
    def __init__(self, message: str, missing_config: Optional[str] = None):
        suggestions = [
            "Check that mysql.env file exists in your project root",
            "Verify database connection parameters",
            "Run 'keymaster init' for interactive setup"
        ]
        
        if missing_config:
            suggestions.insert(0, f"Add missing configuration: {missing_config}")
        
        super().__init__(
            message=message,
            error_code="INIT_ERROR",
            details={"missing_config": missing_config} if missing_config else {},
            suggestions=suggestions
        )


class InvalidKeyError(KeymasterError, PermissionError):
    """Raised when the provided API key cannot be found or parsed."""
    
    def __init__(self, key_preview: Optional[str] = None, reason: Optional[str] = None):
        message = "Invalid API key provided"
        if key_preview:
            message += f" (key: {key_preview})"
        if reason:
            message += f": {reason}"
        
        suggestions = [
            "Verify the API key is correct and complete",
            "Check that the key hasn't been deactivated",
            "Generate a new API key if needed",
            "Ensure the key follows the correct format"
        ]
        
        super().__init__(
            message=message,
            error_code="INVALID_KEY",
            details={"key_preview": key_preview, "reason": reason},
            suggestions=suggestions
        )


class KeyDeactivatedError(KeymasterError, PermissionError):
    """Raised when the API key is deactivated."""
    
    def __init__(self, key_id: Optional[int] = None, deactivated_at: Optional[str] = None):
        message = "API key has been deactivated"
        if key_id:
            message += f" (ID: {key_id})"
        
        suggestions = [
            "Generate a new API key to replace the deactivated one",
            "Contact your administrator if this was unexpected",
            "Check the audit logs for deactivation details"
        ]
        
        super().__init__(
            message=message,
            error_code="KEY_DEACTIVATED",
            details={"key_id": key_id, "deactivated_at": deactivated_at},
            suggestions=suggestions
        )


class KeyExpiredError(KeymasterError, PermissionError):
    """Raised when the API key is expired."""
    
    def __init__(self, key_id: Optional[int] = None, expired_at: Optional[str] = None):
        message = "API key has expired"
        if expired_at:
            message += f" (expired: {expired_at})"
        
        suggestions = [
            "Generate a new API key with a longer expiration period",
            "Update your application with the new key",
            "Consider using key rotation for automatic renewal"
        ]
        
        super().__init__(
            message=message,
            error_code="KEY_EXPIRED", 
            details={"key_id": key_id, "expired_at": expired_at},
            suggestions=suggestions
        )


class RateLimitExceededError(KeymasterError, PermissionError):
    """Raised when the API key exceeds its allowed rate limit."""
    
    def __init__(self, current_rate: Optional[str] = None, limit: Optional[str] = None,
                 reset_time: Optional[int] = None):
        message = "Rate limit exceeded"
        if current_rate and limit:
            message += f" ({current_rate} > {limit})"
        
        suggestions = [
            "Reduce request frequency or implement backoff",
            "Consider upgrading to a higher rate limit",
            "Implement request queuing in your application"
        ]
        
        if reset_time:
            suggestions.insert(0, f"Retry after {reset_time} seconds")
        
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details={
                "current_rate": current_rate,
                "limit": limit, 
                "reset_time": reset_time
            },
            suggestions=suggestions
        )


class ScopeDeniedError(KeymasterError, PermissionError):
    """Raised when the API key lacks the required scope for the requested operation."""
    
    def __init__(self, required_scope: str, available_scopes: Optional[List[str]] = None,
                 key_id: Optional[int] = None):
        message = f"Missing required scope: '{required_scope}'"
        if available_scopes:
            message += f" (available: {', '.join(available_scopes)})"
        
        suggestions = [
            f"Add the '{required_scope}' scope to your API key",
            "Generate a new key with the required permissions",
            "Contact your administrator for scope assignment"
        ]
        
        super().__init__(
            message=message,
            error_code="SCOPE_DENIED",
            details={
                "required_scope": required_scope,
                "available_scopes": available_scopes,
                "key_id": key_id
            },
            suggestions=suggestions
        )


class DatabaseError(KeymasterError, RuntimeError):
    """Raised when database operations fail."""
    
    def __init__(self, operation: str, original_error: Optional[str] = None):
        message = f"Database operation failed: {operation}"
        if original_error:
            message += f" ({original_error})"
        
        suggestions = [
            "Check database connectivity and credentials",
            "Verify the database schema is properly initialized",
            "Check database server status and availability",
            "Review database logs for more details"
        ]
        
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={"operation": operation, "original_error": original_error},
            suggestions=suggestions
        )


class ConfigurationError(KeymasterError, ValueError):
    """Raised when configuration values are invalid."""
    
    def __init__(self, config_key: str, invalid_value: Any, expected_format: Optional[str] = None):
        message = f"Invalid configuration for '{config_key}': {invalid_value}"
        if expected_format:
            message += f" (expected: {expected_format})"
        
        suggestions = [
            f"Update the '{config_key}' configuration value",
            "Check the documentation for valid configuration formats",
            "Run 'keymaster init' to regenerate configuration"
        ]
        
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            details={
                "config_key": config_key,
                "invalid_value": str(invalid_value),
                "expected_format": expected_format
            },
            suggestions=suggestions
        )
