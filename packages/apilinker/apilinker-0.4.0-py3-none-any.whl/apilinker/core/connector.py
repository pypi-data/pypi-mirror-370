"""
API Connector module for handling connections to different types of APIs.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
from pydantic import BaseModel, Field
from pydantic import ConfigDict

from apilinker.core.auth import AuthConfig
from apilinker.core.error_handling import ApiLinkerError, ErrorCategory
from apilinker.core.validation import (
    validate_payload_against_schema,
    pretty_print_diffs,
    is_validator_available,
)

logger = logging.getLogger(__name__)


class EndpointConfig(BaseModel):
    """Configuration for an API endpoint."""

    path: str
    method: str = "GET"
    params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    body_template: Optional[Dict[str, Any]] = None
    pagination: Optional[Dict[str, Any]] = None
    response_path: Optional[str] = None
    # Optional JSON Schemas for validation
    response_schema: Optional[Dict[str, Any]] = None
    request_schema: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ApiConnector:
    """
    API Connector for interacting with REST APIs.

    This class handles the connection to APIs, making requests, and
    processing responses.

    Args:
        connector_type: Type of connector (rest, graphql, etc.)
        base_url: Base URL for the API
        auth_config: Authentication configuration
        endpoints: Dictionary of endpoint configurations
        timeout: Request timeout in seconds
        retry_count: Number of retries on failure
        retry_delay: Delay between retries in seconds
    """

    def __init__(
        self,
        connector_type: str,
        base_url: str,
        auth_config: Optional[AuthConfig] = None,
        endpoints: Optional[Dict[str, Dict[str, Any]]] = None,
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: int = 1,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        self.connector_type = connector_type
        self.base_url = base_url
        self.auth_config = auth_config
        self.timeout = timeout
        self.retry_count = retry_count
        self.retry_delay = retry_delay

        # Default headers (may be provided via explicit parameter or legacy 'headers' kwarg)
        if default_headers is None and "headers" in kwargs:
            try:
                default_headers = dict(kwargs.pop("headers"))
            except Exception:
                default_headers = None
        self.default_headers: Dict[str, str] = default_headers or {}
        # Provide a backwards-compatible attribute name used by some connectors
        self.headers: Dict[str, str] = self.default_headers

        # Parse and store endpoint configurations
        self.endpoints: Dict[str, EndpointConfig] = {}
        if endpoints:
            for name, config in endpoints.items():
                self.endpoints[name] = EndpointConfig(**config)

        # Store additional settings
        self.settings: Dict[str, Any] = kwargs

        # Create HTTP client with default settings
        self.client = self._create_client()

        logger.debug(f"Initialized {connector_type} connector for {base_url}")

    def _create_client(self) -> httpx.Client:
        """Create an HTTP client with appropriate settings."""
        # Initialize with default parameters
        auth = None
        if (
            self.auth_config
            and self.auth_config.type == "basic"
            and hasattr(self.auth_config, "username")
            and hasattr(self.auth_config, "password")
        ):
            auth = httpx.BasicAuth(
                username=getattr(self.auth_config, "username", ""),
                password=getattr(self.auth_config, "password", ""),
            )

        # Create client with properly structured parameters
        return httpx.Client(base_url=self.base_url, timeout=self.timeout, auth=auth)

    def _prepare_request(
        self, endpoint_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare a request for the given endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            params: Additional parameters to include in the request

        Returns:
            Dict containing request details (url, method, headers, params, json)
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]

        # Combine endpoint path with base URL
        url = endpoint.path

        # Combine params from endpoint config and provided params
        request_params = endpoint.params.copy()
        if params:
            request_params.update(params)

        # Prepare headers (merge default headers and endpoint-specific headers)
        headers = {**(self.default_headers or {}), **endpoint.headers}

        # Add auth headers if needed
        if self.auth_config:
            if (
                self.auth_config.type == "api_key"
                and hasattr(self.auth_config, "in_header")
                and getattr(self.auth_config, "in_header", False)
            ):
                header_name = getattr(self.auth_config, "header_name", "X-API-Key")
                key = getattr(self.auth_config, "key", "")
                headers[header_name] = key
            elif self.auth_config.type == "bearer" and hasattr(
                self.auth_config, "token"
            ):
                headers["Authorization"] = (
                    f"Bearer {getattr(self.auth_config, 'token', '')}"
                )

        # Prepare request object
        request = {
            "url": url,
            "method": endpoint.method,
            "headers": headers,
            "params": request_params,
        }

        # Add body if endpoint has a body template
        if endpoint.body_template:
            request["json"] = endpoint.body_template

        return request

    def _process_response(
        self, response: httpx.Response, endpoint_name: str
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Process the API response.

        Args:
            response: The HTTP response
            endpoint_name: Name of the endpoint

        Returns:
            Parsed response data
        """
        # Raise for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        data: Any = response.json()

        # Extract data from response path if configured
        endpoint = self.endpoints[endpoint_name]
        if endpoint.response_path and isinstance(data, dict):
            path_parts = endpoint.response_path.split(".")
            current_data: Any = data
            for part in path_parts:
                if isinstance(current_data, dict) and part in current_data:
                    current_data = current_data[part]
                else:
                    logger.warning(
                        f"Response path '{endpoint.response_path}' not found in response"
                    )
                    break
            # Only update data if we successfully navigated through the path
            if current_data is not data:
                data = current_data

        # Validate against response schema if provided
        endpoint = self.endpoints[endpoint_name]
        if endpoint.response_schema and is_validator_available():
            valid, diffs = validate_payload_against_schema(
                data, endpoint.response_schema
            )
            if not valid:
                logger.warning(
                    "Response schema validation failed for %s\n%s",
                    endpoint_name,
                    pretty_print_diffs(diffs),
                )
                # Record as a rate-limit or validation event via logger context (provenance layer may hook logs)

        # Ensure we return a valid type
        if isinstance(data, (dict, list)):
            return data
        else:
            # If response isn't a dict or list, wrap it in a dict
            return {"value": data}

    def _handle_pagination(
        self,
        initial_data: Union[Dict[str, Any], List[Dict[str, Any]]],
        endpoint_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Handle paginated responses if pagination is configured.

        Args:
            initial_data: Data from the first request
            endpoint_name: Name of the endpoint
            params: Request parameters

        Returns:
            Combined data from all pages
        """
        endpoint = self.endpoints[endpoint_name]

        # If no pagination config or initial data is not a dict, return as is
        if not endpoint.pagination or not isinstance(initial_data, dict):
            if isinstance(initial_data, list):
                return initial_data
            # Convert non-list data to a single-item list
            return (
                [initial_data]
                if isinstance(initial_data, dict)
                else [{"value": initial_data}]
            )

        # Extract the pagination configuration
        pagination = endpoint.pagination
        data_path = pagination.get("data_path", "")
        next_page_path = pagination.get("next_page_path", "")
        page_param = pagination.get("page_param", "page")

        # Extract the items from the first response
        if data_path:
            path_parts = data_path.split(".")
            items: Any = initial_data
            for part in path_parts:
                if isinstance(items, dict) and part in items:
                    items = items[part]
                else:
                    logger.warning(f"Data path '{data_path}' not found in response")
                    return [initial_data]
        else:
            # If no data path is specified, the entire response is the data
            items = initial_data

        # Normalize items to a list of dicts
        if not isinstance(items, list):
            items_list: List[Dict[str, Any]] = (
                [items] if isinstance(items, dict) else [{"value": items}]
            )
        else:
            items_list = []
            for elem in items:
                if isinstance(elem, dict):
                    items_list.append(elem)
                else:
                    items_list.append({"value": elem})

        # Extract next page token/URL if available
        next_page: Optional[Union[str, int]] = None
        if next_page_path:
            path_parts = next_page_path.split(".")
            temp_next_page: Any = initial_data
            for part in path_parts:
                if isinstance(temp_next_page, dict) and part in temp_next_page:
                    temp_next_page = temp_next_page[part]
                else:
                    temp_next_page = None
                    break
            # Only assign if it's a valid type for pagination
            if isinstance(temp_next_page, (str, int)):
                next_page = temp_next_page

        # Return the items if there's no next page
        if not next_page:
            return items_list

        # Fetch all pages
        all_items: List[Dict[str, Any]] = list(items_list)
        page = 2

        while next_page:
            # Update params for next page
            next_params: Dict[str, Any] = params.copy() if params else {}

            # Use either page number or next page token (refined to str|int in this loop)
            next_params[page_param] = next_page

            # Make the next request
            try:
                request = self._prepare_request(endpoint_name, next_params)
                response = self.client.request(
                    request["method"],
                    request["url"],
                    headers=request["headers"],
                    params=request["params"],
                    json=request.get("json"),
                )
                response.raise_for_status()
                page_data = response.json()

                # Extract items from this page
                page_items: Any
                if data_path:
                    path_parts = data_path.split(".")
                    page_items = page_data
                    for part in path_parts:
                        if isinstance(page_items, dict) and part in page_items:
                            page_items = page_items[part]
                        else:
                            page_items = []
                            break
                else:
                    page_items = page_data

                # Add items to the result, normalizing to list[dict]
                if isinstance(page_items, list):
                    for elem in page_items:
                        if isinstance(elem, dict):
                            all_items.append(elem)
                        else:
                            all_items.append({"value": elem})
                else:
                    all_items.append(
                        page_items
                        if isinstance(page_items, dict)
                        else {"value": page_items}
                    )

                # Extract next page token
                if next_page_path:
                    path_parts = next_page_path.split(".")
                    temp_next_page = page_data
                    for part in path_parts:
                        if isinstance(temp_next_page, dict) and part in temp_next_page:
                            temp_next_page = temp_next_page[part]
                        else:
                            temp_next_page = None
                            break
                    # Only assign if it's a valid type for pagination
                    if isinstance(temp_next_page, (str, int)):
                        next_page = temp_next_page
                    else:
                        next_page = None
                else:
                    # If no next page path, just increment the page number
                    page += 1
                    next_page = (
                        page if page <= pagination.get("max_pages", 10) else None
                    )

            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break

        return all_items

    def _categorize_error(self, exc: Exception) -> Tuple[ErrorCategory, int]:
        """
        Categorize an exception to determine its error category and status code.

        Args:
            exc: The exception to categorize

        Returns:
            Tuple of (ErrorCategory, status_code)
        """
        # Default values
        category = ErrorCategory.UNKNOWN
        status_code = None

        # Check for HTTP-specific errors
        if isinstance(exc, httpx.TimeoutException):
            category = ErrorCategory.TIMEOUT
            status_code = 0  # Custom code for timeout
        elif isinstance(exc, httpx.TransportError) or isinstance(
            exc, httpx.RequestError
        ):
            category = ErrorCategory.NETWORK
            status_code = 0  # Custom code for network/transport errors
        elif isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code

            # Categorize based on HTTP status code
            if status_code == 401 or status_code == 403:
                category = ErrorCategory.AUTHENTICATION
            elif status_code == 422 or status_code == 400:
                category = ErrorCategory.VALIDATION
            elif status_code == 429:
                category = ErrorCategory.RATE_LIMIT
            elif status_code >= 500:
                category = ErrorCategory.SERVER
            elif status_code >= 400:
                category = ErrorCategory.CLIENT

        return category, status_code

    def fetch_data(
        self, endpoint_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch data from the specified endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            params: Additional parameters for the request

        Returns:
            The parsed response data

        Raises:
            ApiLinkerError: On API request failure with enhanced error context
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        logger.info(
            f"Fetching data from endpoint: {endpoint_name} ({endpoint.method} {endpoint.path})"
        )

        # Prepare the request
        request = self._prepare_request(endpoint_name, params)

        # Make the request with retries (note: main retries are now handled by the error recovery manager)
        last_exception = None
        for attempt in range(1, self.retry_count + 1):
            try:
                response = self.client.request(
                    request["method"],
                    request["url"],
                    headers=request["headers"],
                    params=request["params"],
                    json=request.get("json"),
                )
                response.raise_for_status()

                # Process the response
                result = self._process_response(response, endpoint_name)

                # Handle pagination if configured
                if endpoint.pagination:
                    result = self._handle_pagination(result, endpoint_name, params)

                logger.info(f"Data fetched successfully from {endpoint_name}")
                return result

            except Exception as e:
                last_exception = e
                error_category, status_code = self._categorize_error(e)

                # Log the error at an appropriate level
                if attempt < self.retry_count:
                    wait_time = self.retry_delay * attempt
                    logger.warning(
                        f"Error fetching data (attempt {attempt}/{self.retry_count}): {str(e)}"
                    )
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed: {str(e)}")

        # If we get here, all retry attempts failed
        if last_exception:
            error_category, status_code = self._categorize_error(last_exception)

            # Extract response data if available
            response_body = None
            if hasattr(last_exception, "response"):
                try:
                    response_body = last_exception.response.text[:1000]  # Limit size
                except:
                    response_body = "<Unable to read response body>"

            # Create an ApiLinkerError with enhanced context
            raise ApiLinkerError(
                message=f"Failed to fetch data from {endpoint_name}: {str(last_exception)}",
                error_category=error_category,
                status_code=status_code,
                response_body=response_body,
                request_url=str(request["url"]),
                request_method=request["method"],
                additional_context={"endpoint": endpoint_name, "params": params},
            )

        # Should not reach here
        raise ApiLinkerError(
            message=f"Unexpected state fetching data from {endpoint_name}",
            error_category=ErrorCategory.UNKNOWN,
            status_code=0,
        )

    def send_data(
        self, endpoint_name: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Send data to the specified endpoint.

        Args:
            endpoint_name: Name of the endpoint to use
            data: Data to send

        Returns:
            The parsed response

        Raises:
            ApiLinkerError: On API request failure with enhanced error context
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found in configuration")

        endpoint = self.endpoints[endpoint_name]
        logger.info(
            f"Sending data to endpoint: {endpoint_name} ({endpoint.method} {endpoint.path})"
        )

        # Prepare the request
        request = self._prepare_request(endpoint_name)

        # Validate single item(s) against request schema if provided
        endpoint = self.endpoints[endpoint_name]
        if endpoint.request_schema and is_validator_available():

            def _validate_item(item: Any) -> None:
                valid, diffs = validate_payload_against_schema(
                    item, endpoint.request_schema
                )
                if not valid:
                    logger.error(
                        "Request schema validation failed for %s\n%s",
                        endpoint_name,
                        pretty_print_diffs(diffs),
                    )
                    raise ApiLinkerError(
                        message="Request failed schema validation",
                        error_category=ErrorCategory.VALIDATION,
                        status_code=0,
                        additional_context={"endpoint": endpoint_name, "diffs": diffs},
                    )

            if isinstance(data, list):
                for item in data:
                    _validate_item(item)
            else:
                _validate_item(data)

        # If data is a list, send each item individually
        if isinstance(data, list):
            results = []
            successful = 0
            failed = 0
            failures = []

            for item_index, item in enumerate(data):
                try:
                    response = self.client.request(
                        request["method"],
                        request["url"],
                        headers=request["headers"],
                        params=request["params"],
                        json=item,
                    )
                    response.raise_for_status()
                    result = response.json() if response.content else {}
                    results.append(result)
                    successful += 1

                except Exception as e:
                    error_category, status_code = self._categorize_error(e)

                    # Extract response data if available
                    response_body = None
                    if hasattr(e, "response"):
                        try:
                            response_body = e.response.text[:1000]  # Limit size
                        except:
                            response_body = "<Unable to read response body>"

                    error = ApiLinkerError(
                        message=f"Failed to send data item {item_index} to {endpoint_name}: {str(e)}",
                        error_category=error_category,
                        status_code=status_code,
                        response_body=response_body,
                        request_url=str(request["url"]),
                        request_method=request["method"],
                        additional_context={
                            "endpoint": endpoint_name,
                            "item_index": item_index,
                        },
                    )
                    failures.append(error.to_dict())
                    logger.error(f"Error sending data item {item_index}: {error}")
                    failed += 1

            logger.info(f"Sent {successful} items successfully, {failed} failed")
            return {
                "success": successful > 0 and failed == 0,
                "sent_count": successful,
                "failed_count": failed,
                "results": results,
                "failures": failures,
            }

        # If data is a single item, send it
        else:
            # Make the request with retries (note: main retries now handled by error recovery manager)
            last_exception = None

            for attempt in range(1, self.retry_count + 1):
                try:
                    response = self.client.request(
                        request["method"],
                        request["url"],
                        headers=request["headers"],
                        params=request["params"],
                        json=data,
                    )
                    response.raise_for_status()
                    result = response.json() if response.content else {}

                    logger.info(f"Data sent successfully to {endpoint_name}")
                    return {
                        "success": True,
                        "result": result,
                    }

                except Exception as e:
                    last_exception = e

                    # Log the error at an appropriate level
                    if attempt < self.retry_count:
                        wait_time = self.retry_delay * attempt
                        logger.warning(
                            f"Error sending data (attempt {attempt}/{self.retry_count}): {str(e)}"
                        )
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All retry attempts failed: {str(e)}")

            # If we get here, all retry attempts failed
            if last_exception:
                error_category, status_code = self._categorize_error(last_exception)

                # Extract response data if available
                response_body = None
                if hasattr(last_exception, "response"):
                    try:
                        response_body = last_exception.response.text[
                            :1000
                        ]  # Limit size
                    except:
                        response_body = "<Unable to read response body>"

                # Create an ApiLinkerError with enhanced context
                raise ApiLinkerError(
                    message=f"Failed to send data to {endpoint_name}: {str(last_exception)}",
                    error_category=error_category,
                    status_code=status_code,
                    response_body=response_body,
                    request_url=str(request["url"]),
                    request_method=request["method"],
                    additional_context={"endpoint": endpoint_name},
                )

            # This should not be reached
            return {"success": False, "error": "Unknown error"}
