from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Optional


class CacheBackend(ABC):
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Return stored entry dict or None if missing/expired.

        Expected dict keys: value, meta, tags, created_at, expires_at
        """

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        meta: Dict[str, Any],
        tags: Iterable[str],
        created_at: int,
        expires_at: Optional[int],
    ) -> None:
        ...

    @abstractmethod
    def purge_key(self, key: str) -> int:
        """Delete a specific key. Return number of removed entries (0 or 1)."""

    @abstractmethod
    def purge_tag(self, tag: str) -> int:
        """Delete entries that contain the tag. Return count removed."""

    @abstractmethod
    def vacuum(self) -> None:
        """Backend-specific compaction (no-op if not supported)."""

    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """Return backend stats dict (at minimum: entries count)."""

