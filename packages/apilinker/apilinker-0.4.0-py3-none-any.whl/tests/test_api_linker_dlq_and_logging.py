from pathlib import Path
from typing import Any, Dict

from apilinker.api_linker import ApiLinker
from apilinker.core.logger import setup_logger


def test_setup_logger_basic(tmp_path):
    log_file = tmp_path / "apilinker.log"
    logger = setup_logger("INFO", str(log_file))
    logger.info("hello")
    assert log_file.exists()


def test_process_dlq_handles_empty_and_unknown(monkeypatch):
    linker = ApiLinker(log_level="ERROR")

    # monkeypatch DLQ to return empty list
    class DummyDLQ:
        def get_items(self, limit: int = 10):
            return []

    linker.dlq = DummyDLQ()  # type: ignore[assignment]
    res = linker.process_dlq(limit=5)
    assert res["total_processed"] == 0
    assert res["successful"] == 0
    assert res["failed"] == 0

    # now return an unknown item
    class DummyDLQ2:
        def get_items(self, limit: int = 10):
            return [{"id": "1", "payload": {"foo": "bar"}, "metadata": {}}]

    linker.dlq = DummyDLQ2()  # type: ignore[assignment]
    res2 = linker.process_dlq(limit=1)
    assert res2["total_processed"] == 1
    assert res2["failed"] == 1
