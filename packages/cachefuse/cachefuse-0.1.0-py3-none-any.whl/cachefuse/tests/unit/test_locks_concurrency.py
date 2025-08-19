from __future__ import annotations

import threading
import time
from typing import List

from cachefuse.api.cache import Cache
from cachefuse.config import CacheConfig


def test_concurrent_get_or_set_with_lock_single_compute():
    cfg = CacheConfig(backend="memory")
    cache = Cache.from_config(cfg)

    key = "concurrent-key"
    compute_calls = {"count": 0}

    def compute():
        compute_calls["count"] += 1
        # Simulate some work
        time.sleep(0.05)
        return "value"

    results: List[str] = []

    def worker() -> None:
        val = cache.get_or_set_with_lock(key, compute=compute, ttl=5)
        results.append(val)  # type: ignore[arg-type]

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Exactly one compute call should have executed
    assert compute_calls["count"] == 1
    assert len(results) == 10 and all(r == "value" for r in results)

