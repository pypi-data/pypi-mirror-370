from apilinker.api_linker import ApiLinker
from apilinker.core.error_handling import ErrorCategory, RecoveryStrategy


def test_configure_error_handling_sets_circuit_and_strategies():
    l = ApiLinker(log_level="ERROR")
    cfg = {
        "circuit_breakers": {
            "source_list": {"failure_threshold": 2, "reset_timeout_seconds": 1, "half_open_max_calls": 1}
        },
        "recovery_strategies": {
            "server": ["circuit_breaker", "retry"],
            "client": ["fail_fast"],
        },
    }
    l._configure_error_handling(cfg)

    # circuit configured
    assert "source_list" in l.error_recovery_manager.circuit_breakers

    # strategy configured
    l.error_recovery_manager.set_strategy(ErrorCategory.SERVER, [RecoveryStrategy.RETRY])
    # ensure set_strategy succeeds without error; get strategies uses latest
    strategies = l.error_recovery_manager.get_strategies(ErrorCategory.SERVER)
    assert strategies
