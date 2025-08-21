import time

from apilinker.core.error_handling import ErrorAnalytics, ApiLinkerError, ErrorCategory


def test_error_analytics_summary_and_rates():
    ea = ErrorAnalytics(max_errors=10)
    # record several errors in different categories
    ea.record_error(ApiLinkerError("a", error_category=ErrorCategory.CLIENT))
    ea.record_error(ApiLinkerError("b", error_category=ErrorCategory.CLIENT))
    ea.record_error(ApiLinkerError("c", error_category=ErrorCategory.SERVER))

    rate_all = ea.get_error_rate(minutes=1)
    rate_client = ea.get_error_rate(category=ErrorCategory.CLIENT, minutes=1)
    top = ea.get_top_errors(limit=1)
    summary = ea.get_summary()

    assert rate_all >= rate_client >= 0
    assert top and top[0]["category"] in (ErrorCategory.CLIENT.value, ErrorCategory.SERVER.value)
    assert summary["total_errors"] >= 3
