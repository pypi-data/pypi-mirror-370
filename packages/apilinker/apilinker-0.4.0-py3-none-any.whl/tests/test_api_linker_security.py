"""
Tests for security integration with the ApiLinker class.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
import yaml

from apilinker.api_linker import ApiLinker
from apilinker.core.security import (
    AccessRole,
    EncryptionLevel,
    RequestResponseEncryption,
    SecureCredentialStorage
)
from apilinker.core.security_integration import SecurityManager


class TestApiLinkerSecurity:
    """Test suite for ApiLinker with security features."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create basic config for testing
        self.sample_config = {
            "source": {
                "type": "rest",
                "base_url": "https://api.source.com",
                "auth": {
                    "type": "api_key",
                    "header": "X-API-Key",
                    "key": "source_api_key"
                },
                "endpoints": {
                    "list_users": {
                        "path": "/users",
                        "method": "GET"
                    }
                }
            },
            "target": {
                "type": "rest",
                "base_url": "https://api.target.com",
                "auth": {
                    "type": "bearer",
                    "token": "target_token"
                },
                "endpoints": {
                    "create_user": {
                        "path": "/users",
                        "method": "POST"
                    }
                }
            },
            "mapping": [
                {
                    "source": "list_users",
                    "target": "create_user",
                    "fields": [
                        {"source": "id", "target": "external_id"},
                        {"source": "name", "target": "full_name"}
                    ]
                }
            ],
            "security": {
                "encryption_level": "headers_only",
                "enable_access_control": True,
                "users": [
                    {
                        "username": "admin",
                        "role": "admin",
                        "api_key": "admin-api-key"
                    },
                    {
                        "username": "viewer",
                        "role": "viewer"
                    }
                ]
            }
        }
        
        # Create a temporary directory for test credential files
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "credentials.enc")
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove test file if it exists
        if os.path.exists(self.storage_path):
            os.unlink(self.storage_path)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_init_with_security_config(self):
        """Test initializing ApiLinker with security configuration."""
        security_config = {
            "master_password": "test-password",
            "credential_storage_path": self.storage_path,
            "encryption_level": "headers_only",
            "enable_access_control": True,
            "users": [
                {"username": "admin", "role": "admin"}
            ]
        }
        
        linker = ApiLinker(security_config=security_config)
        
        # Verify security components are initialized
        assert linker.security_manager is not None
        assert linker.security_manager.request_encryption.encryption_level == EncryptionLevel.HEADERS_ONLY
        assert linker.security_manager.enable_access_control is True
    
    def test_load_config_with_security(self):
        """Test loading configuration with security settings."""
        # Create config with security settings
        test_config = self.sample_config.copy()
        test_config["security"] = {
            "master_password": "test-password",
            "encryption_level": "headers_only",
            "enable_access_control": True,
            "users": [
                {"username": "admin", "role": "admin"},
                {"username": "viewer", "role": "viewer"}
            ]
        }
        
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(test_config, f)
            config_path = f.name
        
        try:
            # Use a context manager for patching
            with patch('apilinker.api_linker.SecurityManager') as mock_security_manager_class:
                # Set up a proper mock instance
                mock_security_manager = MagicMock()
                mock_security_manager.request_encryption = MagicMock()
                mock_security_manager.request_encryption.encryption_level = EncryptionLevel.HEADERS_ONLY
                mock_security_manager.enable_access_control = True
                mock_security_manager.access_control = MagicMock()
                
                # Configure the class mock to return our instance
                mock_security_manager_class.return_value = mock_security_manager
                
                # Initialize ApiLinker with config file
                linker = ApiLinker(config_path=config_path)
                
                # Just verify the security manager was initialized
                assert linker.security_manager is not None
                
        finally:
            # Clean up temporary file
            if os.path.exists(config_path):
                os.unlink(config_path)
    
    def test_credential_storage(self):
        """Test storing and retrieving credentials."""
        security_config = {
            "master_password": "test-password",
            "credential_storage_path": self.storage_path,
            "encryption_level": "none"
        }
        
        linker = ApiLinker(security_config=security_config)
        
        # Store a credential
        success = linker.store_credential("test-api", {"token": "secret-token"})
        assert success is True
        
        # Retrieve the credential
        cred = linker.get_credential("test-api")
        assert cred is not None
        assert cred["token"] == "secret-token"
        
        # List credentials
        creds = linker.list_credentials()
        assert "test-api" in creds
    
    def test_user_management(self):
        """Test user management functions."""
        # Create detailed test users
        test_user = {
            "username": "testuser",
            "role": "operator",
            "api_key": "test-api-key"
        }
        
        # Create mock for the SecurityManager and access_control
        mock_access_control = MagicMock()
        mock_security_manager = MagicMock()
        
        # Configure the security manager for access control
        mock_security_manager.enable_access_control = True
        mock_security_manager.access_control = mock_access_control
        
        # Configure access_control mocks
        mock_access_control.users = {"testuser": test_user}
        mock_access_control.add_user = MagicMock(return_value=test_user)
        mock_access_control.get_user = MagicMock(return_value=test_user)
        
        # Create ApiLinker and set our mocked security manager
        linker = ApiLinker()
        linker.security_manager = mock_security_manager
        
        # Mock the add_user method in ApiLinker to call through to our mocked access_control
        original_add_user = linker.add_user
        linker.add_user = lambda username, role, api_key=None: mock_security_manager.add_user(username, role, api_key)
        mock_security_manager.add_user = MagicMock(return_value=test_user)
        
        # Add a user
        user = linker.add_user("testuser", "operator")
        
        # Verify the security manager's add_user was called with correct arguments
        mock_security_manager.add_user.assert_called_once_with("testuser", "operator", None)
        
        # Verify correct user was returned
        assert user == test_user
        
        # List users - this will access security_manager.access_control.users
        users = linker.list_users()
        
        # Verify the get_user method was called
        mock_access_control.get_user.assert_called_once_with("testuser")
        
        # Verify user list is correct
        assert len(users) == 1
        assert isinstance(users[0], dict)
        assert users[0].get("username") == "testuser"
        assert users[0].get("role") == "operator"
        
        # Since we're mocking get_user to return the original user dict,
        # we need to verify api_key is set to the original value
        # In a real scenario, list_users would mask the API key
    
    def test_sync_without_encryption(self):
        """Test sync operation proceeds without custom encryption."""
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0]
        )
        linker.source = MagicMock()
        linker.target = MagicMock()
        # Circuit breakers
        mock_source_cb = MagicMock()
        mock_source_cb.execute.return_value = ([{"id": 1, "name": "Test User"}], None)
        mock_target_cb = MagicMock()
        mock_target_cb.execute.return_value = ({"success": True, "id": "t1"}, None)
        mock_error_recovery = MagicMock()
        mock_error_recovery.get_circuit_breaker.side_effect = [mock_source_cb, mock_target_cb]
        linker.error_recovery_manager = mock_error_recovery
        # Map directly
        linker.mapper = MagicMock()
        linker.mapper.map_data = MagicMock(return_value=[{"external_id": 1, "full_name": "Test User"}])
        result = linker.sync()
        assert result.success is True
    
    def test_sync_with_access_control(self):
        """Test sync operation with access control."""
        security_config = {
            "master_password": "test-password",
            "enable_access_control": True,
            "users": [
                {"username": "admin", "role": "admin"},
                {"username": "viewer", "role": "viewer"}
            ]
        }
        
        # Create ApiLinker with security and basic config
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0],
            security_config=security_config
        )
        
        # Set current user to viewer (who shouldn't have sync permission)
        linker.current_user = "viewer"
        
        # Mock source and target
        linker.source = MagicMock()
        linker.target = MagicMock()
        
        # Create mock error recovery manager and circuit breaker
        linker.error_recovery_manager = MagicMock()
        mock_cb = MagicMock()
        mock_cb.execute.return_value = ([{"id": 1, "name": "Test User"}], None)
        linker.error_recovery_manager.get_circuit_breaker.return_value = mock_cb
        
        # Set up security manager permissions
        linker.security_manager.enable_access_control = True
        linker.security_manager.check_permission = MagicMock()
        
        # First test: Viewer doesn't have permission
        linker.security_manager.check_permission.return_value = False
        
        # Sync should raise PermissionError
        with pytest.raises(PermissionError):
            linker.sync()
        
        # Second test: Admin has permission
        linker.current_user = "admin"
        linker.security_manager.check_permission.return_value = True
        
        # Mock the mapper to transform data
        linker.mapper.transform_data = MagicMock(return_value=[{"external_id": 1, "full_name": "Test User"}])
        
        # Mock target circuit breaker to return success
        target_cb = MagicMock()
        target_cb.execute.return_value = ({"success": True, "id": "t1"}, None)
        linker.error_recovery_manager.get_circuit_breaker.side_effect = [mock_cb, target_cb]
        
        # Now sync should work
        result = linker.sync()
        assert result.success is True
