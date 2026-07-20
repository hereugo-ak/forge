"""
HYPERION Unified Search — SearxNG → Jina → Obscura → DDG fallback chain.

This is NOT a generic "search multiple engines" wrapper. It implements
the exact tool selection logic from §5.2:

  Search task:
    1. SearxNG (free, unlimited, fast) — always try first
    2. Jina search (if SearxNG returns poor results)
    3. Obscura (if the data is behind JS rendering)

The unified search chain:
1. Tries SearxNG first (free, unlimited, aggregates 70+ engines)
2. If SearxNG returns fewer than `min_results` results, tries Jina
3. If Jina also returns poor results, tries Obscura fetch on top URLs
4. Merges and deduplicates all results
5. Returns a unified response with provenance (which tool found what)

This is how agents get the best possible search results without
wasting API calls on tools that aren't needed.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

from hyperion.tools.jina import JinaClient, JinaSearchResult
from hyperion.tools.obscura import ObscuraClient, ObscuraFetchResult
from hyperion.tools.searxng import SearxNGClient, SearchResult, SearchResponse


@dataclass
class UnifiedSearchResult:
    """A unified search result from multiple search tools."""

    query: str
    results: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    tools_used: list[str] = field(default_factory=list)
    searxng_results: int = 0
    jina_results: int = 0
    obscura_results: int = 0
    took_ms: int = 0
    cached: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "results": self.results,
            "total": self.total,
            "tools_used": self.tools_used,
            "searxng_results": self.searxng_results,
            "jina_results": self.jina_results,
            "obscura_results": self.obscura_results,
            "took_ms": self.took_ms,
            "cached": self.cached,
        }


class UnifiedSearch:
    """Unified search with fallback chain: SearxNG → Jina → Obscura.

    Implements the tool selection logic from §5.2. Tries SearxNG first
    (free, unlimited), falls back to Jina if results are poor, and
    finally tries Obscura for JS-rendered content.

    Usage:
        search = UnifiedSearch(settings=settings)
        result = await search.search("Indian SaaS market size 2024", min_results=5)
        for r in result.results:
            print(f"[{r['source']}] {r['title']} — {r['url']}")
    """

    MIN_RESULTS_THRESHOLD = 5  # If SearxNG returns fewer than this, try Jina
    JINA_MIN_RESULTS = 3       # If Jina also returns fewer than this, try Obscura
    OBSCURA_MAX_URLS = 3       # Max URLs to fetch with Obscura (expensive)

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings
        self._searxng: SearxNGClient | None = None
        self._jina: JinaClient | None = None
        self._obscura: ObscuraClient | None = None

    async def _get_searxng(self) -> SearxNGClient:
        if self._searxng is None:
            self._searxng = SearxNGClient(settings=self.settings)
        return self._searxng

    async def _get_jina(self) -> JinaClient:
        if self._jina is None:
            self._jina = JinaClient(settings=self.settings)
        return self._jina

    async def _get_obscura(self) -> ObscuraClient:
        if self._obscura is None:
            self._obscura = ObscuraClient(settings=self.settings)
        return self._obscura

    def _deduplicate(self, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Deduplicate results by URL, merging source information."""
        seen: dict[str, dict[str, Any]] = {}
        for result in results:
            url = result.get("url", "")
            if not url:
                continue
            if url in seen:
                # Merge sources
                existing_sources = seen[url].get("sources", [])
                new_source = result.get("source", "")
                if new_source and new_source not in existing_sources:
                    existing_sources.append(new_source)
                    seen[url]["sources"] = existing_sources
            else:
                result["sources"] = [result.get("source", "")]
                seen[url] = result
        return list(seen.values())

    async def search(
        self,
        query: str,
        num_results: int = 10,
        min_results: int = MIN_RESULTS_THRESHOLD,
        categories: str = "general",
        language: str = "en",
        use_jina_fallback: bool = True,
        use_obscura_fallback: bool = True,
    ) -> UnifiedSearchResult:
        """Search with the full fallback chain.

        Args:
            query: Search query string
            num_results: Maximum number of results to return
            min_results: Minimum results before trying fallback tools
            categories: SearxNG category filter
            language: Language code
            use_jina_fallback: Whether to try Jina if SearxNG is insufficient
            use_obscura_fallback: Whether to try Obscura if Jina is insufficient

        Returns:
            UnifiedSearchResult with merged, deduplicated results.
        """
        tools_used: list[str] = []
        all_results: list[dict[str, Any]] = []
        searxng_count = 0
        jina_count = 0
        obscura_count = 0

        # Step 1: SearxNG (always try first — free, unlimited, fast)
        try:
            searxng = await self._get_searxng()
            searxng_resp = await searxng.search(
                query=query,
                num_results=num_results,
                categories=categories,
                language=language,
            )

            for result in searxng_resp.results:
                all_results.append({
                    "title": result.title,
                    "url": result.url,
                    "snippet": result.snippet,
                    "source": "searxng",
                    "engine": result.engine,
                    "score": result.score,
                })
            searxng_count = len(searxng_resp.results)
            tools_used.append("searxng")

        except (ConnectionError, RuntimeError, OSError):
            pass

        # Step 2: Jina (if SearxNG returned insufficient results)
        if searxng_count < min_results and use_jina_fallback:
            try:
                jina = await self._get_jina()
                jina_resp = await jina.search(query=query, num_results=num_results)

                for result in jina_resp.results:
                    all_results.append({
                        "title": result.title,
                        "url": result.url,
                        "snippet": result.snippet,
                        "source": "jina",
                        "content": result.content,
                    })
                jina_count = len(jina_resp.results)
                tools_used.append("jina")

            except (ConnectionError, RuntimeError, OSError):
                pass

        # Step 3: Obscura (if Jina also returned insufficient results)
        if (searxng_count + jina_count) < min_results and use_obscura_fallback:
            # Try fetching top URLs with Obscura for JS-rendered content
            top_urls = [r["url"] for r in all_results[:self.OBSCURA_MAX_URLS] if r.get("url")]
            if top_urls:
                try:
                    obscura = await self._get_obscura()
                    scrape_result = await obscura.scrape(top_urls, concurrency=3)

                    for fetch_result in scrape_result.results:
                        if fetch_result.status_code == 200 and fetch_result.content:
                            all_results.append({
                                "title": fetch_result.title,
                                "url": fetch_result.url,
                                "snippet": fetch_result.content[:200],
                                "source": "obscura",
                                "content": fetch_result.content,
                            })
                            obscura_count += 1

                    if obscura_count > 0:
                        tools_used.append("obscura")

                except (ConnectionError, RuntimeError, OSError):
                    pass

        # Deduplicate and sort
        all_results = self._deduplicate(all_results)
        all_results.sort(
            key=lambda r: (
                r.get("score", 0) if r.get("source") == "searxng" else 0.5,
                len(r.get("snippet", "")),
            ),
            reverse=True,
        )
        all_results = all_results[:num_results]

        return UnifiedSearchResult(
            query=query,
            results=all_results,
            total=len(all_results),
            tools_used=tools_used,
            searxng_results=searxng_count,
            jina_results=jina_count,
            obscura_results=obscura_count,
        )

    async def search_news(
        self,
        query: str,
        num_results: int = 10,
        time_range: str = "",
    ) -> UnifiedSearchResult:
        """Search for news articles with the fallback chain."""
        result = await self.search(
            query=query,
            num_results=num_results,
            categories="news",
            time_range=time_range if time_range else None,  # type: ignore
        )
        return result

    async def close(self) -> None:
        """Close all underlying clients."""
        if self._searxng:
            await self._searxng.close()
        if self._jina:
            await self._jina.close()
        if self._obscura:
            await self._obscura.close()

    async def __aenter__(self) -> UnifiedSearch:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
