from typer.testing import CliRunner

from apilinker.cli import app


def test_cli_run_starts_and_stops(tmp_path, monkeypatch):
    # create minimal config (JSON accepted by yaml) with schedule
    cfg = tmp_path / "c.yaml"
    cfg.write_text(
        '{"source": {"type": "rest", "base_url": "https://s", "endpoints": {"a": {"path": "/a"}}},'
        ' "target": {"type": "rest", "base_url": "https://t", "endpoints": {"b": {"path": "/b"}}},'
        ' "mapping": [{"source": "a", "target": "b", "fields": [{"source": "id", "target": "id"}]}],'
        ' "schedule": {"type": "interval", "seconds": 0},'
        ' "logging": {"level": "ERROR"}}'
    )

    # monkeypatch scheduler start to just return
    from apilinker import ApiLinker

    def fake_start(self):
        # immediately stop to simulate one iteration
        self.scheduler.running = False

    monkeypatch.setattr(ApiLinker, "start_scheduled_sync", fake_start)

    runner = CliRunner()
    res = runner.invoke(app, ["run", "--config", str(cfg)])
    assert res.exit_code == 0
