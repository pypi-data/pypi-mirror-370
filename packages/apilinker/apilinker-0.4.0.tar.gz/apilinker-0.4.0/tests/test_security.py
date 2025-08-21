"""
Tests for the security module of APILinker.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apilinker.core.security import (
    AccessControl,
    AccessRole,
    EncryptionLevel,
    RequestResponseEncryption,
    SecureCredentialStorage
)
from apilinker.core.security_integration import SecurityManager


class TestSecureCredentialStorage:
    """Test suite for the SecureCredentialStorage class."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test credential files
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "credentials.enc")
        self.test_password = "test-master-password"
        
        # Create storage instance
        self.storage = SecureCredentialStorage(
            storage_path=self.storage_path,
            master_password=self.test_password,
            auto_load=False
        )
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove test file if it exists
        if os.path.exists(self.storage_path):
            os.unlink(self.storage_path)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_init_with_password(self):
        """Test initialization with a master password."""
        storage = SecureCredentialStorage(
            storage_path=self.storage_path,
            master_password=self.test_password,
            auto_load=False
        )
        
        assert storage.master_password == self.test_password
        assert storage.storage_path == self.storage_path
        assert storage.cipher is not None
    
    @patch.dict(os.environ, {"APILINKER_MASTER_PASSWORD": "env-password"})
    def test_init_with_env_password(self):
        """Test initialization with password from environment variable."""
        storage = SecureCredentialStorage(
            storage_path=self.storage_path,
            auto_load=False
        )
        
        assert storage.master_password == "env-password"
        assert storage.cipher is not None
    
    def test_store_and_retrieve_credential(self):
        """Test storing and retrieving credentials."""
        # Store a credential
        credential_data = {
            "token": "secret-api-token",
            "expires_at": 1735689600
        }
        
        success = self.storage.store_credential("test-api", credential_data)
        assert success is True
        assert os.path.exists(self.storage_path)
        
        # Retrieve the credential
        retrieved = self.storage.get_credential("test-api")
        assert retrieved is not None
        assert retrieved["token"] == "secret-api-token"
        assert retrieved["expires_at"] == 1735689600
    
    def test_list_credentials(self):
        """Test listing available credentials."""
        # Store multiple credentials
        self.storage.store_credential("api1", {"token": "token1"})
        self.storage.store_credential("api2", {"token": "token2"})
        
        # List credentials
        credentials = self.storage.list_credentials()
        assert len(credentials) == 2
        assert "api1" in credentials
        assert "api2" in credentials
    
    def test_delete_credential(self):
        """Test deleting a credential."""
        # Store a credential
        self.storage.store_credential("test-api", {"token": "token"})
        
        # Delete it
        success = self.storage.delete_credential("test-api")
        assert success is True
        
        # Verify it's gone
        assert self.storage.get_credential("test-api") is None
    
    def test_load_saved_credentials(self):
        """Test loading credentials from a file."""
        # Store credentials
        self.storage.store_credential("test-api", {"token": "token"})
        
        # Create a new storage instance that loads from the same file
        new_storage = SecureCredentialStorage(
            storage_path=self.storage_path,
            master_password=self.test_password,
            auto_load=True
        )
        
        # Verify credentials are loaded
        assert new_storage.get_credential("test-api") is not None
        assert new_storage.get_credential("test-api")["token"] == "token"


class TestRequestResponseEncryption:
    """Test suite for the RequestResponseEncryption class."""
    
    def test_init_default(self):
        """Test default initialization."""
        encryption = RequestResponseEncryption()
        
        assert encryption.encryption_level == EncryptionLevel.NONE
        assert encryption.encryption_key is not None
        assert encryption.cipher is not None
    
    def test_init_with_level(self):
        """Test initialization with specific encryption level."""
        encryption = RequestResponseEncryption(encryption_level=EncryptionLevel.FULL)
        
        assert encryption.encryption_level == EncryptionLevel.FULL
    
    def test_init_with_key(self):
        """Test initialization with an encryption key."""
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        
        encryption = RequestResponseEncryption(encryption_key=key)
        
        assert encryption.encryption_key is not None
        
    def test_encrypt_decrypt_headers(self):
        """Test encrypting and decrypting headers."""
        encryption = RequestResponseEncryption(encryption_level=EncryptionLevel.HEADERS_ONLY)
        
        # Original headers
        headers = {
            "Authorization": "Bearer token123",
            "Content-Type": "application/json",
            "Custom-Header": "custom-value"
        }
        
        # Encrypt headers
        encrypted_headers = encryption.encrypt_headers(headers)
        
        # Content-Type should not be encrypted
        assert encrypted_headers["Content-Type"] == "application/json"
        
        # Authorization should be encrypted
        assert "Authorization" not in encrypted_headers
        assert any(k.startswith("X-Encrypted-") for k in encrypted_headers.keys())
        
        # Decrypt headers
        decrypted_headers = encryption.decrypt_headers(encrypted_headers)
        
        assert decrypted_headers["Authorization"] == "Bearer token123"
        assert decrypted_headers["Content-Type"] == "application/json"
        assert decrypted_headers["Custom-Header"] == "custom-value"
    
    def test_encrypt_decrypt_body_dict(self):
        """Test encrypting and decrypting body (dict)."""
        encryption = RequestResponseEncryption(encryption_level=EncryptionLevel.FULL)
        
        # Original body
        body = {"key": "value", "nested": {"inner": "data"}}
        
        # Encrypt body
        encrypted_body = encryption.encrypt_body(body)
        
        # Should be bytes
        assert isinstance(encrypted_body, bytes)
        # Should not be the same as JSON of original
        assert encrypted_body != bytes(str(body), "utf-8")
        
        # Decrypt body
        decrypted_body = encryption.decrypt_body(encrypted_body)
        
        assert isinstance(decrypted_body, dict)
        assert decrypted_body["key"] == "value"
        assert decrypted_body["nested"]["inner"] == "data"
    
    def test_encrypt_decrypt_body_string(self):
        """Test encrypting and decrypting body (string)."""
        encryption = RequestResponseEncryption(encryption_level=EncryptionLevel.BODY_ONLY)
        
        # Original body
        body = "plain text data"
        
        # Encrypt body
        encrypted_body = encryption.encrypt_body(body)
        
        # Decrypt body
        decrypted_body = encryption.decrypt_body(encrypted_body)
        
        assert decrypted_body == body


class TestAccessControl:
    """Test suite for the AccessControl class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.access_control = AccessControl()
    
    def test_add_user(self):
        """Test adding a user."""
        user_data = self.access_control.add_user("testuser", AccessRole.ADMIN)
        
        assert user_data["username"] == "testuser"
        assert user_data["role"] == "admin"
        assert "api_key" in user_data
        assert user_data["api_key"] is not None
    
    def test_add_user_with_api_key(self):
        """Test adding a user with a predefined API key."""
        api_key = "test-api-key-123"
        user_data = self.access_control.add_user("testuser", AccessRole.VIEWER, api_key)
        
        assert user_data["username"] == "testuser"
        assert user_data["role"] == "viewer"
        assert user_data["api_key"] == api_key
    
    def test_get_user(self):
        """Test getting a user by username."""
        self.access_control.add_user("testuser", AccessRole.OPERATOR)
        
        user = self.access_control.get_user("testuser")
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == "operator"
    
    def test_get_user_by_api_key(self):
        """Test getting a user by API key."""
        api_key = "test-api-key-456"
        self.access_control.add_user("testuser", AccessRole.DEVELOPER, api_key)
        
        user = self.access_control.get_user_by_api_key(api_key)
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == "developer"
    
    def test_has_permission(self):
        """Test checking user permissions."""
        self.access_control.add_user("admin", AccessRole.ADMIN)
        self.access_control.add_user("viewer", AccessRole.VIEWER)
        self.access_control.add_user("operator", AccessRole.OPERATOR)
        
        # Admin should have all permissions
        assert self.access_control.has_permission("admin", "view_config") is True
        assert self.access_control.has_permission("admin", "edit_config") is True
        assert self.access_control.has_permission("admin", "run_sync") is True
        
        # Viewer should have limited permissions
        assert self.access_control.has_permission("viewer", "view_config") is True
        assert self.access_control.has_permission("viewer", "edit_config") is False
        assert self.access_control.has_permission("viewer", "run_sync") is False
        
        # Operator should have operational permissions
        assert self.access_control.has_permission("operator", "view_config") is True
        assert self.access_control.has_permission("operator", "run_sync") is True
        assert self.access_control.has_permission("operator", "edit_config") is False
    
    def test_remove_user(self):
        """Test removing a user."""
        self.access_control.add_user("testuser", AccessRole.ADMIN)
        
        success = self.access_control.remove_user("testuser")
        
        assert success is True
        assert self.access_control.get_user("testuser") is None
    
    def test_update_user_role(self):
        """Test updating a user's role."""
        self.access_control.add_user("testuser", AccessRole.VIEWER)
        
        success = self.access_control.update_user_role("testuser", AccessRole.ADMIN)
        
        assert success is True
        user = self.access_control.get_user("testuser")
        assert user["role"] == "admin"


class TestSecurityManager:
    """Test suite for the SecurityManager class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "credentials.enc")
        self.test_password = "test-master-password"
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove test file if it exists
        if os.path.exists(self.storage_path):
            os.unlink(self.storage_path)
        
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_init_default(self):
        """Test default initialization."""
        manager = SecurityManager()
        
        assert manager.credential_storage is not None
        assert manager.request_encryption is not None
        assert manager.request_encryption.encryption_level == EncryptionLevel.NONE
        assert manager.access_control is None
        assert manager.enable_access_control is False
    
    def test_init_with_options(self):
        """Test initialization with options."""
        manager = SecurityManager(
            master_password=self.test_password,
            storage_path=self.storage_path,
            encryption_level=EncryptionLevel.FULL,
            enable_access_control=True
        )
        
        assert manager.credential_storage is not None
        assert manager.credential_storage.master_password == self.test_password
        assert manager.credential_storage.storage_path == self.storage_path
        assert manager.request_encryption.encryption_level == EncryptionLevel.FULL
        assert manager.access_control is not None
        assert manager.enable_access_control is True
    
    def test_store_and_get_credential(self):
        """Test storing and retrieving credentials."""
        manager = SecurityManager(
            master_password=self.test_password,
            storage_path=self.storage_path
        )
        
        # Store credential
        success = manager.store_credential("test-api", {"token": "secret"})
        assert success is True
        
        # Get credential
        cred = manager.get_credential("test-api")
        assert cred is not None
        assert cred["token"] == "secret"
    
    def test_encrypt_decrypt_request(self):
        """Test encrypting and decrypting requests."""
        manager = SecurityManager(
            master_password=self.test_password,
            encryption_level=EncryptionLevel.FULL
        )
        
        # Original request
        headers = {"Authorization": "Bearer token123"}
        body = {"data": "test"}
        
        # Encrypt request
        enc_headers, enc_body = manager.encrypt_request(headers, body)
        
        # Decrypt response
        dec_headers, dec_body = manager.decrypt_response(enc_headers, enc_body)
        
        assert dec_body["data"] == "test"
    
    def test_add_user_and_check_permission(self):
        """Test adding users and checking permissions."""
        manager = SecurityManager(
            master_password=self.test_password,
            enable_access_control=True
        )
        
        # Add users
        admin = manager.add_user("admin", AccessRole.ADMIN)
        viewer = manager.add_user("viewer", AccessRole.VIEWER)
        
        assert admin["username"] == "admin"
        assert viewer["username"] == "viewer"
        
        # Check permissions
        assert manager.check_permission("admin", "edit_config") is True
        assert manager.check_permission("viewer", "edit_config") is False
        assert manager.check_permission("admin", "view_config") is True
        assert manager.check_permission("viewer", "view_config") is True
    
    def test_authenticate_api_key(self):
        """Test authenticating with API key."""
        manager = SecurityManager(
            master_password=self.test_password,
            enable_access_control=True
        )
        
        # Add user with specific API key
        api_key = "test-api-key-789"
        manager.add_user("testuser", AccessRole.OPERATOR, api_key)
        
        # Authenticate with API key
        user = manager.authenticate_api_key(api_key)
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == "operator"
