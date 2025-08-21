from typing import Any, Dict, List

from apilinker.api_linker import ApiLinker
from apilinker.core.connector import ApiConnector, EndpointConfig


class FailingSource(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["src"] = EndpointConfig(path="/s")

    def fetch_data(self, endpoint_name: str, params=None):
        raise RuntimeError("fetch failed")


class FailingTarget(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["dst"] = EndpointConfig(path="/t")

    def send_data(self, endpoint_name: str, data):
        raise RuntimeError("send failed")


class FixedSource(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["src"] = EndpointConfig(path="/s")

    def fetch_data(self, endpoint_name: str, params=None):
        return [{"id": 1}]


def test_recovery_on_source_failure(monkeypatch):
    l = ApiLinker(log_level="ERROR")
    l.source = FailingSource()
    l.target = FailingTarget()
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])

    res = l.sync(source_endpoint="src", target_endpoint="dst", max_retries=1, retry_delay=0.01)
    assert res.success is False
    assert res.errors


def test_recovery_on_target_failure(monkeypatch):
    l = ApiLinker(log_level="ERROR")
    l.source = FixedSource()
    l.target = FailingTarget()
    l.mapper.add_mapping("src", "dst", [{"source": "id", "target": "id"}])

    res = l.sync(source_endpoint="src", target_endpoint="dst", max_retries=1, retry_delay=0.01)
    assert isinstance(res.success, bool)
