"""
Tests for the authentication module.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from apilinker.core.auth import (ApiKeyAuth, AuthConfig, AuthManager, BasicAuth,
                                BearerAuth, OAuth2ClientCredentials)


class TestAuthManager:
    """Test suite for AuthManager class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.auth_manager = AuthManager()

    def test_resolve_env_vars(self):
        """Test resolving environment variables in strings."""
        # Set an environment variable for testing
        os.environ["TEST_API_KEY"] = "test_key_value"
        
        # Test resolving an environment variable
        value = "${TEST_API_KEY}"
        resolved = self.auth_manager._resolve_env_vars(value)
        assert resolved == "test_key_value"
        
        # Test with a non-environment variable string
        value = "plain_string"
        resolved = self.auth_manager._resolve_env_vars(value)
        assert resolved == "plain_string"
        
        # Test with a non-string value
        value = 123
        resolved = self.auth_manager._resolve_env_vars(value)
        assert resolved == 123
        
        # Test with missing environment variable
        value = "${NON_EXISTENT_VAR}"
        resolved = self.auth_manager._resolve_env_vars(value)
        assert resolved == "${NON_EXISTENT_VAR}"

    def test_resolve_env_vars_in_dict(self):
        """Test resolving environment variables in dictionaries."""
        # Set environment variables for testing
        os.environ["TEST_USERNAME"] = "user123"
        os.environ["TEST_PASSWORD"] = "pass456"
        
        # Test dictionary with environment variables
        config = {
            "username": "${TEST_USERNAME}",
            "password": "${TEST_PASSWORD}",
            "nested": {
                "api_key": "${TEST_API_KEY}"
            },
            "number": 42
        }
        
        resolved = self.auth_manager._resolve_env_vars_in_dict(config)
        
        assert resolved["username"] == "user123"
        assert resolved["password"] == "pass456"
        assert resolved["nested"]["api_key"] == "test_key_value"
        assert resolved["number"] == 42

    def test_configure_api_key_auth(self):
        """Test configuring API key authentication."""
        # API key in header
        config = {
            "type": "api_key",
            "key": "test_api_key",
            "header": "X-API-Key"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, ApiKeyAuth)
        assert auth_config.key == "test_api_key"
        assert auth_config.header_name == "X-API-Key"
        assert auth_config.in_header is True
        assert auth_config.in_query is False
        
        # API key in query parameter
        config = {
            "type": "api_key",
            "key": "test_api_key",
            "in": "query",
            "param_name": "api_key"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, ApiKeyAuth)
        assert auth_config.key == "test_api_key"
        assert auth_config.in_header is False
        assert auth_config.in_query is True
        assert auth_config.query_param == "api_key"
        
        # Invalid API key config (missing key)
        with pytest.raises(ValueError):
            self.auth_manager.configure_auth({"type": "api_key"})

    def test_configure_bearer_auth(self):
        """Test configuring bearer token authentication."""
        # Valid bearer token config
        config = {
            "type": "bearer",
            "token": "test_token"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, BearerAuth)
        assert auth_config.token == "test_token"
        
        # Invalid bearer token config (missing token)
        with pytest.raises(ValueError):
            self.auth_manager.configure_auth({"type": "bearer"})

    def test_configure_basic_auth(self):
        """Test configuring basic authentication."""
        # Valid basic auth config
        config = {
            "type": "basic",
            "username": "user123",
            "password": "pass456"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, BasicAuth)
        assert auth_config.username == "user123"
        assert auth_config.password == "pass456"
        
        # Invalid basic auth config (missing username)
        with pytest.raises(ValueError):
            self.auth_manager.configure_auth({
                "type": "basic", 
                "password": "pass456"
            })
        
        # Invalid basic auth config (missing password)
        with pytest.raises(ValueError):
            self.auth_manager.configure_auth({
                "type": "basic", 
                "username": "user123"
            })

    def test_configure_oauth2_auth(self):
        """Test configuring OAuth2 client credentials authentication."""
        # Valid OAuth2 config
        config = {
            "type": "oauth2_client_credentials",
            "client_id": "client123",
            "client_secret": "secret456",
            "token_url": "https://oauth.example.com/token",
            "scope": "read write"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, OAuth2ClientCredentials)
        assert auth_config.client_id == "client123"
        assert auth_config.client_secret == "secret456"
        assert auth_config.token_url == "https://oauth.example.com/token"
        assert auth_config.scope == "read write"
        
        # Invalid OAuth2 config (missing client_id)
        with pytest.raises(ValueError):
            self.auth_manager.configure_auth({
                "type": "oauth2_client_credentials",
                "client_secret": "secret456",
                "token_url": "https://oauth.example.com/token"
            })

    def test_configure_unknown_auth(self):
        """Test configuring an unknown authentication type."""
        # Unknown auth type
        config = {
            "type": "custom",
            "param1": "value1",
            "param2": "value2"
        }
        
        auth_config = self.auth_manager.configure_auth(config)
        
        assert isinstance(auth_config, AuthConfig)
        assert auth_config.type == "custom"
        assert auth_config.param1 == "value1"
        assert auth_config.param2 == "value2"

    @patch("httpx.post")
    def test_refresh_oauth2_token(self, mock_post):
        """Test refreshing OAuth2 token."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new_token_123",
            "expires_in": 3600,
            "token_type": "bearer"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create OAuth2 config
        auth_config = OAuth2ClientCredentials(
            type="oauth2_client_credentials",
            client_id="client123",
            client_secret="secret456",
            token_url="https://oauth.example.com/token",
            scope="read write"
        )
        
        # Refresh token
        new_config = self.auth_manager.refresh_oauth2_token(auth_config)
        
        # Verify the request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        
        assert args[0] == "https://oauth.example.com/token"
        assert kwargs["data"]["grant_type"] == "client_credentials"
        assert kwargs["data"]["client_id"] == "client123"
        assert kwargs["data"]["client_secret"] == "secret456"
        assert kwargs["data"]["scope"] == "read write"
        
        # Verify the new config
        assert new_config.token == "new_token_123"
        assert new_config.expires_at is not None

    @patch("httpx.post")
    def test_refresh_oauth2_token_error(self, mock_post):
        """Test error handling when refreshing OAuth2 token."""
        # Mock error response
        mock_post.side_effect = Exception("Connection error")
        
        # Create OAuth2 config
        auth_config = OAuth2ClientCredentials(
            type="oauth2_client_credentials",
            client_id="client123",
            client_secret="secret456",
            token_url="https://oauth.example.com/token"
        )
        
        # Refresh token should raise exception
        with pytest.raises(Exception):
            self.auth_manager.refresh_oauth2_token(auth_config)
