from __future__ import annotations

from cachefuse.api.cache import Cache
from cachefuse.api.decorators import llm
from cachefuse.config import CacheConfig


def test_hash_only_mode_redacts_inputs(monkeypatch):  # type: ignore[no-redef]
    cfg = CacheConfig(backend="memory", mode="hash_only")

    def redactor(s: str) -> str:
        return s.replace("secret", "[redacted]")

    cache = Cache.from_config(cfg)
    cache = Cache(backend=cache._backend, config=cfg, redactor=redactor)  # type: ignore[attr-defined]

    @llm(cache=cache, ttl="10s", tag="privacy", template_version="1")
    def summarize(text: str) -> str:
        return text[::-1]

    out = summarize("this is secret")
    assert out == "terces si siht"

    # Ensure that a subsequent call with different literal but same redacted value hits the cache
    out2 = summarize("this is [redacted]")
    assert out2 == out

