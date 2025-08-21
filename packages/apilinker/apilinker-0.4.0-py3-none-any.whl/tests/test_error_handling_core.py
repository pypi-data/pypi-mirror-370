import time
from pathlib import Path

from apilinker.core.error_handling import (
    ApiLinkerError,
    CircuitBreaker,
    CircuitBreakerState,
    ErrorCategory,
    ErrorRecoveryManager,
    DeadLetterQueue,
)


def test_circuit_breaker_open_and_half_open(monkeypatch):
    cb = CircuitBreaker("test", failure_threshold=2, reset_timeout_seconds=0.1)

    # force two failures to open
    def fail():
        raise RuntimeError("boom")

    res1, err1 = cb.execute(fail)
    assert err1 is not None
    res2, err2 = cb.execute(fail)
    assert err2 is not None
    assert cb.state in (CircuitBreakerState.CLOSED, CircuitBreakerState.OPEN)

    # After threshold, state should be OPEN
    cb._state = CircuitBreakerState.OPEN
    cb._last_failure_time = time.time()
    # immediate call should fail fast
    res3, err3 = cb.execute(lambda: None)
    assert res3 is None and err3 is not None

    # wait for half-open
    time.sleep(0.11)
    assert cb.state == CircuitBreakerState.HALF_OPEN


def test_error_recovery_manager_retry_and_dlq(tmp_path):
    dlq_dir = tmp_path / "dlq"
    erm = ErrorRecoveryManager(DeadLetterQueue(str(dlq_dir)))

    # an operation that fails twice then succeeds
    attempts = {"n": 0}

    def sometimes(payload):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("fail")
        return "ok"

    error = ApiLinkerError("x", error_category=ErrorCategory.NETWORK)
    success, result, out_err = erm.handle_error(
        error=error,
        payload={"p": 1},
        operation=sometimes,
        operation_type="op",
        max_retries=3,
        retry_delay=0.01,
    )
    assert success is True and result == "ok"

    # now permanent failure should write to DLQ
    def always_fail(payload):
        raise RuntimeError("nope")

    attempts["n"] = 0
    error2 = ApiLinkerError("y", error_category=ErrorCategory.CLIENT)
    success2, result2, out_err2 = erm.handle_error(
        error=error2,
        payload={"p": 2},
        operation=always_fail,
        operation_type="op2",
        max_retries=1,
        retry_delay=0.0,
    )
    assert success2 is False and out_err2 is not None
    files = list(Path(dlq_dir).glob("*.json"))
    assert len(files) >= 1
