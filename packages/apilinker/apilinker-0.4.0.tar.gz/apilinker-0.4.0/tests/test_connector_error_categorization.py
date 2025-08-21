import httpx

from apilinker.core.connector import ApiConnector


def test_categorize_error_network_and_timeout():
    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    cat, code = conn._categorize_error(httpx.TimeoutException("t"))
    assert cat.name == "TIMEOUT"

    cat2, code2 = conn._categorize_error(httpx.NetworkError("n"))
    assert cat2.name == "NETWORK"


def test_categorize_error_http_status():
    class FakeResp:
        def __init__(self, status):
            self.status_code = status

    class HTTPStatusError(httpx.HTTPStatusError):
        def __init__(self, status):
            super().__init__("", request=None, response=None)
            self.response = FakeResp(status)

    conn = ApiConnector("rest", base_url="https://api", endpoints={})
    for status, expected in [(401, "AUTHENTICATION"), (422, "VALIDATION"), (429, "RATE_LIMIT"), (500, "SERVER"), (404, "CLIENT")]:
        cat, code = conn._categorize_error(HTTPStatusError(status))
        assert cat.name == expected
