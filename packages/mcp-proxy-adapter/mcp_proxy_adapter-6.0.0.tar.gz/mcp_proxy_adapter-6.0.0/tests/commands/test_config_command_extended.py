"""
Extended tests for config command.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.config_command import ConfigCommand, ConfigResult


class TestConfigCommandExtended:
    """Extended tests for ConfigCommand."""

    def test_config_result_initialization(self):
        """Test ConfigResult initialization."""
        config = {"test": "value"}
        result = ConfigResult(config, "get", "Test message")
        
        assert result.data["config"] == config
        assert result.data["operation"] == "get"
        assert result.message == "Test message"

    def test_config_result_to_dict(self):
        """Test ConfigResult.to_dict method."""
        config = {"server.host": "localhost"}
        result = ConfigResult(config, "get")
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["data"]["config"] == config
        assert result_dict["data"]["operation"] == "get"

    def test_config_command_schema(self):
        """Test ConfigCommand.get_schema method."""
        schema = ConfigCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "operation" in schema["properties"]
        assert "path" in schema["properties"]
        assert "value" in schema["properties"]
        assert "required" in schema
        assert "operation" in schema["required"]
        assert schema["additionalProperties"] is False

    @pytest.mark.asyncio
    async def test_execute_get_all_config(self):
        """Test execute method with get operation and no path."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.get_all.return_value = {"server.host": "localhost", "server.port": 8000}
            
            result = await command.execute(operation="get")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"server.host": "localhost", "server.port": 8000}
            assert result.data["operation"] == "get"
            assert "Configuration retrieved successfully" in result.message
            mock_config.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_get_specific_config(self):
        """Test execute method with get operation and specific path."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.get.return_value = "localhost"
            
            result = await command.execute(operation="get", path="server.host")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"server.host": "localhost"}
            assert result.data["operation"] == "get"
            mock_config.get.assert_called_once_with("server.host")

    @pytest.mark.asyncio
    async def test_execute_set_config_success(self):
        """Test execute method with set operation."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            result = await command.execute(operation="set", path="server.host", value="newhost")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"server.host": "newhost"}
            assert result.data["operation"] == "set"
            assert "Configuration updated successfully" in result.message
            mock_config.set.assert_called_once_with("server.host", "newhost")
            mock_config.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_set_config_missing_path(self):
        """Test execute method with set operation but missing path."""
        command = ConfigCommand()
        
        with pytest.raises(ValueError, match="Both 'path' and 'value' are required for 'set' operation"):
            await command.execute(operation="set", value="newhost")

    @pytest.mark.asyncio
    async def test_execute_set_config_missing_value(self):
        """Test execute method with set operation but missing value."""
        command = ConfigCommand()
        
        with pytest.raises(ValueError, match="Both 'path' and 'value' are required for 'set' operation"):
            await command.execute(operation="set", path="server.host")

    @pytest.mark.asyncio
    async def test_execute_set_config_missing_both(self):
        """Test execute method with set operation but missing both path and value."""
        command = ConfigCommand()
        
        with pytest.raises(ValueError, match="Both 'path' and 'value' are required for 'set' operation"):
            await command.execute(operation="set")

    @pytest.mark.asyncio
    async def test_execute_invalid_operation(self):
        """Test execute method with invalid operation."""
        command = ConfigCommand()
        
        with pytest.raises(ValueError, match="Invalid operation: invalid. Valid operations: get, set"):
            await command.execute(operation="invalid")

    @pytest.mark.asyncio
    async def test_execute_set_config_none_value(self):
        """Test execute method with set operation and None value."""
        command = ConfigCommand()
        
        # None value should be rejected by the command
        with pytest.raises(ValueError, match="Both 'path' and 'value' are required for 'set' operation"):
            await command.execute(operation="set", path="server.host", value=None)

    @pytest.mark.asyncio
    async def test_execute_set_config_complex_value(self):
        """Test execute method with set operation and complex value."""
        command = ConfigCommand()
        complex_value = {"nested": {"key": "value"}, "array": [1, 2, 3]}
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            result = await command.execute(operation="set", path="complex.config", value=complex_value)
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"complex.config": complex_value}
            mock_config.set.assert_called_once_with("complex.config", complex_value)

    @pytest.mark.asyncio
    async def test_execute_get_config_with_none_value(self):
        """Test execute method with get operation returning None."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.get.return_value = None
            
            result = await command.execute(operation="get", path="nonexistent.key")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"nonexistent.key": None}

    @pytest.mark.asyncio
    async def test_execute_get_config_with_empty_dict(self):
        """Test execute method with get operation returning empty dict."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.get_all.return_value = {}
            
            result = await command.execute(operation="get")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {}

    @pytest.mark.asyncio
    async def test_execute_set_config_with_empty_string(self):
        """Test execute method with set operation and empty string value."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            result = await command.execute(operation="set", path="empty.value", value="")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"empty.value": ""}
            mock_config.set.assert_called_once_with("empty.value", "")

    @pytest.mark.asyncio
    async def test_execute_set_config_with_zero_value(self):
        """Test execute method with set operation and zero value."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            result = await command.execute(operation="set", path="zero.value", value=0)
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"zero.value": 0}
            mock_config.set.assert_called_once_with("zero.value", 0)

    @pytest.mark.asyncio
    async def test_execute_set_config_with_false_value(self):
        """Test execute method with set operation and False value."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            result = await command.execute(operation="set", path="false.value", value=False)
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"false.value": False}
            mock_config.set.assert_called_once_with("false.value", False)

    def test_config_command_name_and_description(self):
        """Test ConfigCommand name and description attributes."""
        assert ConfigCommand.name == "config"
        assert ConfigCommand.description == "Get or set configuration values"
        assert ConfigCommand.result_class == ConfigResult

    def test_config_result_get_schema(self):
        """Test ConfigResult.get_schema method."""
        schema = ConfigResult.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "success" in schema["properties"]
        assert "data" in schema["properties"]
        assert "message" in schema["properties"]

    @pytest.mark.asyncio
    async def test_execute_set_config_save_error(self):
        """Test execute method with set operation when save fails."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.save.side_effect = Exception("Save failed")
            
            # Save error should propagate
            with pytest.raises(Exception, match="Save failed"):
                await command.execute(operation="set", path="server.host", value="newhost")
            
            mock_config.set.assert_called_once_with("server.host", "newhost")
            mock_config.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_get_config_with_special_characters(self):
        """Test execute method with get operation and special characters in path."""
        command = ConfigCommand()
        
        with patch('mcp_proxy_adapter.commands.config_command.config_instance') as mock_config:
            mock_config.get.return_value = "special_value"
            
            result = await command.execute(operation="get", path="special.path.with.dots")
            
            assert isinstance(result, ConfigResult)
            assert result.data["config"] == {"special.path.with.dots": "special_value"}
            mock_config.get.assert_called_once_with("special.path.with.dots") 