from __future__ import annotations

import os

from typer.testing import CliRunner

from cachefuse.cli import app

import pytest


@pytest.mark.integration
def test_stats_and_purge_sqlite_integration(tmp_path):  # type: ignore[no-redef]
    runner = CliRunner()
    db_path = tmp_path / "cache.db"
    env = {
        **os.environ,
        "CF_BACKEND": "sqlite",
        "CF_SQLITE_PATH": str(db_path),
    }

    # stats
    res = runner.invoke(app, ["stats"], env=env)
    assert res.exit_code == 0
    assert "entries:" in res.output

    # purge
    res = runner.invoke(app, ["purge", "--tag", "x"], env=env)
    assert res.exit_code == 0

    # vacuum
    res = runner.invoke(app, ["vacuum"], env=env)
    assert res.exit_code == 0
    assert "sqlite" in res.output

