"""
HYPERION SearxNG Client — self-hosted meta-search, free, unlimited.

SearxNG is the primary search tool for ALL specialists. It aggregates
70+ search engines, has no API key, no rate limit, and no tracking.
It runs in Docker at the URL configured in settings.searxng_url.

This is NOT a generic "search the web" wrapper. It:
- Uses the SearxNG JSON API (/search?q=...&format=json)
- Supports category filtering (general, images, news, files, it, science)
- Supports language and time range filtering
- Returns structured results: title, url, snippet, engine, score
- Caches results to minimize redundant queries
- Handles network errors gracefully with retries
- Deduplicates results by URL

Architecture reference: §5.1 — "Self-hosted meta-search, free, unlimited.
Docker-based. Aggregates 70+ search engines. No API key, no rate limit,
no tracking."

Tool selection logic (§5.2):
  Search task:
    1. SearxNG (free, unlimited, fast) — always try first
    2. Jina search (if SearxNG returns poor results)
    3. Obscura (if the data is behind JS rendering)
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import time
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote_plus

import httpx


@dataclass
class SearchResult:
    """A single search result from SearxNG."""

    title: str
    url: str
    snippet: str = ""
    engine: str = ""
    score: float = 0.0
    category: str = "general"
    published_date: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "engine": self.engine,
            "score": self.score,
            "category": self.category,
            "published_date": self.published_date,
        }


@dataclass
class SearchResponse:
    """A complete search response from SearxNG."""

    query: str
    results: list[SearchResult] = field(default_factory=list)
    total: int = 0
    took_ms: int = 0
    engines_used: list[str] = field(default_factory=list)
    cached: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "took_ms": self.took_ms,
            "engines_used": self.engines_used,
            "cached": self.cached,
        }


class SearxNGClient:
    """SearxNG meta-search client.

    Self-hosted meta-search that aggregates 70+ search engines.
    No API key, no rate limit, no tracking. Docker-based.
    (§5.1)

    Usage:
        client = SearxNGClient(settings=settings)
        response = await client.search("Indian SaaS market size 2024", num_results=10)
        for result in response.results:
            print(f"{result.title} — {result.url}")
    """

    CACHE_DIR = "output/.searxng_cache"
    CACHE_TTL_SECONDS = 3600  # 1 hour
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings
        self._base_url = "http://localhost:8888"
        if settings:
            self._base_url = getattr(settings, "searxng_url", "http://localhost:8888")
        self._base_url = self._base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._cache: dict[str, tuple[float, SearchResponse]] = {}
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    @property
    def base_url(self) -> str:
        """Public accessor for the SearxNG base URL."""
        return self._base_url

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=httpx.Timeout(self.REQUEST_TIMEOUT),
                headers={"Accept": "application/json"},
            )
        return self._client

    def _cache_key(self, query: str, **kwargs: Any) -> str:
        """Generate a cache key from query and parameters."""
        key_str = f"{query}:{kwargs}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cached(self, key: str) -> SearchResponse | None:
        """Get a cached response if it exists and is not expired."""
        if key in self._cache:
            timestamp, response = self._cache[key]
            if time.time() - timestamp < self.CACHE_TTL_SECONDS:
                response.cached = True
                return response
            else:
                del self._cache[key]
        return None

    def _set_cached(self, key: str, response: SearchResponse) -> None:
        """Cache a response."""
        self._cache[key] = (time.time(), response)

    def _deduplicate(self, results: list[SearchResult]) -> list[SearchResult]:
        """Deduplicate results by URL, keeping the highest-scored version."""
        seen: dict[str, SearchResult] = {}
        for result in results:
            if result.url in seen:
                if result.score > seen[result.url].score:
                    seen[result.url] = result
            else:
                seen[result.url] = result
        return list(seen.values())

    async def search(
        self,
        query: str,
        num_results: int = 10,
        categories: str = "general",
        language: str = "en",
        time_range: str = "",
        engines: str = "",
        safesearch: int = 1,
    ) -> SearchResponse:
        """Search via SearxNG JSON API.

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            categories: Search categories (general, images, news, files, it, science)
            language: Language code (en, hi, fr, de, etc.)
            time_range: Time filter (day, week, month, year, or empty for all)
            engines: Comma-separated list of engines to use (empty = all)
            safesearch: Safe search level (0=off, 1=moderate, 2=strict)

        Returns:
            SearchResponse with deduplicated, scored results.
        """
        # Check cache
        cache_key = self._cache_key(query, num_results=num_results, categories=categories,
                                     language=language, time_range=time_range, engines=engines)
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        client = await self._get_client()

        params = {
            "q": query,
            "format": "json",
            "categories": categories,
            "language": language,
            "safesearch": str(safesearch),
            "pageno": "1",
        }
        if time_range:
            params["time_range"] = time_range
        if engines:
            params["engines"] = engines

        last_error: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await client.get("/search", params=params)
                response.raise_for_status()
                data = response.json()

                results: list[SearchResult] = []
                engines_used: set[str] = set()

                for item in data.get("results", []):
                    result = SearchResult(
                        title=item.get("content", "")[:0] or item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        engine=item.get("engine", ""),
                        score=float(item.get("score", 0.0)),
                        category=item.get("category", categories),
                        published_date=item.get("publishedDate", ""),
                    )
                    if result.url:
                        results.append(result)
                        if result.engine:
                            engines_used.add(result.engine)

                # Deduplicate by URL
                results = self._deduplicate(results)

                # Sort by score (descending) and limit
                results.sort(key=lambda r: r.score, reverse=True)
                results = results[:num_results]

                search_response = SearchResponse(
                    query=query,
                    results=results,
                    total=len(results),
                    took_ms=data.get("number_of_results", 0),
                    engines_used=list(engines_used),
                )

                self._set_cached(cache_key, search_response)
                return search_response

            except (httpx.HTTPError, httpx.RequestError, KeyError, ValueError) as e:
                last_error = e
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAY * (attempt + 1))
                continue

        # All retries failed — return empty response
        return SearchResponse(
            query=query,
            results=[],
            total=0,
            took_ms=0,
            engines_used=[],
        )

    async def search_images(
        self,
        query: str,
        num_results: int = 5,
        safesearch: int = 1,
    ) -> SearchResponse:
        """Search for images via SearxNG.

        Uses the 'images' category to find image results.
        """
        return await self.search(
            query=query,
            num_results=num_results,
            categories="images",
            safesearch=safesearch,
        )

    async def search_news(
        self,
        query: str,
        num_results: int = 10,
        time_range: str = "",
        language: str = "en",
    ) -> SearchResponse:
        """Search for news articles via SearxNG.

        Uses the 'news' category with optional time range filtering.
        """
        return await self.search(
            query=query,
            num_results=num_results,
            categories="news",
            time_range=time_range,
            language=language,
        )

    async def search_science(
        self,
        query: str,
        num_results: int = 10,
    ) -> SearchResponse:
        """Search for scientific/academic content via SearxNG.

        Uses the 'science' category which targets academic databases.
        """
        return await self.search(
            query=query,
            num_results=num_results,
            categories="science",
        )

    async def search_it(
        self,
        query: str,
        num_results: int = 10,
    ) -> SearchResponse:
        """Search for IT/technology content via SearxNG.

        Uses the 'it' category which targets tech-specific engines.
        """
        return await self.search(
            query=query,
            num_results=num_results,
            categories="it",
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> SearxNGClient:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
