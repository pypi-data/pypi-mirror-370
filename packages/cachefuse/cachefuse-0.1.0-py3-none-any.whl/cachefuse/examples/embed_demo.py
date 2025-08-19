from __future__ import annotations

import os
import time
from typing import List

from cachefuse.api.decorators import embed
from cachefuse.api.cache import Cache


def _delay_ms() -> int:
    try:
        return int(os.getenv("DEMO_DELAY_MS", "50"))
    except Exception:
        return 50


def build_cache() -> Cache:
    return Cache.from_env()


def run_demo() -> None:
    cache = build_cache()

    @embed(cache=cache, ttl="30d", tag="embed-minilm", template_version="1")
    def make_vecs(docs: List[str], model: str = "all-MiniLM-L6-v2") -> List[int]:
        time.sleep(_delay_ms() / 1000.0)
        return [len(d) for d in docs]

    docs = ["a", "bb", "ccc", "dddd"]

    def timed_call() -> float:
        start = time.perf_counter()
        _ = make_vecs(docs)
        return (time.perf_counter() - start) * 1000.0

    t1 = timed_call()
    t2 = timed_call()
    print(f"First run:  {t1:.1f} ms, Second run (cached): {t2:.1f} ms")


if __name__ == "__main__":
    run_demo()

