"""
Extended tests for settings functionality.

This module contains additional tests for core/settings.py
to improve code coverage to 90%+.
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from mcp_proxy_adapter.core.settings import (
    Settings, ServerSettings, LoggingSettings, CommandsSettings,
    get_server_host, get_server_port, get_server_debug, get_logging_level,
    get_logging_dir, get_auto_discovery, get_discovery_path,
    get_setting, set_setting, reload_settings,
    add_custom_settings, get_custom_settings, get_custom_setting_value,
    set_custom_setting_value, clear_custom_settings
)


class TestSettingsExtended:
    """Extended tests for Settings class."""

    def test_add_custom_settings_new_settings(self):
        """Test add_custom_settings with new settings."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        new_settings = {"feature_enabled": True, "max_retries": 3}
        Settings.add_custom_settings(new_settings)
        
        custom_settings = Settings.get_custom_settings()
        assert custom_settings["feature_enabled"] is True
        assert custom_settings["max_retries"] == 3

    def test_add_custom_settings_merge_existing(self):
        """Test add_custom_settings merges with existing settings."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        # Add initial settings
        initial_settings = {"feature_enabled": True, "max_retries": 3}
        Settings.add_custom_settings(initial_settings)
        
        # Add additional settings
        additional_settings = {"timeout": 30, "feature_enabled": False}
        Settings.add_custom_settings(additional_settings)
        
        custom_settings = Settings.get_custom_settings()
        assert custom_settings["feature_enabled"] is False  # Should be overwritten
        assert custom_settings["max_retries"] == 3
        assert custom_settings["timeout"] == 30

    def test_get_custom_setting_value_simple_key(self):
        """Test get_custom_setting_value with simple key."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        # Add custom setting
        Settings.add_custom_settings({"test_key": "test_value"})
        
        value = Settings.get_custom_setting_value("test_key")
        assert value == "test_value"

    def test_get_custom_setting_value_with_default(self):
        """Test get_custom_setting_value with default value."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        value = Settings.get_custom_setting_value("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_set_custom_setting_value_success(self):
        """Test set_custom_setting_value success."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        Settings.set_custom_setting_value("new_key", "new_value")
        
        value = Settings.get_custom_setting_value("new_key")
        assert value == "new_value"

    def test_set_custom_setting_value_overwrite(self):
        """Test set_custom_setting_value overwrites existing value."""
        # Clear any existing custom settings
        Settings.clear_custom_settings()
        
        # Set initial value
        Settings.set_custom_setting_value("test_key", "initial_value")
        
        # Overwrite value
        Settings.set_custom_setting_value("test_key", "new_value")
        
        value = Settings.get_custom_setting_value("test_key")
        assert value == "new_value"

    def test_clear_custom_settings(self):
        """Test clear_custom_settings removes all custom settings."""
        # Add some custom settings
        Settings.add_custom_settings({"key1": "value1", "key2": "value2"})
        
        # Verify settings exist
        assert Settings.get_custom_setting_value("key1") == "value1"
        assert Settings.get_custom_setting_value("key2") == "value2"
        
        # Clear settings
        Settings.clear_custom_settings()
        
        # Verify settings are removed
        assert Settings.get_custom_setting_value("key1") is None
        assert Settings.get_custom_setting_value("key2") is None

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_server_settings(self, mock_config):
        """Test get_server_settings."""
        mock_config.get.side_effect = lambda key, default=None: {
            "server.host": "127.0.0.1",
            "server.port": 9000,
            "server.debug": True,
            "server.log_level": "DEBUG"
        }.get(key, default)
        
        settings = Settings.get_server_settings()
        
        assert settings["host"] == "127.0.0.1"
        assert settings["port"] == 9000
        assert settings["debug"] is True
        assert settings["log_level"] == "DEBUG"

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_logging_settings(self, mock_config):
        """Test get_logging_settings."""
        mock_config.get.side_effect = lambda key, default=None: {
            "logging.level": "DEBUG",
            "logging.file": "test.log",
            "logging.log_dir": "/tmp/logs",
            "logging.log_file": "app.log",
            "logging.error_log_file": "error.log",
            "logging.access_log_file": "access.log",
            "logging.max_file_size": "20MB",
            "logging.backup_count": 10,
            "logging.format": "custom format",
            "logging.date_format": "custom date",
            "logging.console_output": False,
            "logging.file_output": False
        }.get(key, default)
        
        settings = Settings.get_logging_settings()
        
        assert settings["level"] == "DEBUG"
        assert settings["file"] == "test.log"
        assert settings["log_dir"] == "/tmp/logs"
        assert settings["log_file"] == "app.log"
        assert settings["error_log_file"] == "error.log"
        assert settings["access_log_file"] == "access.log"
        assert settings["max_file_size"] == "20MB"
        assert settings["backup_count"] == 10
        assert settings["format"] == "custom format"
        assert settings["date_format"] == "custom date"
        assert settings["console_output"] is False
        assert settings["file_output"] is False

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_commands_settings(self, mock_config):
        """Test get_commands_settings."""
        mock_config.get.side_effect = lambda key, default=None: {
            "commands.auto_discovery": False,
            "commands.discovery_path": "custom.commands",
            "commands.custom_commands_path": "/custom/path"
        }.get(key, default)
        
        settings = Settings.get_commands_settings()
        
        assert settings["auto_discovery"] is False
        assert settings["discovery_path"] == "custom.commands"
        assert settings["custom_commands_path"] == "/custom/path"

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_custom_setting(self, mock_config):
        """Test get_custom_setting."""
        mock_config.get.return_value = "custom_value"
        
        value = Settings.get_custom_setting("custom.key", "default_value")
        
        assert value == "custom_value"
        mock_config.get.assert_called_once_with("custom.key", "default_value")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_all_settings(self, mock_config):
        """Test get_all_settings."""
        mock_config.get_all.return_value = {"server": {"host": "localhost"}}
        
        # Add some custom settings
        Settings.add_custom_settings({"custom_key": "custom_value"})
        
        all_settings = Settings.get_all_settings()
        
        assert "server" in all_settings
        assert all_settings["server"]["host"] == "localhost"
        assert "custom_settings" in all_settings
        assert all_settings["custom_settings"]["custom_key"] == "custom_value"

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_set_custom_setting(self, mock_config):
        """Test set_custom_setting."""
        Settings.set_custom_setting("test.key", "test_value")
        
        mock_config.set.assert_called_once_with("test.key", "test_value")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_reload_config(self, mock_config):
        """Test reload_config."""
        Settings.reload_config()
        
        mock_config.load_config.assert_called_once()


class TestServerSettingsExtended:
    """Extended tests for ServerSettings class."""

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_host_custom(self, mock_config):
        """Test get_host with custom value."""
        mock_config.get.return_value = "192.168.1.1"
        
        host = ServerSettings.get_host()
        
        assert host == "192.168.1.1"
        mock_config.get.assert_called_once_with("server.host", "0.0.0.0")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_port_custom(self, mock_config):
        """Test get_port with custom value."""
        mock_config.get.return_value = 9000
        
        port = ServerSettings.get_port()
        
        assert port == 9000
        mock_config.get.assert_called_once_with("server.port", 8000)

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_debug_custom(self, mock_config):
        """Test get_debug with custom value."""
        mock_config.get.return_value = True
        
        debug = ServerSettings.get_debug()
        
        assert debug is True
        mock_config.get.assert_called_once_with("server.debug", False)

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_log_level_custom(self, mock_config):
        """Test get_log_level with custom value."""
        mock_config.get.return_value = "DEBUG"
        
        log_level = ServerSettings.get_log_level()
        
        assert log_level == "DEBUG"
        mock_config.get.assert_called_once_with("server.log_level", "INFO")


class TestLoggingSettingsExtended:
    """Extended tests for LoggingSettings class."""

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_level_custom(self, mock_config):
        """Test get_level with custom value."""
        mock_config.get.return_value = "DEBUG"
        
        level = LoggingSettings.get_level()
        
        assert level == "DEBUG"
        mock_config.get.assert_called_once_with("logging.level", "INFO")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_log_dir_custom(self, mock_config):
        """Test get_log_dir with custom value."""
        mock_config.get.return_value = "/custom/logs"
        
        log_dir = LoggingSettings.get_log_dir()
        
        assert log_dir == "/custom/logs"
        mock_config.get.assert_called_once_with("logging.log_dir", "./logs")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_log_file_custom(self, mock_config):
        """Test get_log_file with custom value."""
        mock_config.get.return_value = "custom.log"
        
        log_file = LoggingSettings.get_log_file()
        
        assert log_file == "custom.log"
        mock_config.get.assert_called_once_with("logging.log_file", "mcp_proxy_adapter.log")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_error_log_file_custom(self, mock_config):
        """Test get_error_log_file with custom value."""
        mock_config.get.return_value = "custom_error.log"
        
        error_log_file = LoggingSettings.get_error_log_file()
        
        assert error_log_file == "custom_error.log"
        mock_config.get.assert_called_once_with("logging.error_log_file", "mcp_proxy_adapter_error.log")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_access_log_file_custom(self, mock_config):
        """Test get_access_log_file with custom value."""
        mock_config.get.return_value = "custom_access.log"
        
        access_log_file = LoggingSettings.get_access_log_file()
        
        assert access_log_file == "custom_access.log"
        mock_config.get.assert_called_once_with("logging.access_log_file", "mcp_proxy_adapter_access.log")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_max_file_size_custom(self, mock_config):
        """Test get_max_file_size with custom value."""
        mock_config.get.return_value = "50MB"
        
        max_file_size = LoggingSettings.get_max_file_size()
        
        assert max_file_size == "50MB"
        mock_config.get.assert_called_once_with("logging.max_file_size", "10MB")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_backup_count_custom(self, mock_config):
        """Test get_backup_count with custom value."""
        mock_config.get.return_value = 10
        
        backup_count = LoggingSettings.get_backup_count()
        
        assert backup_count == 10
        mock_config.get.assert_called_once_with("logging.backup_count", 5)

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_format_custom(self, mock_config):
        """Test get_format with custom value."""
        mock_config.get.return_value = "custom format"
        
        format_str = LoggingSettings.get_format()
        
        assert format_str == "custom format"
        mock_config.get.assert_called_once_with("logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_date_format_custom(self, mock_config):
        """Test get_date_format with custom value."""
        mock_config.get.return_value = "custom date format"
        
        date_format = LoggingSettings.get_date_format()
        
        assert date_format == "custom date format"
        mock_config.get.assert_called_once_with("logging.date_format", "%Y-%m-%d %H:%M:%S")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_console_output_custom(self, mock_config):
        """Test get_console_output with custom value."""
        mock_config.get.return_value = False
        
        console_output = LoggingSettings.get_console_output()
        
        assert console_output is False
        mock_config.get.assert_called_once_with("logging.console_output", True)

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_file_output_custom(self, mock_config):
        """Test get_file_output with custom value."""
        mock_config.get.return_value = False
        
        file_output = LoggingSettings.get_file_output()
        
        assert file_output is False
        mock_config.get.assert_called_once_with("logging.file_output", True)


class TestCommandsSettingsExtended:
    """Extended tests for CommandsSettings class."""

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_auto_discovery_custom(self, mock_config):
        """Test get_auto_discovery with custom value."""
        mock_config.get.return_value = False
        
        auto_discovery = CommandsSettings.get_auto_discovery()
        
        assert auto_discovery is False
        mock_config.get.assert_called_once_with("commands.auto_discovery", True)

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_discovery_path_custom(self, mock_config):
        """Test get_discovery_path with custom value."""
        mock_config.get.return_value = "custom.discovery.path"
        
        discovery_path = CommandsSettings.get_discovery_path()
        
        assert discovery_path == "custom.discovery.path"
        mock_config.get.assert_called_once_with("commands.discovery_path", "mcp_proxy_adapter.commands")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_custom_commands_path_custom(self, mock_config):
        """Test get_custom_commands_path with custom value."""
        mock_config.get.return_value = "/custom/commands/path"
        
        custom_commands_path = CommandsSettings.get_custom_commands_path()
        
        assert custom_commands_path == "/custom/commands/path"
        mock_config.get.assert_called_once_with("commands.custom_commands_path")

    @patch('mcp_proxy_adapter.core.settings.config')
    def test_get_custom_commands_path_none(self, mock_config):
        """Test get_custom_commands_path returns None."""
        mock_config.get.return_value = None
        
        custom_commands_path = CommandsSettings.get_custom_commands_path()
        
        assert custom_commands_path is None


class TestConvenienceFunctionsExtended:
    """Extended tests for convenience functions."""

    @patch('mcp_proxy_adapter.core.settings.ServerSettings')
    def test_get_server_host(self, mock_server_settings):
        """Test get_server_host function."""
        mock_server_settings.get_host.return_value = "127.0.0.1"
        
        host = get_server_host()
        
        assert host == "127.0.0.1"
        mock_server_settings.get_host.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.ServerSettings')
    def test_get_server_port(self, mock_server_settings):
        """Test get_server_port function."""
        mock_server_settings.get_port.return_value = 9000
        
        port = get_server_port()
        
        assert port == 9000
        mock_server_settings.get_port.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.ServerSettings')
    def test_get_server_debug(self, mock_server_settings):
        """Test get_server_debug function."""
        mock_server_settings.get_debug.return_value = True
        
        debug = get_server_debug()
        
        assert debug is True
        mock_server_settings.get_debug.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.LoggingSettings')
    def test_get_logging_level(self, mock_logging_settings):
        """Test get_logging_level function."""
        mock_logging_settings.get_level.return_value = "DEBUG"
        
        level = get_logging_level()
        
        assert level == "DEBUG"
        mock_logging_settings.get_level.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.LoggingSettings')
    def test_get_logging_dir(self, mock_logging_settings):
        """Test get_logging_dir function."""
        mock_logging_settings.get_log_dir.return_value = "/custom/logs"
        
        log_dir = get_logging_dir()
        
        assert log_dir == "/custom/logs"
        mock_logging_settings.get_log_dir.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.CommandsSettings')
    def test_get_auto_discovery(self, mock_commands_settings):
        """Test get_auto_discovery function."""
        mock_commands_settings.get_auto_discovery.return_value = False
        
        auto_discovery = get_auto_discovery()
        
        assert auto_discovery is False
        mock_commands_settings.get_auto_discovery.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.CommandsSettings')
    def test_get_discovery_path(self, mock_commands_settings):
        """Test get_discovery_path function."""
        mock_commands_settings.get_discovery_path.return_value = "custom.path"
        
        discovery_path = get_discovery_path()
        
        assert discovery_path == "custom.path"
        mock_commands_settings.get_discovery_path.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_get_setting(self, mock_settings):
        """Test get_setting function."""
        mock_settings.get_custom_setting.return_value = "test_value"
        
        value = get_setting("test.key", "default")
        
        assert value == "test_value"
        mock_settings.get_custom_setting.assert_called_once_with("test.key", "default")

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_set_setting(self, mock_settings):
        """Test set_setting function."""
        set_setting("test.key", "test_value")
        
        mock_settings.set_custom_setting.assert_called_once_with("test.key", "test_value")

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_reload_settings(self, mock_settings):
        """Test reload_settings function."""
        reload_settings()
        
        mock_settings.reload_config.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_add_custom_settings(self, mock_settings):
        """Test add_custom_settings function."""
        custom_settings = {"key": "value"}
        add_custom_settings(custom_settings)
        
        mock_settings.add_custom_settings.assert_called_once_with(custom_settings)

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_get_custom_settings(self, mock_settings):
        """Test get_custom_settings function."""
        mock_settings.get_custom_settings.return_value = {"key": "value"}
        
        settings = get_custom_settings()
        
        assert settings == {"key": "value"}
        mock_settings.get_custom_settings.assert_called_once()

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_get_custom_setting_value(self, mock_settings):
        """Test get_custom_setting_value function."""
        mock_settings.get_custom_setting_value.return_value = "test_value"
        
        value = get_custom_setting_value("test.key", "default")
        
        assert value == "test_value"
        mock_settings.get_custom_setting_value.assert_called_once_with("test.key", "default")

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_set_custom_setting_value(self, mock_settings):
        """Test set_custom_setting_value function."""
        set_custom_setting_value("test.key", "test_value")
        
        mock_settings.set_custom_setting_value.assert_called_once_with("test.key", "test_value")

    @patch('mcp_proxy_adapter.core.settings.Settings')
    def test_clear_custom_settings(self, mock_settings):
        """Test clear_custom_settings function."""
        clear_custom_settings()
        
        mock_settings.clear_custom_settings.assert_called_once() 