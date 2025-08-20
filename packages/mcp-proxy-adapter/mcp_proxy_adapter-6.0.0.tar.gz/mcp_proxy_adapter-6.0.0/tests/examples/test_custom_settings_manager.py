"""
Tests for custom settings manager example.

This module tests the custom settings manager functionality including:
- Settings loading from file
- Default settings fallback
- Settings validation
- Settings access methods
- Convenience functions
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open

from mcp_proxy_adapter.examples.custom_commands import custom_settings_manager


class TestCustomSettingsManager:
    """Test CustomSettingsManager class."""

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.add_custom_settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.os.path.exists')
    def test_init_with_existing_file(self, mock_exists, mock_add_custom_settings, mock_get_logger):
        """Test initialization with existing config file."""
        # Setup mocks
        mock_exists.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        test_settings = {
            "application": {"name": "Test App", "version": "1.0.0"},
            "features": {"test_feature": True}
        }
        
        with patch('builtins.open', mock_open(read_data=json.dumps(test_settings))):
            manager = custom_settings_manager.CustomSettingsManager("test_config.json")
        
        assert manager.config_file == "test_config.json"
        mock_add_custom_settings.assert_called_once_with(test_settings)
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.add_custom_settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.os.path.exists')
    def test_init_without_file(self, mock_exists, mock_add_custom_settings, mock_get_logger):
        """Test initialization without config file."""
        # Setup mocks
        mock_exists.return_value = False
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        manager = custom_settings_manager.CustomSettingsManager("nonexistent.json")
        
        assert manager.config_file == "nonexistent.json"
        mock_add_custom_settings.assert_called_once()
        mock_logger.warning.assert_called()
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.add_custom_settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.os.path.exists')
    def test_init_with_file_error(self, mock_exists, mock_add_custom_settings, mock_get_logger):
        """Test initialization with file reading error."""
        # Setup mocks
        mock_exists.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch('builtins.open', side_effect=Exception("File error")):
            manager = custom_settings_manager.CustomSettingsManager("error_config.json")
        
        assert manager.config_file == "error_config.json"
        mock_add_custom_settings.assert_called_once()
        mock_logger.error.assert_called()
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_application_name(self, mock_get_custom_setting_value):
        """Test get_application_name method."""
        mock_get_custom_setting_value.return_value = "Test App"
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_application_name()
        
        assert result == "Test App"
        mock_get_custom_setting_value.assert_called_once_with("application.name", "Extended MCP Proxy Server")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_application_version(self, mock_get_custom_setting_value):
        """Test get_application_version method."""
        mock_get_custom_setting_value.return_value = "2.1.0"
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_application_version()
        
        assert result == "2.1.0"
        mock_get_custom_setting_value.assert_called_once_with("application.version", "2.0.0")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_environment(self, mock_get_custom_setting_value):
        """Test get_environment method."""
        mock_get_custom_setting_value.return_value = "production"
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_environment()
        
        assert result == "production"
        mock_get_custom_setting_value.assert_called_once_with("application.environment", "development")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_is_feature_enabled_true(self, mock_get_custom_setting_value):
        """Test is_feature_enabled method with enabled feature."""
        mock_get_custom_setting_value.return_value = True
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.is_feature_enabled("test_feature")
        
        assert result is True
        mock_get_custom_setting_value.assert_called_once_with("features.test_feature", False)

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_is_feature_enabled_false(self, mock_get_custom_setting_value):
        """Test is_feature_enabled method with disabled feature."""
        mock_get_custom_setting_value.return_value = False
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.is_feature_enabled("test_feature")
        
        assert result is False
        mock_get_custom_setting_value.assert_called_once_with("features.test_feature", False)

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_security_setting(self, mock_get_custom_setting_value):
        """Test get_security_setting method."""
        mock_get_custom_setting_value.return_value = "enabled"
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_security_setting("auth_mode", "disabled")
        
        assert result == "enabled"
        mock_get_custom_setting_value.assert_called_once_with("security.auth_mode", "disabled")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_monitoring_setting(self, mock_get_custom_setting_value):
        """Test get_monitoring_setting method."""
        mock_get_custom_setting_value.return_value = 60
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_monitoring_setting("interval", 30)
        
        assert result == 60
        mock_get_custom_setting_value.assert_called_once_with("monitoring.interval", 30)

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_custom_command_setting(self, mock_get_custom_setting_value):
        """Test get_custom_command_setting method."""
        mock_get_custom_setting_value.return_value = 1000
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_custom_command_setting("echo", "max_length", 500)
        
        assert result == 1000
        mock_get_custom_setting_value.assert_called_once_with("custom_commands.echo.max_length", 500)

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.set_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    def test_set_custom_setting(self, mock_get_logger, mock_set_custom_setting_value):
        """Test set_custom_setting method."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        manager = custom_settings_manager.CustomSettingsManager()
        manager.set_custom_setting("test.key", "test_value")
        
        mock_set_custom_setting_value.assert_called_once_with("test.key", "test_value")
        # The logger is called twice: once during init and once during set_custom_setting
        assert mock_logger.info.call_count == 2

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_settings')
    def test_get_all_custom_settings(self, mock_get_custom_settings):
        """Test get_all_custom_settings method."""
        test_settings = {"app": {"name": "Test"}, "features": {"enabled": True}}
        mock_get_custom_settings.return_value = test_settings
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.get_all_custom_settings()
        
        assert result == test_settings
        mock_get_custom_settings.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    def test_reload_settings(self, mock_get_logger):
        """Test reload_settings method."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.object(custom_settings_manager.CustomSettingsManager, '_load_custom_settings') as mock_load:
            manager = custom_settings_manager.CustomSettingsManager()
            manager.reload_settings()
        
        # _load_custom_settings is called twice: once during init and once during reload
        assert mock_load.call_count == 2
        assert mock_logger.info.call_count == 2

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_validate_settings_valid(self, mock_get_custom_setting_value):
        """Test validate_settings method with valid settings."""
        # Mock all the calls that validate_settings makes
        mock_get_custom_setting_value.side_effect = [
            "Test App",  # application.name
            "1.0.0",     # application.version
            True,        # features.advanced_hooks
            True,        # features.data_transformation
            True,        # features.custom_commands
            True,        # security.enable_authentication
            True         # security.rate_limiting.enabled
        ]
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.validate_settings()
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_validate_settings_missing_required(self, mock_get_custom_setting_value):
        """Test validate_settings method with missing required settings."""
        # Mock all the calls that validate_settings makes
        mock_get_custom_setting_value.side_effect = [
            None,        # application.name (missing)
            "1.0.0",     # application.version
            True,        # features.advanced_hooks
            True,        # features.data_transformation
            True,        # features.custom_commands
            True,        # security.enable_authentication
            True         # security.rate_limiting.enabled
        ]
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.validate_settings()
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_validate_settings_with_warnings(self, mock_get_custom_setting_value):
        """Test validate_settings method with warnings."""
        mock_get_custom_setting_value.side_effect = ["Test App", "1.0.0", True, True, False, True, False]
        
        manager = custom_settings_manager.CustomSettingsManager()
        result = manager.validate_settings()
        
        assert result["valid"] is True
        assert len(result["warnings"]) > 0

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_logger')
    def test_print_settings_summary(self, mock_get_logger, mock_get_custom_setting_value):
        """Test print_settings_summary method."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_get_custom_setting_value.side_effect = [
            "Test App", "2.0.0", "production",  # application settings
            True, True, True, False,  # features
            False, False,  # security
            True  # monitoring
        ]
        
        manager = custom_settings_manager.CustomSettingsManager()
        manager.print_settings_summary()
        
        assert mock_logger.info.call_count >= 5


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_app_name(self, mock_get_custom_setting_value):
        """Test get_app_name function."""
        mock_get_custom_setting_value.return_value = "Test App"
        
        result = custom_settings_manager.get_app_name()
        
        assert result == "Test App"
        mock_get_custom_setting_value.assert_called_once_with("application.name", "Extended MCP Proxy Server")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_is_feature_enabled_function(self, mock_get_custom_setting_value):
        """Test is_feature_enabled function."""
        mock_get_custom_setting_value.return_value = True
        
        result = custom_settings_manager.is_feature_enabled("test_feature")
        
        assert result is True
        mock_get_custom_setting_value.assert_called_once_with("features.test_feature", False)

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_security_setting_function(self, mock_get_custom_setting_value):
        """Test get_security_setting function."""
        mock_get_custom_setting_value.return_value = "enabled"
        
        result = custom_settings_manager.get_security_setting("auth_mode", "disabled")
        
        assert result == "enabled"
        mock_get_custom_setting_value.assert_called_once_with("security.auth_mode", "disabled")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_settings_manager.get_custom_setting_value')
    def test_get_monitoring_setting_function(self, mock_get_custom_setting_value):
        """Test get_monitoring_setting function."""
        mock_get_custom_setting_value.return_value = 60
        
        result = custom_settings_manager.get_monitoring_setting("interval", 30)
        
        assert result == 60
        mock_get_custom_setting_value.assert_called_once_with("monitoring.interval", 30)


class TestDefaultSettings:
    """Test default settings functionality."""

    def test_get_default_settings_structure(self):
        """Test that default settings have the expected structure."""
        with patch.object(custom_settings_manager.CustomSettingsManager, '_load_custom_settings'):
            manager = custom_settings_manager.CustomSettingsManager()
            default_settings = manager._get_default_settings()
        
        # Check required top-level keys
        assert "application" in default_settings
        assert "features" in default_settings
        assert "security" in default_settings
        assert "monitoring" in default_settings
        assert "custom_commands" in default_settings
        
        # Check application settings
        assert "name" in default_settings["application"]
        assert "version" in default_settings["application"]
        assert "environment" in default_settings["application"]
        
        # Check features
        assert "advanced_hooks" in default_settings["features"]
        assert "custom_commands" in default_settings["features"]
        assert "data_transformation" in default_settings["features"]
        assert "command_interception" in default_settings["features"]
        assert "performance_monitoring" in default_settings["features"]
        
        # Check security settings
        assert "enable_authentication" in default_settings["security"]
        assert "max_request_size" in default_settings["security"]
        assert "rate_limiting" in default_settings["security"]
        
        # Check monitoring settings
        assert "enable_metrics" in default_settings["monitoring"]
        assert "metrics_interval" in default_settings["monitoring"]
        assert "health_check_interval" in default_settings["monitoring"]
        
        # Check custom commands settings
        assert "auto_echo" in default_settings["custom_commands"]
        assert "data_transform" in default_settings["custom_commands"]
        assert "intercept" in default_settings["custom_commands"] 