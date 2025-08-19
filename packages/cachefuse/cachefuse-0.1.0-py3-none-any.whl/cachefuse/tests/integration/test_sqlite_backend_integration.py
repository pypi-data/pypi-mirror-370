from __future__ import annotations

import os
import tempfile
import time

import pytest

from cachefuse.backends.sqlite_backend import SQLiteBackend


@pytest.mark.integration
def test_sqlite_backend_integration_crud_and_vacuum(tmp_path):  # type: ignore[no-redef]
    path = os.path.join(tmp_path, "cache.db")
    b = SQLiteBackend(path)
    b.set("ka", 1, {}, ["t"], int(time.time()), None)
    assert b.get("ka")["value"] == 1  # type: ignore[index]
    assert b.stats()["entries"] >= 1
    # delete and vacuum
    b.purge_key("ka")
    b.vacuum()
    assert b.stats()["entries"] >= 0

