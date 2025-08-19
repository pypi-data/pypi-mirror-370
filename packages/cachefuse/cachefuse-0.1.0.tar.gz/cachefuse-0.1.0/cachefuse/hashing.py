from __future__ import annotations

import hashlib
import re
from typing import Any

from .serialization import canonical_json_bytes


def fingerprint(payload: Any) -> str:
    """Compute a deterministic SHA256 hex digest of the canonical JSON payload."""
    data = canonical_json_bytes(payload)
    return hashlib.sha256(data).hexdigest()


_TTL_PATTERN = re.compile(r"^(?P<num>\d+)(?P<unit>[smhdSMHD]?)$")


def parse_ttl(value: int | str) -> int:
    """Parse TTL to seconds.

    Accepts integers (seconds) or strings like "300", "300s", "12m", "2h", "7d".
    Returns 0 to indicate no expiry when given 0 / "0". Raises ValueError on invalid input.
    """
    if isinstance(value, int):
        if value < 0:
            raise ValueError("TTL must be non-negative")
        return value

    if not isinstance(value, str):
        raise ValueError("TTL must be int or str")

    value = value.strip()
    match = _TTL_PATTERN.match(value)
    if not match:
        raise ValueError(f"Invalid TTL format: {value!r}")

    num = int(match.group("num"))
    unit = match.group("unit").lower()
    if num == 0:
        return 0

    if unit in ("", "s"):
        return num
    if unit == "m":
        return num * 60
    if unit == "h":
        return num * 60 * 60
    if unit == "d":
        return num * 60 * 60 * 24

    # Should not happen due to regex, but keep defensive
    raise ValueError(f"Invalid TTL unit in: {value!r}")

