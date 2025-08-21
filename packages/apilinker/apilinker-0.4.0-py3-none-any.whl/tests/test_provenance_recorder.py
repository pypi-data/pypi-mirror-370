import json

from apilinker.core.provenance import ProvenanceRecorder


def test_provenance_records_jsonl_and_sidecar(tmp_path):
    jsonl = tmp_path / "prov" / "run.log"
    outdir = tmp_path / "out"
    prov = ProvenanceRecorder(output_dir=str(outdir), jsonl_log_path=str(jsonl))

    prov.start_run(correlation_id="cid", config_path=None, source_endpoint="s", target_endpoint="t")
    prov.record_error("oops", category="CLIENT", status_code=400, endpoint="e1")
    prov.complete_run(True, 3, {"k": 1})

    # jsonl lines
    content = jsonl.read_text()
    lines = [json.loads(ln) for ln in content.splitlines() if ln.strip()]
    events = [obj.get("event") for obj in lines]
    assert "run_started" in events and "run_finished" in events

    # sidecar file
    sidecars = list(outdir.glob("run_*.json"))
    assert sidecars, "expected a sidecar json"
