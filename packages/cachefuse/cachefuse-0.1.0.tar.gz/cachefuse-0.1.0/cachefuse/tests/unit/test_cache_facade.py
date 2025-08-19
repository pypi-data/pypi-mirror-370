from __future__ import annotations

import time as _time

from cachefuse.api.cache import Cache
from cachefuse.config import CacheConfig


def test_roundtrip_set_get_with_memory_backend() -> None:
    # Force memory backend through config
    cfg = CacheConfig(backend="memory")
    cache = Cache.from_env()  # default uses memory fallback for now
    # Overwrite to ensure isolation
    cache = Cache(backend=cache._backend, config=cfg)  # type: ignore[attr-defined]

    cache.set("k1", {"v": 1}, ttl=60, meta={"m": 2}, tags=["a", "b"])
    assert cache.get("k1") == {"v": 1}
    st = cache.stats()
    assert st["entries"] >= 1


def test_ttl_expiry(monkeypatch) -> None:  # type: ignore[no-redef]
    start = int(_time.time())

    def now() -> int:
        return now.current

    now.current = start  # type: ignore[attr-defined]

    cfg = CacheConfig(backend="memory")
    cache = Cache.from_env()
    cache = Cache(backend=cache._backend, config=cfg, now_provider=now)  # type: ignore[attr-defined]

    cache.set("k2", "v2", ttl=2)
    assert cache.get("k2") == "v2"
    # Advance time beyond TTL
    now.current = start + 3  # type: ignore[attr-defined]
    assert cache.get("k2") is None


def test_tags_and_purge_tag() -> None:
    cfg = CacheConfig(backend="memory")
    cache = Cache.from_env()
    cache = Cache(backend=cache._backend, config=cfg)  # type: ignore[attr-defined]

    cache.set("ka", 1, ttl=0, tags=["group:x", "alpha"])  # no expiry
    cache.set("kb", 2, ttl=0, tags=["group:x", "beta"])  # no expiry
    cache.set("kc", 3, ttl=0, tags=["group:y"])  # no expiry

    removed = cache.purge_tag("group:x")
    assert removed == 2
    assert cache.get("ka") is None
    assert cache.get("kb") is None
    assert cache.get("kc") == 3

