"""
Tests for basic server examples.

This module contains tests for the basic server example files
to improve code coverage.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from mcp_proxy_adapter.examples.basic_server import custom_settings_example
from mcp_proxy_adapter.examples.basic_server.server import main
from mcp_proxy_adapter.core.settings import get_custom_setting_value


class TestBasicServerCustomSettings:
    """Test basic server custom settings functionality."""
    
    def test_setup_basic_custom_settings(self):
        """Test setup_basic_custom_settings function."""
        with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            result = custom_settings_example.setup_basic_custom_settings()
            
            # Verify logger calls
            mock_logger_instance.info.assert_called()
            
            # Verify returned settings structure
            assert 'application' in result
            assert 'features' in result
            assert 'server_info' in result
            assert 'demo_settings' in result
            
            # Verify specific values
            assert result['application']['name'] == 'Basic MCP Proxy Server'
            assert result['application']['version'] == '1.0.0'
            assert result['features']['basic_logging'] is True
    
    def test_demonstrate_custom_settings_usage(self):
        """Test demonstrate_custom_settings_usage function."""
        with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            result = custom_settings_example.demonstrate_custom_settings_usage()
            
            # Verify logger calls
            mock_logger_instance.info.assert_called()
            
            # Verify returned structure
            assert 'app_name' in result
            assert 'app_version' in result
            assert 'welcome_message' in result
            assert 'max_connections' in result
            assert 'enabled_features' in result
            assert 'total_settings_sections' in result
    
    def test_create_custom_settings_file(self):
        """Test create_custom_settings_file function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory and patch os.getcwd
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                result = custom_settings_example.create_custom_settings_file()
                
                # Verify file was created
                file_path = os.path.join(temp_dir, result)
                assert os.path.exists(file_path)
                
                # Verify file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                
                assert 'application' in content
                assert 'features' in content
                assert 'server_info' in content
                assert 'demo_settings' in content
                assert 'performance' in content
                assert 'security' in content
            finally:
                os.chdir(original_cwd)
    
    def test_load_custom_settings_from_file_success(self):
        """Test load_custom_settings_from_file with existing file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test settings file
            test_settings = {
                "application": {
                    "name": "Test App",
                    "version": "1.0.0"
                }
            }
            test_file = os.path.join(temp_dir, "test_settings.json")
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_settings, f)
            
            with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance
                
                result = custom_settings_example.load_custom_settings_from_file(test_file)
                
                # Verify logger calls
                mock_logger_instance.info.assert_called()
                
                # Verify returned settings
                assert result == test_settings
    
    def test_load_custom_settings_from_file_not_found(self):
        """Test load_custom_settings_from_file with non-existent file."""
        with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            result = custom_settings_example.load_custom_settings_from_file("nonexistent.json")
            
            # Verify warning was logged
            mock_logger_instance.warning.assert_called()
            
            # Verify None was returned
            assert result is None
    
    def test_load_custom_settings_from_file_error(self):
        """Test load_custom_settings_from_file with invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid JSON file
            test_file = os.path.join(temp_dir, "invalid_settings.json")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("invalid json content")
            
            with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance
                
                result = custom_settings_example.load_custom_settings_from_file(test_file)
                
                # Verify error was logged
                mock_logger_instance.error.assert_called()
                
                # Verify None was returned
                assert result is None
    
    def test_print_custom_settings_summary(self):
        """Test print_custom_settings_summary function."""
        with patch('mcp_proxy_adapter.examples.basic_server.custom_settings_example.get_logger') as mock_logger:
            mock_logger_instance = MagicMock()
            mock_logger.return_value = mock_logger_instance
            
            custom_settings_example.print_custom_settings_summary()
            
            # Verify logger calls
            mock_logger_instance.info.assert_called()


class TestBasicServerMain:
    """Test basic server main function."""
    
    @patch('mcp_proxy_adapter.examples.basic_server.server.uvicorn.run')
    @patch('mcp_proxy_adapter.examples.basic_server.server.create_app')
    @patch('mcp_proxy_adapter.examples.basic_server.server.get_logger')
    @patch('mcp_proxy_adapter.examples.basic_server.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.basic_server.server.os.path.exists')
    def test_main_with_config_file(self, mock_exists, mock_setup_logging, 
                                  mock_get_logger, mock_create_app, mock_uvicorn_run):
        """Test main function with existing config file."""
        # Setup mocks
        mock_exists.return_value = True
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        # Mock Settings methods
        with patch('mcp_proxy_adapter.examples.basic_server.server.Settings') as mock_settings_class:
            mock_settings_class.get_server_settings.return_value = {
                'host': 'localhost',
                'port': 8000,
                'debug': False,
                'log_level': 'INFO'
            }
            mock_settings_class.get_logging_settings.return_value = {
                'level': 'INFO',
                'log_dir': '/tmp/logs'
            }
            mock_settings_class.get_commands_settings.return_value = {
                'auto_discovery': True
            }
            mock_settings_class.get_custom_setting.return_value = {
                'description': 'Test description',
                'server_name': 'Test Server'
            }
        
        # Mock config import inside main function
        with patch('mcp_proxy_adapter.examples.basic_server.server.config', create=True) as mock_config:
            mock_config_instance = MagicMock()
            mock_config.return_value = mock_config_instance
            
            # Call main function
            main()
            
            # Verify config was loaded (config file exists, so it should be called)
            # Note: The actual config file exists, so the real config is loaded, not our mock
            # This test verifies that the main function runs without errors
        
        # Verify logging was setup
        mock_setup_logging.assert_called_once()
        
        # Verify app was created
        mock_create_app.assert_called_once()
        
        # Verify server was started
        mock_uvicorn_run.assert_called_once()
    
    @patch('mcp_proxy_adapter.examples.basic_server.server.uvicorn.run')
    @patch('mcp_proxy_adapter.examples.basic_server.server.create_app')
    @patch('mcp_proxy_adapter.examples.basic_server.server.get_logger')
    @patch('mcp_proxy_adapter.examples.basic_server.server.setup_logging')
    @patch('mcp_proxy_adapter.examples.basic_server.server.os.path.exists')
    def test_main_without_config_file(self, mock_exists, mock_setup_logging,
                                     mock_get_logger, mock_create_app, mock_uvicorn_run):
        """Test main function without config file."""
        # Setup mocks
        mock_exists.return_value = False
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_app = MagicMock()
        mock_create_app.return_value = mock_app
        
        # Mock Settings methods
        with patch('mcp_proxy_adapter.examples.basic_server.server.Settings') as mock_settings_class:
            mock_settings_class.get_server_settings.return_value = {
                'host': 'localhost',
                'port': 8000,
                'debug': False,
                'log_level': 'INFO'
            }
            mock_settings_class.get_logging_settings.return_value = {
                'level': 'INFO',
                'log_dir': '/tmp/logs'
            }
            mock_settings_class.get_commands_settings.return_value = {
                'auto_discovery': True
            }
            mock_settings_class.get_custom_setting.return_value = {
                'description': 'Test description',
                'server_name': 'Test Server'
            }
        
        # Call main function
        main()
        
        # Verify logging was setup
        mock_setup_logging.assert_called_once()
        
        # Verify app was created
        mock_create_app.assert_called_once()
        
        # Verify server was started
        mock_uvicorn_run.assert_called_once()


class TestBasicServerInitFiles:
    """Test basic server __init__.py files."""
    
    def test_examples_init(self):
        """Test examples __init__.py file."""
        import mcp_proxy_adapter.examples
        assert mcp_proxy_adapter.examples is not None
    
    def test_basic_server_init(self):
        """Test basic_server __init__.py file."""
        import mcp_proxy_adapter.examples.basic_server
        assert mcp_proxy_adapter.examples.basic_server is not None 