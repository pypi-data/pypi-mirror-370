"""
Dataclass models for Dolfi API requests and responses.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional, List, Union
import uuid

# Constants
MAX_QUERY_LENGTH = 400
MAX_ANSWER_INSTRUCTION_LENGTH = 400

# Supported language codes
LANGUAGE_CODES = Literal[
    "zh", "en", "hi", "es", "ar", "fr", "bn", "pt", "ru", "ja",
    "pa", "de", "jv", "ko", "vi", "te", "mr", "tr", "ta", "ur"
]

# Search Models
@dataclass
class SearchRequest:
    """Request model for search endpoint."""
    query: str
    max_results: Optional[int] = 5
    time_range: Optional[Literal["day", "month", "year"]] = None
    search_language: Optional[LANGUAGE_CODES] = "en"
    include_answer: Optional[bool] = True
    answer_language: Optional[LANGUAGE_CODES] = "en"
    answer_instruction: Optional[str] = "Answer in short one paragraph (about 100 words) for the query based on provided resource."

@dataclass
class SearchResultItem:
    """Individual search result item."""
    title: str
    url: str
    snippet: str
    score: float
    favicon: str
    content_type: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class SearchResponse:
    """Response model for search endpoint."""
    query: str
    num_of_results: int
    answer: str
    search_words: str
    results: List[SearchResultItem]
    turn_around: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

# Scrape Models
@dataclass
class ScrapeRequest:
    """Request model for scrape endpoint."""
    urls: Union[str, List[str]]
    format: Literal["markdown", "text"] = "markdown"
    ignore_links: bool = False
    ignore_images: bool = False
    mobile: bool = False

@dataclass
class ScrapedImage:
    """Scraped image information."""
    url: str
    alt_text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class ScrapedLink:
    """Scraped link information."""
    url: str
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class ScrapeResponseItem:
    """Individual scrape result item."""
    status: int
    url: str
    html: str
    formatted_content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    images: List[ScrapedImage] = field(default_factory=list)
    links: List[ScrapedLink] = field(default_factory=list)

@dataclass
class ScrapeResponse:
    """Response model for scrape endpoint."""
    request_format: Literal["markdown", "text"]
    results: List[ScrapeResponseItem]
    turn_around: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))