"""
Asynchronous client for Dolfi API.
"""

import aiohttp, os
from dataclasses import asdict
from typing import Optional, Union, List, Literal, Any
from pydantic import ValidationError

from .models import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    ScrapeRequest,
    ScrapeResponse,
    ScrapeResponseItem,
    ScrapedImage,
    ScrapedLink,
    LANGUAGE_CODES
)
from .exceptions import (
    DolfiAuthenticationError,
    DolfiValidationError,
    DolfiAPIError,
    DolfiConnectionError,
    DolfiTimeoutError
)
from .constants import DOLFI_BASE_URL


class AsyncDolfiClient:
    """
    Asynchronous client for interacting with the Dolfi API.
    
    Provides async methods for searching and scraping web content.
    """
    
    def __init__(self, api_key: str = "", base_url: str = DOLFI_BASE_URL, timeout: int = 30):
        """
        Initialize the async Dolfi client.
        
        Args:
            api_key: Your Dolfi API key
            base_url: Base URL for the API (default: https://api.dolfi.com)
            timeout: Request timeout in seconds (default: 30)
        """
        if api_key: self.api_key = api_key
        else:       self.api_key = os.getenv("DOLFI_API_KEY")
        
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        
        self.session = None
        self.headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "dolfi-python-sdk/1.0.0"
        }
    
    def _dataclass_to_dict(self, obj: Any, exclude_none: bool = False) -> dict:
        """
        Convert dataclass to dictionary.
        
        Args:
            obj: Dataclass instance
            exclude_none: Whether to exclude None values
            
        Returns:
            Dictionary representation
        """
        data = asdict(obj)
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data
    
    def _build_search_response(self, data: dict) -> SearchResponse:
        """Build SearchResponse from API response data."""
        results = []
        for result_data in data.get("results", []):
            result = SearchResultItem(
                title=result_data.get("title", ""),
                url=result_data.get("url", ""),
                snippet=result_data.get("snippet", ""),
                score=result_data.get("score", 0.0),
                favicon=result_data.get("favicon", ""),
                content_type=result_data.get("content_type", ""),
                id=result_data.get("id", "")
            )
            results.append(result)
        
        return SearchResponse(
            query=data.get("query", ""),
            num_of_results=data.get("num_of_results", 0),
            answer=data.get("answer", ""),
            search_words=data.get("search_words", ""),
            results=results,
            turn_around=data.get("turn_around", 0.0),
            id=data.get("id", "")
        )
    
    def _build_scrape_response(self, data: dict) -> ScrapeResponse:
        """Build ScrapeResponse from API response data."""
        results = []
        for result_data in data.get("results", []):
            images = []
            for img_data in result_data.get("images", []):
                image = ScrapedImage(
                    url=img_data.get("url", ""),
                    alt_text=img_data.get("alt_text", ""),
                    id=img_data.get("id", "")
                )
                images.append(image)
            
            links = []
            for link_data in result_data.get("links", []):
                link = ScrapedLink(
                    url=link_data.get("url", ""),
                    title=link_data.get("title", ""),
                    id=link_data.get("id", "")
                )
                links.append(link)
            
            result = ScrapeResponseItem(
                status=result_data.get("status", 0),
                url=result_data.get("url", ""),
                html=result_data.get("html", ""),
                formatted_content=result_data.get("formatted_content", ""),
                id=result_data.get("id", ""),
                images=images,
                links=links
            )
            results.append(result)
        
        return ScrapeResponse(
            request_format=data.get("request_format", "markdown"),
            results=results,
            turn_around=data.get("turn_around", 0.0),
            id=data.get("id", "")
        )
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=timeout
            )
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """
        Make async HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            DolfiAuthenticationError: On 401 Unauthorized
            DolfiValidationError: On 422 Validation Error
            DolfiAPIError: On other HTTP errors
            DolfiConnectionError: On connection errors
            DolfiTimeoutError: On timeout errors
        """
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        try:
            async with session.request(method, url, json=data) as response:
                response_data = await response.json() if response.content_length else {}
                
                # Handle different status codes
                if response.status == 401:
                    error_message = response_data.get("detail", "Authentication failed")
                    raise DolfiAuthenticationError(error_message)
                
                elif response.status == 422:
                    error_message = "Validation error"
                    if "detail" in response_data:
                        error_message = f"Validation error: {response_data['detail']}"
                    raise DolfiValidationError(error_message, response_data)
                
                elif not response.ok:
                    error_message = f"API error: {response.status}"
                    if "detail" in response_data:
                        error_message = f"API error: {response_data['detail']}"
                    raise DolfiAPIError(error_message, response.status, response_data)
                
                return response_data
                
        except aiohttp.ClientTimeout:
            raise DolfiTimeoutError()
        except aiohttp.ClientConnectionError:
            raise DolfiConnectionError()
        except aiohttp.ClientError as e:
            raise DolfiAPIError(f"Request failed: {str(e)}", 0)
    
    async def search(
        self,
        query: str,
        max_results: Optional[int] = 10,
        time_range: Optional[Literal["day", "month", "year"]] = None,
        search_language: Optional[LANGUAGE_CODES] = None,
        include_answer: Optional[bool] = True,
        answer_language: Optional[LANGUAGE_CODES] = None,
        answer_instruction: Optional[str] = None
    ) -> SearchResponse:
        """
        Search the web using natural language queries.
        
        Args:
            query: Natural language search query (max 400 characters)
            max_results: Maximum number of results to return (1-20, default: 5)
            time_range: Filter by time period ("day", "month", "year", or None)
            search_language: Language code for search (default: "en")
            include_answer: Whether to include AI-generated answer (default: True)
            answer_language: Language code for AI answer (default: "en")
            answer_instruction: Custom instructions for AI answer formatting
            
        Returns:
            SearchResponse object containing search results and AI answer
            
        Raises:
            DolfiValidationError: On invalid request parameters
            DolfiAuthenticationError: On authentication failure
            DolfiAPIError: On API errors
        """
        try:
            request = SearchRequest(
                query=query,
                max_results=max_results,
                time_range=time_range,
                search_language=search_language,
                include_answer=include_answer,
                answer_language=answer_language,
                answer_instruction=answer_instruction
            )
        except ValidationError as e:
            raise DolfiValidationError(f"Invalid search parameters: {str(e)}")
        
        response_data = await self._make_request("POST", "/search", self._dataclass_to_dict(request, exclude_none=True))
        return self._build_search_response(response_data)
    
    async def scrape(
        self,
        urls: Union[str, List[str]],
        format: Literal["markdown", "text"] = "markdown",
        ignore_links: bool = False,
        ignore_images: bool = False,
        mobile: bool = False
    ) -> ScrapeResponse:
        """
        Scrape content from web pages.
        
        Args:
            urls: Single URL string or list of URLs to scrape
            format: Output format ("markdown" or "text", default: "markdown")
            ignore_links: Exclude hyperlinks from output (default: False)
            ignore_images: Exclude images from output (default: False)
            mobile: Use mobile version of websites (default: False)
            
        Returns:
            ScrapeResponse object containing scraped content
            
        Raises:
            DolfiValidationError: On invalid request parameters
            DolfiAuthenticationError: On authentication failure
            DolfiAPIError: On API errors
        """
        try:
            request = ScrapeRequest(
                urls=urls,
                format=format,
                ignore_links=ignore_links,
                ignore_images=ignore_images,
                mobile=mobile
            )
        except ValidationError as e:
            raise DolfiValidationError(f"Invalid scrape parameters: {str(e)}")
        
        response_data = await self._make_request("POST", "/scrape", self._dataclass_to_dict(request))
        return self._build_scrape_response(response_data)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def __aenter__(self) -> "AsyncDolfiClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args: Any) -> bool:  # type: ignore
        """Async context manager exit."""
        await self.close()
        return False