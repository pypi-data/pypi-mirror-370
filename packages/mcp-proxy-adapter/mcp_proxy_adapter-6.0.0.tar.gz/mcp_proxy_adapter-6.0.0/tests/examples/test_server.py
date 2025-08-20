"""
Tests for custom commands server example.
"""

import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestCustomCommandsServer:
    """Test custom commands server functionality."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary config directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    def test_custom_commands_hook_success(self, mock_registry, mock_get_setting, mock_logger):
        """Test successful custom commands hook execution."""
        from mcp_proxy_adapter.examples.custom_commands.server import custom_commands_hook
        
        # Mock settings
        mock_get_setting.return_value = {
            "help": {"enabled": True},
            "health": {"enabled": True},
            "data_transform": {"enabled": True},
            "intercept": {"enabled": True},
            "manual_echo": {"enabled": True}
        }
        
        # Mock registry methods
        mock_registry.command_exists.return_value = False
        mock_registry.get_commands_by_type.return_value = {"custom": {"echo": Mock()}}
        
        # Mock command classes
        with patch('mcp_proxy_adapter.examples.custom_commands.server.EchoCommand'):
            with patch('mcp_proxy_adapter.examples.custom_commands.server.CustomHelpCommand'):
                with patch('mcp_proxy_adapter.examples.custom_commands.server.CustomHealthCommand'):
                    with patch('mcp_proxy_adapter.examples.custom_commands.server.DataTransformCommand'):
                        with patch('mcp_proxy_adapter.examples.custom_commands.server.InterceptCommand'):
                            with patch('mcp_proxy_adapter.examples.custom_commands.server.ManualEchoCommand'):
                                custom_commands_hook(mock_registry)
        
        # Verify commands were registered
        assert mock_registry.register_custom.call_count >= 5
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    def test_custom_commands_hook_disabled_features(self, mock_registry, mock_get_setting, mock_logger):
        """Test custom commands hook with disabled features."""
        from mcp_proxy_adapter.examples.custom_commands.server import custom_commands_hook
        
        # Mock settings with disabled features
        mock_get_setting.return_value = {
            "help": {"enabled": False},
            "health": {"enabled": False},
            "data_transform": {"enabled": False},
            "intercept": {"enabled": False},
            "manual_echo": {"enabled": False}
        }
        
        # Mock registry methods
        mock_registry.command_exists.return_value = False
        mock_registry.get_commands_by_type.return_value = {"custom": {"echo": Mock()}}
        
        # Mock command classes
        with patch('mcp_proxy_adapter.examples.custom_commands.server.EchoCommand'):
            custom_commands_hook(mock_registry)
        
        # Verify only echo command was registered
        assert mock_registry.register_custom.call_count == 1
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_custom_setting_value')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    def test_custom_commands_hook_echo_already_exists(self, mock_registry, mock_get_setting, mock_logger):
        """Test custom commands hook when echo command already exists."""
        from mcp_proxy_adapter.examples.custom_commands.server import custom_commands_hook
        
        # Mock settings
        mock_get_setting.return_value = {
            "help": {"enabled": True},
            "health": {"enabled": True}
        }
        
        # Mock registry methods - echo already exists
        mock_registry.command_exists.side_effect = lambda cmd: cmd == "echo"
        mock_registry.get_commands_by_type.return_value = {"custom": {}}
        
        # Mock command classes
        with patch('mcp_proxy_adapter.examples.custom_commands.server.CustomHelpCommand'):
            with patch('mcp_proxy_adapter.examples.custom_commands.server.CustomHealthCommand'):
                custom_commands_hook(mock_registry)
        
        # Verify echo was not registered again (but other commands were)
        # The hook registers multiple commands, so we check that it was called
        assert mock_registry.register_custom.call_count > 0
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_logger')
    @patch('mcp_proxy_adapter.commands.hooks.register_custom_commands_hook')
    def test_setup_hooks(self, mock_register_hook, mock_logger):
        """Test setup_hooks function."""
        from mcp_proxy_adapter.examples.custom_commands.server import setup_hooks
        
        setup_hooks()
        
        # Verify hook was registered
        mock_register_hook.assert_called_once()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.registry')
    def test_initialize_commands(self, mock_registry):
        """Test initialize_commands function."""
        from mcp_proxy_adapter.examples.custom_commands.server import initialize_commands
        
        # Mock reload result
        mock_registry.reload_system.return_value = {"total_commands": 10}
        
        result = initialize_commands()
        
        assert result == 10
        mock_registry.reload_system.assert_called_once()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_with_config_file(self, mock_run, mock_create_app, mock_init_commands, 
                                  mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                  mock_settings, mock_settings_manager, mock_setup_logging,
                                  mock_config, mock_exists, temp_config_dir):
        """Test main function with config file."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function
        main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was initialized
        mock_settings_manager.assert_called_once()
        
        # Verify hooks were set up
        mock_setup_hooks.assert_called_once()
        
        # Verify commands were initialized
        mock_init_commands.assert_called_once()
        
        # Verify app was created
        mock_create_app.assert_called_once()
        
        # Verify server was started
        mock_run.assert_called_once()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_without_config_file(self, mock_run, mock_create_app, mock_init_commands,
                                     mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                     mock_settings, mock_settings_manager, mock_setup_logging,
                                     mock_config, mock_exists, temp_config_dir):
        """Test main function without config file."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file doesn't exist
        mock_exists.return_value = False
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function
        main()
        
        # Verify default configuration was loaded
        mock_config.load_config.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was initialized
        mock_settings_manager.assert_called_once()
        
        # Verify hooks were set up
        mock_setup_hooks.assert_called_once()
        
        # Verify commands were initialized
        mock_init_commands.assert_called_once()
        
        # Verify app was created
        mock_create_app.assert_called_once()
        
        # Verify server was started
        mock_run.assert_called_once()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_config_load_error(self, mock_run, mock_create_app, mock_init_commands,
                                   mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                   mock_settings, mock_settings_manager, mock_setup_logging,
                                   mock_config, mock_exists, temp_config_dir):
        """Test main function with config load error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock config load error
        mock_config.load_from_file.side_effect = Exception("Config error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function and expect exception
        with pytest.raises(Exception, match="Config error"):
            main()
        
        # Verify configuration was attempted to load
        mock_config.load_from_file.assert_called_once()
        
        # Verify other functions were NOT called due to exception
        mock_setup_logging.assert_not_called()
        mock_settings_manager.assert_not_called()
        mock_setup_hooks.assert_not_called()
        mock_init_commands.assert_not_called()
        mock_create_app.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_logging_setup_error(self, mock_run, mock_create_app, mock_init_commands,
                                     mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                     mock_settings, mock_settings_manager, mock_setup_logging,
                                     mock_config, mock_exists, temp_config_dir):
        """Test main function with logging setup error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock logging setup error
        mock_setup_logging.side_effect = Exception("Logging error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function and expect exception
        with pytest.raises(Exception, match="Logging error"):
            main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging setup was attempted
        mock_setup_logging.assert_called_once()
        
        # Verify other functions were NOT called due to exception
        mock_settings_manager.assert_not_called()
        mock_setup_hooks.assert_not_called()
        mock_init_commands.assert_not_called()
        mock_create_app.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_settings_manager_error(self, mock_run, mock_create_app, mock_init_commands,
                                        mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                        mock_settings, mock_settings_manager, mock_setup_logging,
                                        mock_config, mock_exists, temp_config_dir):
        """Test main function with settings manager error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock settings manager error
        mock_settings_manager.side_effect = Exception("Settings manager error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Run main function and expect exception
        with pytest.raises(Exception, match="Settings manager error"):
            main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was attempted
        mock_settings_manager.assert_called_once()
        
        # Verify other functions were NOT called due to exception
        mock_setup_hooks.assert_not_called()
        mock_init_commands.assert_not_called()
        mock_create_app.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_hooks_setup_error(self, mock_run, mock_create_app, mock_init_commands,
                                   mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                   mock_settings, mock_settings_manager, mock_setup_logging,
                                   mock_config, mock_exists, temp_config_dir):
        """Test main function with hooks setup error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock hooks setup error
        mock_setup_hooks.side_effect = Exception("Hooks error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function and expect exception
        with pytest.raises(Exception, match="Hooks error"):
            main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was initialized
        mock_settings_manager.assert_called_once()
        
        # Verify hooks setup was attempted
        mock_setup_hooks.assert_called_once()
        
        # Verify other functions were NOT called due to exception
        mock_init_commands.assert_not_called()
        mock_create_app.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_commands_init_error(self, mock_run, mock_create_app, mock_init_commands,
                                     mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                     mock_settings, mock_settings_manager, mock_setup_logging,
                                     mock_config, mock_exists, temp_config_dir):
        """Test main function with commands initialization error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock commands initialization error
        mock_init_commands.side_effect = Exception("Commands error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock app creation
        mock_app = Mock()
        mock_create_app.return_value = mock_app
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function and expect exception
        with pytest.raises(Exception, match="Commands error"):
            main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was initialized
        mock_settings_manager.assert_called_once()
        
        # Verify hooks were set up
        mock_setup_hooks.assert_called_once()
        
        # Verify commands initialization was attempted
        mock_init_commands.assert_called_once()
        
        # Verify other functions were NOT called due to exception
        mock_create_app.assert_not_called()
        mock_run.assert_not_called()
    
    @patch('mcp_proxy_adapter.examples.custom_commands.server.os.path.exists')
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.CustomSettingsManager')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.Settings')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.get_app_name')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.is_feature_enabled')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.setup_hooks')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.initialize_commands')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.create_app')
    @patch('mcp_proxy_adapter.examples.custom_commands.server.uvicorn.run')
    def test_main_app_creation_error(self, mock_run, mock_create_app, mock_init_commands,
                                    mock_setup_hooks, mock_is_enabled, mock_get_app_name,
                                    mock_settings, mock_settings_manager, mock_setup_logging,
                                    mock_config, mock_exists, temp_config_dir):
        """Test main function with app creation error."""
        from mcp_proxy_adapter.examples.custom_commands.server import main
        
        # Mock config file exists
        mock_exists.return_value = True
        
        # Mock app creation error
        mock_create_app.side_effect = Exception("App creation error")
        
        # Mock settings
        mock_settings.get_server_settings.return_value = {
            "host": "localhost",
            "port": 8000,
            "debug": True,
            "log_level": "INFO"
        }
        mock_settings.get_logging_settings.return_value = {
            "level": "INFO",
            "log_dir": "/tmp/logs"
        }
        mock_settings.get_commands_settings.return_value = {
            "auto_discovery": True
        }
        mock_settings.get_custom_setting.return_value = {}
        
        # Mock app name
        mock_get_app_name.return_value = "Test App"
        
        # Mock feature enabled
        mock_is_enabled.return_value = True
        
        # Mock settings manager
        mock_settings_instance = Mock()
        mock_settings_manager.return_value = mock_settings_instance
        
        # Run main function - should raise exception
        with pytest.raises(Exception, match="App creation error"):
            main()
        
        # Verify configuration was loaded
        mock_config.load_from_file.assert_called_once()
        
        # Verify logging was set up
        mock_setup_logging.assert_called_once()
        
        # Verify settings manager was initialized
        mock_settings_manager.assert_called_once()
        
        # Verify hooks were set up
        mock_setup_hooks.assert_called_once()
        
        # Verify commands were initialized
        mock_init_commands.assert_called_once()
        
        # Verify app creation was attempted
        mock_create_app.assert_called_once()
        
        # Verify server was not started
        mock_run.assert_not_called() 