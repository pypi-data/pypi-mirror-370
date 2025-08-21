from pathlib import Path
import json

from typer.testing import CliRunner

from apilinker.cli import app
from apilinker import __version__


def write_basic_config(tmp_path: Path) -> Path:
    cfg = {
        "source": {
            "type": "rest",
            "base_url": "https://example.com/src",
            "endpoints": {"list_items": {"path": "/items", "method": "GET"}},
        },
        "target": {
            "type": "rest",
            "base_url": "https://example.com/dst",
            "endpoints": {"create_item": {"path": "/items", "method": "POST"}},
        },
        "mapping": [
            {
                "source": "list_items",
                "target": "create_item",
                "fields": [{"source": "id", "target": "external_id"}],
            }
        ],
        "state": {"type": "file", "path": str(tmp_path / "state.json")},
        "logging": {"level": "INFO", "file": str(tmp_path / "apilinker.log")},
    }
    p = tmp_path / "config.yaml"
    p.write_text(json.dumps(cfg))  # yaml.safe_load accepts JSON too
    return p


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(app, ["version"])  # prints version
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_init_and_validate(tmp_path):
    runner = CliRunner()
    out = tmp_path / "config.yaml"
    result = runner.invoke(app, ["init", "--output", str(out), "--force"])
    assert result.exit_code == 0
    assert out.exists()

    # validate
    result2 = runner.invoke(app, ["validate", "--config", str(out)])
    assert result2.exit_code == 0


def test_cli_state_show_and_reset(tmp_path):
    runner = CliRunner()
    cfg = write_basic_config(tmp_path)

    # show
    res_show = runner.invoke(app, ["state", "--config", str(cfg), "--action", "show"])
    assert res_show.exit_code == 0

    # reset
    res_reset = runner.invoke(app, ["state", "--config", str(cfg), "--action", "reset"])
    assert res_reset.exit_code == 0


def test_cli_sync_dry_run(tmp_path):
    runner = CliRunner()
    cfg = write_basic_config(tmp_path)
    res = runner.invoke(app, ["sync", "--config", str(cfg), "--dry-run"])
    assert res.exit_code == 0
    assert "DRY RUN" in res.output
