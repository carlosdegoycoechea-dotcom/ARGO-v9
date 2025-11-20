"""
ARGO v9.0 - Web Search Engine
Real-time web search with multiple providers
Supports: DuckDuckGo, Serper, Brave, Tavily
"""
import os
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

from core.logger import get_logger

logger = get_logger("WebSearch")


@dataclass
class SearchResult:
    """Web search result"""
    title: str
    url: str
    snippet: str
    source: str = "web"
    published_date: Optional[str] = None
    score: float = 0.0


class WebSearchEngine:
    """
    Unified web search engine with multiple providers

    Providers:
    - duckduckgo: Free, no API key required
    - serper: $5/1000 queries, Google results
    - brave: Free tier 2000/month
    - tavily: AI-optimized search
    """

    def __init__(self, provider: str = "duckduckgo"):
        """
        Initialize web search engine

        Args:
            provider: Search provider (duckduckgo, serper, brave, tavily)
        """
        self.provider = provider.lower()

        # API keys from environment
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")

        logger.info(f"Web search engine initialized with provider: {self.provider}")

    def search(
        self,
        query: str,
        count: int = 5,
        **kwargs
    ) -> List[SearchResult]:
        """
        Perform web search

        Args:
            query: Search query
            count: Number of results
            **kwargs: Provider-specific parameters

        Returns:
            List of SearchResult objects
        """
        logger.info(f"Web search: '{query}' (provider: {self.provider}, count: {count})")

        try:
            if self.provider == "duckduckgo":
                results = self._search_duckduckgo(query, count)
            elif self.provider == "serper":
                results = self._search_serper(query, count)
            elif self.provider == "brave":
                results = self._search_brave(query, count)
            elif self.provider == "tavily":
                results = self._search_tavily(query, count)
            else:
                logger.warning(f"Unknown provider: {self.provider}, falling back to DuckDuckGo")
                results = self._search_duckduckgo(query, count)

            logger.info(f"Found {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Web search failed: {e}", exc_info=True)
            return []

    def _search_duckduckgo(self, query: str, count: int) -> List[SearchResult]:
        """
        Search using DuckDuckGo (free, no API key)

        Uses duckduckgo_search library
        """
        try:
            from duckduckgo_search import DDGS
            import time

            results = []
            max_retries = 2
            retry_delay = 2  # seconds

            for attempt in range(max_retries + 1):
                try:
                    with DDGS() as ddgs:
                        search_results = ddgs.text(query, max_results=count)

                        for idx, result in enumerate(search_results):
                            results.append(SearchResult(
                                title=result.get('title', ''),
                                url=result.get('href', ''),
                                snippet=result.get('body', ''),
                                source='duckduckgo',
                                score=1.0 - (idx * 0.1)  # Descending score
                            ))

                    return results

                except Exception as e:
                    error_msg = str(e).lower()
                    # Check for rate limit errors
                    if ('ratelimit' in error_msg or '202' in error_msg or 'rate limit' in error_msg):
                        if attempt < max_retries:
                            logger.warning(f"DuckDuckGo rate limit hit, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            logger.error(f"DuckDuckGo rate limit exceeded after {max_retries} retries")
                            # Return informative error result instead of empty list
                            return [SearchResult(
                                title="Rate Limit Exceeded",
                                url="",
                                snippet="DuckDuckGo rate limit exceeded. Try again in a few minutes or configure alternative search providers (Brave, Serper, Tavily) in your .env file.",
                                source='error'
                            )]
                    else:
                        # Other error, raise it
                        raise

        except ImportError:
            logger.warning("duckduckgo_search not installed. Run: pip install duckduckgo-search")
            return [SearchResult(
                title="Library Not Installed",
                url="",
                snippet="duckduckgo_search library not installed. Run: pip install duckduckgo-search",
                source='error'
            )]
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return [SearchResult(
                title="Search Failed",
                url="",
                snippet=f"DuckDuckGo search failed: {str(e)}",
                source='error'
            )]

    def _search_serper(self, query: str, count: int) -> List[SearchResult]:
        """
        Search using Serper API (Google results)

        Requires: SERPER_API_KEY in .env
        Cost: $5 per 1000 searches
        Sign up: https://serper.dev
        """
        if not self.serper_key:
            logger.warning("SERPER_API_KEY not found in environment")
            return []

        try:
            url = "https://google.serper.dev/search"

            payload = {
                "q": query,
                "num": count
            }

            headers = {
                "X-API-KEY": self.serper_key,
                "Content-Type": "application/json"
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            # Organic results
            for idx, item in enumerate(data.get('organic', [])[:count]):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('link', ''),
                    snippet=item.get('snippet', ''),
                    source='serper',
                    published_date=item.get('date'),
                    score=1.0 - (idx * 0.1)
                ))

            return results

        except requests.RequestException as e:
            logger.error(f"Serper API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Serper search failed: {e}")
            return []

    def _search_brave(self, query: str, count: int) -> List[SearchResult]:
        """
        Search using Brave Search API

        Requires: BRAVE_API_KEY in .env
        Free tier: 2000 queries/month
        Sign up: https://brave.com/search/api/
        """
        if not self.brave_key:
            logger.warning("BRAVE_API_KEY not found in environment")
            return []

        try:
            url = "https://api.search.brave.com/res/v1/web/search"

            params = {
                "q": query,
                "count": count
            }

            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_key
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            # Web results
            for idx, item in enumerate(data.get('web', {}).get('results', [])[:count]):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('description', ''),
                    source='brave',
                    published_date=item.get('page_age'),
                    score=1.0 - (idx * 0.1)
                ))

            return results

        except requests.RequestException as e:
            logger.error(f"Brave API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []

    def _search_tavily(self, query: str, count: int) -> List[SearchResult]:
        """
        Search using Tavily API (AI-optimized)

        Requires: TAVILY_API_KEY in .env
        Free tier: 1000 queries/month
        Sign up: https://tavily.com
        """
        if not self.tavily_key:
            logger.warning("TAVILY_API_KEY not found in environment")
            return []

        try:
            url = "https://api.tavily.com/search"

            payload = {
                "api_key": self.tavily_key,
                "query": query,
                "max_results": count,
                "search_depth": "basic",
                "include_answer": False,
                "include_raw_content": False
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            data = response.json()
            results = []

            # Results
            for idx, item in enumerate(data.get('results', [])[:count]):
                results.append(SearchResult(
                    title=item.get('title', ''),
                    url=item.get('url', ''),
                    snippet=item.get('content', ''),
                    source='tavily',
                    published_date=item.get('published_date'),
                    score=item.get('score', 1.0 - (idx * 0.1))
                ))

            return results

        except requests.RequestException as e:
            logger.error(f"Tavily API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    def format_results_for_context(self, results: List[SearchResult]) -> str:
        """
        Format search results for LLM context

        Args:
            results: List of SearchResult objects

        Returns:
            Formatted string for context
        """
        if not results:
            return "No web search results found."

        context = "Web Search Results:\n\n"

        for idx, result in enumerate(results, 1):
            context += f"{idx}. {result.title}\n"
            context += f"   Source: {result.url}\n"
            context += f"   {result.snippet}\n\n"

        return context


def should_use_web_search(query: str) -> bool:
    """
    Determine if query should trigger web search

    Args:
        query: User query

    Returns:
        True if web search recommended
    """
    # Keywords that trigger web search
    web_keywords = [
        "latest", "recent", "current", "today", "news", "update",
        "what is", "who is", "when did", "search", "find",
        "google", "web", "internet", "online",
        "actualidad", "noticia", "información", "buscar", "busca"
    ]

    query_lower = query.lower()

    return any(keyword in query_lower for keyword in web_keywords)


# Example usage
if __name__ == "__main__":
    # Test DuckDuckGo (no API key needed)
    engine = WebSearchEngine(provider="duckduckgo")
    results = engine.search("Python programming best practices", count=3)

    for result in results:
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:100]}...")
        print("-" * 80)
