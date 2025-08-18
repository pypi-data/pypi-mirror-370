"""
API Marketplace Client Library
"""

__version__ = "1.0.0.5"
__author__ = "venilo_o"
__email__ = "ilyasaminev3@mail.ru"

from .sync.client import EncarClient, KBchachachaClient
from .async_.client import AsyncEncarClient, AsyncKBchachachaClient
from .exceptions import MarketplaceAPIException, APIError, AuthError, ForbiddenError, ValidationError

__all__ = [
    # Sync clients
    "EncarClient",
    "KBchachachaClient",
    # Async clients
    "AsyncEncarClient",
    "AsyncKBchachachaClient",
    # Exceptions
    "MarketplaceAPIException",
    "APIError",
    "AuthError",
    "ForbiddenError",
    "ValidationError"
]
