"""
Tests for the ApiConnector class.
"""

import json
import os
import unittest
from unittest.mock import MagicMock, patch

import httpx
import pytest

from apilinker.core.auth import AuthConfig, ApiKeyAuth
from apilinker.core.connector import ApiConnector, EndpointConfig
from apilinker.core.error_handling import ApiLinkerError, ErrorCategory


class TestApiConnector:
    """Test suite for ApiConnector class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.base_url = "https://api.example.com/v1"
        self.auth_config = ApiKeyAuth(
            key="test_api_key",
            header_name="X-API-Key"
        )
        self.endpoints = {
            "list_users": {
                "path": "/users",
                "method": "GET",
                "params": {"limit": 100},
            },
            "create_user": {
                "path": "/users",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
            },
            "update_user": {
                "path": "/users/{id}",
                "method": "PUT",
            }
        }
        
        self.connector = ApiConnector(
            connector_type="rest",
            base_url=self.base_url,
            auth_config=self.auth_config,
            endpoints=self.endpoints
        )

    @patch("httpx.Client.request")
    def test_fetch_data_success(self, mock_request):
        """Test successful data fetching."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"id": 1, "name": "Test User"}]}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Call fetch_data
        result = self.connector.fetch_data("list_users")
        
        # Verify the request
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[0] == "GET"
        assert args[1] == "/users"
        assert kwargs["headers"] == {"X-API-Key": "test_api_key"}
        assert kwargs["params"] == {"limit": 100}
        
        # Verify the result
        assert result == {"data": [{"id": 1, "name": "Test User"}]}

    @patch("httpx.Client.request")
    def test_send_data_single_item(self, mock_request):
        """Test sending a single data item."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "name": "Test User"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        # Data to send
        data = {"name": "Test User", "email": "test@example.com"}
        
        # Call send_data
        result = self.connector.send_data("create_user", data)
        
        # Verify the request
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[0] == "POST"
        assert args[1] == "/users"
        assert kwargs["headers"] == {"X-API-Key": "test_api_key", "Content-Type": "application/json"}
        assert kwargs["json"] == data
        
        # Verify the result
        assert result["success"] is True
        assert result["result"] == {"id": 1, "name": "Test User"}

    @patch("httpx.Client.request")
    def test_send_data_multiple_items(self, mock_request):
        """Test sending multiple data items."""
        # Mock responses for multiple calls
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"id": 1, "name": "User 1"}
        mock_response1.raise_for_status.return_value = None
        
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {"id": 2, "name": "User 2"}
        mock_response2.raise_for_status.return_value = None
        
        mock_request.side_effect = [mock_response1, mock_response2]
        
        # Data to send
        data = [
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"}
        ]
        
        # Call send_data
        result = self.connector.send_data("create_user", data)
        
        # Verify the request
        assert mock_request.call_count == 2
        
        # Verify the result
        assert result["success"] is True
        assert result["sent_count"] == 2
        assert result["failed_count"] == 0
        assert len(result["results"]) == 2
        assert result["results"][0] == {"id": 1, "name": "User 1"}
        assert result["results"][1] == {"id": 2, "name": "User 2"}

    @patch("httpx.Client.request")
    def test_fetch_data_with_pagination(self, mock_request):
        """Test fetching paginated data."""
        # Create connector with pagination config
        endpoints_with_pagination = {
            "list_users": {
                "path": "/users",
                "method": "GET",
                "params": {"limit": 100},
                "pagination": {
                    "data_path": "data",
                    "next_page_path": "meta.next_page",
                    "page_param": "page"
                }
            }
        }
        
        connector = ApiConnector(
            connector_type="rest",
            base_url=self.base_url,
            auth_config=self.auth_config,
            endpoints=endpoints_with_pagination
        )
        
        # Mock responses for pagination
        # Page 1
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {
            "data": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}],
            "meta": {"next_page": 2}
        }
        mock_response1.raise_for_status.return_value = None
        
        # Page 2
        mock_response2 = MagicMock()
        mock_response2.json.return_value = {
            "data": [{"id": 3, "name": "User 3"}],
            "meta": {"next_page": None}
        }
        mock_response2.raise_for_status.return_value = None
        
        mock_request.side_effect = [mock_response1, mock_response2]
        
        # Call fetch_data
        result = connector.fetch_data("list_users")
        
        # Verify the request
        assert mock_request.call_count == 2
        
        # Verify calls
        first_call_args = mock_request.call_args_list[0][0]
        assert first_call_args[0] == "GET"
        assert first_call_args[1] == "/users"
        
        second_call_args = mock_request.call_args_list[1][0]
        assert second_call_args[0] == "GET"
        assert second_call_args[1] == "/users"
        
        second_call_kwargs = mock_request.call_args_list[1][1]
        assert "page" in second_call_kwargs["params"]
        assert second_call_kwargs["params"]["page"] == 2
        
        # Verify the result - should have all items from both pages
        assert len(result) == 3
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert result[2]["id"] == 3

    @patch("httpx.Client.request")
    def test_http_error_handling(self, mock_request):
        """Test handling of HTTP errors."""
        # Create a proper mock request and response
        mock_req = MagicMock()
        mock_req.url = "http://example.com/users"
        mock_req.method = "GET"
        
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = "Not Found"
        
        # Create HTTPStatusError with proper request and response
        http_error = httpx.HTTPStatusError(
            "404 Not Found", 
            request=mock_req,
            response=mock_resp
        )
        
        # Mock response object that will raise the HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = http_error
        mock_request.return_value = mock_response
        
        # Set up retry config for faster testing
        self.connector.retry_count = 2
        self.connector.retry_delay = 0
        
        # Call fetch_data and expect ApiLinkerError
        with pytest.raises(ApiLinkerError) as exc_info:
            self.connector.fetch_data("list_users")
            
        # Verify the error category and status code
        error = exc_info.value
        assert error.error_category == ErrorCategory.CLIENT
        assert error.status_code == 404
        
        # Verify the request was retried
        assert mock_request.call_count == 2
