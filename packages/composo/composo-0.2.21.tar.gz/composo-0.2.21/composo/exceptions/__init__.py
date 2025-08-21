"""
Composo SDK exceptions module
"""

from .api_exceptions import (
    ComposoError,
    RateLimitError,
    MalformedError,
    APIError,
    AuthenticationError,
    get_exception_for_status_code,
    TimeoutError,
)

__all__ = [
    "ComposoError",
    "RateLimitError",
    "MalformedError",
    "APIError",
    "AuthenticationError",
    "get_exception_for_status_code",
    "TimeoutError",
]
