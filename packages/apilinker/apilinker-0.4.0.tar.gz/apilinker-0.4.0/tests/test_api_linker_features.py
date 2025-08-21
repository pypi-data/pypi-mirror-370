from typing import Any, Dict, List

import pytest

from apilinker.api_linker import ApiLinker
from apilinker.core.connector import ApiConnector


class DummyConnector(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.sent: List[Dict[str, Any]] = []
        self.endpoints["src"] = type("Cfg", (), {"path": "/s", "method": "GET", "params": {}, "headers": {}, "body_template": None, "pagination": None, "response_path": None, "response_schema": None, "request_schema": None})()  # type: ignore
        self.endpoints["dst"] = type("Cfg", (), {"path": "/t", "method": "POST", "params": {}, "headers": {}, "body_template": None, "pagination": None, "response_path": None, "response_schema": None, "request_schema": None})()  # type: ignore

    def _prepare_request(self, endpoint_name, params=None):
        return {"method": "GET", "url": "/", "headers": {}, "params": {}, "json": None}

    def fetch_data(self, endpoint_name: str, params=None):
        # return duplicate items to test idempotency filtering
        return [{"id": 1}, {"id": 1}, {"id": 2}]

    def send_data(self, endpoint_name: str, data):
        if isinstance(data, list):
            self.sent.extend(data)
            return {"success": True}
        return {"success": True}


def test_idempotency_filters_duplicates(monkeypatch):
    l = ApiLinker(log_level="ERROR")
    l.source = DummyConnector()
    l.target = DummyConnector()
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])
    l.idempotency_config = {"enabled": True, "salt": "s"}

    res = l.sync(source_endpoint="src", target_endpoint="dst")
    assert res.success
    # filtered to unique ids
    assert [x["id"] for x in l.target.sent] == [1, 2]


def test_strict_schema_validation_failure(monkeypatch):
    l = ApiLinker(log_level="ERROR")
    src = DummyConnector()
    dst = DummyConnector()
    # define a strict request schema that will fail
    dst.endpoints["dst"].request_schema = {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}
    l.source = src
    l.target = dst
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])
    l.validation_config = {"strict_mode": True}

    result = l.sync(source_endpoint="src", target_endpoint="dst")
    assert result.success is False
    assert result.errors, "expected validation errors recorded"


def test_state_store_injection(tmp_path, monkeypatch):
    # configure state store in linker via direct attribute
    l = ApiLinker(log_level="ERROR")
    src = DummyConnector()
    dst = DummyConnector()
    l.source = src
    l.target = dst
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])

    from apilinker.core.state_store import FileStateStore

    st = FileStateStore(str(tmp_path / "s.json"), default_last_sync="2000-01-01T00:00:00+00:00")
    l.state_store = st

    # Sync with params None should inject updated_since
    res = l.sync(source_endpoint="src", target_endpoint="dst", params=None)
    assert res.success
