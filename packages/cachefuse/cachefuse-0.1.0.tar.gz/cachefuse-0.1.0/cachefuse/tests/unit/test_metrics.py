from __future__ import annotations

from cachefuse.api.cache import Cache
from cachefuse.api.decorators import llm
from cachefuse.config import CacheConfig


def test_stats_hit_rate_and_latency():
    cache = Cache.from_config(CacheConfig(backend="memory"))

    calls = {"n": 0}

    @llm(cache=cache, ttl="10s", tag="m", template_version="1")
    def f(x: int) -> int:
        calls["n"] += 1
        return x + 1

    # 1 miss
    assert f(1) == 2
    # 3 hits
    for _ in range(3):
        assert f(1) == 2

    s = cache.stats()
    assert s["total_calls"] == 4
    assert s["hits"] == 3
    assert 0.70 <= s["hit_rate"] <= 0.90
    assert s["avg_latency_ms"] >= 0.0

