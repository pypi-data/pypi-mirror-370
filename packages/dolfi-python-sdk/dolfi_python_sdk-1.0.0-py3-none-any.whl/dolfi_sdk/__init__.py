"""
Dolfi Python SDK

An easy-to-use Python SDK for the Dolfi API that provides search and web scraping capabilities.
"""

from .client import DolfiClient
from .async_client import AsyncDolfiClient
from .models import (
    SearchRequest,
    SearchResponse, 
    SearchResultItem,
    ScrapeRequest,
    ScrapeResponse,
    ScrapeResponseItem,
    ScrapedImage,
    ScrapedLink
)
from .exceptions import (
    DolfiError,
    DolfiAuthenticationError,
    DolfiValidationError,
    DolfiAPIError
)

__version__ = "1.0.0"
__author__ = "Dolfi SDK Team"
__email__ = "support@dolfi.com"

__all__ = [
    "DolfiClient",
    "AsyncDolfiClient", 
    "SearchRequest",
    "SearchResponse",
    "SearchResultItem",
    "ScrapeRequest", 
    "ScrapeResponse",
    "ScrapeResponseItem",
    "ScrapedImage",
    "ScrapedLink",
    "DolfiError",
    "DolfiAuthenticationError", 
    "DolfiValidationError",
    "DolfiAPIError"
]