"""
Tests for plugins command.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_proxy_adapter.commands.plugins_command import PluginsCommand, PluginsResult


class TestPluginsResult:
    """Test PluginsResult class."""
    
    def test_init_success(self):
        """Test successful initialization."""
        result = PluginsResult(
            success=True,
            plugins_server="http://test.com",
            plugins=[{"name": "test"}],
            total_plugins=1
        )
        assert result.data["success"] is True
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["plugins"] == [{"name": "test"}]
        assert result.data["total_plugins"] == 1
        assert "error" not in result.data
        assert "Found 1 plugins from http://test.com" in result.message
    
    def test_init_error(self):
        """Test initialization with error."""
        result = PluginsResult(
            success=False,
            plugins_server="http://test.com",
            plugins=[],
            total_plugins=0,
            error="Test error"
        )
        assert result.data["success"] is False
        assert result.data["error"] == "Test error"
        assert "Failed to load plugins from http://test.com: Test error" in result.message
    
    def test_get_schema(self):
        """Test schema generation."""
        schema = PluginsResult.get_schema()
        assert "type" in schema
        assert "properties" in schema
        assert "required" in schema


class TestPluginsCommand:
    """Test PluginsCommand class."""
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_success_standard_format(self, mock_import, mock_config):
        """Test successful execution with standard format."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "plugins": [
                {
                    "name": "test_plugin",
                    "description": "Test plugin",
                    "url": "http://test.com/plugin.py",
                    "version": "1.0.0",
                    "author": "Test Author"
                }
            ]
        }
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is True
        assert result.data["plugins_server"] == "http://test.com"
        assert len(result.data["plugins"]) == 1
        assert result.data["total_plugins"] == 1
        assert result.data["plugins"][0]["name"] == "test_plugin"
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_success_direct_array_format(self, mock_import, mock_config):
        """Test successful execution with direct array format."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "name": "test_plugin",
                "description": "Test plugin",
                "url": "http://test.com/plugin.py",
                "version": "1.0.0",
                "author": "Test Author"
            }
        ]
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is True
        assert result.data["total_plugins"] == 1
        assert len(result.data["plugins"]) == 1
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_success_single_plugin_format(self, mock_import, mock_config):
        """Test successful execution with single plugin format."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "plugin": "test_plugin.py",
            "descr": "Test plugin description",
            "category": "test"
        }
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is True
        assert result.data["total_plugins"] == 1
        assert result.data["plugins"][0]["name"] == "test_plugin"
        assert result.data["plugins"][0]["description"] == "Test plugin description"
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_success_unknown_format(self, mock_import, mock_config):
        """Test successful execution with unknown format."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "plugin1": {
                "name": "test_plugin1",
                "url": "http://test.com/plugin1.py"
            },
            "plugin2": {
                "name": "test_plugin2",
                "url": "http://test.com/plugin2.py"
            }
        }
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is True
        assert result.data["total_plugins"] == 2
        assert len(result.data["plugins"]) == 2
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    async def test_execute_no_server_url(self, mock_config):
        """Test execution with no server URL configured."""
        mock_config.get.return_value = None
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert result.data["error"] == "Plugins server URL not configured"
        assert result.data["plugins_server"] == ""
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    async def test_execute_requests_not_available(self, mock_config):
        """Test execution when requests library is not available."""
        mock_config.get.return_value = "http://test.com"
        with patch('builtins.__import__', side_effect=ImportError("No module named 'requests'")):
            command = PluginsCommand()
            result = await command.execute()
            assert result.data["success"] is False
            assert result.data["error"] == "requests library not available"
            assert result.data["plugins_server"] == "http://test.com"
            assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_request_exception(self, mock_import, mock_config):
        """Test execution with request exception."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_requests.get.side_effect = Exception("Connection error")
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "Connection error" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_http_error(self, mock_import, mock_config):
        """Test execution with HTTP error."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "HTTP 404" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_json_decode_error(self, mock_import, mock_config):
        """Test execution with JSON decode error."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_requests.get.return_value = mock_response
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "Invalid JSON" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_timeout_error(self, mock_import, mock_config):
        """Test execution with timeout error."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_requests.get.side_effect = Exception("Timeout")
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "Timeout" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_connection_error(self, mock_import, mock_config):
        """Test execution with connection error."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_requests.get.side_effect = Exception("Connection refused")
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "Connection refused" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    @patch('mcp_proxy_adapter.commands.plugins_command.config_instance')
    @patch('builtins.__import__')
    async def test_execute_generic_exception(self, mock_import, mock_config):
        """Test execution with generic exception."""
        mock_config.get.return_value = "http://test.com"
        mock_requests = Mock()
        mock_requests.get.side_effect = Exception("Unknown error")
        mock_import.return_value = mock_requests
        command = PluginsCommand()
        result = await command.execute()
        assert result.data["success"] is False
        assert "Unknown error" in result.data["error"]
        assert result.data["plugins_server"] == "http://test.com"
        assert result.data["total_plugins"] == 0
    
    def test_get_metadata(self):
        """Test metadata retrieval."""
        command = PluginsCommand()
        metadata = command.get_metadata()
        assert "name" in metadata
        assert "description" in metadata
        assert "summary" in metadata
        assert "parameters" in metadata
    
    def test_generate_examples(self):
        """Test examples generation."""
        command = PluginsCommand()
        examples = command._generate_examples({})
        assert isinstance(examples, list)
        assert len(examples) > 0
        for example in examples:
            assert "command" in example
            assert "description" in example 