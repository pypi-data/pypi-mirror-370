import time

from apilinker.core.error_handling import (
    ApiLinkerError,
    ErrorCategory,
    ErrorRecoveryManager,
    RecoveryStrategy,
    CircuitBreakerState,
)


def test_handle_error_skip_strategy(tmp_path):
    erm = ErrorRecoveryManager()
    erm.set_strategy(ErrorCategory.UNKNOWN, [RecoveryStrategy.SKIP], operation_type="op-skip")
    err = ApiLinkerError("x", error_category=ErrorCategory.UNKNOWN)

    s, r, e = erm.handle_error(
        error=err,
        payload={"p": 1},
        operation=lambda p: 1 / 0,  # always fail
        operation_type="op-skip",
    )
    assert s is False and e is not None


def test_handle_error_fail_fast(tmp_path):
    erm = ErrorRecoveryManager()
    erm.set_strategy(ErrorCategory.CLIENT, [RecoveryStrategy.FAIL_FAST], operation_type="op-ff")
    err = ApiLinkerError("y", error_category=ErrorCategory.CLIENT)

    s, r, e = erm.handle_error(
        error=err,
        payload={"p": 2},
        operation=lambda p: (_ for _ in ()).throw(RuntimeError("boom")),
        operation_type="op-ff",
    )
    assert s is False and e is not None


def test_circuit_breaker_open_path(monkeypatch):
    erm = ErrorRecoveryManager()
    # force strategies to use CB only
    erm.set_strategy(ErrorCategory.SERVER, [RecoveryStrategy.CIRCUIT_BREAKER], operation_type="op-cb")

    # open circuit by adjusting internals
    cb = erm.get_circuit_breaker("op-cb")
    cb._state = CircuitBreakerState.OPEN
    cb._last_failure_time = time.time()

    err = ApiLinkerError("z", error_category=ErrorCategory.SERVER)
    s, r, e = erm.handle_error(
        error=err,
        payload={},
        operation=lambda p: 42,
        operation_type="op-cb",
    )
    assert s is False and e is not None
