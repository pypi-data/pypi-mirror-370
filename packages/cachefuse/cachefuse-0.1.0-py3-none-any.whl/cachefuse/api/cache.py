from __future__ import annotations

import logging
import time
from typing import Any, Callable, Dict, Iterable, Optional

from ..backends.base import CacheBackend
from ..backends.sqlite_backend import SQLiteBackend
from ..backends.redis_backend import RedisBackend
from ..config import CacheConfig
from ..locks import acquire_lock_for_key
from .metrics import Metrics


logger = logging.getLogger("cachefuse")


class Cache:
    def __init__(
        self,
        backend: CacheBackend,
        config: CacheConfig,
        now_provider: Callable[[], int] | None = None,
        redactor: Callable[[str], str] | None = None,
    ) -> None:
        self._backend = backend
        self._config = config
        self._now = now_provider or (lambda: int(time.time()))
        self._metrics = Metrics()
        self._redactor = redactor

    @property
    def config(self) -> CacheConfig:
        return self._config

    @classmethod
    def from_env(cls) -> "Cache":
        cfg = CacheConfig.from_env()
        return cls.from_config(cfg)

    @classmethod
    def from_config(cls, cfg: CacheConfig) -> "Cache":
        backend: CacheBackend
        if cfg.backend == "redis":
            if not cfg.redis_url:
                logger.warning("CF_REDIS_URL not set; using memory backend")
                backend = _MemoryBackend()
            else:
                backend = RedisBackend.from_url(cfg.redis_url)
        elif cfg.backend == "sqlite":
            backend = SQLiteBackend(cfg.sqlite_path)
        elif cfg.backend == "memory":
            backend = _MemoryBackend()
        else:
            logger.warning("Unknown backend %s; using memory backend", cfg.backend)
            backend = _MemoryBackend()
        return cls(backend=backend, config=cfg)

    @property
    def mode(self) -> str:
        return self._config.mode

    def get_redactor(self) -> Callable[[str], str] | None:
        return self._redactor

    def get(self, key: str) -> Optional[Any]:
        entry = self._backend.get(key)
        if entry is None:
            return None
        expires_at = entry.get("expires_at")
        if expires_at is not None and self._now() >= int(expires_at):
            # Ensure consistent expiry behavior regardless of backend clock
            self._backend.purge_key(key)
            return None
        return entry["value"]

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
        meta: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> None:
        meta = dict(meta or {})
        tags = list(tags or [])
        created_at = self._now()
        expires_at = None if not ttl or ttl == 0 else created_at + int(ttl)
        self._backend.set(
            key=key,
            value=value,
            meta=meta,
            tags=tags,
            created_at=created_at,
            expires_at=expires_at,
        )

    def purge_key(self, key: str) -> int:
        return self._backend.purge_key(key)

    def purge_tag(self, tag: str) -> int:
        return self._backend.purge_tag(tag)

    def vacuum(self) -> None:
        self._backend.vacuum()

    def stats(self) -> Dict[str, Any]:
        snap = self._metrics.snapshot().to_dict()
        backend_stats = self._backend.stats()
        return {
            **backend_stats,
            **snap,
        }

    def record_hit(self, latency_ms: int, cost_saved: float = 0.0) -> None:
        self._metrics.record_hit(latency_ms=latency_ms, cost_saved=cost_saved)

    def record_miss(self, latency_ms: int) -> None:
        self._metrics.record_miss(latency_ms=latency_ms)

    def get_or_set_with_lock(
        self,
        key: str,
        compute: Callable[[], Any],
        ttl: int | None = None,
        meta: Optional[Dict[str, Any]] = None,
        tags: Optional[Iterable[str]] = None,
    ) -> Any:
        """Compute value under per-key lock if not present.

        Prevents stampede on first-miss by serializing providers.
        """
        value = self.get(key)
        if value is not None:
            return value
        timeout = self._config.lock_timeout_seconds
        with acquire_lock_for_key(key, timeout_seconds=timeout):
            # Double-check after acquiring to avoid duplicate work
            value = self.get(key)
            if value is not None:
                # Record hit for threads that waited for lock
                self.record_hit(latency_ms=0)
                return value
            computed = compute()
            self.set(key, computed, ttl=ttl, meta=meta, tags=tags)
            return computed


class _MemoryBackend(CacheBackend):
    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}

    def _is_expired(self, entry: Dict[str, Any], now: Optional[int] = None) -> bool:
        now = int(time.time()) if now is None else now
        exp = entry.get("expires_at")
        return exp is not None and now >= int(exp)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        entry = self._store.get(key)
        if not entry:
            return None
        if self._is_expired(entry):
            self._store.pop(key, None)
            return None
        return dict(entry)

    def set(
        self,
        key: str,
        value: Any,
        meta: Dict[str, Any],
        tags: Iterable[str],
        created_at: int,
        expires_at: Optional[int],
    ) -> None:
        self._store[key] = {
            "value": value,
            "meta": dict(meta),
            "tags": list(tags),
            "created_at": int(created_at),
            "expires_at": int(expires_at) if expires_at is not None else None,
        }

    def purge_key(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0

    def purge_tag(self, tag: str) -> int:
        to_delete = [k for k, v in self._store.items() if tag in (v.get("tags") or [])]
        for k in to_delete:
            self._store.pop(k, None)
        return len(to_delete)

    def vacuum(self) -> None:
        # purge any expired
        now = int(time.time())
        expired = [k for k, v in self._store.items() if self._is_expired(v, now)]
        for k in expired:
            self._store.pop(k, None)

    def stats(self) -> Dict[str, Any]:
        self.vacuum()
        return {"entries": len(self._store)}

