"""
Security integration module for APILinker.

This module integrates the security features with the rest of the APILinker system.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from apilinker.core.security import (
    AccessControl,
    AccessRole,
    EncryptionLevel,
    RequestResponseEncryption,
    SecureCredentialStorage,
)

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Manager for security features in APILinker.

    This class integrates and coordinates all security features including:
    - Secure credential storage
    - Request/response encryption
    - Access control for multi-user environments
    """

    def __init__(
        self,
        master_password: Optional[str] = None,
        storage_path: Optional[str] = None,
        encryption_level: Union[EncryptionLevel, str] = EncryptionLevel.NONE,
        encryption_key: Optional[str] = None,
        enable_access_control: bool = False,
    ) -> None:
        """
        Initialize the security manager.

        Args:
            master_password: Master password for credential encryption
                             If None, will look for APILINKER_MASTER_PASSWORD env var
            storage_path: Path to store encrypted credentials
                          If None, defaults to ~/.apilinker/credentials.enc
            encryption_level: Level of API request/response encryption
            encryption_key: Key for request/response encryption
            enable_access_control: Whether to enable multi-user access control
        """
        # Get master password from env var if not provided
        if not master_password:
            master_password = os.environ.get("APILINKER_MASTER_PASSWORD")

        # Initialize secure credential storage
        self.credential_storage = SecureCredentialStorage(
            storage_path=storage_path, master_password=master_password, auto_load=True
        )

        # Convert string to enum if necessary
        if isinstance(encryption_level, str):
            try:
                encryption_level = EncryptionLevel[encryption_level.upper()]
            except KeyError:
                encryption_level = EncryptionLevel.NONE
                logger.warning(
                    f"Invalid encryption level: {encryption_level}. Using NONE."
                )

        # Initialize request/response encryption
        self.request_encryption = RequestResponseEncryption(
            encryption_level=encryption_level, encryption_key=encryption_key
        )

        # Initialize access control if enabled
        self.access_control = AccessControl() if enable_access_control else None
        self.enable_access_control = enable_access_control

        logger.info(
            f"Initialized SecurityManager (encryption: {encryption_level.value}, access control: {enable_access_control})"
        )

    def store_credential(self, name: str, credential_data: Dict[str, Any]) -> bool:
        """
        Store API credentials securely.

        Args:
            name: Name to identify the credential
            credential_data: Credential data to store

        Returns:
            True if successful, False otherwise
        """
        return self.credential_storage.store_credential(name, credential_data)

    def get_credential(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get stored API credentials.

        Args:
            name: Name of the credential

        Returns:
            Credential data if found, None otherwise
        """
        return self.credential_storage.get_credential(name)

    def list_credentials(self) -> List[str]:
        """
        List available credential names.

        Returns:
            List of credential names
        """
        return self.credential_storage.list_credentials()

    def encrypt_request(self, headers: Dict[str, str], body: Any) -> tuple:
        """
        Encrypt an API request.

        Args:
            headers: Request headers
            body: Request body

        Returns:
            Tuple of (encrypted_headers, encrypted_body)
        """
        encrypted_headers = self.request_encryption.encrypt_headers(headers)
        encrypted_body = self.request_encryption.encrypt_body(body)
        return encrypted_headers, encrypted_body

    def decrypt_response(self, headers: Dict[str, str], body: bytes) -> tuple:
        """
        Decrypt an API response.

        Args:
            headers: Response headers
            body: Response body

        Returns:
            Tuple of (decrypted_headers, decrypted_body)
        """
        decrypted_headers = self.request_encryption.decrypt_headers(headers)
        decrypted_body = self.request_encryption.decrypt_body(body)
        return decrypted_headers, decrypted_body

    def add_user(
        self, username: str, role: Union[str, AccessRole], api_key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Add a user with specified role.

        Args:
            username: Username
            role: Access role (string or AccessRole enum)
            api_key: Optional API key for authentication

        Returns:
            User data if successful, None if access control is disabled
        """
        if not self.enable_access_control:
            logger.warning("Access control is disabled, cannot add user")
            return None

        # Convert string to enum if necessary
        if isinstance(role, str):
            try:
                role = AccessRole[role.upper()]
            except KeyError:
                logger.warning(f"Invalid role: {role}. Using VIEWER.")
                role = AccessRole.VIEWER

        return self.access_control.add_user(username, role, api_key)

    def check_permission(self, username: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            username: Username
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise
        """
        if not self.enable_access_control:
            # If access control is disabled, allow all operations
            return True

        return self.access_control.has_permission(username, permission)

    def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user by API key.

        Args:
            api_key: API key to authenticate

        Returns:
            User data if found, None otherwise
        """
        if not self.enable_access_control:
            return None

        return self.access_control.get_user_by_api_key(api_key)


def integrate_security_with_auth_manager(
    security_manager: SecurityManager, auth_manager: Any
) -> None:
    """
    Integrate the security manager with the authentication manager.

    Args:
        security_manager: SecurityManager instance
        auth_manager: AuthManager instance
    """
    # Set the secure storage in the auth manager
    auth_manager.secure_storage = security_manager.credential_storage
    logger.debug("Integrated security manager with authentication manager")
