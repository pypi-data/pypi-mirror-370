from __future__ import annotations

from cachefuse.hashing import fingerprint, parse_ttl
from cachefuse.serialization import canonical_json_str


def test_canonical_json_deterministic_order() -> None:
    a = {"b": 1, "a": [3, 2, 1]}
    b = {"a": [3, 2, 1], "b": 1}
    assert canonical_json_str(a) == canonical_json_str(b)


def test_fingerprint_stable_for_key_order() -> None:
    payload1 = {"x": 1, "y": {"b": 2, "a": 3}}
    payload2 = {"y": {"a": 3, "b": 2}, "x": 1}
    assert fingerprint(payload1) == fingerprint(payload2)


def test_fingerprint_large_payload() -> None:
    large = {"text": "abc" * 10000, "n": 123}
    digest = fingerprint(large)
    assert len(digest) == 64
    # A second call should equal the first
    assert fingerprint(large) == digest


def test_parse_ttl_valid_values() -> None:
    assert parse_ttl(0) == 0
    assert parse_ttl(15) == 15
    assert parse_ttl("0") == 0
    assert parse_ttl("30s") == 30
    assert parse_ttl("30") == 30
    assert parse_ttl("2m") == 120
    assert parse_ttl("1h") == 3600
    assert parse_ttl("2d") == 172800


def test_parse_ttl_invalid_values() -> None:
    for bad in ["-1", -5, "abc", "10w", 3.14]:  # type: ignore[arg-type]
        try:
            parse_ttl(bad)  # type: ignore[arg-type]
        except ValueError:
            pass
        else:
            raise AssertionError(f"Expected ValueError for {bad!r}")

