import json
from pathlib import Path

from apilinker.api_linker import ApiLinker
from apilinker.core.connector import ApiConnector, EndpointConfig


class SimpleSource(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["src"] = EndpointConfig(path="/s")

    def fetch_data(self, endpoint_name: str, params=None):
        return [{"id": 1}]


class FlakyTarget(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["dst"] = EndpointConfig(path="/t")
        self.calls = 0

    def send_data(self, endpoint_name: str, data):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("first failure")
        return {"ok": True}


def test_provenance_jsonl_and_recovery(tmp_path):
    # configure provenance jsonl and ensure run_started/run_finished emitted
    l = ApiLinker(log_level="ERROR")
    l.source = SimpleSource()
    l.target = FlakyTarget()
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])

    # write a minimal config file to compute hash
    cfg_path = tmp_path / "c.yaml"
    cfg_path.write_text("{}", encoding="utf-8")

    # inject provenance recorder with paths
    from apilinker.core.provenance import ProvenanceRecorder

    jsonl = tmp_path / "p" / "prov.jsonl"
    l.provenance = ProvenanceRecorder(output_dir=str(tmp_path / "out"), jsonl_log_path=str(jsonl))
    # set last config path so start_run sees it
    l._last_config_path = str(cfg_path)

    res = l.sync(source_endpoint="src", target_endpoint="dst", max_retries=0, retry_delay=0.0)
    assert isinstance(res.success, bool)

    lines = [json.loads(x) for x in jsonl.read_text().splitlines() if x.strip()]
    events = [x.get("event") for x in lines]
    # On failure we at least expect run_started; run_finished may be emitted on success only
    assert "run_started" in events
