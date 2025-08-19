from typer.testing import CliRunner

from cachefuse.cli import app


def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])  # smoke test
    assert result.exit_code == 0
    # Either the app help string or the default Usage header should appear
    assert ("CacheFuse CLI" in result.output) or ("Usage" in result.output)

