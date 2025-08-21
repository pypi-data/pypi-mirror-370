"""
Plugin system for extending ApiLinker functionality.

This module provides the foundation for ApiLinker's extensibility through
a plugin architecture. It includes base classes for different plugin types
(transformers, connectors, and authentication) and a plugin manager for
discovery and loading of plugins.

Example:
    >>> from apilinker.core.plugins import PluginManager
    >>> manager = PluginManager()
    >>> manager.discover_plugins()
    >>> transformer = manager.get_transformer('my_transformer')
    >>> result = transformer('input value')
"""

import importlib
import inspect
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type

# Set up module logger
logger = logging.getLogger(__name__)


class PluginError(Exception):
    """Base exception for all plugin-related errors."""


class PluginNotFoundError(PluginError):
    """Raised when a requested plugin cannot be found."""


class PluginValidationError(PluginError):
    """Raised when a plugin fails validation checks."""


class PluginInitializationError(PluginError):
    """Raised when a plugin cannot be initialized."""


class PluginBase:
    """
    Base class for all ApiLinker plugins.

    All plugins must inherit from this class or one of its subclasses
    and provide required implementation details.

    Attributes:
        plugin_type (str): Type of the plugin (e.g., transformer, connector, auth)
        plugin_name (str): Unique name of the plugin
        config (dict): Configuration parameters passed during initialization
    """

    plugin_type: str = "base"
    plugin_name: str = "base"

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the plugin with the provided configuration.

        Args:
            **kwargs: Configuration parameters for the plugin
        """
        self.config: Dict[str, Any] = kwargs
        logger.debug(f"Initialized {self.plugin_type} plugin: {self.plugin_name}")

    @classmethod
    def get_plugin_info(cls) -> Dict[str, Any]:
        """
        Get metadata about this plugin.

        Returns:
            Dictionary containing plugin metadata (type, name, description)
        """
        return {
            "type": cls.plugin_type,
            "name": cls.plugin_name,
            "description": cls.__doc__,
            "version": getattr(cls, "version", "0.4.0"),
            "author": getattr(cls, "author", "Unknown"),
        }


class TransformerPlugin(PluginBase):
    """
    Base class for data transformation plugins.

    Transformer plugins are used to convert, format, or validate data
    during the mapping process between source and target APIs.

    Example:
        ```python
        class LowercaseTransformer(TransformerPlugin):
            plugin_name = "lowercase"

            def transform(self, value: str, **kwargs) -> str:
                return value.lower() if isinstance(value, str) else value
        ```
    """

    plugin_type: str = "transformer"

    def transform(self, value: Any, **kwargs) -> Any:
        """
        Transform a value according to the plugin's logic.

        Args:
            value: Input value to transform
            **kwargs: Additional parameters for customizing the transformation

        Returns:
            Transformed value

        Raises:
            NotImplementedError: If the subclass does not implement this method
            ValueError: If the input value is not valid for this transformer
            TypeError: If the input value is of an incompatible type
        """
        raise NotImplementedError(
            "Transformer plugins must implement the transform method"
        )

    def validate_input(self, value: Any) -> bool:
        """
        Validate that the input value is appropriate for this transformer.

        Args:
            value: Input value to validate

        Returns:
            True if valid, False otherwise
        """
        return True  # Default implementation accepts any input


class ConnectorPlugin(PluginBase):
    """
    Base class for API connector plugins.

    Connector plugins handle the communication with external APIs,
    including connection management, data fetching, and sending.

    Example:
        ```python
        class RestConnector(ConnectorPlugin):
            plugin_name = "rest"

            def connect(self, base_url: str, **kwargs) -> dict:
                session = requests.Session()
                return {"session": session, "base_url": base_url}

            def fetch(self, connection: dict, endpoint: str, **kwargs) -> dict:
                url = f"{connection['base_url']}/{endpoint}"
                response = connection['session'].get(url, **kwargs)
                response.raise_for_status()
                return response.json()
        ```
    """

    plugin_type: str = "connector"

    def connect(self, **kwargs) -> Any:
        """
        Create a connection to the API.

        This method should establish a connection or create a client
        that can be used for subsequent API operations.

        Args:
            **kwargs: Connection parameters like base_url, timeout, etc.

        Returns:
            Connection object that will be passed to fetch and send methods

        Raises:
            NotImplementedError: If the subclass does not implement this method
            ConnectionError: If the connection cannot be established
            ValueError: If required parameters are missing or invalid
        """
        raise NotImplementedError("Connector plugins must implement the connect method")

    def fetch(self, connection: Any, endpoint: str, **kwargs) -> Any:
        """
        Fetch data from the API.

        This method should retrieve data from the specified API endpoint
        using the previously established connection.

        Args:
            connection: Connection object from connect()
            endpoint: Endpoint path or identifier to fetch from
            **kwargs: Additional parameters like query params, headers, etc.

        Returns:
            Fetched data, typically parsed from JSON response

        Raises:
            NotImplementedError: If the subclass does not implement this method
            ConnectionError: If the request fails due to network issues
            ValueError: If the endpoint or parameters are invalid
            Exception: Other API-specific errors that might occur
        """
        raise NotImplementedError("Connector plugins must implement the fetch method")

    def send(self, connection: Any, endpoint: str, data: Any, **kwargs) -> Any:
        """
        Send data to the API.

        This method should send data to the specified API endpoint
        using the previously established connection.

        Args:
            connection: Connection object from connect()
            endpoint: Endpoint path or identifier to send to
            data: Data to send (typically a dict that will be serialized to JSON)
            **kwargs: Additional parameters like headers, query params, etc.

        Returns:
            API response, typically parsed from JSON response

        Raises:
            NotImplementedError: If the subclass does not implement this method
            ConnectionError: If the request fails due to network issues
            ValueError: If the endpoint, data, or parameters are invalid
            Exception: Other API-specific errors that might occur
        """
        raise NotImplementedError("Connector plugins must implement the send method")

    def validate_connection(self, connection: Any) -> bool:
        """
        Validate that a connection object is properly formed.

        Args:
            connection: Connection object to validate

        Returns:
            True if valid, False otherwise
        """
        return connection is not None


class AuthPlugin(PluginBase):
    """
    Base class for authentication plugins.

    Authentication plugins handle different methods of API authentication,
    such as API keys, OAuth2, JWT tokens, etc.

    Example:
        ```python
        class BearerTokenAuth(AuthPlugin):
            plugin_name = "bearer"

            def authenticate(self, token: str, **kwargs) -> Dict[str, Any]:
                if not token:
                    raise ValueError("Bearer token cannot be empty")
                return {"type": "bearer", "headers": {"Authorization": f"Bearer {token}"}}
        ```
    """

    plugin_type: str = "auth"

    def authenticate(self, **kwargs) -> Dict[str, Any]:
        """
        Perform authentication and return credentials.

        This method should implement the authentication logic and
        return credentials in a format that can be used by connectors.

        Args:
            **kwargs: Authentication parameters (tokens, keys, etc.)

        Returns:
            Dictionary containing authentication result with at least:
                - headers: Dict of HTTP headers to include in requests
                - params: Dict of URL parameters to include (optional)
                - auth: Auth object for requests library (optional)
                - type: String identifier of the auth type

        Raises:
            NotImplementedError: If the subclass does not implement this method
            ValueError: If required parameters are missing or invalid
            AuthenticationError: If authentication fails
        """
        raise NotImplementedError("Auth plugins must implement the authenticate method")

    def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Validate that the credentials dictionary has the required fields.

        Args:
            credentials: Credentials dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        return isinstance(credentials, dict) and "type" in credentials


class PluginManager:
    """
    Manager for loading and using plugins.

    This class handles the discovery, loading, and management of plugins
    for extending ApiLinker functionality.

    Example:
        ```python
        # Initialize the manager
        manager = PluginManager()

        # Discover available plugins
        discovered = manager.discover_plugins()
        print(f"Found {len(discovered)} plugins")

        # Register a custom plugin class
        manager.register_plugin(MyCustomTransformer)

        # Get a transformer instance
        transformer = manager.instantiate_plugin("transformer", "my_custom")
        result = transformer.transform("input data")
        ```
    """

    def __init__(self):
        """
        Initialize the plugin manager with empty plugin registries.
        """
        self.plugins: Dict[str, Dict[str, Type[PluginBase]]] = {
            "transformer": {},
            "connector": {},
            "auth": {},
        }
        # Track loaded modules to avoid duplicates
        self._loaded_modules: Set[str] = set()
        logger.debug("Initialized PluginManager")

    def discover_plugins(
        self, plugin_dir: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discover available plugins from built-in and custom directories.

        This method searches for Python modules containing plugin classes
        in the built-in plugins directory and optional custom directories.
        Discovered plugins are automatically registered with the manager.

        Args:
            plugin_dir: Optional custom directory to search for plugins.
                        If None, default locations will be searched.

        Returns:
            List of dictionaries containing information about discovered plugins

        Raises:
            PermissionError: If a plugin directory exists but cannot be read
            ImportError: If a plugin module exists but cannot be imported
        """
        discovered: List[Dict[str, Any]] = []

        # Check built-in plugins
        try:
            from apilinker.plugins import builtin

            module_plugins = self._get_plugins_from_module(builtin)
            discovered.extend(module_plugins)
            logger.debug(f"Loaded {len(module_plugins)} built-in plugins")
        except ImportError as e:
            logger.warning(f"Could not load built-in plugins: {str(e)}")

        # Check user plugins directory
        if plugin_dir is None:
            # Check default locations
            plugin_paths = [
                Path.home() / ".apilinker" / "plugins",  # User plugins
                Path(__file__).parent.parent / "plugins",  # Package plugins
            ]
        else:
            plugin_paths = [Path(plugin_dir)]

        # Load plugins from directories
        for plugin_path in plugin_paths:
            if not plugin_path.exists() or not plugin_path.is_dir():
                continue

            logger.info(f"Searching for plugins in {plugin_path}")

            # Temporarily add to path for importing
            sys.path.insert(0, str(plugin_path))

            for filename in os.listdir(plugin_path):
                if filename.endswith(".py") and not filename.startswith("_"):
                    module_name = filename[:-3]

                    # Skip already loaded modules
                    module_path = str(plugin_path / filename)
                    if module_path in self._loaded_modules:
                        continue

                    try:
                        module = importlib.import_module(module_name)
                        self._loaded_modules.add(module_path)
                        module_plugins = self._get_plugins_from_module(module)
                        discovered.extend(module_plugins)
                        logger.debug(
                            f"Loaded {len(module_plugins)} plugins from {module_name}"
                        )
                    except ImportError as e:
                        logger.warning(f"Failed to import plugin {module_name}: {e}")
                        logger.debug(f"Import error details: {traceback.format_exc()}")

            sys.path.pop(0)

        return discovered

    def _get_plugins_from_module(self, module) -> List[Dict[str, Any]]:
        """
        Extract plugin classes from a module and register them.

        Args:
            module: Python module object to extract plugins from

        Returns:
            List of plugin information dictionaries for discovered plugins

        Raises:
            PluginValidationError: If a plugin class is invalid
        """
        plugins: List[Dict[str, Any]] = []

        # Find all classes derived from PluginBase
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue

            # Check if it's a valid plugin class
            if (
                issubclass(obj, PluginBase)
                and obj is not PluginBase
                and obj is not TransformerPlugin
                and obj is not ConnectorPlugin
                and obj is not AuthPlugin
            ):

                # Validate plugin has required attributes
                if not hasattr(obj, "plugin_type") or not hasattr(obj, "plugin_name"):
                    logger.warning(
                        f"Skipping invalid plugin class {name}: missing type or name"
                    )
                    continue

                if obj.plugin_name == "base" or not obj.plugin_name:
                    logger.warning(f"Skipping plugin class {name}: invalid plugin_name")
                    continue

                # Register the plugin
                plugin_info = obj.get_plugin_info()
                plugins.append(plugin_info)
                self.register_plugin(obj)

        return plugins

    def register_plugin(self, plugin_class: Type[PluginBase]) -> None:
        """
        Register a plugin class with the manager.

        Args:
            plugin_class: Plugin class to register, must be a subclass of PluginBase

        Raises:
            PluginValidationError: If the plugin class is invalid
            TypeError: If the provided class is not a PluginBase subclass
        """
        if not inspect.isclass(plugin_class) or not issubclass(
            plugin_class, PluginBase
        ):
            raise TypeError(f"Plugin must be a subclass of PluginBase: {plugin_class}")

        plugin_type = plugin_class.plugin_type
        plugin_name = plugin_class.plugin_name

        # Validate plugin type and name
        if not plugin_type or plugin_type == "base":
            raise PluginValidationError(f"Invalid plugin_type: {plugin_type}")

        if not plugin_name or plugin_name == "base":
            raise PluginValidationError(f"Invalid plugin_name: {plugin_name}")

        # Create new category if needed
        if plugin_type not in self.plugins:
            self.plugins[plugin_type] = {}

        # Log if we're overwriting an existing plugin
        if plugin_name in self.plugins[plugin_type]:
            logger.warning(f"Overwriting existing plugin: {plugin_type}.{plugin_name}")

        self.plugins[plugin_type][plugin_name] = plugin_class
        logger.debug(f"Registered plugin: {plugin_type}.{plugin_name}")

    def get_plugin(
        self, plugin_type: str, plugin_name: str
    ) -> Optional[Type[PluginBase]]:
        """
        Get a plugin class by type and name.

        Args:
            plugin_type: Type of plugin (transformer, connector, auth, etc.)
            plugin_name: Name of the specific plugin

        Returns:
            Plugin class if found, None otherwise

        Raises:
            TypeError: If plugin_type or plugin_name are not strings
        """
        if not isinstance(plugin_type, str) or not isinstance(plugin_name, str):
            raise TypeError("Plugin type and name must be strings")

        if not plugin_type or not plugin_name:
            logger.warning("Empty plugin type or name provided")
            return None

        if plugin_type not in self.plugins:
            logger.debug(f"Plugin type not found: {plugin_type}")
            return None

        if plugin_name not in self.plugins[plugin_type]:
            logger.debug(f"Plugin {plugin_name} not found in type {plugin_type}")
            return None

        return self.plugins[plugin_type][plugin_name]

    def instantiate_plugin(
        self, plugin_type: str, plugin_name: str, **kwargs
    ) -> Optional[PluginBase]:
        """
        Create an instance of a plugin with the given parameters.

        Args:
            plugin_type: Type of plugin to instantiate
            plugin_name: Name of plugin to instantiate
            **kwargs: Parameters to pass to the plugin constructor

        Returns:
            Instantiated plugin object if successful, None otherwise

        Raises:
            PluginNotFoundError: If the plugin cannot be found
            PluginInitializationError: If the plugin cannot be initialized
        """
        plugin_class = self.get_plugin(plugin_type, plugin_name)

        if not plugin_class:
            error_msg = f"Plugin not found: {plugin_type}.{plugin_name}"
            logger.warning(error_msg)
            raise PluginNotFoundError(error_msg)

        try:
            return plugin_class(**kwargs)
        except Exception as e:
            error_msg = (
                f"Error instantiating plugin {plugin_type}.{plugin_name}: {str(e)}"
            )
            logger.error(error_msg)
            logger.debug(
                f"Plugin initialization error details: {traceback.format_exc()}"
            )
            raise PluginInitializationError(error_msg) from e

    def get_transformer(self, name: str, **kwargs) -> Optional[Callable[[Any], Any]]:
        """
        Get a transformer function from a plugin.

        This is a convenience method that returns a callable function
        wrapping the transform method of a TransformerPlugin instance.

        Args:
            name: Name of the transformer plugin
            **kwargs: Plugin initialization parameters

        Returns:
            Callable function that accepts a value and parameters and returns transformed value

        Raises:
            PluginNotFoundError: If the transformer plugin cannot be found
            PluginInitializationError: If the plugin cannot be initialized
            TypeError: If the plugin is not a TransformerPlugin
        """
        try:
            plugin = self.instantiate_plugin("transformer", name, **kwargs)

            if not isinstance(plugin, TransformerPlugin):
                error_msg = f"Plugin {name} is not a transformer plugin"
                logger.error(error_msg)
                raise TypeError(error_msg)

            # Return a function that wraps the plugin's transform method
            return lambda value, **params: plugin.transform(value, **params)

        except (PluginNotFoundError, PluginInitializationError) as e:
            logger.warning(f"Could not get transformer {name}: {str(e)}")
            return None

    def get_connector(self, name: str, **kwargs) -> Optional[ConnectorPlugin]:
        """
        Get a connector plugin instance.

        Args:
            name: Name of the connector plugin
            **kwargs: Plugin initialization parameters

        Returns:
            Connector plugin instance or None if not found

        Raises:
            PluginNotFoundError: If the connector plugin cannot be found
            PluginInitializationError: If the plugin cannot be initialized
            TypeError: If the plugin is not a ConnectorPlugin
        """
        try:
            plugin = self.instantiate_plugin("connector", name, **kwargs)

            if not isinstance(plugin, ConnectorPlugin):
                error_msg = f"Plugin {name} is not a connector plugin"
                logger.error(error_msg)
                raise TypeError(error_msg)

            return plugin

        except (PluginNotFoundError, PluginInitializationError) as e:
            logger.warning(f"Could not get connector {name}: {str(e)}")
            return None

    def get_auth_plugin(self, name: str, **kwargs) -> Optional[AuthPlugin]:
        """
        Get an authentication plugin instance.

        Args:
            name: Name of the authentication plugin
            **kwargs: Plugin initialization parameters

        Returns:
            Auth plugin instance or None if not found

        Raises:
            PluginNotFoundError: If the auth plugin cannot be found
            PluginInitializationError: If the plugin cannot be initialized
            TypeError: If the plugin is not an AuthPlugin
        """
        try:
            plugin = self.instantiate_plugin("auth", name, **kwargs)

            if not isinstance(plugin, AuthPlugin):
                error_msg = f"Plugin {name} is not an auth plugin"
                logger.error(error_msg)
                raise TypeError(error_msg)

            return plugin

        except (PluginNotFoundError, PluginInitializationError) as e:
            logger.warning(f"Could not get auth plugin {name}: {str(e)}")
            return None
