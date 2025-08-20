"""
Tavily Search Tool for Web Research

This module provides a Tavily-powered web search tool that can be used
by agents for real-time web research and information gathering.
"""

import os
import re
import asyncio
import logging
from typing import Any, Union, Optional, List, Dict
from datetime import datetime
from asyncio import Semaphore

from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)

# Rate limiting constants
DEFAULT_MAX_CONCURRENT_SEARCHES = 3
DEFAULT_RATE_LIMIT_DELAY = 0.1  # seconds between requests

# Query sanitization constants
MAX_QUERY_LENGTH = 500
SANITIZATION_PATTERN = re.compile(r'[<>"\';\\]')


def sanitize_query(query: str) -> str:
    """
    Sanitize search query to prevent injection attacks and ensure valid input.

    Args:
        query: Raw search query string

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query is empty or too long after sanitization
    """
    if not query or not query.strip():
        raise ValueError("Search query cannot be empty")

    # Remove potentially harmful characters
    sanitized = SANITIZATION_PATTERN.sub("", query.strip())

    # Truncate if too long
    if len(sanitized) > MAX_QUERY_LENGTH:
        sanitized = sanitized[:MAX_QUERY_LENGTH].rstrip()
        logger.warning(f"Query truncated to {MAX_QUERY_LENGTH} characters")

    if not sanitized:
        raise ValueError("Query becomes empty after sanitization")

    return sanitized


class TavilySearchInput(BaseModel):
    """Input schema for Tavily search tool."""

    query: str = Field(description="The search query to execute")
    max_results: int | None = Field(
        default=5, description="Maximum number of search results to return (1-20)"
    )
    search_depth: str | None = Field(
        default="basic", description="Search depth: 'basic' or 'advanced'"
    )
    topic: str | None = Field(
        default="general", description="Search topic: 'general', 'news', or 'finance'"
    )
    time_range: str | None = Field(
        default=None, description="Time filter: 'day', 'week', 'month', or 'year'"
    )
    include_answer: bool | None = Field(
        default=True, description="Include a short answer to the query"
    )
    include_raw_content: bool | None = Field(
        default=True, description="Include cleaned HTML content from search results"
    )
    include_images: bool | None = Field(
        default=False, description="Include related images in the response"
    )
    include_domains: list[str] | None = Field(
        default=None, description="List of domains to specifically include"
    )
    exclude_domains: list[str] | None = Field(
        default=None, description="List of domains to specifically exclude"
    )


class TavilyWebSearchTool:
    """
    Tavily-powered web search tool for comprehensive internet research.

    This tool uses Tavily's search API to perform real-time web searches
    and return structured, AI-ready results including summaries, sources,
    and content snippets.
    """

    def __init__(
        self,
        api_key: str | None = None,
        max_concurrent: int = DEFAULT_MAX_CONCURRENT_SEARCHES,
        rate_limit_delay: float = DEFAULT_RATE_LIMIT_DELAY,
    ):
        """
        Initialize the Tavily search tool.

        Args:
            api_key: Tavily API key. If not provided, will use TAVILY_API_KEY env var.
            max_concurrent: Maximum number of concurrent searches allowed.
            rate_limit_delay: Delay in seconds between requests for rate limiting.

        Raises:
            ValueError: If API key is missing or invalid.
            ImportError: If required dependencies are not available.
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Tavily API key is required. Set TAVILY_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Rate limiting setup
        self._semaphore = Semaphore(max_concurrent)
        self._rate_limit_delay = rate_limit_delay

        # Initialize the Tavily search tool with default settings
        self.tavily_tool = TavilySearch(
            max_results=5,
            search_depth="basic",
            include_answer=True,
            include_raw_content=True,
            include_images=False,
        )

        logger.info("TavilyWebSearchTool initialized successfully")

    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        topic: str = "general",
        time_range: str | None = None,
        include_answer: bool = True,
        include_raw_content: bool = True,
        include_images: bool = False,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform a web search using Tavily's API.

        Args:
            query: The search query
            max_results: Maximum number of results to return (1-20)
            search_depth: 'basic' or 'advanced' search depth
            topic: 'general', 'news', or 'finance'
            time_range: 'day', 'week', 'month', or 'year'
            include_answer: Include AI-generated answer
            include_raw_content: Include cleaned HTML content
            include_images: Include related images
            include_domains: Specific domains to include
            exclude_domains: Specific domains to exclude

        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Sanitize the query first
            sanitized_query = sanitize_query(query)
            logger.info(f"Performing Tavily search for: {sanitized_query}")

            # Create a new TavilySearch instance with the specific parameters
            search_tool = TavilySearch(
                max_results=min(max_results, 20),  # Cap at 20
                search_depth=search_depth,
                topic=topic,
                time_range=time_range,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
            )

            # Perform the search with sanitized query
            search_input = {"query": sanitized_query}
            raw_results = search_tool.invoke(search_input)

            # Parse and structure the results
            structured_results = self._structure_results(raw_results, query)

            logger.info(
                f"Tavily search completed. Found {len(structured_results.get('results', []))} results"
            )

            return structured_results

        except ValueError as e:
            logger.error(f"Invalid query for Tavily search: {e}")
            raise
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}")
            raise RuntimeError(f"Tavily search failed for query '{query}': {e}")

    async def search_async(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = "basic",
        topic: str = "general",
        time_range: str | None = None,
        include_answer: bool = True,
        include_raw_content: bool = True,
        include_images: bool = False,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform an async web search using Tavily's API with rate limiting.

        Args:
            query: The search query
            max_results: Maximum number of results to return (1-20)
            search_depth: 'basic' or 'advanced' search depth
            topic: 'general', 'news', or 'finance'
            time_range: 'day', 'week', 'month', or 'year'
            include_answer: Include AI-generated answer
            include_raw_content: Include cleaned HTML content
            include_images: Include related images
            include_domains: Specific domains to include
            exclude_domains: Specific domains to exclude

        Returns:
            Dictionary containing search results and metadata
        """
        async with self._semaphore:
            # Apply rate limiting delay
            await asyncio.sleep(self._rate_limit_delay)

            # Use the synchronous search method for the actual API call
            # This is a common pattern when wrapping sync APIs with async rate limiting
            return self.search(
                query=query,
                max_results=max_results,
                search_depth=search_depth,
                topic=topic,
                time_range=time_range,
                include_answer=include_answer,
                include_raw_content=include_raw_content,
                include_images=include_images,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
            )

    def _structure_results(
        self, raw_results: Union[str, dict], query: str
    ) -> dict[str, Any]:
        """
        Structure the raw Tavily results into a consistent format.

        Args:
            raw_results: Raw results from Tavily API
            query: Original search query

        Returns:
            Structured results dictionary
        """
        try:
            # If raw_results is a string (JSON), parse it
            if isinstance(raw_results, str):
                import json

                results_data = json.loads(raw_results)
            else:
                results_data = raw_results

            # Extract key components
            search_results = results_data.get("results", [])
            answer = results_data.get("answer")
            images = results_data.get("images", [])
            follow_up_questions = results_data.get("follow_up_questions", [])

            # Structure the results
            structured_results = {
                "query": query,
                "answer": answer,
                "results": [],
                "images": images,
                "follow_up_questions": follow_up_questions,
                "total_results": len(search_results),
                "timestamp": datetime.now().isoformat(),
                "success": True,
            }

            # Process each search result
            for result in search_results:
                structured_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "raw_content": result.get("raw_content"),
                    "score": result.get("score", 0.0),
                    "published_date": result.get("published_date"),
                }
                structured_results["results"].append(structured_result)

            return structured_results

        except Exception as e:
            logger.error(f"Failed to structure Tavily results: {e}")
            raise RuntimeError(
                f"Failed to parse Tavily results for query '{query}': {e}"
            )


# Tool function for use with the agent system
def tavily_web_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    topic: str = "general",
    time_range: Optional[str] = None,
    include_answer: bool = True,
    include_raw_content: bool = True,
    include_images: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Perform a web search using Tavily's search API.

    This function provides real-time web search capabilities using Tavily's
    AI-optimized search API. It returns comprehensive search results including
    summaries, source URLs, content snippets, and optional AI-generated answers.

    Args:
        query: The search query to execute
        max_results: Maximum number of search results to return (1-20, default: 5)
        search_depth: Search depth - 'basic' or 'advanced' (default: 'basic')
        topic: Search topic - 'general', 'news', or 'finance' (default: 'general')
        time_range: Time filter - 'day', 'week', 'month', or 'year' (default: None)
        include_answer: Include AI-generated answer to the query (default: True)
        include_raw_content: Include cleaned HTML content from results (default: True)
        include_images: Include related images in the response (default: False)
        include_domains: List of domains to specifically include (default: None)
        exclude_domains: List of domains to specifically exclude (default: None)

    Returns:
        Dictionary containing:
        - query: Original search query
        - answer: AI-generated answer (if requested)
        - results: List of search results with title, URL, content, score
        - images: List of related images (if requested)
        - follow_up_questions: Suggested follow-up questions
        - total_results: Number of results found
        - timestamp: When the search was performed
        - success: Whether the search was successful

    Example:
        >>> results = tavily_web_search("latest AI developments 2024")
        >>> print(results["answer"])
        >>> for result in results["results"]:
        ...     print(f"{result['title']}: {result['url']}")
    """
    try:
        # Initialize the tool (will use TAVILY_API_KEY from environment)
        search_tool = TavilyWebSearchTool()

        # Perform the search
        return search_tool.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            topic=topic,
            time_range=time_range,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
        )

    except Exception as e:
        logger.error(f"tavily_web_search function failed: {e}")
        raise RuntimeError(f"Tavily web search failed: {e}")


# Alternative function name for compatibility
def search_web_tavily(query: str, **kwargs) -> dict[str, Any]:
    """
    Alternative function name for Tavily web search.

    This is an alias for tavily_web_search() to provide flexibility
    in naming conventions.
    """
    return tavily_web_search(query, **kwargs)
