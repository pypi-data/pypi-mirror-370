from typing import Any, Dict, List, Union

import types

from apilinker.core.connector import ApiConnector, EndpointConfig


class DummyResponse:
    def __init__(self, json_obj: Any, status_code: int = 200):
        self._json = json_obj
        self.status_code = status_code
        self.content = b"{}"

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError("bad status")

    def json(self):
        return self._json


def test_process_response_extract_path():
    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    conn.endpoints["e1"] = EndpointConfig(path="/e1", response_path="data.items")
    data = {"data": {"items": [{"id": 1}]}}
    out = conn._process_response(DummyResponse(data), "e1")
    assert isinstance(out, list)
    assert out[0]["id"] == 1


def test_handle_pagination_list_and_no_next():
    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    conn.endpoints["e2"] = EndpointConfig(
        path="/e2",
        pagination={"data_path": "results", "next_page_path": "next", "page_param": "page"},
    )

    # initial_data as dict with list inside
    initial = {"results": [{"id": 1}, {"id": 2}], "next": None}
    items = conn._handle_pagination(initial, "e2", params={})
    assert isinstance(items, list)
    assert len(items) == 2


def test_process_response_wrap_scalar():
    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    conn.endpoints["e3"] = EndpointConfig(path="/e3")
    out = conn._process_response(DummyResponse(123), "e3")
    assert isinstance(out, dict)
    assert out["value"] == 123
