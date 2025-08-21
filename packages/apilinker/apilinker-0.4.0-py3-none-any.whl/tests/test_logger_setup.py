import json
from pathlib import Path

from apilinker.core.logger import setup_logger, with_correlation_id


def test_setup_logger_writes_file_text(tmp_path):
    log_file = tmp_path / "text.log"
    logger = setup_logger("DEBUG", str(log_file), format_as_json=False)
    with with_correlation_id("cid-1"):
        logger.info("hello text")
    assert log_file.exists()
    content = log_file.read_text()
    assert "hello text" in content
    assert "cid-1" in content


def test_setup_logger_writes_file_json(tmp_path):
    log_file = tmp_path / "json.log"
    logger = setup_logger("INFO", str(log_file), format_as_json=True)
    logger.info("hello json")
    lines = [ln for ln in log_file.read_text().splitlines() if ln.strip()]
    assert lines, "expected some json logs"
    obj = json.loads(lines[-1])
    assert obj["message"] == "hello json"
    assert "correlation_id" in obj
