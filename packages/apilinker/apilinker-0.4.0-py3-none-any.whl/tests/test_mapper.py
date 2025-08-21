"""
Tests for the FieldMapper class.
"""

import unittest
from datetime import datetime

import pytest

from apilinker.core.mapper import FieldMapper


class TestFieldMapper:
    """Test suite for FieldMapper class."""

    def setup_method(self):
        """Set up test environment before each test."""
        self.mapper = FieldMapper()
        
        # Add sample mapping
        self.mapper.add_mapping(
            source="users",
            target="contacts",
            fields=[
                {"source": "id", "target": "external_id"},
                {"source": "name", "target": "full_name"},
                {"source": "email", "target": "contact.email"},
                {"source": "created_at", "target": "metadata.created", "transform": "iso_to_timestamp"},
                {"source": "address.street", "target": "location.street"},
                {"source": "address.city", "target": "location.city"},
                {
                    "source": "status", 
                    "target": "account_status", 
                    "transform": "uppercase",
                    "condition": {
                        "field": "status",
                        "operator": "exists"
                    }
                },
                {
                    "source": "tags",
                    "target": "labels",
                    "transform": ["lowercase", "none_if_empty"]
                }
            ]
        )

    def test_add_mapping(self):
        """Test adding a mapping."""
        # Add a new mapping
        self.mapper.add_mapping(
            source="products",
            target="items",
            fields=[
                {"source": "id", "target": "product_id"},
                {"source": "name", "target": "title"}
            ]
        )
        
        # Verify mappings
        mappings = self.mapper.get_mappings()
        assert len(mappings) == 2
        assert mappings[1]["source"] == "products"
        assert mappings[1]["target"] == "items"
        assert len(mappings[1]["fields"]) == 2

    def test_get_value_from_path(self):
        """Test getting values from nested paths."""
        # Test data
        data = {
            "id": 123,
            "name": "Test User",
            "address": {
                "street": "123 Main St",
                "city": "Test City",
                "zip": "12345"
            },
            "tags": ["test", "user", "api"],
            "items": [
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"}
            ]
        }
        
        # Test simple path
        assert self.mapper.get_value_from_path(data, "id") == 123
        assert self.mapper.get_value_from_path(data, "name") == "Test User"
        
        # Test nested path
        assert self.mapper.get_value_from_path(data, "address.street") == "123 Main St"
        assert self.mapper.get_value_from_path(data, "address.city") == "Test City"
        
        # Test array index
        assert self.mapper.get_value_from_path(data, "tags[0]") == "test"
        assert self.mapper.get_value_from_path(data, "items[1].name") == "Item 2"
        
        # Test missing path
        assert self.mapper.get_value_from_path(data, "missing") is None
        assert self.mapper.get_value_from_path(data, "address.missing") is None
        assert self.mapper.get_value_from_path(data, "items[5]") is None

    def test_set_value_at_path(self):
        """Test setting values at nested paths."""
        # Test data
        data = {}
        
        # Set simple value
        self.mapper.set_value_at_path(data, "id", 123)
        assert data["id"] == 123
        
        # Set nested value
        self.mapper.set_value_at_path(data, "user.name", "Test User")
        assert data["user"]["name"] == "Test User"
        
        # Set deeper nested value
        self.mapper.set_value_at_path(data, "user.address.street", "123 Main St")
        assert data["user"]["address"]["street"] == "123 Main St"
        
        # Overwrite existing value
        self.mapper.set_value_at_path(data, "id", 456)
        assert data["id"] == 456

    def test_apply_transform(self):
        """Test applying transformations to values."""
        # Test built-in transformers
        assert self.mapper.apply_transform("test@example.com", "lowercase") == "test@example.com"
        assert self.mapper.apply_transform("test@example.com", "uppercase") == "TEST@EXAMPLE.COM"
        assert self.mapper.apply_transform(" test ", "strip") == "test"
        assert self.mapper.apply_transform(None, "default_empty_string") == ""
        assert self.mapper.apply_transform(None, "default_zero") == 0
        assert self.mapper.apply_transform("", "none_if_empty") is None
        
        # Test timestamp conversion (approximately)
        iso_date = "2023-01-01T12:00:00Z"
        timestamp = self.mapper.apply_transform(iso_date, "iso_to_timestamp")
        assert isinstance(timestamp, int)
        assert datetime.fromtimestamp(timestamp).year == 2023
        assert datetime.fromtimestamp(timestamp).month == 1
        assert datetime.fromtimestamp(timestamp).day == 1

    def test_register_custom_transformer(self):
        """Test registering a custom transformer."""
        # Define custom transformer
        def reverse_string(value):
            if not value:
                return value
            return value[::-1]
        
        # Register transformer
        self.mapper.register_transformer("reverse", reverse_string)
        
        # Test transformer
        assert self.mapper.apply_transform("hello", "reverse") == "olleh"
        assert self.mapper.apply_transform(None, "reverse") is None

    def test_map_data(self):
        """Test mapping data from source to target format."""
        # Source data
        source_data = {
            "id": 123,
            "name": "Test User",
            "email": "TEST@example.com",
            "created_at": "2023-01-01T12:00:00Z",
            "address": {
                "street": "123 Main St",
                "city": "Test City"
            },
            "status": "active",
            "tags": ["Test", "User", "API"]
        }
        
        # Map data
        result = self.mapper.map_data("users", "contacts", source_data)
        
        # Verify mapping
        assert result["external_id"] == 123
        assert result["full_name"] == "Test User"
        assert result["contact"]["email"] == "TEST@example.com"
        assert isinstance(result["metadata"]["created"], int)
        assert result["location"]["street"] == "123 Main St"
        assert result["location"]["city"] == "Test City"
        assert result["account_status"] == "ACTIVE"
        assert isinstance(result["labels"], list)
        assert "test" in result["labels"]
        assert "user" in result["labels"]
        assert "api" in result["labels"]

    def test_map_data_list(self):
        """Test mapping a list of data items."""
        # Source data list
        source_data = [
            {
                "id": 1,
                "name": "User 1",
                "email": "user1@example.com"
            },
            {
                "id": 2,
                "name": "User 2",
                "email": "user2@example.com"
            }
        ]
        
        # Map data
        result = self.mapper.map_data("users", "contacts", source_data)
        
        # Verify mapping
        assert len(result) == 2
        assert result[0]["external_id"] == 1
        assert result[0]["full_name"] == "User 1"
        assert result[0]["contact"]["email"] == "user1@example.com"
        assert result[1]["external_id"] == 2
        assert result[1]["full_name"] == "User 2"
        assert result[1]["contact"]["email"] == "user2@example.com"

    def test_conditional_mapping(self):
        """Test conditional field mapping."""
        # Source data with missing status
        source_data = {
            "id": 123,
            "name": "Test User",
            "email": "test@example.com"
            # No status field
        }
        
        # Map data
        result = self.mapper.map_data("users", "contacts", source_data)
        
        # Verify mapping - account_status should not be present
        assert "account_status" not in result
        
        # Add status and map again
        source_data["status"] = "pending"
        result = self.mapper.map_data("users", "contacts", source_data)
        
        # Verify mapping - account_status should now be present and uppercase
        assert result["account_status"] == "PENDING"
