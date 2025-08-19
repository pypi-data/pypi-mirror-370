"""
Exception classes for PyGard client.
"""

from typing import Any, Dict, Optional


class GardException(Exception):
    """Base exception for all PyGard related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}


class GardConnectionError(GardException):
    """Raised when there's a connection error with the Gard service."""
    pass


class GardValidationError(GardException):
    """Raised when request validation fails."""
    pass


class GardNotFoundError(GardException):
    """Raised when a requested resource is not found."""
    pass


class GardAuthenticationError(GardException):
    """Raised when authentication fails."""
    pass


class GardRateLimitError(GardException):
    """Raised when rate limit is exceeded."""
    pass 