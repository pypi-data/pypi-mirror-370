from __future__ import annotations

import runpy

import pytest


@pytest.mark.integration
def test_rag_demo_runs():
    # Just verify the script runs end-to-end without exceptions
    runpy.run_module("cachefuse.examples.rag_demo", run_name="__main__")


@pytest.mark.integration
def test_embed_demo_runs():
    runpy.run_module("cachefuse.examples.embed_demo", run_name="__main__")

