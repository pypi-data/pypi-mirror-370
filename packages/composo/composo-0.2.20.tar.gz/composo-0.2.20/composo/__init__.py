"""
Composo SDK - A Python SDK for Composo evaluation services

This package provides both synchronous and asynchronous clients for evaluating
LLM conversations using simple dictionary message formats, with support for
results from various LLM providers including OpenAI and Anthropic.
"""

__version__ = "0.1.0"
__author__ = "Composo Team"
__email__ = "support@composo.ai"
__description__ = "A Python SDK for Composo evaluation services"

from .client import Composo, AsyncComposo
from .exceptions import (
    ComposoError,
    RateLimitError,
    MalformedError,
    APIError,
    AuthenticationError,
)
from .models import CriteriaSet


# Create a criteria module-like object for backward compatibility
class CriteriaModule:
    """Module-like object for accessing predefined criteria sets"""

    @property
    def basic(self):
        return CriteriaSet.basic

    @property
    def rag(self):
        return CriteriaSet.rag

    @property
    def tool_call(self):
        return CriteriaSet.tool_call

    @property
    def tool_response(self):
        return CriteriaSet.tool_response


# Create a singleton instance
criteria = CriteriaModule()


# Package exports
__all__ = [
    # Main clients
    "Composo",
    "AsyncComposo",
    # Exceptions
    "ComposoError",
    "RateLimitError",
    "MalformedError",
    "APIError",
    "AuthenticationError",
    # Criteria libraries
    "CriteriaSet",
    "criteria",
    # Metadata
    "__version__",
]


# Welcome message - removed for performance
# print(f"🚀 Composo SDK v{__version__} loaded successfully!")
