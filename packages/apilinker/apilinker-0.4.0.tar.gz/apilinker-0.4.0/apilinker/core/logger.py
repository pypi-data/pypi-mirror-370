"""
Logging configuration for ApiLinker.

Provides structured logging with correlation IDs for request tracing and enhanced
debugability. Supports both standard text-based logging and JSON formatting for
better integration with log management systems.
"""

import json
import logging
import os
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Optional


class CorrelationFilter(logging.Filter):
    """Filter that adds correlation_id to LogRecords if not present."""

    def __init__(self):
        super().__init__()
        self._context_correlation_id = None

    def set_correlation_id(self, correlation_id: str) -> None:
        """Set the correlation ID for the current context."""
        self._context_correlation_id = correlation_id

    def clear_correlation_id(self) -> None:
        """Clear the correlation ID for the current context."""
        self._context_correlation_id = None

    def filter(self, record: logging.LogRecord) -> bool:
        # Don't override if already set in the record
        if not hasattr(record, "correlation_id") or not record.correlation_id:
            record.correlation_id = self._context_correlation_id or "no-correlation-id"
        return True


class CorrelationFormatter(logging.Formatter):
    """Formatter that ensures correlation_id is available."""

    def format(self, record: logging.LogRecord) -> str:
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "no-correlation-id"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation ID if present
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        else:
            log_data["correlation_id"] = "no-correlation-id"

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra attributes that were passed
        for key, value in record.__dict__.items():
            if key not in [
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


# Global correlation filter for context tracking
_correlation_filter = CorrelationFilter()


@contextmanager
def with_correlation_id(
    correlation_id: Optional[str] = None,
) -> Generator[str, None, None]:
    """Context manager to set correlation ID for all logs within the context.

    Args:
        correlation_id: Correlation ID to use, or None to generate a new one

    Yields:
        The correlation ID being used
    """
    cid = correlation_id or str(uuid.uuid4())
    previous_cid = getattr(_correlation_filter, "_context_correlation_id", None)

    try:
        _correlation_filter.set_correlation_id(cid)
        yield cid
    finally:
        if previous_cid:
            _correlation_filter.set_correlation_id(previous_cid)
        else:
            _correlation_filter.clear_correlation_id()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for the current context.

    Args:
        correlation_id: Correlation ID to use for subsequent log calls
    """
    _correlation_filter.set_correlation_id(correlation_id)


def clear_correlation_id() -> None:
    """Clear the correlation ID for the current context."""
    _correlation_filter.clear_correlation_id()


def log_with_context(
    logger: logging.Logger,
    level: int,
    msg: str,
    correlation_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Log a message with correlation ID context.

    Args:
        logger: Logger instance to use
        level: Log level (e.g., logging.INFO)
        msg: Log message
        correlation_id: Optional correlation ID to use for this message only
        **kwargs: Additional log record attributes
    """
    extra = kwargs.pop("extra", {}) or {}
    if correlation_id:
        extra["correlation_id"] = correlation_id

    logger.log(level, msg, extra=extra, **kwargs)


def setup_logger(
    level: str = "INFO",
    log_file: Optional[str] = None,
    logger_name: str = "apilinker",
    format_as_json: bool = False,
) -> logging.Logger:
    """
    Configure and get a logger instance.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file (None for console only)
        logger_name: Name of the logger

    Returns:
        Configured logger instance
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Get logger
    logger = logging.getLogger(logger_name)

    # Clear existing handlers
    if logger.hasHandlers():
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Set level
    logger.setLevel(numeric_level)

    # Create formatter based on format_as_json parameter
    if format_as_json:
        formatter = JsonFormatter()
    else:
        formatter = CorrelationFormatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] [%(correlation_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Add console handler with correlation filter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(_correlation_filter)
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        # Ensure directory exists
        log_path = Path(log_file)
        log_dir = log_path.parent
        if not log_dir.exists() and str(log_dir) != ".":
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_correlation_filter)
        logger.addHandler(file_handler)

    # Add convenience methods for correlation ID logging
    def info_with_correlation(
        msg: str, correlation_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        log_with_context(logger, logging.INFO, msg, correlation_id, **kwargs)

    def error_with_correlation(
        msg: str, correlation_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        log_with_context(logger, logging.ERROR, msg, correlation_id, **kwargs)

    def warning_with_correlation(
        msg: str, correlation_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        log_with_context(logger, logging.WARNING, msg, correlation_id, **kwargs)

    def debug_with_correlation(
        msg: str, correlation_id: Optional[str] = None, **kwargs: Any
    ) -> None:
        log_with_context(logger, logging.DEBUG, msg, correlation_id, **kwargs)

    # Monkey patch the logger instance with the new methods
    logger.info_with_correlation = info_with_correlation
    logger.error_with_correlation = error_with_correlation
    logger.warning_with_correlation = warning_with_correlation
    logger.debug_with_correlation = debug_with_correlation

    return logger
