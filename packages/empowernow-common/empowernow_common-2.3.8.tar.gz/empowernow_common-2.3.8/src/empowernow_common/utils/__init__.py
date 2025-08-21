"""
Utilities Module

This module provides utility functions and classes for common operations.
"""


# Placeholder classes for now - will be implemented in future modules
class HTTPClient:
    """HTTP client placeholder."""

    pass


class ConfigManager:
    """Configuration manager placeholder."""

    pass


# Re-export retry helpers
from .retry import with_retry, retryable
from .env import is_truthy

__all__ = [
    "HTTPClient",
    "ConfigManager",
    # Retry
    "with_retry",
    "retryable",
    "is_truthy",
]
