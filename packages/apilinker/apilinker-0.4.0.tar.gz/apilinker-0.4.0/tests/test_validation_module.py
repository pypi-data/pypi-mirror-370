import os
import tempfile
from typing import Any, Dict

import pytest

from apilinker.core.validation import (
    is_validator_available,
    validate_payload_against_schema,
    pretty_print_diffs,
    dump_example_for_schema,
)
from apilinker.core.schema_probe import infer_schema, suggest_mapping_template
from apilinker.core.state_store import FileStateStore


def test_validate_payload_against_schema_basic():
    schema: Dict[str, Any] = {
        "type": "object",
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
        "required": ["id", "name"],
        "additionalProperties": False,
    }
    valid, diffs = validate_payload_against_schema({"id": 1, "name": "ok"}, schema)
    assert valid is True
    assert diffs == []

    valid, diffs = validate_payload_against_schema({"id": 1}, schema)
    assert valid is False
    assert any("Missing required" in d for d in diffs)

    valid, diffs = validate_payload_against_schema({"id": 1, "name": "ok", "x": 5}, schema)
    assert valid is False
    assert any("Unexpected properties" in d for d in diffs)

    # pretty print
    pp = pretty_print_diffs(diffs)
    assert pp.startswith("-")


def test_dump_example_for_schema():
    example = dump_example_for_schema(
        {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "meta": {"type": "object", "properties": {"a": {"type": "boolean"}}},
            },
        }
    )
    assert isinstance(example["id"], int)
    assert isinstance(example["tags"], list)
    assert isinstance(example["meta"], dict)


@pytest.mark.skipif(not is_validator_available(), reason="jsonschema not available")
def test_validation_available_flag():
    assert is_validator_available() is True


def test_schema_probe_infer_and_suggest():
    src = {"a": 1, "b": {"c": [1, 2]}}
    tgt = {"x": {"y": "z"}}
    s = infer_schema(src)
    assert s["type"] == "object"
    assert "properties" in s

    mapping = suggest_mapping_template(src, tgt)
    assert "fields" in mapping
    assert isinstance(mapping["fields"], list)


def test_file_state_store_roundtrip(tmp_path):
    path = tmp_path / "state.json"
    store = FileStateStore(str(path), default_last_sync="1970-01-01T00:00:00+00:00")

    # default when empty
    assert store.get_last_sync("e1") == "1970-01-01T00:00:00+00:00"

    # set/get last_sync
    store.set_last_sync("e1", "2025-01-01T00:00:00+00:00")
    assert store.get_last_sync("e1") == "2025-01-01T00:00:00+00:00"

    # checkpoints
    store.set_checkpoint("cp1", {"k": 1})
    assert store.get_checkpoint("cp1") == {"k": 1}

    # dlq pointer
    store.set_dlq_pointer("p1")
    assert store.get_dlq_pointer() == "p1"

    # list helpers
    ls = store.list_last_sync()
    cps = store.list_checkpoints()
    assert ls["e1"].startswith("2025")
    assert cps["cp1"]["k"] == 1

    # reset
    store.reset()
    assert store.list_last_sync() == {}
    assert store.list_checkpoints() == {}
    assert store.get_dlq_pointer() is None
