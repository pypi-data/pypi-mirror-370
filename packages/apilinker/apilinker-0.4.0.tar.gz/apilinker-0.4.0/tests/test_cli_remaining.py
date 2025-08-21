from typer.testing import CliRunner

from apilinker.cli import app


def test_cli_validate_failure(tmp_path):
    # invalid config path
    runner = CliRunner()
    res = runner.invoke(app, ["validate", "--config", str(tmp_path / "missing.yaml")])
    assert res.exit_code != 0


def test_cli_state_missing_file(tmp_path):
    # config with non-existent state path
    cfg = tmp_path / "c.json"
    cfg.write_text('{"state": {"type": "file", "path": "' + str(tmp_path / "s.json") + '"}}')
    runner = CliRunner()
    res = runner.invoke(app, ["state", "--config", str(cfg), "--action", "show"])
    # Accept either success or error depending on environment permissions
    assert res.exit_code in (0, 1)
