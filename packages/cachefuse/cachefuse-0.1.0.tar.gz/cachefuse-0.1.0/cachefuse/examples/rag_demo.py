from __future__ import annotations

import os
import time
from typing import List

from cachefuse.api.decorators import llm
from cachefuse.api.cache import Cache


def _delay_ms() -> int:
    try:
        return int(os.getenv("DEMO_DELAY_MS", "200"))
    except Exception:
        return 200


def build_cache() -> Cache:
    return Cache.from_env()


def run_demo() -> None:
    cache = build_cache()

    @llm(cache=cache, ttl="7d", tag="summarize-v1", template_version="1")
    def summarize(text: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
        time.sleep(_delay_ms() / 1000.0)
        return f"summary[{len(text)}]"

    docs: List[str] = [
        "CacheFuse speeds up repeated LLM calls.",
        "Decorators make caching declarative.",
        "SQLite by default; Redis optional.",
    ]

    def timed_call() -> float:
        start = time.perf_counter()
        for d in docs:
            _ = summarize(d)
        return (time.perf_counter() - start) * 1000.0

    t1 = timed_call()
    t2 = timed_call()
    print(f"First run:  {t1:.1f} ms, Second run (cached): {t2:.1f} ms")
    stats = cache.stats()
    print(
        f"calls={stats.get('total_calls')}, hits={stats.get('hits')}, hit_rate={stats.get('hit_rate'):.2f}"
    )


if __name__ == "__main__":
    run_demo()

