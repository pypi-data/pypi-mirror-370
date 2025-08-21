"""
Main ApiLinker class that orchestrates the connection, mapping, and data transfer between APIs.
"""

import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple, TypedDict, Union

import yaml
from pydantic import BaseModel, Field

from apilinker.core.auth import AuthManager
from apilinker.core.connector import ApiConnector
from apilinker.core.error_handling import (
    ApiLinkerError,
    CircuitBreaker,
    DeadLetterQueue,
    ErrorCategory,
    RecoveryStrategy,
    create_error_handler,
)
from apilinker.core.logger import setup_logger
from apilinker.core.mapper import FieldMapper
from apilinker.core.scheduler import Scheduler
from apilinker.core.security import (
    EncryptionLevel,
)
from apilinker.core.security_integration import (
    SecurityManager,
    integrate_security_with_auth_manager,
)
from apilinker.core.validation import (
    validate_payload_against_schema,
    is_validator_available,
)
from apilinker.core.provenance import ProvenanceRecorder
from apilinker.core.idempotency import InMemoryDeduplicator, generate_idempotency_key
from apilinker.core.state_store import (
    FileStateStore,
    SQLiteStateStore,
    StateStore,
    now_iso,
)


# Legacy error detail class kept for backward compatibility
class ErrorDetail(BaseModel):
    """Detailed error information for API requests."""

    message: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    request_url: Optional[str] = None
    request_method: Optional[str] = None
    timestamp: Optional[str] = None
    error_type: str = "general"

    @classmethod
    def from_apilinker_error(cls, error: ApiLinkerError) -> "ErrorDetail":
        """Convert an ApiLinkerError to ErrorDetail for backward compatibility."""
        return cls(
            message=error.message,
            status_code=error.status_code,
            response_body=error.response_body,
            request_url=error.request_url,
            request_method=error.request_method,
            timestamp=error.timestamp,
            error_type=error.error_category.value.lower(),
        )


class SyncResult(BaseModel):
    """Result of a sync operation with enhanced error reporting."""

    count: int = 0
    success: bool = True
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_response: Dict[str, Any] = Field(default_factory=dict)
    target_response: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[int] = None


class ApiLinker:
    """
    Main class for connecting, mapping and transferring data between APIs.

    This class orchestrates the entire process of:
    1. Connecting to source and target APIs
    2. Fetching data from the source
    3. Mapping fields according to configuration
    4. Transforming data as needed
    5. Sending data to the target
    6. Scheduling recurring operations

    Args:
        config_path: Path to YAML/JSON configuration file
        source_config: Direct source configuration dictionary
        target_config: Direct target configuration dictionary
        mapping_config: Direct mapping configuration dictionary
        schedule_config: Direct scheduling configuration dictionary
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        source_config: Optional[Dict[str, Any]] = None,
        target_config: Optional[Dict[str, Any]] = None,
        mapping_config: Optional[Dict[str, Any]] = None,
        schedule_config: Optional[Dict[str, Any]] = None,
        error_handling_config: Optional[Dict[str, Any]] = None,
        security_config: Optional[Dict[str, Any]] = None,
        validation_config: Optional[Dict[str, Any]] = None,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
    ) -> None:
        # Initialize logger
        self.logger = setup_logger(log_level, log_file)
        self.logger.info("Initializing ApiLinker")

        # Initialize components
        self.source: Optional[ApiConnector] = None
        self.target: Optional[ApiConnector] = None
        self.mapper = FieldMapper()
        self.scheduler = Scheduler()
        self.validation_config = validation_config or {"strict_mode": False}
        self.provenance = ProvenanceRecorder()
        self.deduplicator = InMemoryDeduplicator()
        self.state_store: Optional[StateStore] = None

        # Initialize security system
        self.security_manager = self._initialize_security(security_config)

        # Initialize auth manager and integrate with security
        self.auth_manager = AuthManager()
        integrate_security_with_auth_manager(self.security_manager, self.auth_manager)

        # Initialize error handling system
        self.dlq, self.error_recovery_manager, self.error_analytics = (
            create_error_handler()
        )

        # Load configuration if provided
        if config_path:
            self.load_config(config_path)
        else:
            # Set up direct configurations if provided
            if source_config:
                self.add_source(**source_config)
            if target_config:
                self.add_target(**target_config)
            if mapping_config:
                self.add_mapping(**mapping_config)
            if schedule_config:
                self.add_schedule(**schedule_config)
            if error_handling_config:
                self._configure_error_handling(error_handling_config)
            if security_config:
                self._configure_security(security_config)

    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a YAML or JSON file.

        Args:
            config_path: Path to the configuration file
        """
        self.logger.info(f"Loading configuration from {config_path}")

        # Resolve environment variables in config path
        config_path = os.path.expandvars(config_path)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Set up components from config
        if "source" in config:
            self.add_source(**config["source"])

        if "target" in config:
            self.add_target(**config["target"])

        if "mapping" in config:
            if isinstance(config["mapping"], list):
                for mapping in config["mapping"]:
                    self.add_mapping(**mapping)
            else:
                self.add_mapping(**config["mapping"])

        if "schedule" in config:
            self.add_schedule(**config["schedule"])

        # Configure error handling if specified
        if "error_handling" in config:
            self._configure_error_handling(config["error_handling"])

        # Configure security if specified
        if "security" in config:
            self._configure_security(config["security"])

        # Validation configuration
        if "validation" in config:
            self.validation_config = config["validation"]

        if "logging" in config:
            log_config = config["logging"]
            log_level = log_config.get("level", "INFO")
            log_file = log_config.get("file")
            self.logger = setup_logger(log_level, log_file)

        # Provenance options
        if "provenance" in config:
            prov_cfg = config["provenance"]
            output_dir = prov_cfg.get("output_dir")
            jsonl_log = prov_cfg.get("jsonl_log")
            self.provenance = ProvenanceRecorder(
                output_dir=output_dir, jsonl_log_path=jsonl_log
            )

        # Idempotency
        if "idempotency" in config:
            self.idempotency_config = config["idempotency"]
        else:
            self.idempotency_config = {"enabled": False, "salt": ""}

        # State store
        if "state" in config:
            st_cfg = config["state"]
            st_type = st_cfg.get("type", "file")
            if st_type == "file":
                path = st_cfg.get("path", ".apilinker/state.json")
                default_last_sync = st_cfg.get("default_last_sync")
                self.state_store = FileStateStore(
                    path, default_last_sync=default_last_sync
                )
            elif st_type == "sqlite":
                path = st_cfg.get("path", ".apilinker/state.db")
                default_last_sync = st_cfg.get("default_last_sync")
                self.state_store = SQLiteStateStore(
                    path, default_last_sync=default_last_sync
                )

    def add_source(
        self,
        type: str,
        base_url: str,
        auth: Optional[Dict[str, Any]] = None,
        endpoints: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Add a source API connector.

        Args:
            type: Type of API connector (rest, graphql, etc.)
            base_url: Base URL of the API
            auth: Authentication configuration
            endpoints: Configured endpoints
            **kwargs: Additional configuration parameters
        """
        self.logger.info(f"Adding source connector: {type} for {base_url}")

        # Set up authentication if provided
        if auth:
            auth_config = self.auth_manager.configure_auth(auth)
        else:
            auth_config = None

        # Create source connector
        self.source = ApiConnector(
            connector_type=type,
            base_url=base_url,
            auth_config=auth_config,
            endpoints=endpoints or {},
            **kwargs,
        )

    def add_target(
        self,
        type: str,
        base_url: str,
        auth: Optional[Dict[str, Any]] = None,
        endpoints: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Add a target API connector.

        Args:
            type: Type of API connector (rest, graphql, etc.)
            base_url: Base URL of the API
            auth: Authentication configuration
            endpoints: Configured endpoints
            **kwargs: Additional configuration parameters
        """
        self.logger.info(f"Adding target connector: {type} for {base_url}")

        # Set up authentication if provided
        if auth:
            auth_config = self.auth_manager.configure_auth(auth)
        else:
            auth_config = None

        # Create target connector
        self.target = ApiConnector(
            connector_type=type,
            base_url=base_url,
            auth_config=auth_config,
            endpoints=endpoints or {},
            **kwargs,
        )

    def add_mapping(
        self, source: str, target: str, fields: List[Dict[str, Any]]
    ) -> None:
        """
        Add a field mapping between source and target endpoints.

        Args:
            source: Source endpoint name
            target: Target endpoint name
            fields: List of field mappings
        """
        self.logger.info(
            f"Adding mapping from {source} to {target} with {len(fields)} fields"
        )
        self.mapper.add_mapping(source, target, fields)

    def add_schedule(self, type: str, **kwargs: Any) -> None:
        """
        Add a schedule for recurring syncs.

        Args:
            type: Type of schedule (interval, cron)
            **kwargs: Schedule-specific parameters
        """
        self.logger.info(f"Adding schedule: {type}")
        self.scheduler.add_schedule(type, **kwargs)

    def _initialize_security(
        self, config: Optional[Dict[str, Any]] = None
    ) -> SecurityManager:
        """
        Initialize the security system based on provided configuration.

        Args:
            config: Security configuration dictionary

        Returns:
            SecurityManager instance
        """
        if not config:
            config = {}

        # Extract security configuration
        master_password = config.get("master_password")
        storage_path = config.get("credential_storage_path")
        encryption_level = config.get("encryption_level", "none")
        encryption_key = config.get("encryption_key")
        enable_access_control = config.get("enable_access_control", False)

        # Initialize security manager
        security_manager = SecurityManager(
            master_password=master_password,
            storage_path=storage_path,
            encryption_level=encryption_level,
            encryption_key=encryption_key,
            enable_access_control=enable_access_control,
        )

        # Set up initial users if access control is enabled
        if enable_access_control and "users" in config:
            for user_config in config["users"]:
                username = user_config.get("username")
                role = user_config.get("role", "viewer")
                api_key = user_config.get("api_key")

                if username:
                    security_manager.add_user(username, role, api_key)

        return security_manager

    def _configure_security(self, config: Dict[str, Any]) -> None:
        """
        Configure security features based on provided configuration.

        Args:
            config: Security configuration dictionary
        """
        self.logger.info("Configuring security features")

        # Update encryption level if specified
        if "encryption_level" in config:
            encryption_level = config["encryption_level"]
            try:
                if isinstance(encryption_level, str):
                    encryption_level = EncryptionLevel[encryption_level.upper()]
                self.security_manager.request_encryption.encryption_level = (
                    encryption_level
                )
                self.logger.debug(f"Updated encryption level to {encryption_level}")
            except (KeyError, ValueError):
                self.logger.warning(f"Invalid encryption level: {encryption_level}")

        # Add users if specified and access control is enabled
        if self.security_manager.enable_access_control and "users" in config:
            for user_config in config["users"]:
                username = user_config.get("username")
                role = user_config.get("role", "viewer")
                api_key = user_config.get("api_key")

                if username:
                    self.security_manager.add_user(username, role, api_key)
                    self.logger.debug(f"Added user {username} with role {role}")

    def _configure_error_handling(self, config: Dict[str, Any]) -> None:
        """
        Configure the error handling system based on provided configuration.

        Args:
            config: Error handling configuration dictionary
        """
        self.logger.info("Configuring error handling system")

        # Configure circuit breakers
        if "circuit_breakers" in config:
            for cb_name, cb_config in config["circuit_breakers"].items():
                failure_threshold = cb_config.get("failure_threshold", 5)
                reset_timeout = cb_config.get("reset_timeout_seconds", 60)
                half_open_max_calls = cb_config.get("half_open_max_calls", 1)

                # Create and register circuit breaker
                circuit: CircuitBreaker = CircuitBreaker(
                    name=cb_name,
                    failure_threshold=failure_threshold,
                    reset_timeout_seconds=reset_timeout,
                    half_open_max_calls=half_open_max_calls,
                )

                self.error_recovery_manager.circuit_breakers[cb_name] = circuit
                self.logger.debug(f"Configured circuit breaker: {cb_name}")

        # Configure recovery strategies
        if "recovery_strategies" in config:
            for category_name, strategies in config["recovery_strategies"].items():
                try:
                    error_category = ErrorCategory[category_name.upper()]
                    strategy_list = [
                        RecoveryStrategy[str(s).upper()] for s in strategies
                    ]

                    self.error_recovery_manager.set_strategy(
                        error_category, strategy_list
                    )
                    self.logger.debug(
                        f"Configured recovery strategies for {category_name}: {strategies}"
                    )

                except (KeyError, ValueError) as e:
                    self.logger.warning(
                        f"Invalid recovery strategy configuration: {str(e)}"
                    )

        # Configure DLQ
        if "dlq" in config:
            dlq_dir = config["dlq"].get("directory")
            if dlq_dir:
                self.dlq = DeadLetterQueue(dlq_dir)
                self.error_recovery_manager.dlq = self.dlq
                self.logger.info(f"Configured Dead Letter Queue at {dlq_dir}")

    def get_error_analytics(self) -> Dict[str, Any]:
        """
        Get error analytics summary.

        Returns:
            Dictionary with error statistics
        """
        return self.error_analytics.get_summary()

    def add_user(
        self, username: str, role: str, api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a user to the system with specified role.

        Args:
            username: Username to identify the user
            role: Access role (admin, operator, viewer, developer)
            api_key: Optional API key for authentication

        Returns:
            User data including generated API key if not provided
        """
        if not self.security_manager.enable_access_control:
            raise ValueError(
                "Access control is not enabled. Enable it in the security configuration."
            )

        return self.security_manager.add_user(username, role, api_key)

    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users in the system.

        Returns:
            List of user data dictionaries
        """
        if not self.security_manager.enable_access_control:
            raise ValueError(
                "Access control is not enabled. Enable it in the security configuration."
            )

        users = []
        for username in self.security_manager.access_control.users:
            user_data = self.security_manager.access_control.get_user(username)
            # Remove sensitive data like API key
            if "api_key" in user_data:
                user_data["api_key"] = "*" * 8  # Mask API key
            users.append(user_data)

        return users

    def store_credential(self, name: str, credential_data: Dict[str, Any]) -> bool:
        """
        Store API credentials securely.

        Args:
            name: Name to identify the credential
            credential_data: Credential data to store

        Returns:
            True if successful, False otherwise
        """
        return self.security_manager.store_credential(name, credential_data)

    def get_credential(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get stored API credentials.

        Args:
            name: Name of the credential

        Returns:
            Credential data if found, None otherwise
        """
        return self.security_manager.get_credential(name)

    def list_credentials(self) -> List[str]:
        """
        List available credential names.

        Returns:
            List of credential names
        """
        return self.security_manager.list_credentials()

    def process_dlq(
        self, operation_type: Optional[str] = None, limit: int = 10
    ) -> Dict[str, Any]:
        """
        Process items in the Dead Letter Queue for retry.

        Args:
            operation_type: Optional operation type to filter by
            limit: Maximum number of items to process

        Returns:
            Dictionary with processing results
        """
        self.logger.info(
            f"Processing Dead Letter Queue (type={operation_type}, limit={limit})"
        )

        # Get DLQ items
        items = self.dlq.get_items(limit=limit)

        class DLQResults(TypedDict):
            total_processed: int
            successful: int
            failed: int
            items: List[Dict[str, Any]]

        results: DLQResults = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "items": [],
        }

        for item in items:
            # Skip if not matching the requested operation type
            if (
                operation_type
                and item.get("metadata", {}).get("operation_type") != operation_type
            ):
                continue

            item_id = item.get("id", "unknown")
            payload = item.get("payload", {})
            metadata = item.get("metadata", {})

            retry_result = {
                "id": item_id,
                "success": False,
                "message": "Operation not retried",
            }

            # Determine what type of operation this is and how to retry it
            if "endpoint" in payload and "source_" in metadata.get(
                "operation_type", ""
            ):
                # This is a source operation
                try:
                    self.source.fetch_data(
                        payload.get("endpoint"), payload.get("params")
                    )
                    retry_result["success"] = True
                    retry_result["message"] = "Successfully retried source operation"
                    results["successful"] += 1
                except Exception as e:
                    retry_result["message"] = (
                        f"Failed to retry source operation: {str(e)}"
                    )
                    results["failed"] += 1

            elif "endpoint" in payload and "target_" in metadata.get(
                "operation_type", ""
            ):
                # This is a target operation
                try:
                    self.target.send_data(payload.get("endpoint"), payload.get("data"))
                    retry_result["success"] = True
                    retry_result["message"] = "Successfully retried target operation"
                    results["successful"] += 1
                except Exception as e:
                    retry_result["message"] = (
                        f"Failed to retry target operation: {str(e)}"
                    )
                    results["failed"] += 1

            else:
                # Unknown operation type
                retry_result["message"] = "Unknown operation type - cannot retry"
                results["failed"] += 1

            results["total_processed"] += 1
            results["items"].append(retry_result)

        self.logger.info(
            f"DLQ processing complete: {results['successful']} successful, {results['failed']} failed"
        )
        return dict(results)

    def sync(
        self,
        source_endpoint: Optional[str] = None,
        target_endpoint: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        retry_backoff_factor: float = 2.0,
        retry_status_codes: Optional[List[int]] = None,
    ) -> SyncResult:
        """
        Execute a sync operation between source and target APIs.

        Args:
            source_endpoint: Source endpoint to use (overrides mapping)
            target_endpoint: Target endpoint to use (overrides mapping)
            params: Additional parameters for the source API call
            max_retries: Maximum number of retry attempts for transient failures
            retry_delay: Initial delay between retries in seconds
            retry_backoff_factor: Multiplicative factor for retry delay
            retry_status_codes: HTTP status codes to retry (default: 429, 502, 503, 504)

        Returns:
            SyncResult: Result of the sync operation
        """
        if not self.source or not self.target:
            raise ValueError(
                "Source and target connectors must be configured before syncing"
            )

        # If no endpoints specified, use the first mapping
        if not source_endpoint or not target_endpoint:
            mapping = self.mapper.get_first_mapping()
            if not mapping:
                raise ValueError("No mapping configured and no endpoints specified")
            source_endpoint = mapping["source"]
            target_endpoint = mapping["target"]

        # Generate correlation ID for this sync operation
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        # Start provenance
        self.provenance.start_run(
            correlation_id=correlation_id,
            config_path=(
                config_path
                if (config_path := getattr(self, "_last_config_path", None))
                else None
            ),
            source_endpoint=source_endpoint,
            target_endpoint=target_endpoint,
        )

        # Default retry status codes if none provided
        if retry_status_codes is None:
            retry_status_codes = [429, 502, 503, 504]  # Common transient failures

        self.logger.info(
            f"[{correlation_id}] Starting sync from {source_endpoint} to {target_endpoint}"
        )

        # Initialize result object
        sync_result = SyncResult(correlation_id=correlation_id)

        # Get circuit breaker for source endpoint
        source_circuit_name = f"source_{source_endpoint}"
        source_cb = self.error_recovery_manager.get_circuit_breaker(source_circuit_name)

        # Check if user has permission for this operation
        if self.security_manager.enable_access_control:
            current_user = getattr(self, "current_user", None)
            if current_user and not self.security_manager.check_permission(
                current_user, "run_sync"
            ):
                raise PermissionError(
                    f"User {current_user} does not have permission to run sync operations"
                )

        # Merge last_sync into params from state store if not provided
        if params is None:
            effective_params = None
        else:
            effective_params = dict(params)
        if self.state_store:
            # Ensure we have a dict if we are going to inject
            need_inject = (effective_params is None) or (
                "updated_since" not in effective_params
            )
            if need_inject:
                last_sync = self.state_store.get_last_sync(source_endpoint)
                if last_sync:
                    effective_params = dict(effective_params or {})
                    effective_params["updated_since"] = last_sync

        # Always use standard non-encrypted call
        source_data, source_error = source_cb.execute(
            lambda: self.source.fetch_data(source_endpoint, effective_params)
        )

        # If circuit breaker failed, try recovery strategies
        if source_error:
            # Create payload for retry
            fetch_payload = {"endpoint": source_endpoint, "params": params}

            # Apply recovery strategies
            success, result, error = self.error_recovery_manager.handle_error(
                error=source_error,
                payload=fetch_payload,
                operation=lambda p: self.source.fetch_data(p["endpoint"], p["params"]),
                operation_type=source_circuit_name,
                max_retries=max_retries,
                retry_delay=retry_delay,
                retry_backoff_factor=retry_backoff_factor,
            )

            if success:
                source_data = result
            else:
                # Record the error for analytics
                self.error_analytics.record_error(error)

                # Update result with error details
                end_time = time.time()
                sync_result.duration_ms = int((end_time - start_time) * 1000)
                sync_result.success = False
                sync_result.errors.append(error.to_dict())
                self.logger.error(f"[{correlation_id}] Sync failed: {error}")
                return sync_result

        try:
            # Map fields according to configuration
            transformed_data = self.mapper.map_data(
                source_endpoint, target_endpoint, source_data
            )

            # Optional strict validation against target request schema (if defined in connector)
            if self.validation_config.get("strict_mode") and is_validator_available():
                target_endpoint_cfg = (
                    self.target.endpoints.get(target_endpoint) if self.target else None
                )
                if target_endpoint_cfg and target_endpoint_cfg.request_schema:
                    if isinstance(transformed_data, list):
                        for item in transformed_data:
                            valid, diffs = validate_payload_against_schema(
                                item, target_endpoint_cfg.request_schema
                            )
                            if not valid:
                                raise ApiLinkerError(
                                    message="Strict mode: target payload failed schema validation",
                                    error_category=ErrorCategory.VALIDATION,
                                    status_code=0,
                                    additional_context={"diffs": diffs},
                                )
                    else:
                        valid, diffs = validate_payload_against_schema(
                            transformed_data, target_endpoint_cfg.request_schema
                        )
                        if not valid:
                            raise ApiLinkerError(
                                message="Strict mode: target payload failed schema validation",
                                error_category=ErrorCategory.VALIDATION,
                                status_code=0,
                                additional_context={"diffs": diffs},
                            )

            # Record source data metrics
            source_count = len(source_data) if isinstance(source_data, list) else 1
            sync_result.details["source_count"] = source_count

            # Get circuit breaker for target endpoint
            target_circuit_name = f"target_{target_endpoint}"
            target_cb = self.error_recovery_manager.get_circuit_breaker(
                target_circuit_name
            )

            # Idempotency: skip payloads we've already sent during replays
            def _send():
                # If idempotency enabled, de-duplicate per item
                if self.idempotency_config.get("enabled") and isinstance(
                    transformed_data, list
                ):
                    salt = self.idempotency_config.get("salt", "")
                    filtered = []
                    for item in transformed_data:
                        key = generate_idempotency_key(item, salt=salt)
                        if not self.deduplicator.has_seen(target_endpoint, key):
                            self.deduplicator.mark_seen(target_endpoint, key)
                            filtered.append(item)
                    payload: Union[Dict[str, Any], List[Dict[str, Any]]] = filtered
                else:
                    payload = transformed_data
                return self.target.send_data(target_endpoint, payload)

            # Always use standard non-encrypted call
            target_result, target_error = target_cb.execute(_send)

            # If circuit breaker failed, try recovery strategies
            if target_error:
                # Create payload for retry
                send_payload = {"endpoint": target_endpoint, "data": transformed_data}

                # Apply recovery strategies
                success, result, error = self.error_recovery_manager.handle_error(
                    error=target_error,
                    payload=send_payload,
                    operation=lambda p: self.target.send_data(p["endpoint"], p["data"]),
                    operation_type=target_circuit_name,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    retry_backoff_factor=retry_backoff_factor,
                )

                if success:
                    target_result = result
                else:
                    # Record the error for analytics
                    self.error_analytics.record_error(error)

                    # Update result with error details
                    end_time = time.time()
                    sync_result.duration_ms = int((end_time - start_time) * 1000)
                    sync_result.success = False
                    sync_result.errors.append(error.to_dict())
                    self.logger.error(f"[{correlation_id}] Sync failed: {error}")
                    return sync_result

            # Update result with success information
            sync_result.count = (
                len(transformed_data) if isinstance(transformed_data, list) else 1
            )
            sync_result.success = True

            # Set target response directly
            if isinstance(target_result, dict):
                sync_result.target_response = target_result
            else:
                sync_result.target_response = {}

            # Calculate duration
            end_time = time.time()
            sync_result.duration_ms = int((end_time - start_time) * 1000)

            self.logger.info(
                f"[{correlation_id}] Sync completed successfully: {sync_result.count} items transferred in {sync_result.duration_ms}ms"
            )
            # Update last_sync checkpoint
            if self.state_store:
                self.state_store.set_last_sync(source_endpoint, now_iso())
            # Complete provenance
            self.provenance.complete_run(True, sync_result.count, sync_result.details)
            return sync_result

        except Exception as e:
            # Convert to ApiLinkerError
            error = ApiLinkerError.from_exception(
                e,
                error_category=ErrorCategory.MAPPING,
                correlation_id=correlation_id,
                operation_id=f"mapping_{source_endpoint}_to_{target_endpoint}",
            )

            # Record the error for analytics
            self.error_analytics.record_error(error)

            # Update result
            end_time = time.time()
            sync_result.duration_ms = int((end_time - start_time) * 1000)
            sync_result.success = False
            sync_result.errors.append(error.to_dict())

            self.logger.error(f"[{correlation_id}] Sync failed during mapping: {error}")
            # Record error in provenance
            self.provenance.record_error(
                error.message,
                category=error.error_category.value,
                status_code=error.status_code,
                endpoint=target_endpoint,
            )
            self.provenance.complete_run(False, 0, {})
            return sync_result

    def start_scheduled_sync(self) -> None:
        """Start scheduled sync operations."""
        self.logger.info("Starting scheduled sync")
        self.scheduler.start(self.sync)

    def stop_scheduled_sync(self) -> None:
        """Stop scheduled sync operations."""
        self.logger.info("Stopping scheduled sync")
        self.scheduler.stop()

    def _with_retries(
        self,
        operation: Callable[[], Any],
        operation_name: str,
        max_retries: int,
        retry_delay: float,
        retry_backoff_factor: float,
        retry_status_codes: List[int],
        correlation_id: str,
    ) -> Tuple[Any, Optional[ErrorDetail]]:
        """
        Execute an operation with configurable retry logic for transient failures.

        Args:
            operation: Callable function to execute
            operation_name: Name of operation for logging
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            retry_backoff_factor: Multiplicative factor for retry delay
            retry_status_codes: HTTP status codes that should trigger a retry
            correlation_id: Correlation ID for tracing

        Returns:
            Tuple of (result, error_detail) - If successful, error_detail will be None
        """
        current_delay = retry_delay

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.info(
                        f"[{correlation_id}] Retry attempt {attempt}/{max_retries} for {operation_name} after {current_delay:.2f}s delay"
                    )
                    time.sleep(current_delay)
                    current_delay *= retry_backoff_factor

                result = operation()

                if attempt > 0:
                    self.logger.info(
                        f"[{correlation_id}] Retry succeeded for {operation_name}"
                    )

                return result, None

            except Exception as e:
                status_code = getattr(e, "status_code", None)
                response_body = getattr(e, "response", None)
                request_url = getattr(e, "url", None)
                request_method = getattr(e, "method", None)

                # Convert response to string if it's not already
                if response_body and not isinstance(response_body, str):
                    try:
                        response_body = str(response_body)[:1000]  # Limit size
                    except:
                        response_body = "<Unable to convert response to string>"

                error_detail = ErrorDetail(
                    message=str(e),
                    status_code=status_code,
                    response_body=response_body,
                    request_url=request_url,
                    request_method=request_method,
                    timestamp=datetime.now().isoformat(),
                    error_type=(
                        "transient_error"
                        if status_code in retry_status_codes
                        else "api_error"
                    ),
                )

                # Check if this is a retryable error
                is_retryable = (
                    status_code in retry_status_codes if status_code else False
                )

                if is_retryable and attempt < max_retries:
                    self.logger.warning(
                        f"[{correlation_id}] {operation_name} failed with retryable error (status: {status_code}): {str(e)}"
                    )
                else:
                    # Either not retryable or out of retries
                    log_level = logging.WARNING if is_retryable else logging.ERROR
                    retry_msg = (
                        "out of retry attempts"
                        if is_retryable
                        else "non-retryable error"
                    )

                    self.logger.log(
                        log_level,
                        f"[{correlation_id}] {operation_name} failed with {retry_msg}: {str(e)}",
                    )
                    return None, error_detail

        # We should never reach here, but just in case
        fallback_error = ErrorDetail(
            message=f"Unknown error during {operation_name}",
            timestamp=datetime.now().isoformat(),
            error_type="unknown_error",
        )
        return None, fallback_error
