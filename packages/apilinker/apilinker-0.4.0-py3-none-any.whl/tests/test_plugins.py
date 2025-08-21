"""
Comprehensive test suite for the ApiLinker plugin system.

These tests validate the core functionality, error handling, type validation,
and plugin management features of the plugin system.
"""

import os
import sys
import tempfile
from pathlib import Path
import importlib
import unittest
from unittest.mock import MagicMock, patch, mock_open

import pytest

from apilinker.core.plugins import (
    PluginManager, PluginBase, TransformerPlugin, ConnectorPlugin, AuthPlugin,
    PluginError, PluginNotFoundError, PluginValidationError, PluginInitializationError
)


class TestPluginBase:
    """Test suite for the PluginBase class and its exceptions."""
    
    def test_plugin_base_init(self):
        """Test initialization of PluginBase with config parameters."""
        plugin = PluginBase(param1="value1", param2="value2")
        assert plugin.config["param1"] == "value1"
        assert plugin.config["param2"] == "value2"
    
    def test_plugin_info(self):
        """Test plugin info includes all required fields."""
        # Create a custom plugin class with version and author
        class CustomPlugin(PluginBase):
            """Test plugin docstring"""
            plugin_name = "custom"
            plugin_type = "test"
            version = "1.2.3"
            author = "Test Author"
        
        info = CustomPlugin.get_plugin_info()
        assert info["name"] == "custom"
        assert info["type"] == "test"
        assert info["version"] == "1.2.3"  # Check actual class attribute, not default
        assert info["author"] == "Test Author"
        assert "Test plugin docstring" in info["description"]
    
    def test_plugin_info_defaults(self):
        """Test plugin info includes default values when not specified."""
        class BasicPlugin(PluginBase):
            plugin_name = "basic"
            plugin_type = "minimal"
        
        info = BasicPlugin.get_plugin_info()
        assert info["version"] == "0.4.0"
        assert info["author"] == "Unknown"


class TestPluginExceptions:
    """Test suite for plugin exception classes."""
    
    def test_plugin_error_inheritance(self):
        """Test that all plugin exceptions inherit from PluginError."""
        assert issubclass(PluginNotFoundError, PluginError)
        assert issubclass(PluginValidationError, PluginError)
        assert issubclass(PluginInitializationError, PluginError)
    
    def test_plugin_error_messages(self):
        """Test error messages for plugin exceptions."""
        not_found = PluginNotFoundError("Plugin not found")
        validation = PluginValidationError("Invalid plugin")
        init_error = PluginInitializationError("Failed to initialize")
        
        assert str(not_found) == "Plugin not found"
        assert str(validation) == "Invalid plugin"
        assert str(init_error) == "Failed to initialize"


class TestPluginManager:
    """Test suite for PluginManager."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.plugin_manager = PluginManager()
        # Clear loaded modules tracking between tests
        self.plugin_manager._loaded_modules.clear()

    def test_register_plugin(self):
        """Test registering a plugin."""
        # Create a mock plugin class
        class TestTransformer(TransformerPlugin):
            plugin_name = "test_transformer"
            
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
        
        # Register the plugin
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Verify plugin was registered
        assert "transformer" in self.plugin_manager.plugins
        assert "test_transformer" in self.plugin_manager.plugins["transformer"]
        assert self.plugin_manager.plugins["transformer"]["test_transformer"] is TestTransformer
    
    def test_register_plugin_validation_errors(self):
        """Test that invalid plugins raise appropriate validation errors."""
        # Test non-plugin class
        with pytest.raises(TypeError, match="Plugin must be a subclass of PluginBase"):
            self.plugin_manager.register_plugin(object)
        
        # Test missing plugin name
        class NoNamePlugin(PluginBase):
            plugin_type = "test"
            plugin_name = ""
            
        with pytest.raises(PluginValidationError, match="Invalid plugin_name"):
            self.plugin_manager.register_plugin(NoNamePlugin)
        
        # Test invalid plugin type
        class InvalidTypePlugin(PluginBase):
            plugin_type = "base"  # Invalid - should not be "base"
            plugin_name = "invalid_type"
            
        with pytest.raises(PluginValidationError, match="Invalid plugin_type"):
            self.plugin_manager.register_plugin(InvalidTypePlugin)
    
    def test_get_plugin_types(self):
        """Test getting available plugin types."""
        # Register a test plugin
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
                
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Get plugin types
        types = list(self.plugin_manager.plugins.keys())
        
        # Verify transformer is in types
        assert "transformer" in types
    
    def test_get_plugins_by_type(self):
        """Test getting plugins of a specific type."""
        # Register test plugins
        class TestTransformer1(TransformerPlugin):
            plugin_name = "test1"
            
            def transform(self, value, **kwargs):
                return f"transformed1_{value}"
                
        class TestTransformer2(TransformerPlugin):
            plugin_name = "test2"
            
            def transform(self, value, **kwargs):
                return f"transformed2_{value}"
        
        self.plugin_manager.register_plugin(TestTransformer1)
        self.plugin_manager.register_plugin(TestTransformer2)
        
        # Get plugins by type
        plugins = self.plugin_manager.plugins["transformer"]
        
        # Verify plugins are returned
        assert len(plugins) == 2
        assert "test1" in plugins
        assert "test2" in plugins
        
    def test_instantiate_plugin(self):
        """Test instantiating a plugin."""
        # Create a plugin class that tracks instantiation
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def __init__(self, **kwargs):
                self.init_params = kwargs
                super().__init__(**kwargs)
                
            def transform(self, value, **kwargs):
                return f"transformed_{value}"
        
        # Register the plugin class
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Instantiate the plugin
        plugin = self.plugin_manager.instantiate_plugin("transformer", "test", param1="value1")
        
        # Verify plugin was instantiated with correct parameters
        assert plugin is not None
        assert isinstance(plugin, TestTransformer)
        assert plugin.init_params.get("param1") == "value1"
        
    def test_instantiate_plugin_not_found(self):
        """Test instantiating a non-existent plugin raises the correct error."""
        with pytest.raises(PluginNotFoundError, match="Plugin not found: transformer.nonexistent"):
            self.plugin_manager.instantiate_plugin("transformer", "nonexistent")
    
    def test_instantiate_plugin_initialization_error(self):
        """Test that initialization errors are properly caught and raised."""
        # Create a plugin class that raises an error during initialization
        class BrokenPlugin(TransformerPlugin):
            plugin_name = "broken"
            
            def __init__(self, **kwargs):
                raise ValueError("Initialization failed")
                
            def transform(self, value, **kwargs):
                return value
        
        # Register the plugin class
        self.plugin_manager.register_plugin(BrokenPlugin)
        
        # Attempt to instantiate the plugin
        with pytest.raises(PluginInitializationError, match="Error instantiating plugin transformer.broken"):
            self.plugin_manager.instantiate_plugin("transformer", "broken")
    
    def test_discover_plugins(self):
        """Test discovering plugins from directories."""
        # Create a test plugin class that we can register manually
        class TestDiscoveryPlugin(TransformerPlugin):
            plugin_name = "discovered"
            def transform(self, value, **kwargs):
                return f"discovered_{value}"

        # Add the test plugin class to our test registry
        self.plugin_manager.register_plugin(TestDiscoveryPlugin)
        
        # Verify plugin registration worked
        plugin_class = self.plugin_manager.get_plugin("transformer", "discovered")
        assert plugin_class is TestDiscoveryPlugin
        
        # Test discover_plugins functionality by monkey patching the internal methods it calls
        with patch.object(self.plugin_manager, '_get_plugins_from_module') as mock_get_plugins:
            # Configure the mock to return our test plugin info
            mock_get_plugins.return_value = [{"name": "discovered", "type": "transformer"}]
            
            # Bypass filesystem operations by monkeypatching built-in methods used by discover_plugins
            original_listdir = os.listdir
            original_exists = Path.exists
            original_is_dir = Path.is_dir
            original_import = importlib.import_module
            
            # Create mock implementations
            def mock_listdir(path):
                return ["discovered_plugin.py", "__pycache__"]
                
            def mock_exists(self):
                return True
                
            def mock_is_dir(self):
                return True
                
            def mock_import(name):
                mock_module = MagicMock()
                mock_module.__name__ = name
                return mock_module
                
            try:
                # Apply monkey patches
                os.listdir = mock_listdir
                Path.exists = mock_exists
                Path.is_dir = mock_is_dir
                importlib.import_module = mock_import
                
                # Call discover_plugins with a dummy path
                discovered = self.plugin_manager.discover_plugins("/test/plugins/dir")
                
                # Verify the results
                assert len(discovered) > 0
                assert any(p["name"] == "discovered" and p["type"] == "transformer" for p in discovered)
                
                # Verify the mock was called
                assert mock_get_plugins.called
                
            finally:
                # Restore original methods
                os.listdir = original_listdir
                Path.exists = original_exists
                Path.is_dir = original_is_dir
                importlib.import_module = original_import
    
    def test_get_transformer(self):
        """Test getting a transformer function."""
        # Create a transformer plugin with known behavior
        class TestTransformer(TransformerPlugin):
            plugin_name = "test"
            
            def transform(self, value, **kwargs):
                suffix = kwargs.get('suffix', '')
                return f"transformed_{value}{suffix}"
        
        # Register the plugin class
        self.plugin_manager.register_plugin(TestTransformer)
        
        # Get the transformer function
        transformer = self.plugin_manager.get_transformer("test")
        
        # Test the transformer function
        result = transformer("input", suffix="_extra")
        assert result == "transformed_input_extra"


class TestTransformerPlugin:
    """Test suite for TransformerPlugin base class."""
    
    def test_transform_not_implemented(self):
        """Test that transform raises NotImplementedError."""
        plugin = TransformerPlugin()
        with pytest.raises(NotImplementedError, match="Transformer plugins must implement the transform method"):
            plugin.transform("test")
    
    def test_validate_input(self):
        """Test the default validate_input implementation."""
        plugin = TransformerPlugin()
        assert plugin.validate_input(None) is True
        assert plugin.validate_input("test") is True
        assert plugin.validate_input(123) is True
    
    def test_custom_transformer_implementation(self):
        """Test a custom transformer implementation with validation."""
        class StringTransformer(TransformerPlugin):
            plugin_name = "string_transformer"
            
            def validate_input(self, value):
                return isinstance(value, str)
                
            def transform(self, value, **kwargs):
                if not self.validate_input(value):
                    raise TypeError("Value must be a string")
                return value.upper()
        
        transformer = StringTransformer()
        assert transformer.transform("test") == "TEST"
        with pytest.raises(TypeError, match="Value must be a string"):
            transformer.transform(123)


class TestConnectorPlugin:
    """Test suite for ConnectorPlugin base class."""
    
    def test_connect_not_implemented(self):
        """Test that connect raises NotImplementedError."""
        plugin = ConnectorPlugin()
        with pytest.raises(NotImplementedError, match="Connector plugins must implement the connect method"):
            plugin.connect(base_url="https://example.com")
    
    def test_fetch_not_implemented(self):
        """Test that fetch raises NotImplementedError."""
        plugin = ConnectorPlugin()
        with pytest.raises(NotImplementedError, match="Connector plugins must implement the fetch method"):
            plugin.fetch({}, "endpoint")
    
    def test_send_not_implemented(self):
        """Test that send raises NotImplementedError."""
        plugin = ConnectorPlugin()
        with pytest.raises(NotImplementedError, match="Connector plugins must implement the send method"):
            plugin.send({}, "endpoint", {})
    
    def test_validate_connection(self):
        """Test the default validate_connection implementation."""
        plugin = ConnectorPlugin()
        assert plugin.validate_connection({}) is True
        assert plugin.validate_connection(None) is False
    
    def test_custom_connector_implementation(self):
        """Test a custom connector implementation."""
        class TestConnector(ConnectorPlugin):
            plugin_name = "test_connector"
            
            def connect(self, **kwargs):
                return {"base_url": kwargs.get("base_url"), "headers": kwargs.get("headers", {})}
            
            def fetch(self, connection, endpoint, **kwargs):
                if not self.validate_connection(connection):
                    raise ValueError("Invalid connection")
                return {"url": f"{connection['base_url']}/{endpoint}", "method": "GET", "data": None}
            
            def send(self, connection, endpoint, data, **kwargs):
                if not self.validate_connection(connection):
                    raise ValueError("Invalid connection")
                return {"url": f"{connection['base_url']}/{endpoint}", "method": "POST", "data": data}
        
        connector = TestConnector()
        connection = connector.connect(base_url="https://example.com", headers={"X-Test": "Value"})
        
        assert connection["base_url"] == "https://example.com"
        assert connection["headers"] == {"X-Test": "Value"}
        
        fetch_result = connector.fetch(connection, "users")
        assert fetch_result["url"] == "https://example.com/users"
        assert fetch_result["method"] == "GET"
        
        send_result = connector.send(connection, "users", {"name": "Test User"})
        assert send_result["url"] == "https://example.com/users"
        assert send_result["method"] == "POST"
        assert send_result["data"] == {"name": "Test User"}


class TestAuthPlugin:
    """Test suite for AuthPlugin base class."""
    
    def test_authenticate_not_implemented(self):
        """Test that authenticate raises NotImplementedError."""
        plugin = AuthPlugin()
        with pytest.raises(NotImplementedError, match="Auth plugins must implement the authenticate method"):
            plugin.authenticate(token="abc123")
    
    def test_validate_credentials(self):
        """Test the default validate_credentials implementation."""
        plugin = AuthPlugin()
        assert plugin.validate_credentials({"type": "bearer"}) is True
        assert plugin.validate_credentials({}) is False
        assert plugin.validate_credentials(None) is False
    
    def test_custom_auth_implementation(self):
        """Test a custom authentication implementation."""
        class BearerAuth(AuthPlugin):
            plugin_name = "bearer_auth"
            
            def authenticate(self, **kwargs):
                token = kwargs.get("token")
                if not token:
                    raise ValueError("Token is required")
                return {
                    "type": "bearer",
                    "headers": {"Authorization": f"Bearer {token}"},
                    "params": {}
                }
        
        auth = BearerAuth()
        credentials = auth.authenticate(token="abc123")
        
        assert credentials["type"] == "bearer"
        assert credentials["headers"]["Authorization"] == "Bearer abc123"
        
        with pytest.raises(ValueError, match="Token is required"):
            auth.authenticate()


class TestPluginManagerIntegration:
    """Integration tests for the plugin manager with different plugin types."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.plugin_manager = PluginManager()
    
    def test_get_connector(self):
        """Test getting a connector plugin."""
        # Define a test connector
        class TestConnector(ConnectorPlugin):
            plugin_name = "test_connector"
            
            def connect(self, **kwargs):
                return {"connected": True, **kwargs}
                
            def fetch(self, connection, endpoint, **kwargs):
                return {"data": f"Fetched from {endpoint}"}
                
            def send(self, connection, endpoint, data, **kwargs):
                return {"success": True, "endpoint": endpoint}
        
        # Register and retrieve the connector
        self.plugin_manager.register_plugin(TestConnector)
        connector = self.plugin_manager.get_connector("test_connector", debug=True)
        
        assert connector is not None
        assert isinstance(connector, ConnectorPlugin)
        assert connector.plugin_name == "test_connector"
        
        # Test the connector functionality
        conn = connector.connect(api_key="test_key")
        assert conn["connected"] is True
        assert conn["api_key"] == "test_key"
        
        fetch_result = connector.fetch(conn, "users")
        assert fetch_result["data"] == "Fetched from users"
    
    def test_get_auth_plugin(self):
        """Test getting an auth plugin."""
        # Define a test auth plugin
        class TestAuth(AuthPlugin):
            plugin_name = "test_auth"
            
            def authenticate(self, **kwargs):
                username = kwargs.get("username")
                password = kwargs.get("password")
                
                if not username or not password:
                    raise ValueError("Username and password are required")
                    
                return {
                    "type": "basic",
                    "headers": {"Authorization": f"Basic {username}:{password}"},
                    "authenticated": True
                }
        
        # Register and retrieve the auth plugin
        self.plugin_manager.register_plugin(TestAuth)
        auth = self.plugin_manager.get_auth_plugin("test_auth")
        
        assert auth is not None
        assert isinstance(auth, AuthPlugin)
        assert auth.plugin_name == "test_auth"
        
        # Test the auth functionality
        credentials = auth.authenticate(username="testuser", password="testpass")
        assert credentials["type"] == "basic"
        assert "Authorization" in credentials["headers"]
        assert credentials["authenticated"] is True
