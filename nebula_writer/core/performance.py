import asyncio
import time
from typing import Any, Dict, Optional


class NarrativeCache:
    """
    Simple Caching Layer (Step 8)
    Caches context blocks and summaries to improve performance.
    """

    _cache: Dict[str, Dict[str, Any]] = {}
    TTL = 300  # 5 minutes

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        if key in cls._cache:
            entry = cls._cache[key]
            if time.time() - entry["timestamp"] < cls.TTL:
                return entry["data"]
            else:
                del cls._cache[key]
        return None

    @classmethod
    def set(cls, key: str, data: Any):
        cls._cache[key] = {"data": data, "timestamp": time.time()}

    @classmethod
    def clear(cls):
        """Clear all cached narrative data."""
        cls._cache.clear()


async def run_parallel_checks(ripple_checker, description: str, research_engine=None):
    """
    Runs research and ripple checks in parallel (Step 8).
    """
    tasks = [asyncio.to_thread(ripple_checker.analyze_change, description)]

    if research_engine:
        # tasks.append(research_engine.perform_research(description))
        pass

    results = await asyncio.gather(*tasks)
    return {"ripples": results[0], "research": results[1] if len(results) > 1 else None}
