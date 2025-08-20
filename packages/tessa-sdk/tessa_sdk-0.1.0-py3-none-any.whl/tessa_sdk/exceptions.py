"""Custom exceptions for the Tessa SDK."""

from typing import Optional, Dict, Any


class TessaError(Exception):
    """Base exception for all Tessa SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(TessaError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(message)


class RateLimitError(TessaError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.retry_after = retry_after


class JobNotFoundError(TessaError):
    """Raised when a job is not found."""
    
    def __init__(self, job_id: str):
        message = f"Job not found: {job_id}"
        super().__init__(message)
        self.job_id = job_id


class JobFailedError(TessaError):
    """Raised when a job fails to complete."""
    
    def __init__(self, job_id: str, error_message: str):
        message = f"Job {job_id} failed: {error_message}"
        super().__init__(message, {"job_id": job_id, "error": error_message})
        self.job_id = job_id
        self.error_message = error_message


class ValidationError(TessaError):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, errors: Optional[list] = None):
        super().__init__(message, {"errors": errors or []})
        self.errors = errors or []


class TimeoutError(TessaError):
    """Raised when a job times out."""
    
    def __init__(self, job_id: str, timeout_seconds: float):
        message = f"Job {job_id} timed out after {timeout_seconds} seconds"
        super().__init__(message)
        self.job_id = job_id
        self.timeout_seconds = timeout_seconds


class ConfigurationError(TessaError):
    """Raised when SDK configuration is invalid."""
    
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")
