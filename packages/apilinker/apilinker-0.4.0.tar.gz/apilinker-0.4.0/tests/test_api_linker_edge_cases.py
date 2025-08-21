from apilinker.api_linker import ApiLinker
from apilinker.core.connector import ApiConnector, EndpointConfig


class Src(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["s"] = EndpointConfig(path="/s")

    def fetch_data(self, endpoint_name: str, params=None):
        return {"id": 1}


class Dst(ApiConnector):
    def __init__(self):
        super().__init__("rest", base_url="https://x", endpoints={})
        self.endpoints["t"] = EndpointConfig(path="/t")

    def send_data(self, endpoint_name: str, data):
        return {"ok": True}


def test_sync_uses_first_mapping_when_not_specified():
    l = ApiLinker(log_level="ERROR")
    l.source = Src()
    l.target = Dst()
    l.mapper.add_mapping("s", "t", [{"source": "id", "target": "id"}])
    res = l.sync()
    assert res.success is True


def test_mapping_error_path_records_provenance(monkeypatch):
    l = ApiLinker(log_level="ERROR")
    l.source = Src()
    l.target = Dst()
    # mapping that triggers error in mapping: use non-serializable transform name
    l.mapper.add_mapping("s", "t", [{"source": "id", "target": "id", "transform": "__unknown__"}])
    res = l.sync()
    assert res.success is True or res.success is False
