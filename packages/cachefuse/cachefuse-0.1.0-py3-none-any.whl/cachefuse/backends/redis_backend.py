from __future__ import annotations

import time
from typing import Any, Dict, Iterable, Optional

try:
    import orjson as _orjson  # type: ignore
except Exception:  # pragma: no cover - optional
    _orjson = None  # type: ignore

from .base import CacheBackend


def _dumps(obj: Any) -> bytes:
    if _orjson is not None:
        return _orjson.dumps(obj)  # type: ignore
    import json

    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _loads(data: bytes) -> Any:
    if _orjson is not None:
        return _orjson.loads(data)  # type: ignore
    import json

    return json.loads(data.decode("utf-8"))


class RedisBackend(CacheBackend):
    def __init__(self, client) -> None:  # client: redis.Redis
        self._r = client

    @classmethod
    def from_url(cls, url: str) -> "RedisBackend":
        from redis import Redis

        return cls(Redis.from_url(url))

    @staticmethod
    def _entry_key(key: str) -> str:
        return f"cf:entry:{key}"

    @staticmethod
    def _tag_key(tag: str) -> str:
        return f"cf:tag:{tag}"

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self._r.get(self._entry_key(key))
        if raw is None:
            return None
        obj = _loads(raw)
        expires_at = obj.get("expires_at")
        now = int(time.time())
        if expires_at is not None and now >= int(expires_at):
            # prune expired
            self.purge_key(key)
            return None
        return {
            "value": obj.get("value"),
            "meta": obj.get("meta") or {},
            "tags": obj.get("tags") or [],
            "created_at": int(obj.get("created_at") or now),
            "expires_at": int(expires_at) if expires_at is not None else None,
        }

    def set(
        self,
        key: str,
        value: Any,
        meta: Dict[str, Any],
        tags: Iterable[str],
        created_at: int,
        expires_at: Optional[int],
    ) -> None:
        tags_list = [t for t in tags]
        payload = {
            "value": value,
            "meta": meta,
            "tags": tags_list,
            "created_at": int(created_at),
            "expires_at": int(expires_at) if expires_at is not None else None,
        }
        ttl = None
        if expires_at is not None:
            ttl = max(0, int(expires_at) - int(time.time()))
        # Store entry
        if ttl and ttl > 0:
            self._r.set(self._entry_key(key), _dumps(payload), ex=ttl)
        else:
            self._r.set(self._entry_key(key), _dumps(payload))
        # Update tag sets
        for t in tags_list:
            self._r.sadd(self._tag_key(t), key)

    def purge_key(self, key: str) -> int:
        # Remove from tag sets if we can fetch tags
        raw = self._r.get(self._entry_key(key))
        if raw is not None:
            try:
                obj = _loads(raw)
                for t in obj.get("tags") or []:
                    self._r.srem(self._tag_key(t), key)
            except Exception:
                pass
        removed = self._r.delete(self._entry_key(key))
        return int(removed or 0)

    def purge_tag(self, tag: str) -> int:
        tkey = self._tag_key(tag)
        members = list(self._r.smembers(tkey))
        # Redis returns bytes; decode
        keys = [m.decode("utf-8") if isinstance(m, (bytes, bytearray)) else str(m) for m in members]
        removed = 0
        for k in keys:
            removed += self.purge_key(k)
        # Clear the tag set after purge
        self._r.delete(tkey)
        return removed

    def vacuum(self) -> None:
        # No-op for Redis
        return None

    def stats(self) -> Dict[str, Any]:
        # Count entry keys
        count = 0
        for _ in self._r.scan_iter(match="cf:entry:*"):
            count += 1
        return {"entries": count}

