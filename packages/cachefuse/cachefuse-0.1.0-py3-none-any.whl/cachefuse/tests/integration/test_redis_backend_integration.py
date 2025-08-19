from __future__ import annotations

import os
import time

import pytest

import fakeredis

from cachefuse.backends.redis_backend import RedisBackend


@pytest.mark.integration
def test_redis_backend_integration_basic():
    r = fakeredis.FakeRedis()
    b = RedisBackend(r)
    now = int(time.time())
    b.set("k", 1, {}, ["t"], now, None)
    assert b.get("k")["value"] == 1  # type: ignore[index]
    assert b.stats()["entries"] >= 1
    b.purge_tag("t")
    assert b.get("k") is None

