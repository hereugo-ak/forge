"""Tool registry — SearxNG, Jina, Obscura, Crawl4AI, Wayback, Alpha Vantage, FRED, Unsplash, Second Brain, Unified Search, Unified Extract.

Every tool is assigned to agents who actually use it. No decorative tools.
No tool is assigned to an agent that doesn't need it. No agent lacks a tool
it does need. This is deliberate — tool assignment is a design decision.
(§5.1)
"""

from hyperion.tools.alpha_vantage import AlphaVantageClient, FundamentalData, StockQuote, TimeSeriesData
from hyperion.tools.crawl4ai import Crawl4AIClient, CrawlResult
from hyperion.tools.fred import FredClient, FREDSeries, FREDSearchResult
from hyperion.tools.jina import JinaClient, JinaReadResult, JinaSearchResponse, JinaSearchResult
from hyperion.tools.obscura import ObscuraClient, ObscuraFetchResult, ObscuraScrapeResult
from hyperion.tools.searxng import SearxNGClient, SearchResponse, SearchResult
from hyperion.tools.second_brain import SecondBrainClient, VaultNote, VaultSearchResult
from hyperion.tools.unified_extract import UnifiedExtract, UnifiedExtractResult
from hyperion.tools.unified_search import UnifiedSearch, UnifiedSearchResult
from hyperion.tools.unsplash import UnsplashClient, UnsplashImage, UnsplashSearchResult
from hyperion.tools.wayback import WaybackClient, WaybackContentResult, WaybackSnapshot, WaybackTimelineResult

__all__ = [
    # SearxNG
    "SearxNGClient",
    "SearchResult",
    "SearchResponse",
    # Jina
    "JinaClient",
    "JinaSearchResult",
    "JinaSearchResponse",
    "JinaReadResult",
    # Obscura
    "ObscuraClient",
    "ObscuraFetchResult",
    "ObscuraScrapeResult",
    # Crawl4AI
    "Crawl4AIClient",
    "CrawlResult",
    # Wayback
    "WaybackClient",
    "WaybackSnapshot",
    "WaybackTimelineResult",
    "WaybackContentResult",
    # Alpha Vantage
    "AlphaVantageClient",
    "StockQuote",
    "TimeSeriesData",
    "FundamentalData",
    # FRED
    "FredClient",
    "FREDSeries",
    "FREDSearchResult",
    # Unsplash
    "UnsplashClient",
    "UnsplashImage",
    "UnsplashSearchResult",
    # Second Brain
    "SecondBrainClient",
    "VaultNote",
    "VaultSearchResult",
    # Unified Search
    "UnifiedSearch",
    "UnifiedSearchResult",
    # Unified Extract
    "UnifiedExtract",
    "UnifiedExtractResult",
]
