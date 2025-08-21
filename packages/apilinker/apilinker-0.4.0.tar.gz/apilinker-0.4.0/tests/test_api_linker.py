"""
Tests for the main ApiLinker class.
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from apilinker.api_linker import ApiLinker, SyncResult


class TestApiLinker:
    """Test suite for ApiLinker class."""

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
            "schedule": {
                "type": "interval",
                "minutes": 30
            },
            "logging": {
                "level": "INFO"
            }
        }

    def test_init_with_direct_config(self):
        """Test initializing ApiLinker with direct configuration."""
        # Create ApiLinker with direct config
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0],
            schedule_config=self.sample_config["schedule"]
        )
        
        # Verify components are initialized
        assert linker.source is not None
        assert linker.target is not None
        assert len(linker.mapper.get_mappings()) == 1
        assert linker.scheduler.schedule_type == "interval"
        assert linker.scheduler.schedule_config["minutes"] == 30

    def test_init_with_config_file(self):
        """Test initializing ApiLinker with a config file."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(self.sample_config, f)
            config_path = f.name
        
        try:
            # Initialize ApiLinker with config file
            linker = ApiLinker(config_path=config_path)
            
            # Verify components are initialized
            assert linker.source is not None
            assert linker.target is not None
            assert len(linker.mapper.get_mappings()) == 1
            assert linker.scheduler.schedule_type == "interval"
            assert linker.scheduler.schedule_config["minutes"] == 30
            
        finally:
            # Clean up temporary file
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_load_config_file_not_found(self):
        """Test error handling when config file is not found."""
        # Try to load non-existent config
        with pytest.raises(FileNotFoundError):
            ApiLinker(config_path="/nonexistent/config.yaml")

    @patch("apilinker.core.connector.ApiConnector.fetch_data")
    @patch("apilinker.core.connector.ApiConnector.send_data")
    def test_sync_success(self, mock_send_data, mock_fetch_data):
        """Test successful sync operation."""
        # Mock source data
        source_data = [
            {"id": 1, "name": "User 1", "email": "user1@example.com"},
            {"id": 2, "name": "User 2", "email": "user2@example.com"}
        ]
        mock_fetch_data.return_value = source_data
        
        # Mock target response
        mock_send_data.return_value = {
            "success": True,
            "sent_count": 2,
            "results": [{"id": "t1"}, {"id": "t2"}]
        }
        
        # Create ApiLinker
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0]
        )
        
        # Run sync
        result = linker.sync()
        
        # Verify sync result
        assert isinstance(result, SyncResult)
        assert result.success is True
        assert result.count == 2
        assert len(result.errors) == 0
        
        # Verify API calls
        mock_fetch_data.assert_called_once_with("list_users", None)
        assert mock_send_data.call_count == 1

    @patch("apilinker.core.error_handling.create_error_handler")
    def test_sync_error(self, mock_create_error_handler):
        """Test error handling during sync operation."""
        # Set up complete mocking of the error handling system
        # Mock the error itself
        error = Exception("API error")
        
        # Create mock circuit breaker
        mock_cb = MagicMock()
        mock_cb.execute.return_value = (None, error)
        
        # Create mock error recovery manager
        mock_error_recovery = MagicMock()
        mock_error_recovery.get_circuit_breaker.return_value = mock_cb
        mock_error_recovery.recover.return_value = (None, error)
        
        # Create mock DLQ and analytics
        mock_dlq = MagicMock()
        mock_analytics = MagicMock()
        
        # Configure create_error_handler to return our mocks
        mock_create_error_handler.return_value = (mock_dlq, mock_error_recovery, mock_analytics)
        
        # Create ApiLinker - this will use our mocked error handling system
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0]
        )
        
        # Mock fetch_data - this is easier than mocking the whole circuit breaker flow
        linker.source = MagicMock()
        linker.source.fetch_data.side_effect = Exception("API error")
        
        # Mock error formatting to ensure consistent error format
        mock_error_dict = {
            "message": "API error", 
            "status_code": 500, 
            "error_category": "client",
            "timestamp": datetime.now().isoformat()
        }
        mock_error_recovery.format_error.return_value = mock_error_dict
        
        # Run sync
        result = linker.sync()
        
        # Verify sync result
        assert isinstance(result, SyncResult)
        assert result.success is False
        assert result.count == 0
        assert len(result.errors) == 1
        assert "API error" in result.errors[0]["message"]

    def test_sync_missing_connectors(self):
        """Test sync operation with missing connectors."""
        # Create ApiLinker without connectors
        linker = ApiLinker()
        
        # Try to sync
        with pytest.raises(ValueError, match="Source and target connectors must be configured"):
            linker.sync()

    def test_sync_missing_mapping(self):
        """Test sync operation with missing mapping."""
        # Create ApiLinker with connectors but no mapping
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"]
        )
        
        # Try to sync
        with pytest.raises(ValueError, match="No mapping configured"):
            linker.sync()

    @patch("apilinker.core.scheduler.Scheduler.start")
    def test_start_scheduled_sync(self, mock_start):
        """Test starting scheduled sync."""
        # Create ApiLinker
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0],
            schedule_config=self.sample_config["schedule"]
        )
        
        # Start scheduled sync
        linker.start_scheduled_sync()
        
        # Verify scheduler was started
        mock_start.assert_called_once()
        
        # Verify it was called with the sync method
        args, _ = mock_start.call_args
        assert args[0] == linker.sync

    @patch("apilinker.core.scheduler.Scheduler.stop")
    def test_stop_scheduled_sync(self, mock_stop):
        """Test stopping scheduled sync."""
        # Create ApiLinker
        linker = ApiLinker(
            source_config=self.sample_config["source"],
            target_config=self.sample_config["target"],
            mapping_config=self.sample_config["mapping"][0],
            schedule_config=self.sample_config["schedule"]
        )
        
        # Stop scheduled sync
        linker.stop_scheduled_sync()
        
        # Verify scheduler was stopped
        mock_stop.assert_called_once()
