"""
Tests for the enhanced authentication module with security features.
"""

import time
from unittest.mock import MagicMock, patch

import pytest
import httpx
import base64
import hashlib
import secrets

from apilinker.core.auth import (
    AuthManager,
    OAuth2ClientCredentials,
    OAuth2PKCE,
    OAuth2DeviceFlow
)
from apilinker.core.security import SecureCredentialStorage


class TestAuthManager:
    """Test suite for enhanced AuthManager with security features."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.auth_manager = AuthManager()
    
    def test_init_with_secure_storage(self):
        """Test initializing AuthManager with secure storage."""
        # Create mock secure storage
        mock_storage = MagicMock(spec=SecureCredentialStorage)
        auth_manager = AuthManager(secure_storage=mock_storage)
        
        assert auth_manager.secure_storage == mock_storage
    
    def test_generate_random_string(self):
        """Test generating random strings for PKCE."""
        random_string = self.auth_manager._generate_random_string(32)
        
        assert len(random_string) == 32
        assert isinstance(random_string, str)
        assert all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~" for c in random_string)
    
    def test_create_code_challenge(self):
        """Test creating code challenge from verifier."""
        verifier = "test_verifier_string"
        challenge = self.auth_manager._create_code_challenge(verifier)
        
        # Manual calculation for comparison
        digest = hashlib.sha256(verifier.encode()).digest()
        expected = base64.urlsafe_b64encode(digest).decode().rstrip("=")
        
        assert challenge == expected


class TestOAuth2PKCE:
    """Test suite for OAuth2 PKCE flow."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.auth_manager = AuthManager()
        self.mock_secure_storage = MagicMock(spec=SecureCredentialStorage)
        self.auth_manager.secure_storage = self.mock_secure_storage
        
        # Basic PKCE config
        self.pkce_config = {
            "type": "oauth2_pkce",
            "client_id": "test-client-id",
            "redirect_uri": "http://localhost:8080/callback",
            "authorization_url": "https://auth.example.com/oauth/authorize",
            "token_url": "https://auth.example.com/oauth/token",
            "scope": "read write",
            "storage_key": "test_pkce_storage"
        }
    
    def test_configure_pkce(self):
        """Test configuring PKCE authentication."""
        # Configure PKCE
        pkce_auth = self.auth_manager.configure_auth(self.pkce_config)
        
        # Check basic properties
        assert pkce_auth.type == "oauth2_pkce"
        assert pkce_auth.client_id == "test-client-id"
        assert pkce_auth.redirect_uri == "http://localhost:8080/callback"
        
        # Check auto-generated values
        assert pkce_auth.code_verifier is not None
        assert pkce_auth.code_challenge is not None
        assert pkce_auth.state is not None
    
    def test_get_authorization_url(self):
        """Test getting authorization URL for PKCE flow."""
        # Configure PKCE
        pkce_auth = self.auth_manager.configure_auth(self.pkce_config)
        
        # Get authorization URL
        auth_url = self.auth_manager.get_pkce_authorization_url(pkce_auth)
        
        # URL should contain all necessary parameters
        assert "https://auth.example.com/oauth/authorize?" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8080%2Fcallback" in auth_url
        assert "response_type=code" in auth_url
        assert "state=" in auth_url
        assert "code_challenge=" in auth_url
        assert "code_challenge_method=S256" in auth_url
        assert "scope=read+write" in auth_url
    
    @patch("httpx.post")
    def test_complete_pkce_flow(self, mock_post):
        """Test completing PKCE flow with authorization code."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Configure PKCE
        pkce_auth = self.auth_manager.configure_auth(self.pkce_config)
        
        # Complete PKCE flow
        updated_auth = self.auth_manager.complete_pkce_flow(pkce_auth, "test-authorization-code")
        
        # Check tokens were received
        assert updated_auth.token == "test-access-token"
        assert updated_auth.refresh_token == "test-refresh-token"
        assert updated_auth.expires_at is not None
        
        # Check secure storage was updated
        self.mock_secure_storage.store_credential.assert_called_once()
        args, kwargs = self.mock_secure_storage.store_credential.call_args
        assert args[0] == "test_pkce_storage"
        assert args[1]["token"] == "test-access-token"
        assert args[1]["refresh_token"] == "test-refresh-token"
    
    @patch("httpx.post")
    def test_refresh_pkce_token(self, mock_post):
        """Test refreshing token obtained via PKCE flow."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create PKCE auth with existing tokens
        pkce_auth = OAuth2PKCE(
            client_id="test-client-id",
            redirect_uri="http://localhost:8080/callback",
            authorization_url="https://auth.example.com/oauth/authorize",
            token_url="https://auth.example.com/oauth/token",
            scope="read write",
            code_verifier="test-verifier",
            code_challenge="test-challenge",
            state="test-state",
            token="old-token",
            refresh_token="test-refresh-token",
            storage_key="test_pkce_storage"
        )
        
        # Refresh token
        updated_auth = self.auth_manager.refresh_pkce_token(pkce_auth)
        
        # Check tokens were updated
        assert updated_auth.token == "new-access-token"
        assert updated_auth.refresh_token == "new-refresh-token"
        
        # Check secure storage was updated
        self.mock_secure_storage.store_credential.assert_called_once()


class TestOAuth2DeviceFlow:
    """Test suite for OAuth2 Device Flow."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.auth_manager = AuthManager()
        self.mock_secure_storage = MagicMock(spec=SecureCredentialStorage)
        self.auth_manager.secure_storage = self.mock_secure_storage
        
        # Basic Device Flow config
        self.device_config = {
            "type": "oauth2_device_flow",
            "client_id": "test-client-id",
            "device_authorization_url": "https://auth.example.com/device/code",
            "token_url": "https://auth.example.com/oauth/token",
            "scope": "read write",
            "storage_key": "test_device_storage"
        }
    
    def test_configure_device_flow(self):
        """Test configuring Device Flow authentication."""
        # Configure Device Flow
        device_auth = self.auth_manager.configure_auth(self.device_config)
        
        # Check basic properties
        assert device_auth.type == "oauth2_device_flow"
        assert device_auth.client_id == "test-client-id"
        assert device_auth.device_authorization_url == "https://auth.example.com/device/code"
        assert device_auth.token_url == "https://auth.example.com/oauth/token"
    
    @patch("httpx.post")
    def test_start_device_flow(self, mock_post):
        """Test starting Device Flow."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "device_code": "test-device-code",
            "user_code": "ABCD-1234",
            "verification_uri": "https://auth.example.com/device",
            "verification_uri_complete": "https://auth.example.com/device?code=ABCD-1234",
            "expires_in": 1800,
            "interval": 5
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Configure Device Flow
        device_auth = self.auth_manager.configure_auth(self.device_config)
        
        # Start Device Flow
        updated_auth = self.auth_manager.start_device_flow(device_auth)
        
        # Check device codes were received
        assert updated_auth.device_code == "test-device-code"
        assert updated_auth.user_code == "ABCD-1234"
        assert updated_auth.verification_uri == "https://auth.example.com/device"
        assert updated_auth.verification_uri_complete == "https://auth.example.com/device?code=ABCD-1234"
        assert updated_auth.interval == 5
    
    @patch("httpx.post")
    def test_poll_device_flow_pending(self, mock_post):
        """Test polling Device Flow when authorization is pending."""
        # Configure mock response for pending state
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "authorization_pending"
        }
        mock_post.return_value = mock_response
        
        # Create Device Flow auth with device code
        device_auth = OAuth2DeviceFlow(
            client_id="test-client-id",
            device_authorization_url="https://auth.example.com/device/code",
            token_url="https://auth.example.com/oauth/token",
            device_code="test-device-code",
            user_code="ABCD-1234",
            verification_uri="https://auth.example.com/device",
            interval=5,
            storage_key="test_device_storage"
        )
        
        # Poll Device Flow
        completed, updated_auth = self.auth_manager.poll_device_flow(device_auth)
        
        # Should not be completed
        assert completed is False
        assert updated_auth is None
    
    @patch("httpx.post")
    def test_poll_device_flow_slow_down(self, mock_post):
        """Test polling Device Flow when getting slow_down error."""
        # Configure mock response for slow_down state
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "slow_down"
        }
        mock_post.return_value = mock_response
        
        # Create Device Flow auth with device code
        device_auth = OAuth2DeviceFlow(
            client_id="test-client-id",
            device_authorization_url="https://auth.example.com/device/code",
            token_url="https://auth.example.com/oauth/token",
            device_code="test-device-code",
            user_code="ABCD-1234",
            verification_uri="https://auth.example.com/device",
            interval=5,  # Start with 5 seconds
            storage_key="test_device_storage"
        )
        
        # Poll Device Flow
        completed, updated_auth = self.auth_manager.poll_device_flow(device_auth)
        
        # Should not be completed but interval should be increased
        assert completed is False
        assert updated_auth is not None
        assert updated_auth.interval > 5  # Should be increased from the initial 5 seconds
    
    @patch("httpx.post")
    def test_poll_device_flow_complete(self, mock_post):
        """Test polling Device Flow when authorization is complete."""
        # Configure mock response for completion
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-access-token",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Create Device Flow auth with device code
        device_auth = OAuth2DeviceFlow(
            client_id="test-client-id",
            device_authorization_url="https://auth.example.com/device/code",
            token_url="https://auth.example.com/oauth/token",
            device_code="test-device-code",
            user_code="ABCD-1234",
            verification_uri="https://auth.example.com/device",
            interval=5,
            storage_key="test_device_storage"
        )
        
        # Poll Device Flow
        completed, updated_auth = self.auth_manager.poll_device_flow(device_auth)
        
        # Should be completed
        assert completed is True
        assert updated_auth is not None
        assert updated_auth.token == "test-access-token"
        assert updated_auth.refresh_token == "test-refresh-token"
        
        # Check secure storage was updated
        self.mock_secure_storage.store_credential.assert_called_once()
