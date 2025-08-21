import time

from apilinker.api_linker import ApiLinker


def test_with_retries_succeeds_after_retry():
    l = ApiLinker(log_level="ERROR")
    calls = {"n": 0}

    class RetryableError(Exception):
        def __init__(self, msg):
            super().__init__(msg)
            self.status_code = 500

    def op():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RetryableError("fail once")
        return 42

    res, err = l._with_retries(
        operation=op,
        operation_name="op",
        max_retries=2,
        retry_delay=0.01,
        retry_backoff_factor=2.0,
        retry_status_codes=[429, 500],
        correlation_id="cid",
    )
    assert res == 42 and err is None


def test_with_retries_exhausts_and_returns_error():
    l = ApiLinker(log_level="ERROR")

    def op():
        raise RuntimeError("always")

    res, err = l._with_retries(
        operation=op,
        operation_name="op",
        max_retries=1,
        retry_delay=0.0,
        retry_backoff_factor=2.0,
        retry_status_codes=[429, 500],
        correlation_id="cid",
    )
    assert res is None and err is not None
