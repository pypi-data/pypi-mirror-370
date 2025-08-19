from __future__ import annotations

import os
import sqlite3
import threading
import time
from typing import Any, Dict, Iterable, Optional

from .base import CacheBackend


def _json_dumps(obj: Any) -> bytes:
    try:
        import orjson  # type: ignore

        return orjson.dumps(obj)
    except Exception:
        import json

        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def _json_loads(data: bytes) -> Any:
    try:
        import orjson  # type: ignore

        return orjson.loads(data)
    except Exception:
        import json

        return json.loads(data.decode("utf-8"))


class SQLiteBackend(CacheBackend):
    def __init__(self, path: str) -> None:
        self._path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self._db = sqlite3.connect(self._path, check_same_thread=False)
        self._mutex = threading.RLock()
        self._db.execute("PRAGMA journal_mode=WAL;")
        self._db.execute("PRAGMA synchronous=NORMAL;")
        self._migrate()

    def _migrate(self) -> None:
        with self._mutex:
            self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                meta  BLOB NOT NULL,
                tags TEXT,
                created_at INTEGER NOT NULL,
                expires_at INTEGER
            )
            """
            )
            self._db.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON entries(expires_at)")
            self._db.commit()

    def _normalize_tags(self, tags: Iterable[str]) -> str:
        uniq = [t.strip() for t in dict.fromkeys(tags) if t and t.strip()]
        # Store with surrounding commas to allow LIKE matching on whole tokens
        return "," + ",".join(uniq) + "," if uniq else ""

    def _prune_expired_key(self, key: str, now: Optional[int] = None) -> None:
        now = int(time.time()) if now is None else now
        with self._mutex:
            self._db.execute(
                "DELETE FROM entries WHERE key = ? AND expires_at IS NOT NULL AND expires_at <= ?",
                (key, now),
            )
            self._db.commit()

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        self._prune_expired_key(key)
        with self._mutex:
            cur = self._db.execute(
                "SELECT value, meta, tags, created_at, expires_at FROM entries WHERE key = ?",
                (key,),
            )
            row = cur.fetchone()
        if not row:
            return None
        value_b, meta_b, tags_s, created_at, expires_at = row
        value = _json_loads(value_b)
        meta = _json_loads(meta_b)
        tags = [] if not tags_s else [t for t in tags_s.split(",") if t]
        return {
            "value": value,
            "meta": meta,
            "tags": tags,
            "created_at": int(created_at),
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
        tags_s = self._normalize_tags(tags)
        with self._mutex:
            self._db.execute(
                """
                INSERT INTO entries(key, value, meta, tags, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    meta=excluded.meta,
                    tags=excluded.tags,
                    created_at=excluded.created_at,
                    expires_at=excluded.expires_at
                """,
                (
                    key,
                    _json_dumps(value),
                    _json_dumps(meta),
                    tags_s if tags_s else None,
                    int(created_at),
                    int(expires_at) if expires_at is not None else None,
                ),
            )
            self._db.commit()

    def purge_key(self, key: str) -> int:
        with self._mutex:
            cur = self._db.execute("DELETE FROM entries WHERE key = ?", (key,))
            self._db.commit()
        return cur.rowcount or 0

    def purge_tag(self, tag: str) -> int:
        pattern = f"%,{tag},%"
        # Count first for return value
        with self._mutex:
            cur = self._db.execute("SELECT COUNT(*) FROM entries WHERE tags LIKE ?", (pattern,))
            (count,) = cur.fetchone() or (0,)
            self._db.execute("DELETE FROM entries WHERE tags LIKE ?", (pattern,))
            self._db.commit()
        return int(count)

    def vacuum(self) -> None:
        # Ensure all transactions flushed then vacuum
        with self._mutex:
            self._db.execute("PRAGMA wal_checkpoint(FULL)")
            self._db.commit()
            self._db.execute("VACUUM")
            self._db.commit()

    def stats(self) -> Dict[str, Any]:
        now = int(time.time())
        with self._mutex:
            cur = self._db.execute(
                "SELECT COUNT(*) FROM entries WHERE expires_at IS NULL OR expires_at > ?",
                (now,),
            )
            (count,) = cur.fetchone() or (0,)
        return {"entries": int(count)}

