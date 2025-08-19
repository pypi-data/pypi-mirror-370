from __future__ import annotations

import inspect
import time
from functools import wraps
from typing import Any, Callable, Iterable, Optional

from ..hashing import fingerprint, parse_ttl
from ..serialization import canonical_json_bytes
from .cache import Cache


_CONTENT_KEYS = {"text", "prompt", "docs", "inputs", "content"}


def _build_fingerprint(
    kind: str,
    bound_args: inspect.BoundArguments,
    template_version: Optional[str],
    provider: Optional[str],
    cache: Cache,
) -> str:
    args_dict = {k: v for k, v in bound_args.arguments.items() if k != "self"}
    content = {k: args_dict[k] for k in args_dict.keys() & _CONTENT_KEYS} or args_dict
    params = {k: v for k, v in args_dict.items() if k not in _CONTENT_KEYS}

    input_material: Any = content
    if cache.mode == "hash_only":
        redactor = cache.get_redactor()

        def redact_any(x: Any) -> Any:
            if redactor is None:
                return x
            if isinstance(x, str):
                return redactor(x)
            if isinstance(x, list):
                return [redact_any(i) for i in x]
            if isinstance(x, dict):
                return {k: redact_any(v) for k, v in x.items()}
            return x

        input_material = redact_any(content)

    input_hash = fingerprint(input_material)
    model = args_dict.get("model")
    payload = {
        "kind": kind,
        "model": model,
        "provider": provider,
        "params": params,
        "template_version": template_version,
        "input_hash": input_hash,
    }
    return fingerprint(payload)


def _decorate(
    kind: str,
    *,
    cache: Cache,
    ttl: int | str | None = None,
    tag: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    template_version: Optional[str] = None,
    provider: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    ttl_seconds = parse_ttl(ttl) if ttl is not None else 0
    tag_list = list(tags or ([] if tag is None else [tag]))

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()
            key = _build_fingerprint(kind, bound, template_version, provider, cache)

            def compute() -> Any:
                start = time.perf_counter()
                result = func(*args, **kwargs)
                latency_ms = int((time.perf_counter() - start) * 1000)
                meta = {
                    "kind": kind,
                    "template_version": template_version,
                    "provider": provider,
                    "latency_ms": latency_ms,
                    "fingerprint": key,
                    "was_hit": False,
                }
                cache.set(key, result, ttl=ttl_seconds, meta=meta, tags=tag_list)
                cache.record_miss(latency_ms=latency_ms)
                return result

            # Attempt fast path first, then lock + compute if absent
            existing = cache.get(key)
            if existing is not None:
                cache.record_hit(latency_ms=0)
                return existing
            return cache.get_or_set_with_lock(
                key, compute=compute, ttl=ttl_seconds, meta=None, tags=tag_list
            )

        return wrapper

    return decorator


def llm(
    *,
    cache: Cache,
    ttl: int | str | None = None,
    tag: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    template_version: Optional[str] = None,
    provider: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return _decorate(
        "llm",
        cache=cache,
        ttl=ttl,
        tag=tag,
        tags=tags,
        template_version=template_version,
        provider=provider,
    )


def embed(
    *,
    cache: Cache,
    ttl: int | str | None = None,
    tag: Optional[str] = None,
    tags: Optional[Iterable[str]] = None,
    template_version: Optional[str] = None,
    provider: Optional[str] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return _decorate(
        "embed",
        cache=cache,
        ttl=ttl,
        tag=tag,
        tags=tags,
        template_version=template_version,
        provider=provider,
    )

