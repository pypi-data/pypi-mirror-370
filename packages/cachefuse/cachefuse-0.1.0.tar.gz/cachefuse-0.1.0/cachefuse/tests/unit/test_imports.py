def test_import_version() -> None:
    import cachefuse

    assert hasattr(cachefuse, "__version__")
    assert isinstance(cachefuse.__version__, str)
    assert cachefuse.__version__

