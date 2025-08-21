"""
Advanced error handling and recovery system for APILinker.

This module provides sophisticated error handling capabilities including:
1. Circuit breakers to prevent cascading failures
2. Dead Letter Queue (DLQ) for failed operations
3. Configurable recovery strategies
4. Detailed error logging and analytics
"""

import json
import logging
import os
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    TypeVar,
    Generic,
)

import httpx

# Type variable for circuit breaker result type
T = TypeVar("T")

# Set up module logger
logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """States for the circuit breaker pattern."""

    CLOSED = "CLOSED"  # Normal operation, requests pass through
    OPEN = "OPEN"  # Circuit is open, requests fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service is back online


class ErrorCategory(Enum):
    """Categories of errors for better handling and reporting."""

    NETWORK = "NETWORK"  # Network connectivity issues
    AUTHENTICATION = "AUTH"  # Authentication/authorization failures
    VALIDATION = "VALIDATION"  # Invalid request data
    TIMEOUT = "TIMEOUT"  # Request timeout
    RATE_LIMIT = "RATE_LIMIT"  # API rate limit exceeded
    SERVER = "SERVER"  # Server-side errors (5xx)
    CLIENT = "CLIENT"  # Client-side errors (4xx)
    MAPPING = "MAPPING"  # Data mapping errors
    PLUGIN = "PLUGIN"  # Plugin-related errors
    UNKNOWN = "UNKNOWN"  # Uncategorized errors


class RecoveryStrategy(Enum):
    """Strategies for recovering from errors."""

    RETRY = "RETRY"  # Simple retry
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"  # Retry with increasing delay
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"  # Circuit breaker pattern
    FALLBACK = "FALLBACK"  # Use fallback data/operation
    SKIP = "SKIP"  # Skip this operation
    FAIL_FAST = "FAIL_FAST"  # Fail immediately


class ApiLinkerError(Exception):
    """Base exception class for APILinker errors with enhanced context."""

    def __init__(
        self,
        message: str,
        error_category: ErrorCategory = ErrorCategory.UNKNOWN,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        request_url: Optional[str] = None,
        request_method: Optional[str] = None,
        operation_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_category = error_category
        self.status_code = status_code
        self.response_body = response_body
        self.request_url = request_url
        self.request_method = request_method
        self.timestamp = datetime.now().isoformat()
        self.operation_id = operation_id
        self.correlation_id = correlation_id
        self.additional_context = additional_context or {}

    @classmethod
    def from_exception(cls, exc: Exception, **kwargs) -> "ApiLinkerError":
        """Convert a standard exception to an ApiLinkerError with additional context."""
        # Extract HTTP-specific information if available
        status_code = getattr(exc, "status_code", None)
        response_body = getattr(exc, "response", None)
        request_url = getattr(exc, "url", None)
        request_method = getattr(exc, "method", None)

        # Determine error category based on exception type or status code
        error_category = ErrorCategory.UNKNOWN
        if isinstance(exc, httpx.TimeoutException):
            error_category = ErrorCategory.TIMEOUT
        elif isinstance(exc, httpx.NetworkError):
            error_category = ErrorCategory.NETWORK
        elif status_code:
            if 400 <= status_code < 500:
                if status_code == 401 or status_code == 403:
                    error_category = ErrorCategory.AUTHENTICATION
                elif status_code == 422:
                    error_category = ErrorCategory.VALIDATION
                elif status_code == 429:
                    error_category = ErrorCategory.RATE_LIMIT
                else:
                    error_category = ErrorCategory.CLIENT
            elif 500 <= status_code < 600:
                error_category = ErrorCategory.SERVER

        # Convert response to string if it's not already
        if response_body and not isinstance(response_body, str):
            try:
                response_body = str(response_body)[:1000]  # Limit size
            except:
                response_body = "<Unable to convert response to string>"

        # Merge with provided kwargs, kwargs take precedence
        error_kwargs = {
            "message": str(exc),
            "error_category": error_category,
            "status_code": status_code,
            "response_body": response_body,
            "request_url": request_url,
            "request_method": request_method,
        }
        error_kwargs.update(kwargs)

        return cls(**error_kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to a dictionary for logging or serialization."""
        return {
            "message": self.message,
            "error_category": self.error_category.value,
            "status_code": self.status_code,
            "response_body": self.response_body,
            "request_url": self.request_url,
            "request_method": self.request_method,
            "timestamp": self.timestamp,
            "operation_id": self.operation_id,
            "correlation_id": self.correlation_id,
            "additional_context": self.additional_context,
        }

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.error_category.value}] {self.message}"]

        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_method and self.request_url:
            parts.append(f"{self.request_method} {self.request_url}")
        if self.correlation_id:
            parts.append(f"Correlation ID: {self.correlation_id}")

        return " | ".join(parts)


class DeadLetterQueue:
    """
    Dead Letter Queue for storing failed operations for later analysis or retry.

    This implementation stores failed operations as JSON files in a specified
    directory for durability and easy inspection.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        """
        Initialize the Dead Letter Queue.

        Args:
            storage_dir: Directory to store DLQ items. If None, defaults to
                         a 'dlq' subdirectory in the current working directory.
        """
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "dlq")
        os.makedirs(self.storage_dir, exist_ok=True)
        logger.info(f"Initialized Dead Letter Queue at {self.storage_dir}")

    def add_item(
        self,
        error: ApiLinkerError,
        payload: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Add a failed item to the Dead Letter Queue.

        Args:
            error: The error that caused the operation to fail
            payload: The data that was being processed when the failure occurred
            metadata: Additional metadata about the operation

        Returns:
            ID of the DLQ item for reference
        """
        # Generate a unique ID for the item based on timestamp and error details
        item_id = f"{int(time.time())}_{error.error_category.value}_{error.correlation_id or 'unknown'}"

        # Create the DLQ item with all relevant information
        dlq_item = {
            "id": item_id,
            "timestamp": datetime.now().isoformat(),
            "error": error.to_dict(),
            "payload": payload,
            "metadata": metadata or {},
        }

        # Write to file for persistence
        file_path = os.path.join(self.storage_dir, f"{item_id}.json")
        with open(file_path, "w") as f:
            json.dump(dlq_item, f, default=str, indent=2)

        logger.info(f"Added item to DLQ: {item_id}")
        return item_id

    def get_items(
        self,
        error_category: Optional[ErrorCategory] = None,
        since_timestamp: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve items from the Dead Letter Queue with optional filtering.

        Args:
            error_category: Filter items by error category
            since_timestamp: Only return items after this timestamp
            limit: Maximum number of items to return

        Returns:
            List of DLQ items matching the criteria
        """
        items = []

        # List all DLQ files
        dlq_files = list(Path(self.storage_dir).glob("*.json"))

        # Sort by creation time (newest first)
        dlq_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Apply filters and load items
        for file_path in dlq_files[:limit]:
            try:
                with open(file_path, "r") as f:
                    item = json.load(f)

                # Apply filters
                if (
                    error_category
                    and item["error"]["error_category"] != error_category.value
                ):
                    continue

                if since_timestamp and item["timestamp"] < since_timestamp:
                    continue

                items.append(item)

                if len(items) >= limit:
                    break

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error reading DLQ item {file_path}: {str(e)}")

        return items

    def retry_item(
        self, item_id: str, operation: Callable[[Any], Any]
    ) -> Tuple[bool, Optional[Any], Optional[ApiLinkerError]]:
        """
        Retry a specific item from the Dead Letter Queue.

        Args:
            item_id: ID of the item to retry
            operation: Function to call with the payload

        Returns:
            Tuple of (success, result, error)
        """
        file_path = os.path.join(self.storage_dir, f"{item_id}.json")

        if not os.path.exists(file_path):
            logger.error(f"DLQ item not found: {item_id}")
            return False, None, ApiLinkerError(f"DLQ item not found: {item_id}")

        try:
            with open(file_path, "r") as f:
                item = json.load(f)

            payload = item["payload"]

            # Attempt to retry the operation
            result = operation(payload)

            # If successful, move the item to a 'processed' subdirectory
            processed_dir = os.path.join(self.storage_dir, "processed")
            os.makedirs(processed_dir, exist_ok=True)
            os.rename(file_path, os.path.join(processed_dir, f"{item_id}.json"))

            logger.info(f"Successfully retried DLQ item: {item_id}")
            return True, result, None

        except Exception as e:
            error = ApiLinkerError.from_exception(
                e,
                correlation_id=item.get("error", {}).get("correlation_id"),
                operation_id=f"dlq_retry_{item_id}",
            )
            logger.error(f"Failed to retry DLQ item: {item_id} - {error}")
            return False, None, error


class CircuitBreaker(Generic[T]):
    """
    Circuit Breaker implementation to prevent cascading failures.

    When a service is failing, the circuit breaker will "open" after a certain
    threshold of failures, preventing further calls to the failing service until
    a reset timeout has passed. This helps to:

    1. Prevent overwhelming an already struggling service
    2. Fail fast rather than waiting for timeouts
    3. Allow the service time to recover
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        reset_timeout_seconds: float = 60.0,
        half_open_max_calls: int = 1,
    ):
        """
        Initialize a circuit breaker.

        Args:
            name: Name of this circuit breaker for logging
            failure_threshold: Number of consecutive failures before opening circuit
            reset_timeout_seconds: Time to wait before trying again (moving to HALF_OPEN)
            half_open_max_calls: Number of test calls allowed in HALF_OPEN state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.reset_timeout_seconds = reset_timeout_seconds
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitBreakerState.CLOSED
        self._failure_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0

        logger.info(
            f"Initialized circuit breaker '{name}' with failure threshold {failure_threshold}"
        )

    @property
    def state(self) -> CircuitBreakerState:
        """Get the current state of the circuit breaker."""
        # Check if it's time to move from OPEN to HALF_OPEN
        if (
            self._state == CircuitBreakerState.OPEN
            and time.time() - self._last_failure_time >= self.reset_timeout_seconds
        ):
            self._state = CircuitBreakerState.HALF_OPEN
            self._half_open_calls = 0
            logger.info(f"Circuit '{self.name}' state changed from OPEN to HALF_OPEN")

        return self._state

    def execute(
        self, operation: Callable[[], T]
    ) -> Tuple[Optional[T], Optional[ApiLinkerError]]:
        """
        Execute an operation with circuit breaker protection.

        Args:
            operation: The function to execute

        Returns:
            Tuple of (result, error)
        """
        current_state = self.state

        # Check if circuit is open - fail fast
        if current_state == CircuitBreakerState.OPEN:
            logger.warning(f"Circuit '{self.name}' is OPEN - failing fast")
            return None, ApiLinkerError(
                message=f"Circuit breaker '{self.name}' is open",
                error_category=ErrorCategory.SERVER,
                additional_context={"circuit_breaker": self.name},
            )

        # Check if we've reached the call limit in HALF_OPEN state
        if (
            current_state == CircuitBreakerState.HALF_OPEN
            and self._half_open_calls >= self.half_open_max_calls
        ):
            logger.warning(
                f"Circuit '{self.name}' is HALF_OPEN and call limit reached - failing fast"
            )
            return None, ApiLinkerError(
                message=f"Circuit breaker '{self.name}' is half-open and call limit reached",
                error_category=ErrorCategory.SERVER,
                additional_context={"circuit_breaker": self.name},
            )

        # Increment call counter in HALF_OPEN state
        if current_state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls += 1

        try:
            # Execute the operation
            result = operation()

            # Success - reset failure count
            self._success()
            return result, None

        except Exception as e:
            # Handle failure
            error = ApiLinkerError.from_exception(
                e, additional_context={"circuit_breaker": self.name}
            )
            self._failure()
            return None, error

    def _success(self) -> None:
        """Handle a successful operation."""
        if self._state != CircuitBreakerState.CLOSED:
            logger.info(f"Circuit '{self.name}' closing due to successful operation")
            self._state = CircuitBreakerState.CLOSED

        self._failure_count = 0

    def _failure(self) -> None:
        """Handle a failed operation."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if (
            self._state == CircuitBreakerState.CLOSED
            and self._failure_count >= self.failure_threshold
        ):
            logger.warning(
                f"Circuit '{self.name}' opening after {self._failure_count} consecutive failures"
            )
            self._state = CircuitBreakerState.OPEN

        elif self._state == CircuitBreakerState.HALF_OPEN:
            logger.warning(
                f"Circuit '{self.name}' reopening after failure in HALF_OPEN state"
            )
            self._state = CircuitBreakerState.OPEN

        logger.debug(
            f"Circuit '{self.name}' recorded failure ({self._failure_count}/{self.failure_threshold})"
        )


class ErrorRecoveryManager:
    """
    Manages error recovery strategies for different types of operations.

    This class centralizes error recovery logic to make it configurable and consistent
    across the application.
    """

    def __init__(self, dlq: Optional[DeadLetterQueue] = None):
        """
        Initialize the error recovery manager.

        Args:
            dlq: Dead letter queue for storing failed operations
        """
        self.dlq = dlq or DeadLetterQueue()
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_strategies: Dict[ErrorCategory, List[RecoveryStrategy]] = {
            ErrorCategory.NETWORK: [RecoveryStrategy.EXPONENTIAL_BACKOFF],
            ErrorCategory.TIMEOUT: [RecoveryStrategy.EXPONENTIAL_BACKOFF],
            ErrorCategory.RATE_LIMIT: [RecoveryStrategy.EXPONENTIAL_BACKOFF],
            ErrorCategory.SERVER: [
                RecoveryStrategy.CIRCUIT_BREAKER,
                RecoveryStrategy.EXPONENTIAL_BACKOFF,
            ],
            ErrorCategory.CLIENT: [RecoveryStrategy.FAIL_FAST],
            ErrorCategory.AUTHENTICATION: [RecoveryStrategy.FAIL_FAST],
            ErrorCategory.VALIDATION: [RecoveryStrategy.FAIL_FAST],
            ErrorCategory.MAPPING: [RecoveryStrategy.FAIL_FAST],
            ErrorCategory.PLUGIN: [RecoveryStrategy.FAIL_FAST],
            ErrorCategory.UNKNOWN: [RecoveryStrategy.RETRY],
        }

        # Custom strategies by operation type
        self.custom_strategies: Dict[
            str, Dict[ErrorCategory, List[RecoveryStrategy]]
        ] = {}

        logger.info("Initialized ErrorRecoveryManager")

    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """
        Get or create a circuit breaker for a specific operation.

        Args:
            name: Name of the circuit breaker

        Returns:
            CircuitBreaker instance
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        return self.circuit_breakers[name]

    def set_strategy(
        self,
        error_category: ErrorCategory,
        strategies: List[RecoveryStrategy],
        operation_type: Optional[str] = None,
    ) -> None:
        """
        Set recovery strategies for an error category.

        Args:
            error_category: Type of error
            strategies: List of strategies to apply in order
            operation_type: Optional specific operation type, or None for default
        """
        if operation_type:
            if operation_type not in self.custom_strategies:
                self.custom_strategies[operation_type] = {}
            self.custom_strategies[operation_type][error_category] = strategies
        else:
            self.default_strategies[error_category] = strategies

        logger.debug(
            f"Set {len(strategies)} recovery strategies for {error_category.value}"
            + (f" in {operation_type}" if operation_type else "")
        )

    def get_strategies(
        self, error_category: ErrorCategory, operation_type: Optional[str] = None
    ) -> List[RecoveryStrategy]:
        """
        Get recovery strategies for an error category and operation type.

        Args:
            error_category: Type of error
            operation_type: Optional specific operation type

        Returns:
            List of recovery strategies
        """
        # Check for custom strategies first
        if operation_type and operation_type in self.custom_strategies:
            if error_category in self.custom_strategies[operation_type]:
                return self.custom_strategies[operation_type][error_category]

        # Fall back to default strategies
        return self.default_strategies.get(error_category, [RecoveryStrategy.RETRY])

    def handle_error(
        self,
        error: ApiLinkerError,
        payload: Any,
        operation: Callable[[Any], Any],
        operation_type: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff_factor: float = 2.0,
    ) -> Tuple[bool, Any, Optional[ApiLinkerError]]:
        """
        Handle an error using appropriate recovery strategies.

        Args:
            error: The error that occurred
            payload: Data being processed when the error occurred
            operation: Function to call for retry attempts
            operation_type: Type of operation for strategy selection
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            retry_backoff_factor: Multiplicative factor for retry delay

        Returns:
            Tuple of (success, result, error)
        """
        logger.debug(f"Handling error for {operation_type}: {error}")

        # Get applicable strategies
        strategies = self.get_strategies(error.error_category, operation_type)

        # Track whether we need to add to DLQ
        add_to_dlq = True

        # Apply each strategy in order
        for strategy in strategies:
            logger.debug(f"Applying {strategy.value} strategy for {operation_type}")

            # Circuit breaker strategy
            if strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                circuit = self.get_circuit_breaker(operation_type)
                result, cb_error = circuit.execute(lambda: operation(payload))

                if result is not None:
                    # Circuit breaker allowed the call and it succeeded
                    return True, result, None

                # If circuit is open, skip other strategies
                if cb_error and cb_error.additional_context.get("circuit_breaker"):
                    return False, None, cb_error

            # Simple retry strategy
            elif strategy == RecoveryStrategy.RETRY:
                for attempt in range(max_retries):
                    try:
                        result = operation(payload)
                        return True, result, None
                    except Exception as e:
                        logger.warning(
                            f"Retry {attempt+1}/{max_retries} failed: {str(e)}"
                        )
                        if attempt == max_retries - 1:
                            error = ApiLinkerError.from_exception(
                                e,
                                operation_id=f"{operation_type}_retry_{attempt}",
                                correlation_id=error.correlation_id,
                            )

            # Exponential backoff retry strategy
            elif strategy == RecoveryStrategy.EXPONENTIAL_BACKOFF:
                current_delay = retry_delay

                for attempt in range(max_retries):
                    try:
                        if attempt > 0:
                            logger.info(
                                f"Waiting {current_delay:.2f}s before retry {attempt+1}/{max_retries}"
                            )
                            time.sleep(current_delay)
                            current_delay *= retry_backoff_factor

                        result = operation(payload)
                        return True, result, None

                    except Exception as e:
                        logger.warning(
                            f"Retry {attempt+1}/{max_retries} failed: {str(e)}"
                        )
                        if attempt == max_retries - 1:
                            error = ApiLinkerError.from_exception(
                                e,
                                operation_id=f"{operation_type}_retry_{attempt}",
                                correlation_id=error.correlation_id,
                            )

            # Skip strategy - don't add to DLQ
            elif strategy == RecoveryStrategy.SKIP:
                add_to_dlq = False
                return False, None, error

            # Fail fast strategy - just return the error
            elif strategy == RecoveryStrategy.FAIL_FAST:
                # Still add to DLQ for analysis
                break

            # Fallback strategy would go here - not implemented yet

        # If we reach here, all strategies failed

        # Add to DLQ if configured
        if add_to_dlq:
            dlq_id = self.dlq.add_item(
                error=error,
                payload=payload,
                metadata={"operation_type": operation_type},
            )
            # Update error with DLQ information
            if error.additional_context is None:
                error.additional_context = {}
            error.additional_context["dlq_id"] = dlq_id

        return False, None, error


class ErrorAnalytics:
    """
    Collects and analyzes error data to provide insights on system health.
    """

    def __init__(self, max_errors: int = 1000):
        """
        Initialize error analytics.

        Args:
            max_errors: Maximum number of errors to keep in memory
        """
        self.max_errors = max_errors
        self.errors: List[Dict[str, Any]] = []
        self.error_counts: Dict[str, int] = {}  # By category
        self.error_rates: Dict[str, List[Tuple[float, int]]] = (
            {}
        )  # Category -> [(timestamp, count)]
        self.last_analyzed: float = time.time()

    def record_error(self, error: ApiLinkerError) -> None:
        """Record an error for analysis."""
        # Convert to dict for storage
        error_dict = error.to_dict()

        # Add to errors list, keeping under max size
        self.errors.append(error_dict)
        if len(self.errors) > self.max_errors:
            self.errors.pop(0)

        # Update error counts by category
        category = error.error_category.value
        self.error_counts[category] = self.error_counts.get(category, 0) + 1

        # Update error rates
        if category not in self.error_rates:
            self.error_rates[category] = []

        now = time.time()
        self.error_rates[category].append((now, 1))

        # Clean up old rate data (older than 1 hour)
        one_hour_ago = now - 3600
        for cat in self.error_rates:
            self.error_rates[cat] = [
                (ts, count) for ts, count in self.error_rates[cat] if ts > one_hour_ago
            ]

    def get_error_rate(
        self, category: Optional[ErrorCategory] = None, minutes: int = 5
    ) -> float:
        """
        Get the error rate for a category over the specified time period.

        Args:
            category: Error category or None for all categories
            minutes: Time window in minutes

        Returns:
            Errors per minute
        """
        now = time.time()
        since = now - (minutes * 60)

        if category:
            categories = [category.value]
        else:
            categories = list(self.error_rates.keys())

        error_count = 0
        for cat in categories:
            if cat in self.error_rates:
                error_count += sum(
                    count for ts, count in self.error_rates[cat] if ts > since
                )

        return error_count / minutes if minutes > 0 else 0

    def get_top_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most frequent error categories."""
        sorted_categories = sorted(
            self.error_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"category": cat, "count": count}
            for cat, count in sorted_categories[:limit]
        ]

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of error statistics."""
        total_errors = sum(self.error_counts.values())

        return {
            "total_errors": total_errors,
            "error_counts_by_category": self.error_counts,
            "recent_error_rate": self.get_error_rate(minutes=5),
            "top_errors": self.get_top_errors(),
        }


# Factory function to create ErrorHandler for easy usage
def create_error_handler(
    dlq_dir: Optional[str] = None,
) -> Tuple[DeadLetterQueue, ErrorRecoveryManager, ErrorAnalytics]:
    """
    Create a complete error handling system.

    Args:
        dlq_dir: Directory to store DLQ items

    Returns:
        Tuple of (DeadLetterQueue, ErrorRecoveryManager, ErrorAnalytics)
    """
    dlq = DeadLetterQueue(dlq_dir)
    recovery_manager = ErrorRecoveryManager(dlq)
    analytics = ErrorAnalytics()
    return dlq, recovery_manager, analytics
