from pathlib import Path

from apilinker.api_linker import ApiLinker


def test_add_source_target_mapping_and_schedule():
    l = ApiLinker(log_level="ERROR")
    l.add_source(type="rest", base_url="https://s")
    l.add_target(type="rest", base_url="https://t")
    l.add_mapping(source="a", target="b", fields=[{"source": "id", "target": "id"}])
    l.add_schedule(type="interval", seconds=0)
    assert l.source is not None and l.target is not None


def test_load_config_with_json(tmp_path):
    cfg = {
        "source": {"type": "rest", "base_url": "https://s"},
        "target": {"type": "rest", "base_url": "https://t"},
        "mapping": {"source": "a", "target": "b", "fields": [{"source": "id", "target": "id"}]},
        "schedule": {"type": "interval", "seconds": 0},
        "logging": {"level": "ERROR"},
        "idempotency": {"enabled": True, "salt": "x"},
        "state": {"type": "file", "path": str(tmp_path / "state.json")},
    }
    p = tmp_path / "c.json"
    p.write_text(__import__("json").dumps(cfg))
    l = ApiLinker(config_path=str(p), log_level="ERROR")
    assert l.source is not None and l.target is not None
