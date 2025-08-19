from __future__ import annotations

import hashlib
import os
import pathlib
import time
from contextlib import contextmanager
from typing import Iterator

from filelock import FileLock, Timeout


def _locks_dir() -> pathlib.Path:
    base = pathlib.Path(os.path.expanduser("~/.cache/cachefuse/locks"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _lock_path_for_key(key: str) -> pathlib.Path:
    sha = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return _locks_dir() / f"{sha}.lock"


@contextmanager
def acquire_lock_for_key(key: str, timeout_seconds: int = 30) -> Iterator[None]:
    """Acquire a per-key file lock with a timeout.

    Raises filelock.Timeout on failure to acquire within timeout.
    """
    path = _lock_path_for_key(key)
    lock = FileLock(str(path))
    lock.acquire(timeout=timeout_seconds)
    try:
        yield
    finally:
        try:
            lock.release()
        except Exception:
            # If lock already released or file removed, ignore
            pass

