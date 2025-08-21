"""
Authentication module for handling API authentication.
"""

import base64
import hashlib
import logging
import os
import random
import string
import time
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)


class AuthConfig(BaseModel):
    """Base authentication configuration."""

    type: str
    model_config = ConfigDict(extra="allow")


class ApiKeyAuth(AuthConfig):
    """API Key authentication configuration."""

    type: str = "api_key"
    key: str
    header_name: str = "X-API-Key"
    in_header: bool = True
    in_query: bool = False
    query_param: Optional[str] = None


class BearerAuth(AuthConfig):
    """Bearer token authentication configuration."""

    type: str = "bearer"
    token: str


class BasicAuth(AuthConfig):
    """Basic authentication configuration."""

    type: str = "basic"
    username: str
    password: str


class OAuth2ClientCredentials(AuthConfig):
    """OAuth2 client credentials authentication configuration."""

    type: str = "oauth2_client_credentials"
    client_id: str
    client_secret: str
    token_url: str
    scope: Optional[str] = None
    token: Optional[str] = None
    expires_at: Optional[int] = None


class OAuth2PKCE(AuthConfig):
    """OAuth2 PKCE (Proof Key for Code Exchange) authentication configuration.

    This flow is designed for public clients that cannot securely store a client secret,
    such as single-page applications and mobile apps.
    """

    type: str = "oauth2_pkce"
    client_id: str
    redirect_uri: str
    authorization_url: str
    token_url: str
    scope: Optional[str] = None
    code_verifier: Optional[str] = None  # Random string used to generate the challenge
    code_challenge: Optional[str] = None  # SHA256 hash of code_verifier
    authorization_code: Optional[str] = None
    state: Optional[str] = None  # Security state to prevent CSRF attacks
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    storage_key: Optional[str] = None  # Key to store credentials in secure storage


class OAuth2DeviceFlow(AuthConfig):
    """OAuth2 Device Flow authentication configuration.

    This flow is designed for devices with limited input capabilities, such as
    TVs, IoT devices, and CLI applications.
    """

    type: str = "oauth2_device_flow"
    client_id: str
    client_secret: Optional[str] = None  # Some providers require this
    device_authorization_url: str
    token_url: str
    scope: Optional[str] = None
    device_code: Optional[str] = None  # Code returned by authorization request
    user_code: Optional[str] = None  # Code shown to the user
    verification_uri: Optional[str] = None  # URL where user enters the code
    verification_uri_complete: Optional[str] = None  # Direct URL with code embedded
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    interval: Optional[int] = None  # Polling interval in seconds
    storage_key: Optional[str] = None  # Key to store credentials in secure storage


class AuthManager:
    """
    Manager for handling different types of authentication.

    This class creates and manages authentication configurations for different APIs.
    It supports:
    - API Key
    - Bearer Token
    - Basic Auth
    - OAuth2 Client Credentials
    - OAuth2 PKCE (Proof Key for Code Exchange)
    - OAuth2 Device Flow

    It also integrates with the secure credential storage system to safely store
    sensitive authentication information.
    """

    def __init__(self, secure_storage=None) -> None:
        logger.debug("Initialized AuthManager")
        self.secure_storage = secure_storage

    def _generate_random_string(self, length: int = 64) -> str:
        """Generate a random string for PKCE code verifier or state."""
        chars = string.ascii_letters + string.digits + "-._~"
        return "".join(random.choice(chars) for _ in range(length))

    def _create_code_challenge(self, code_verifier: str) -> str:
        """Create a code challenge from a code verifier using SHA-256."""
        # Hash the verifier using SHA-256
        code_challenge = hashlib.sha256(code_verifier.encode()).digest()
        # Base64-URL encode the hash
        return base64.urlsafe_b64encode(code_challenge).decode().rstrip("=")

    def _resolve_env_vars(self, value: Any) -> Any:
        """
        Resolve environment variables in a string value.

        Args:
            value: Value that may contain environment variable references like ${VAR_NAME}

        Returns:
            Value with environment variables resolved
        """
        if not isinstance(value, str):
            return value

        if value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            env_value = os.environ.get(env_var)
            if env_value is None:
                logger.warning(f"Environment variable {env_var} not found")
                return value
            return env_value

        return value

    def _resolve_env_vars_in_dict(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively resolve environment variables in a dictionary.

        Args:
            config: Dictionary that may contain environment variable references

        Returns:
            Dictionary with environment variables resolved
        """
        resolved: Dict[str, Any] = {}

        for key, value in config.items():
            if isinstance(value, dict):
                resolved[key] = self._resolve_env_vars_in_dict(value)
            elif isinstance(value, str):
                resolved[key] = self._resolve_env_vars(value)
            else:
                resolved[key] = value

        return resolved

    def configure_auth(self, auth_config: Dict[str, Any]) -> AuthConfig:
        """
        Configure authentication based on provided configuration.

        Args:
            auth_config: Authentication configuration dictionary

        Returns:
            AuthConfig instance for the specified authentication type
        """
        # Resolve any environment variables in the config
        auth_config = self._resolve_env_vars_in_dict(auth_config)

        auth_type = auth_config.get("type", "").lower()

        if auth_type == "api_key":
            if "key" not in auth_config:
                raise ValueError("API Key authentication requires 'key' parameter")

            # Determine if API key goes in header or query parameter
            in_header = True
            in_query = False
            header_name = auth_config.get("header", "X-API-Key")
            query_param = None

            if "in" in auth_config:
                location = str(auth_config["in"]).lower()
                if location == "query":
                    in_header = False
                    in_query = True
                    query_param = auth_config.get("param_name", "api_key")

            return ApiKeyAuth(
                key=str(auth_config["key"]),
                header_name=header_name,
                in_header=in_header,
                in_query=in_query,
                query_param=query_param,
            )

        elif auth_type == "bearer":
            if "token" not in auth_config:
                raise ValueError("Bearer authentication requires 'token' parameter")

            return BearerAuth(token=str(auth_config["token"]))

        elif auth_type == "basic":
            if "username" not in auth_config or "password" not in auth_config:
                raise ValueError(
                    "Basic authentication requires 'username' and 'password' parameters"
                )

            return BasicAuth(
                username=str(auth_config["username"]),
                password=str(auth_config["password"]),
            )

        elif auth_type in ["oauth2", "oauth2_client_credentials"]:
            required_params = ["client_id", "client_secret", "token_url"]
            missing_params = [
                param for param in required_params if param not in auth_config
            ]

            if missing_params:
                raise ValueError(
                    f"OAuth2 client credentials authentication requires {', '.join(missing_params)} parameters"
                )

            return OAuth2ClientCredentials(
                client_id=auth_config["client_id"],
                client_secret=auth_config["client_secret"],
                token_url=auth_config["token_url"],
                scope=auth_config.get("scope"),
                token=auth_config.get("token"),
                expires_at=auth_config.get("expires_at"),
            )

        elif auth_type == "oauth2_pkce":
            required_params = [
                "client_id",
                "authorization_url",
                "token_url",
                "redirect_uri",
            ]
            missing_params = [
                param for param in required_params if param not in auth_config
            ]

            if missing_params:
                raise ValueError(
                    f"OAuth2 PKCE authentication requires {', '.join(missing_params)} parameters"
                )

            # Generate code verifier and challenge if not provided
            code_verifier = auth_config.get("code_verifier")
            code_challenge = auth_config.get("code_challenge")

            if not code_verifier:
                code_verifier = self._generate_random_string(64)
                code_challenge = self._create_code_challenge(code_verifier)

            # Generate state if not provided
            state = auth_config.get("state") or self._generate_random_string(32)

            return OAuth2PKCE(
                client_id=auth_config["client_id"],
                redirect_uri=auth_config["redirect_uri"],
                authorization_url=auth_config["authorization_url"],
                token_url=auth_config["token_url"],
                scope=auth_config.get("scope"),
                code_verifier=code_verifier,
                code_challenge=code_challenge,
                state=state,
                token=auth_config.get("token"),
                refresh_token=auth_config.get("refresh_token"),
                expires_at=auth_config.get("expires_at"),
                storage_key=auth_config.get("storage_key"),
            )

        elif auth_type == "oauth2_device_flow":
            required_params = ["client_id", "device_authorization_url", "token_url"]
            missing_params = [
                param for param in required_params if param not in auth_config
            ]

            if missing_params:
                raise ValueError(
                    f"OAuth2 Device Flow authentication requires {', '.join(missing_params)} parameters"
                )

            return OAuth2DeviceFlow(
                client_id=auth_config["client_id"],
                client_secret=auth_config.get("client_secret"),
                device_authorization_url=auth_config["device_authorization_url"],
                token_url=auth_config["token_url"],
                scope=auth_config.get("scope"),
                device_code=auth_config.get("device_code"),
                user_code=auth_config.get("user_code"),
                verification_uri=auth_config.get("verification_uri"),
                verification_uri_complete=auth_config.get("verification_uri_complete"),
                token=auth_config.get("token"),
                refresh_token=auth_config.get("refresh_token"),
                expires_at=auth_config.get("expires_at"),
                interval=auth_config.get("interval"),
                storage_key=auth_config.get("storage_key"),
            )

        else:
            logger.warning(
                f"Unknown authentication type: {auth_type}, using base AuthConfig"
            )
            # Remove type from auth_config to avoid duplicate parameter error
            auth_config_copy = auth_config.copy()
            auth_config_copy.pop("type", None)
            return AuthConfig(type=auth_type, **auth_config_copy)

    def refresh_oauth2_token(
        self, auth_config: OAuth2ClientCredentials
    ) -> OAuth2ClientCredentials:
        """
        Refresh an OAuth2 token using client credentials flow.

        Args:
            auth_config: OAuth2 client credentials configuration

        Returns:
            Updated OAuth2ClientCredentials with new token and expiry
        """
        try:
            data = {
                "grant_type": "client_credentials",
                "client_id": auth_config.client_id,
                "client_secret": auth_config.client_secret,
            }

            if auth_config.scope:
                data["scope"] = auth_config.scope

            response = httpx.post(
                auth_config.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

            # Update token and expiry
            token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            expires_at = int(time.time() + expires_in)

            logger.debug("OAuth2 token refreshed")

            # Update secure storage if available
            if (
                self.secure_storage
                and hasattr(auth_config, "storage_key")
                and auth_config.storage_key
            ):
                self.secure_storage.store_credential(
                    auth_config.storage_key,
                    {
                        "token": token,
                        "expires_at": expires_at,
                        "updated_at": int(time.time()),
                    },
                )

            return OAuth2ClientCredentials(
                type=auth_config.type,
                client_id=auth_config.client_id,
                client_secret=auth_config.client_secret,
                token_url=auth_config.token_url,
                scope=auth_config.scope,
                token=token,
                expires_at=expires_at,
            )

        except Exception as e:
            logger.error(f"Error refreshing OAuth2 token: {str(e)}")
            raise

    def get_pkce_authorization_url(self, auth_config: OAuth2PKCE) -> str:
        """
        Get the authorization URL for OAuth2 PKCE flow.

        Args:
            auth_config: OAuth2 PKCE configuration

        Returns:
            Authorization URL for the user to visit
        """
        params = {
            "client_id": auth_config.client_id,
            "redirect_uri": auth_config.redirect_uri,
            "response_type": "code",
            "state": auth_config.state,
            "code_challenge": auth_config.code_challenge,
            "code_challenge_method": "S256",
        }

        if auth_config.scope:
            params["scope"] = auth_config.scope

        # Build the authorization URL
        query_string = urlencode(params)
        return f"{auth_config.authorization_url}?{query_string}"

    def complete_pkce_flow(
        self, auth_config: OAuth2PKCE, authorization_code: str
    ) -> OAuth2PKCE:
        """
        Complete the OAuth2 PKCE flow by exchanging the authorization code for tokens.

        Args:
            auth_config: OAuth2 PKCE configuration
            authorization_code: Authorization code received from redirect

        Returns:
            Updated OAuth2PKCE with token information
        """
        try:
            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": auth_config.redirect_uri,
                "client_id": auth_config.client_id,
                "code_verifier": auth_config.code_verifier,
            }

            response = httpx.post(
                auth_config.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

            # Extract token information
            token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)
            expires_at = int(time.time() + expires_in)

            logger.debug("OAuth2 PKCE flow completed successfully")

            # Update secure storage if available
            if self.secure_storage and auth_config.storage_key:
                self.secure_storage.store_credential(
                    auth_config.storage_key,
                    {
                        "token": token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "updated_at": int(time.time()),
                    },
                )

            return OAuth2PKCE(
                type=auth_config.type,
                client_id=auth_config.client_id,
                redirect_uri=auth_config.redirect_uri,
                authorization_url=auth_config.authorization_url,
                token_url=auth_config.token_url,
                scope=auth_config.scope,
                code_verifier=auth_config.code_verifier,
                code_challenge=auth_config.code_challenge,
                state=auth_config.state,
                authorization_code=authorization_code,
                token=token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                storage_key=auth_config.storage_key,
            )

        except Exception as e:
            logger.error(f"Error completing OAuth2 PKCE flow: {str(e)}")
            raise

    def refresh_pkce_token(self, auth_config: OAuth2PKCE) -> OAuth2PKCE:
        """
        Refresh an OAuth2 token obtained via PKCE flow.

        Args:
            auth_config: OAuth2 PKCE configuration with refresh token

        Returns:
            Updated OAuth2PKCE with new token information
        """
        if not auth_config.refresh_token:
            raise ValueError("Refresh token is required to refresh PKCE token")

        try:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": auth_config.refresh_token,
                "client_id": auth_config.client_id,
            }

            response = httpx.post(
                auth_config.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            token_data = response.json()

            # Extract token information
            token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token", auth_config.refresh_token)
            expires_in = token_data.get("expires_in", 3600)
            expires_at = int(time.time() + expires_in)

            logger.debug("OAuth2 PKCE token refreshed")

            # Update secure storage if available
            if self.secure_storage and auth_config.storage_key:
                self.secure_storage.store_credential(
                    auth_config.storage_key,
                    {
                        "token": token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "updated_at": int(time.time()),
                    },
                )

            return OAuth2PKCE(
                type=auth_config.type,
                client_id=auth_config.client_id,
                redirect_uri=auth_config.redirect_uri,
                authorization_url=auth_config.authorization_url,
                token_url=auth_config.token_url,
                scope=auth_config.scope,
                code_verifier=auth_config.code_verifier,
                code_challenge=auth_config.code_challenge,
                state=auth_config.state,
                authorization_code=auth_config.authorization_code,
                token=token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                storage_key=auth_config.storage_key,
            )

        except Exception as e:
            logger.error(f"Error refreshing OAuth2 PKCE token: {str(e)}")
            raise

    def start_device_flow(self, auth_config: OAuth2DeviceFlow) -> OAuth2DeviceFlow:
        """
        Start the OAuth2 device flow authentication process.

        Args:
            auth_config: OAuth2 Device Flow configuration

        Returns:
            Updated OAuth2DeviceFlow with device code information
        """
        try:
            data = {
                "client_id": auth_config.client_id,
            }

            if auth_config.client_secret:
                data["client_secret"] = auth_config.client_secret

            if auth_config.scope:
                data["scope"] = auth_config.scope

            response = httpx.post(
                auth_config.device_authorization_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            device_data = response.json()

            # Extract device flow information
            device_code = device_data.get("device_code")
            user_code = device_data.get("user_code")
            verification_uri = device_data.get("verification_uri") or device_data.get(
                "verification_url"
            )
            verification_uri_complete = device_data.get("verification_uri_complete")
            # expires_in not used in client; polling interval governs timing
            interval = device_data.get("interval", 5)  # Default 5 seconds

            logger.debug("OAuth2 device flow started successfully")

            return OAuth2DeviceFlow(
                type=auth_config.type,
                client_id=auth_config.client_id,
                client_secret=auth_config.client_secret,
                device_authorization_url=auth_config.device_authorization_url,
                token_url=auth_config.token_url,
                scope=auth_config.scope,
                device_code=device_code,
                user_code=user_code,
                verification_uri=verification_uri,
                verification_uri_complete=verification_uri_complete,
                interval=interval,
                storage_key=auth_config.storage_key,
            )

        except Exception as e:
            logger.error(f"Error starting OAuth2 device flow: {str(e)}")
            raise

    def poll_device_flow(
        self, auth_config: OAuth2DeviceFlow
    ) -> Tuple[bool, Optional[OAuth2DeviceFlow]]:
        """
        Poll for device flow completion and token retrieval.

        Args:
            auth_config: OAuth2 Device Flow configuration with device code

        Returns:
            Tuple of (completed, updated_config)
            - completed: True if the flow is complete, False if still pending
            - updated_config: Updated OAuth2DeviceFlow with token information if completed
        """
        if not auth_config.device_code:
            raise ValueError(
                "Device code is required to poll for device flow completion"
            )

        try:
            data = {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": auth_config.device_code,
                "client_id": auth_config.client_id,
            }

            if auth_config.client_secret:
                data["client_secret"] = auth_config.client_secret

            response = httpx.post(
                auth_config.token_url,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            # Check if authorization is still pending
            if response.status_code == 400:
                error_data = response.json()
                error = error_data.get("error")

                if error == "authorization_pending":
                    logger.debug("Device flow authorization pending")
                    return False, None

                if error == "slow_down":
                    logger.debug("Device flow polling too fast, slowing down")
                    # Increase interval for next poll
                    auth_config.interval = auth_config.interval + 5
                    return False, auth_config

            # Handle other errors
            response.raise_for_status()

            # Authorization complete, extract tokens
            token_data = response.json()
            token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            expires_at = int(time.time() + expires_in)

            logger.debug("OAuth2 device flow completed successfully")

            # Update secure storage if available
            if self.secure_storage and auth_config.storage_key:
                self.secure_storage.store_credential(
                    auth_config.storage_key,
                    {
                        "token": token,
                        "refresh_token": refresh_token,
                        "expires_at": expires_at,
                        "updated_at": int(time.time()),
                    },
                )

            updated_config = OAuth2DeviceFlow(
                type=auth_config.type,
                client_id=auth_config.client_id,
                client_secret=auth_config.client_secret,
                device_authorization_url=auth_config.device_authorization_url,
                token_url=auth_config.token_url,
                scope=auth_config.scope,
                device_code=auth_config.device_code,
                user_code=auth_config.user_code,
                verification_uri=auth_config.verification_uri,
                verification_uri_complete=auth_config.verification_uri_complete,
                token=token,
                refresh_token=refresh_token,
                expires_at=expires_at,
                interval=auth_config.interval,
                storage_key=auth_config.storage_key,
            )

            return True, updated_config

        except httpx.HTTPStatusError as e:
            # Handle other HTTP errors
            logger.error(f"HTTP error during device flow polling: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Error polling OAuth2 device flow: {str(e)}")
            raise
