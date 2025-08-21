"""
Security module for APILinker.

This module provides enhanced security features including:
1. Secure credential storage
2. Request/response encryption
3. Access control for multi-user environments
"""

import base64
import json
import logging
import os
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class EncryptionLevel(Enum):
    """Encryption level for API requests and responses."""

    NONE = "none"  # No encryption
    HEADERS_ONLY = "headers"  # Encrypt only headers
    BODY_ONLY = "body"  # Encrypt only body
    FULL = "full"  # Encrypt entire request/response


class AccessRole(Enum):
    """Access roles for multi-user environments."""

    ADMIN = "admin"  # Full access
    OPERATOR = "operator"  # Can run syncs and view results
    VIEWER = "viewer"  # Can only view configurations and results
    DEVELOPER = "developer"  # Can modify configurations but not run syncs


class SecureCredentialStorage:
    """
    Secure storage for API credentials.

    This class provides encryption-at-rest for sensitive API credentials.
    It uses Fernet symmetric encryption with key derivation based on a master password.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        master_password: Optional[str] = None,
        auto_load: bool = True,
    ) -> None:
        """
        Initialize secure credential storage.

        Args:
            storage_path: Path to store encrypted credentials
            master_password: Master password for encryption/decryption
                             If None, will look for APILINKER_MASTER_PASSWORD env var
            auto_load: Whether to automatically load credentials on init
        """
        self.storage_path = storage_path or os.path.join(
            os.path.expanduser("~"), ".apilinker", "credentials.enc"
        )
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # Get master password from env var if not provided
        if not master_password:
            master_password = os.environ.get("APILINKER_MASTER_PASSWORD")

        self.master_password = master_password
        self.credentials: Dict[str, Dict[str, Any]] = {}
        self.cipher = None
        self._salt: Optional[bytes] = None

        # Attempt to auto-load existing credentials (initializes cipher from persisted salt)
        if auto_load and os.path.exists(self.storage_path):
            self.load()

        # Ensure cipher is initialized when a master password is provided,
        # even if no credentials file exists yet (tests expect this behavior)
        if self.master_password and self.cipher is None:
            self._init_cipher(os.urandom(16))

    def _init_cipher(self, salt: bytes) -> None:
        """Initialize encryption cipher from master password and provided salt (no side files)."""
        if not self.master_password:
            logger.warning("Cannot initialize encryption without master password")
            return
        self._salt = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password.encode()))
        self.cipher = Fernet(key)

    def save(self) -> bool:
        """
        Save credentials to encrypted storage.

        Returns:
            True if successful, False otherwise
        """
        if not self.master_password:
            logger.error("Master password not set - cannot save credentials")
            return False

        try:
            # Ensure cipher is initialized with a stable salt
            if self.cipher is None:
                salt = os.urandom(16)
                self._init_cipher(salt)

            # Convert credentials to JSON and encrypt
            data = json.dumps(self.credentials).encode()
            encrypted_data = self.cipher.encrypt(data)

            # Persist JSON structure containing salt and encrypted data
            payload = {
                "salt": base64.urlsafe_b64encode(self._salt or b"").decode(),
                "data": base64.urlsafe_b64encode(encrypted_data).decode(),
                "version": 1,
            }

            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(payload, f)

            logger.info(f"Credentials saved to {self.storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save credentials: {str(e)}")
            return False

    def load(self) -> bool:
        """
        Load credentials from encrypted storage.

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(self.storage_path):
            logger.warning(f"No credentials file found at {self.storage_path}")
            return False

        try:
            # Attempt to read new JSON payload format first
            with open(self.storage_path, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                payload = json.loads(content)
                if (
                    isinstance(payload, dict)
                    and "salt" in payload
                    and "data" in payload
                ):
                    salt = base64.urlsafe_b64decode(payload["salt"].encode())
                    self._init_cipher(salt)
                    encrypted_bytes = base64.urlsafe_b64decode(payload["data"].encode())
                    data = self.cipher.decrypt(encrypted_bytes)
                    self.credentials = json.loads(data.decode())
                else:
                    raise ValueError("Invalid payload format")
            except Exception:
                # Legacy format fallback: raw encrypted bytes + side .salt file (do not create new side files)
                try:
                    # Read raw bytes again (content may be binary)
                    with open(self.storage_path, "rb") as fb:
                        encrypted_data = fb.read()
                    salt_path = self.storage_path + ".salt"
                    if os.path.exists(salt_path):
                        with open(salt_path, "rb") as sf:
                            salt = sf.read()
                        self._init_cipher(salt)
                        data = self.cipher.decrypt(encrypted_data)
                        self.credentials = json.loads(data.decode())
                    else:
                        raise ValueError("Missing salt for legacy credentials file")
                except Exception as e2:
                    logger.error(f"Failed to load legacy credentials: {str(e2)}")
                    return False

            logger.info(f"Credentials loaded from {self.storage_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load credentials: {str(e)}")
            return False

    def store_credential(self, name: str, credential_data: Dict[str, Any]) -> bool:
        """
        Store a credential securely.

        Args:
            name: Name to identify the credential (e.g., "github_api")
            credential_data: Dictionary of credential data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            self.credentials[name] = credential_data
            return self.save()

        except Exception as e:
            logger.error(f"Failed to store credential {name}: {str(e)}")
            return False

    def get_credential(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a stored credential.

        Args:
            name: Name of the credential to retrieve

        Returns:
            Dictionary of credential data or None if not found
        """
        return self.credentials.get(name)

    def delete_credential(self, name: str) -> bool:
        """
        Delete a stored credential.

        Args:
            name: Name of the credential to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            if name in self.credentials:
                del self.credentials[name]
                return self.save()
            return False
        except Exception as e:
            logger.error(f"Failed to delete credential {name}: {str(e)}")
            return False

    def list_credentials(self) -> List[str]:
        """
        List available credential names.

        Returns:
            List of credential names
        """
        return list(self.credentials.keys())


class AccessControl:
    """
    Access control for multi-user environments.

    This class provides role-based access control for APILinker.
    """

    def __init__(self) -> None:
        """Initialize access control."""
        self.users: Dict[str, Dict[str, Any]] = {}
        self.default_role = AccessRole.VIEWER

        # Define permissions by role
        self.permissions: Dict[AccessRole, Set[str]] = {
            AccessRole.ADMIN: {
                "view_config",
                "edit_config",
                "run_sync",
                "view_results",
                "manage_users",
                "manage_credentials",
                "view_logs",
                "access_analytics",
            },
            AccessRole.OPERATOR: {
                "view_config",
                "run_sync",
                "view_results",
                "view_logs",
                "access_analytics",
            },
            AccessRole.VIEWER: {"view_config", "view_results"},
            AccessRole.DEVELOPER: {
                "view_config",
                "edit_config",
                "view_results",
                "view_logs",
            },
        }

    def add_user(
        self, username: str, role: AccessRole, api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a user with specified role.

        Args:
            username: Username to identify the user
            role: Access role for the user
            api_key: Optional API key for API authentication

        Returns:
            User data including generated API key if not provided
        """
        # Generate API key if not provided
        if api_key is None:
            import secrets

            api_key = secrets.token_urlsafe(32)

        user_data = {
            "username": username,
            "role": role.value,
            "api_key": api_key,
            "created_at": int(time.time()),
        }

        self.users[username] = user_data
        logger.info(f"Added user {username} with role {role.value}")

        return user_data

    def remove_user(self, username: str) -> bool:
        """
        Remove a user.

        Args:
            username: Username to remove

        Returns:
            True if successful, False if user not found
        """
        if username in self.users:
            del self.users[username]
            logger.info(f"Removed user {username}")
            return True
        return False

    def update_user_role(self, username: str, role: AccessRole) -> bool:
        """
        Update a user's role.

        Args:
            username: Username to update
            role: New access role

        Returns:
            True if successful, False if user not found
        """
        if username in self.users:
            self.users[username]["role"] = role.value
            logger.info(f"Updated user {username} role to {role.value}")
            return True
        return False

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user data.

        Args:
            username: Username to retrieve

        Returns:
            User data or None if not found
        """
        return self.users.get(username)

    def get_user_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by API key.

        Args:
            api_key: API key to look up

        Returns:
            User data or None if not found
        """
        for user_data in self.users.values():
            if user_data["api_key"] == api_key:
                return user_data
        return None

    def has_permission(self, username: str, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            username: Username to check
            permission: Permission to check for

        Returns:
            True if user has permission, False otherwise
        """
        user_data = self.get_user(username)
        if not user_data:
            return False

        try:
            role = AccessRole(user_data["role"])
        except ValueError:
            role = self.default_role

        return permission in self.permissions.get(role, set())


class RequestResponseEncryption:
    """
    Encryption for API requests and responses.

    This class provides end-to-end encryption for sensitive API data.
    """

    def __init__(
        self,
        encryption_level: EncryptionLevel = EncryptionLevel.NONE,
        encryption_key: Optional[str] = None,
    ) -> None:
        """
        Initialize request/response encryption.

        Args:
            encryption_level: Level of encryption to apply
            encryption_key: Key for encryption/decryption
                            If None, a new key will be generated
        """
        self.encryption_level = encryption_level

        # Generate or use provided encryption key
        if encryption_key:
            key_bytes = base64.urlsafe_b64decode(encryption_key.encode())
        else:
            key = Fernet.generate_key()
            key_bytes = base64.urlsafe_b64decode(key)

        # Store the key in urlsafe base64 format
        self.encryption_key = base64.urlsafe_b64encode(key_bytes).decode()

        # Initialize cipher
        self.cipher = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Encrypt HTTP headers.

        Args:
            headers: Dictionary of HTTP headers

        Returns:
            Dictionary with encrypted headers
        """
        if self.encryption_level in [EncryptionLevel.NONE, EncryptionLevel.BODY_ONLY]:
            return headers

        encrypted_headers = {}

        # Special handling for certain headers that shouldn't be encrypted
        preserve_headers = {"Content-Type", "Content-Length", "Host", "Accept"}

        for key, value in headers.items():
            if key in preserve_headers:
                encrypted_headers[key] = value
            else:
                # Encrypt header value
                encrypted_value = self.cipher.encrypt(value.encode()).decode()
                encrypted_headers[f"X-Encrypted-{key}"] = encrypted_value

        return encrypted_headers

    def decrypt_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Decrypt HTTP headers.

        Args:
            headers: Dictionary of encrypted HTTP headers

        Returns:
            Dictionary with decrypted headers
        """
        if self.encryption_level in [EncryptionLevel.NONE, EncryptionLevel.BODY_ONLY]:
            return headers

        decrypted_headers = {}
        prefix = "X-Encrypted-"

        for key, value in headers.items():
            if key.startswith(prefix):
                original_key = key[len(prefix) :]
                try:
                    decrypted_value = self.cipher.decrypt(value.encode()).decode()
                    decrypted_headers[original_key] = decrypted_value
                except Exception as e:
                    logger.warning(f"Failed to decrypt header {key}: {str(e)}")
                    decrypted_headers[key] = value
            else:
                decrypted_headers[key] = value

        return decrypted_headers

    def encrypt_body(self, body: Union[Dict[str, Any], str, bytes]) -> bytes:
        """
        Encrypt request/response body.

        Args:
            body: Body data to encrypt

        Returns:
            Encrypted body data
        """
        if self.encryption_level in [
            EncryptionLevel.NONE,
            EncryptionLevel.HEADERS_ONLY,
        ]:
            if isinstance(body, bytes):
                return body
            elif isinstance(body, str):
                return body.encode()
            else:
                return json.dumps(body).encode()

        # Convert body to bytes if it's not already
        if isinstance(body, dict):
            data = json.dumps(body).encode()
        elif isinstance(body, str):
            data = body.encode()
        else:
            data = body

        # Encrypt the data
        return self.cipher.encrypt(data)

    def decrypt_body(self, body: bytes) -> Union[Dict[str, Any], str]:
        """
        Decrypt request/response body.

        Args:
            body: Encrypted body data

        Returns:
            Decrypted body data
        """
        if self.encryption_level in [
            EncryptionLevel.NONE,
            EncryptionLevel.HEADERS_ONLY,
        ]:
            try:
                return json.loads(body.decode())
            except:
                return body.decode()

        try:
            # Decrypt the data
            decrypted_data = self.cipher.decrypt(body)

            # Try to parse as JSON
            try:
                return json.loads(decrypted_data.decode())
            except:
                return decrypted_data.decode()

        except Exception as e:
            logger.error(f"Failed to decrypt body: {str(e)}")
            # Return the raw data if decryption fails
            return body
