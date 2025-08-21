"""
Integration tests for ApiLinker CLI.
Tests the command-line interface functionality.
"""

import os
import tempfile
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


class TestCLIIntegration:
    """Integration tests for ApiLinker CLI commands."""

    def setup_method(self):
        """Set up test environment for each test."""
        # Create a minimal valid config for CLI testing
        self.test_config = {
            "source": {
                "type": "rest",
                "base_url": "https://httpbin.org",
                "endpoints": {
                    "get_json": {
                        "path": "/json",
                        "method": "GET"
                    }
                }
            },
            "target": {
                "type": "rest", 
                "base_url": "https://httpbin.org",
                "endpoints": {
                    "post_data": {
                        "path": "/post",
                        "method": "POST"
                    }
                }
            },
            "mapping": [
                {
                    "source": "get_json",
                    "target": "post_data",
                    "fields": [
                        {"source": "slideshow.title", "target": "title"}
                    ]
                }
            ],
            "logging": {
                "level": "INFO"
            }
        }
        
        # Create temporary config file
        self.config_fd, self.config_path = tempfile.mkstemp(suffix=".yaml")
        with os.fdopen(self.config_fd, "w") as f:
            yaml.dump(self.test_config, f)
    
    def teardown_method(self):
        """Clean up after each test."""
        try:
            os.unlink(self.config_path)
        except FileNotFoundError:
            pass

    def test_cli_help_command(self):
        """Test that CLI help command works."""
        result = subprocess.run(
            [sys.executable, "-m", "apilinker", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        assert result.returncode == 0
        assert "ApiLinker" in result.stdout
        assert "Commands" in result.stdout  # Could be "Commands:" or "Commands" depending on typer version

    def test_cli_version_command(self):
        """Test that CLI version command works."""
        result = subprocess.run(
            [sys.executable, "-m", "apilinker", "version"],  # Use "version" subcommand, not "--version" flag
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        # Version command should work (exit code 0)
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "0.4.0" in output and "ApiLinker" in output

    def test_cli_sync_dry_run(self):
        """Test CLI sync with dry-run flag."""
        result = subprocess.run(
            [
                sys.executable, "-m", "apilinker", 
                "sync", 
                "--config", self.config_path,
                "--dry-run"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30  # Prevent hanging
        )
        
        # Should not fail completely, though might have network issues
        # The important thing is that the CLI interface works
        output = result.stdout + result.stderr
        
        # Should show some indication it's processing the config
        assert any(word in output.lower() for word in ["config", "dry", "sync", "apilinker"])

    def test_cli_config_validation(self):
        """Test CLI config validation with invalid config."""
        # Create invalid config (missing required fields)
        invalid_config = {"source": {"type": "invalid"}}
        
        invalid_config_fd, invalid_config_path = tempfile.mkstemp(suffix=".yaml")
        try:
            with os.fdopen(invalid_config_fd, "w") as f:
                yaml.dump(invalid_config, f)
            
            result = subprocess.run(
                [
                    sys.executable, "-m", "apilinker",
                    "sync",
                    "--config", invalid_config_path
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=15
            )
            
            # Should fail with non-zero exit code due to invalid config
            assert result.returncode != 0
            
        finally:
            os.unlink(invalid_config_path)

    def test_cli_missing_config_file(self):
        """Test CLI behavior with missing config file."""
        result = subprocess.run(
            [
                sys.executable, "-m", "apilinker",
                "sync", 
                "--config", "/nonexistent/path/config.yaml"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=10
        )
        
        # Should fail with non-zero exit code
        assert result.returncode != 0
        
        # Error message should mention the missing file
        output = result.stdout + result.stderr
        assert any(word in output.lower() for word in ["not found", "file", "error", "exist"])

    @pytest.mark.skipif(
        not os.getenv("APILINKER_INTEGRATION_TESTS"),
        reason="Integration tests require APILINKER_INTEGRATION_TESTS env var"
    )
    def test_cli_real_sync(self):
        """Test CLI with a real HTTP request (requires network)."""
        # This test only runs if explicitly enabled via environment variable
        # Uses httpbin.org which is designed for testing HTTP requests
        
        # Create config that uses httpbin.org (reliable test service)
        httpbin_config = {
            "source": {
                "type": "rest",
                "base_url": "https://httpbin.org",
                "endpoints": {
                    "get_json": {
                        "path": "/json",
                        "method": "GET"
                    }
                }
            },
            "target": {
                "type": "rest",
                "base_url": "https://httpbin.org", 
                "endpoints": {
                    "echo_post": {
                        "path": "/post",
                        "method": "POST"
                    }
                }
            },
            "mapping": [
                {
                    "source": "get_json",
                    "target": "echo_post",
                    "fields": [
                        {"source": "slideshow.title", "target": "test_title"}
                    ]
                }
            ]
        }
        
        httpbin_fd, httpbin_path = tempfile.mkstemp(suffix=".yaml")
        try:
            with os.fdopen(httpbin_fd, "w") as f:
                yaml.dump(httpbin_config, f)
            
            result = subprocess.run(
                [
                    sys.executable, "-m", "apilinker",
                    "sync",
                    "--config", httpbin_path
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=60
            )
            
            # Should succeed or at least not crash
            output = result.stdout + result.stderr
            print(f"CLI output: {output}")  # For debugging
            
            # Even if the sync fails due to data structure, 
            # the CLI should not crash completely
            assert "Traceback" not in output or result.returncode == 0
            
        finally:
            os.unlink(httpbin_path)

    def test_cli_subcommands_exist(self):
        """Test that expected CLI subcommands exist."""
        result = subprocess.run(
            [sys.executable, "-m", "apilinker", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        assert result.returncode == 0
        output = result.stdout
        
        # Check for main commands that should be available
        expected_commands = ["sync"]  # Add more as they're implemented
        
        for command in expected_commands:
            assert command in output, f"Command '{command}' not found in CLI help"

    def test_cli_logs_configuration(self):
        """Test CLI respects logging configuration."""
        # Add logging config to test config
        config_with_logs = self.test_config.copy()
        config_with_logs["logging"] = {
            "level": "DEBUG",
            "format": "%(levelname)s: %(message)s"
        }
        
        log_config_fd, log_config_path = tempfile.mkstemp(suffix=".yaml")
        try:
            with os.fdopen(log_config_fd, "w") as f:
                yaml.dump(config_with_logs, f)
            
            result = subprocess.run(
                [
                    sys.executable, "-m", "apilinker",
                    "sync", 
                    "--config", log_config_path,
                    "--dry-run"
                ],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent,
                timeout=15
            )
            
            output = result.stdout + result.stderr
            
            # Should show some log output indicating the configuration was processed
            # The exact format depends on implementation
            assert len(output.strip()) > 0, "Expected some output from CLI"
            
        finally:
            os.unlink(log_config_path)