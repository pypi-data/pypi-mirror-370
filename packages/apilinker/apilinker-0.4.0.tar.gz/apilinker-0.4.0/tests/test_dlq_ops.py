import json
from pathlib import Path

from apilinker.core.error_handling import DeadLetterQueue, ApiLinkerError, ErrorCategory


def test_dlq_add_get_and_retry_success(tmp_path):
    dlq_dir = tmp_path / "dlq"
    dlq = DeadLetterQueue(str(dlq_dir))

    # add one item
    err = ApiLinkerError("oops", error_category=ErrorCategory.CLIENT, correlation_id="cid")
    item_id = dlq.add_item(err, payload={"x": 1}, metadata={"operation_type": "op"})

    # get items
    items = dlq.get_items()
    assert items and items[0]["id"].startswith(item_id.split("_")[0])

    # retry moving to processed
    ok, result, out_err = dlq.retry_item(item_id, operation=lambda p: {"ok": True})
    assert ok is True and out_err is None
    assert (dlq_dir / "processed").exists()

    # retry missing
    ok2, result2, out_err2 = dlq.retry_item("non-existent", operation=lambda p: p)
    assert ok2 is False and out_err2 is not None
