from __future__ import annotations

import json
from typing import Any


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize an object to deterministic JSON bytes.

    Uses orjson if available for speed, otherwise falls back to stdlib json.
    Keys are sorted and NaN/Infinity are disallowed to keep hashes stable.
    """
    try:
        import orjson  # type: ignore

        # OPT_INDENT_2 is human-friendly; not required for hashing, but stable.
        opts = orjson.OPT_SORT_KEYS | orjson.OPT_APPEND_NEWLINE
        return orjson.dumps(obj, option=opts)
    except Exception:
        return (
            json.dumps(
                obj,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
                ensure_ascii=False,
            )
            + "\n"
        ).encode("utf-8")


def canonical_json_str(obj: Any) -> str:
    return canonical_json_bytes(obj).decode("utf-8")

