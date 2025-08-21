from typing import Any, Dict

from apilinker.core.connector import ApiConnector, EndpointConfig


class DummyClient:
    def __init__(self, pages):
        self.pages = pages
        self.calls = 0

    def request(self, method, url, headers=None, params=None, json=None):
        class Resp:
            def __init__(self, payload):
                self._payload = payload
                self.content = b"{}"

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        payload = self.pages[self.calls]
        self.calls += 1
        return Resp(payload)


def test_handle_pagination_multiple_pages():
    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    conn.endpoints["e"] = EndpointConfig(
        path="/e",
        pagination={"data_path": "results", "next_page_path": "next", "page_param": "page"},
    )

    # initial data with next page token
    initial = {"results": [{"id": 1}], "next": "token"}

    # set up client to return page 2 then page 3 (with no next)
    conn.client = DummyClient(
        [
            {"results": [{"id": 2}], "next": "token2"},
            {"results": [{"id": 3}], "next": None},
        ]
    )

    items = conn._handle_pagination(initial, "e", params={})
    ids = [it["id"] for it in items]
    assert ids == [1, 2, 3]
