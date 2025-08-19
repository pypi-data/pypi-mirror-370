from __future__ import annotations

import os
import pathlib
from typing import Literal, Optional

from pydantic import BaseModel, Field


def _default_cache_dir() -> pathlib.Path:
    base = pathlib.Path(os.path.expanduser("~/.cache/cachefuse"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _default_sqlite_path() -> str:
    return str(_default_cache_dir() / "cache.db")


class CacheConfig(BaseModel):
    backend: Literal["sqlite", "redis", "memory"] = Field(
        default="sqlite", description="Cache backend type"
    )
    sqlite_path: str = Field(default_factory=_default_sqlite_path)
    redis_url: Optional[str] = None
    mode: Literal["normal", "hash_only"] = "normal"
    lock_timeout_seconds: int = 30

    @classmethod
    def from_env(cls) -> "CacheConfig":
        backend = os.getenv("CF_BACKEND", "sqlite").strip().lower()
        sqlite_path = os.getenv("CF_SQLITE_PATH", _default_sqlite_path())
        redis_url = os.getenv("CF_REDIS_URL")
        mode = os.getenv("CF_MODE", "normal").strip().lower()
        lock_timeout_seconds = int(os.getenv("CF_LOCK_TIMEOUT", "30"))
        return cls(
            backend=backend,  # type: ignore[arg-type]
            sqlite_path=sqlite_path,
            redis_url=redis_url,
            mode=mode,  # type: ignore[arg-type]
            lock_timeout_seconds=lock_timeout_seconds,
        )

