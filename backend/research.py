"""
Nebula-Writer Research Engine
Free/open-source web search for fiction writing research
Uses DuckDuckGo HTML (no API key required) or custom SearXNG instance
"""

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict, List


class SearchResult:
    """A single search result"""

    def __init__(self, title: str, url: str, snippet: str, source: str = None):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.source = source or self._extract_domain(url)
        self.created_at = datetime.now().isoformat()

    def _extract_domain(self, url: str) -> str:
        try:
            from urllib.parse import urlparse

            return urlparse(url).netloc
        except:
            return "unknown"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "created_at": self.created_at,
        }


class ResearchEngine:
    """
    Free web research engine for fiction writing.
    Uses DuckDuckGo HTML (no API key) or configurable to use SearXNG/self-hosted.
    """

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.search_engine = self.config.get("search_engine", "duckduckgo")
        self.searx_url = self.config.get("searx_url", "http://localhost:8888")
        self.cache = {}  # Simple in-memory cache
        self.recent_searches = []  # Track research history

    def search(self, query: str, num_results: int = 5) -> List[SearchResult]:
        """
        Search the web for information.
        No API key required for DuckDuckGo!
        """
        # Check cache
        cache_key = f"{query}:{num_results}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            if self.search_engine == "duckduckgo":
                results = self._duckduckgo_search(query, num_results)
            elif self.search_engine == "searxng":
                results = self._searxng_search(query, num_results)
            else:
                results = self._duckduckgo_search(query, num_results)

            # Cache results
            self.cache[cache_key] = results
            self.recent_searches.append(
                {"query": query, "timestamp": datetime.now().isoformat(), "results_count": len(results)}
            )

            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _duckduckgo_search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using DuckDuckGo HTML (free, no API key)
        """
        results = []

        # Encode query
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://duckduckgo.com/html/?q={encoded_query}&kl=wt-wt"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
        }

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode("utf-8", errors="ignore")

            # Parse results
            # DuckDuckGo HTML format
            pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            snippets_pattern = r'<a class="result__a"[^>]*>[^<]+</a>\s*<p class="result__snippet">([^<]+)</p>'

            matches = re.findall(pattern, html)
            snippets_match = re.findall(snippets_pattern, html)

            snippets_dict = {m[0]: m[1] for m in snippets_match} if snippets_match else {}

            for _i, (url, title) in enumerate(matches[:num_results]):
                # Clean title
                title = re.sub(r"<[^>]+>", "", title)
                title = title.strip()

                # Get snippet
                snippet = snippets_dict.get(url, "")
                snippet = re.sub(r"<[^>]+>", "", snippet)
                snippet = snippet.strip()

                if url and title:
                    results.append(SearchResult(title, url, snippet))

        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")

        return results

    def _searxng_search(self, query: str, num_results: int) -> List[SearchResult]:
        """
        Search using SearXNG (self-hosted, privacy-respecting search)
        """
        results = []

        encoded_query = urllib.parse.quote_plus(query)
        url = f"{self.searx_url}/search?q={encoded_query}&format=json&engines=duckduckgo,brave&limit={num_results}"

        headers = {
            "User-Agent": "Nebula-Writer/1.0",
            "Accept": "application/json",
        }

        req = urllib.request.Request(url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))

            for result in data.get("results", [])[:num_results]:
                results.append(
                    SearchResult(
                        title=result.get("title", ""),
                        url=result.get("url", ""),
                        snippet=result.get("content", ""),
                        source=result.get("engine", ""),
                    )
                )
        except Exception as e:
            print(f"SearXNG search failed: {e}")

        return results

    def research_for_fiction(self, topic: str, context: Dict = None) -> Dict:
        """
        Research a topic specifically for fiction writing.
        Returns structured research data.
        """
        context = context or {}
        context.get("genre", "")
        setting = context.get("setting", "")
        time_period = context.get("time_period", "")

        results = {
            "topic": topic,
            "researched_at": datetime.now().isoformat(),
            "facts": [],
            "sources": [],
            "fiction_notes": "",
        }

        # Build search queries based on context
        queries = []

        if time_period:
            queries.append(f"{time_period} {topic}")
        if setting:
            queries.append(f"{setting} {topic}")
        queries.append(topic)

        # Also search for "<topic fiction writing tips>"
        if not any(q for q in queries if "tips" in q or "fiction" in q):
            queries.append(f"{topic} fiction writing")

        all_facts = []

        for query in queries[:3]:  # Limit to 3 searches
            search_results = self.search(query, num_results=3)

            for result in search_results:
                if result.snippet:
                    all_facts.append(
                        {"fact": result.snippet, "source": result.source, "url": result.url, "query_used": query}
                    )

                if result.url:
                    results["sources"].append({"title": result.title, "url": result.url, "source": result.source})

        # Deduplicate facts
        seen = set()
        for fact in all_facts:
            fact_text = fact["fact"][:100].lower()  # Dedupe by first 100 chars
            if fact_text not in seen:
                seen.add(fact_text)
                results["facts"].append(fact)

        return results

    def get_historical_context(self, year_or_period: str, location: str = "") -> Dict:
        """
        Get historical context for a time period and optional location.
        Useful for historical fiction.
        """
        query = f"{year_or_period} {location} history daily life".strip()
        results = self.search(query, num_results=5)

        context = {
            "period": year_or_period,
            "location": location,
            "queried_at": datetime.now().isoformat(),
            "research": [r.to_dict() for r in results],
        }

        return context

    def get_location_facts(self, location_name: str) -> Dict:
        """
        Get facts about a real-world location for fiction accuracy.
        """
        query = f"{location_name} city description geography culture"
        results = self.search(query, num_results=5)

        return {
            "location": location_name,
            "queried_at": datetime.now().isoformat(),
            "facts": [r.to_dict() for r in results],
        }


def create_research_engine() -> ResearchEngine:
    """Create a default research engine instance"""
    return ResearchEngine()


if __name__ == "__main__":
    # Test
    engine = create_research_engine()

    print("Testing research engine...")

    # Test basic search
    results = engine.search("detective 1920s Shanghai", num_results=3)
    print(f"\nFound {len(results)} results:")
    for r in results:
        print(f"  - {r.title}")
        print(f"    {r.snippet[:100]}...")

    # Test fiction research
    research = engine.research_for_fiction(
        "Art Deco architecture", context={"time_period": "1920s", "setting": "Shanghai"}
    )
    print(f"\nResearch: {len(research['facts'])} facts collected")

    print("\nResearch engine working!")
