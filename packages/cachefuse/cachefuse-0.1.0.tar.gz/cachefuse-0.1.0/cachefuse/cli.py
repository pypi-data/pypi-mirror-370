from __future__ import annotations

import os
from typing import Optional

import typer

from .api.cache import Cache
from .config import CacheConfig


app = typer.Typer(no_args_is_help=True, add_completion=False, help="CacheFuse CLI")


@app.callback()
def _root_callback() -> None:
    """CacheFuse command-line interface.

    Subcommands will be added in later steps (stats, purge, vacuum).
    """
    # No-op root
    return None


def _load_cache_from_env() -> Cache:
    # Allow overriding via env; defaults handled in CacheConfig
    cfg = CacheConfig.from_env()
    return Cache.from_config(cfg)


@app.command()
def stats() -> None:
    """Print aggregated stats (hit-rate, counts, latency) and backend entries."""
    cache = _load_cache_from_env()
    s = cache.stats()
    typer.echo(f"entries: {s.get('entries', 0)}")
    typer.echo(f"total_calls: {s.get('total_calls', 0)}")
    typer.echo(f"hits: {s.get('hits', 0)}")
    typer.echo(f"hit_rate: {s.get('hit_rate', 0.0):.2f}")
    typer.echo(f"avg_latency_ms: {s.get('avg_latency_ms', 0.0):.2f}")
    if 'cost_saved' in s:
        typer.echo(f"cost_saved: {s.get('cost_saved', 0.0):.4f}")


@app.command()
def purge(
    key: Optional[str] = typer.Option(None, "--key", help="Purge a single key"),
    tag: Optional[str] = typer.Option(None, "--tag", help="Purge all entries with tag"),
) -> None:
    """Purge entries by key and/or tag."""
    if key is None and tag is None:
        raise typer.BadParameter("Provide --key and/or --tag")
    cache = _load_cache_from_env()
    total_removed = 0
    if key is not None:
        removed = cache.purge_key(key)
        total_removed += removed
        typer.echo(f"purged key: {removed}")
    if tag is not None:
        removed = cache.purge_tag(tag)
        total_removed += removed
        typer.echo(f"purged tag: {removed}")
    typer.echo(f"total_removed: {total_removed}")


@app.command()
def vacuum() -> None:
    """Vacuum/compact backend storage (SQLite)."""
    cache = _load_cache_from_env()
    backend = cache.config.backend
    if backend == "sqlite":
        cache.vacuum()
        typer.echo("vacuum: done (sqlite)")
    else:
        typer.echo("vacuum: no-op for backend")


def run() -> None:
    app()


if __name__ == "__main__":
    run()

