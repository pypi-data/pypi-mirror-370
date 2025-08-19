from __future__ import annotations

import time

from cachefuse.api.decorators import embed, llm
from cachefuse.api.cache import Cache
from cachefuse.config import CacheConfig


def test_llm_hit_miss_and_template_bust():
    cache = Cache.from_config(CacheConfig(backend="memory"))

    calls = {"n": 0}

    @llm(cache=cache, ttl="2s", tag="summarize-v1", template_version="1")
    def summarize(text: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
        calls["n"] += 1
        return text.upper()

    out1 = summarize("hello")
    out2 = summarize("hello")
    assert out1 == out2 == "HELLO"
    # Only first call executes
    assert calls["n"] == 1

    # template bump should bust cache
    @llm(cache=cache, ttl="2s", tag="summarize-v2", template_version="2")
    def summarize_v2(text: str, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
        calls["n"] += 1
        return text.upper() + "!"

    out3 = summarize_v2("hello")
    assert out3 == "HELLO!"
    assert calls["n"] == 2


def test_embed_params_change_busts_cache():
    cache = Cache.from_config(CacheConfig(backend="memory"))

    calls = {"n": 0}

    @embed(cache=cache, ttl="2s", tag="embed-minilm", template_version="1")
    def make_vecs(docs: list[str], model: str = "all-MiniLM-L6-v2", norm: bool = True):
        calls["n"] += 1
        return [len(d) for d in docs]

    v1 = make_vecs(["a", "bb"], norm=True)
    v2 = make_vecs(["a", "bb"], norm=True)
    assert v1 == v2 == [1, 2]
    assert calls["n"] == 1

    # param change should bust
    v3 = make_vecs(["a", "bb"], norm=False)
    assert v3 == [1, 2]
    assert calls["n"] == 2

