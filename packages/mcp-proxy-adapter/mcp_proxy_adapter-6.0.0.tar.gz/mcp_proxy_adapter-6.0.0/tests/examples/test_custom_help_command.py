"""
Tests for custom help command example.

This module tests the custom help command functionality including:
- CustomHelpResult class
- CustomHelpCommand class
- Result serialization
- Command execution
- Error handling
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.examples.custom_commands import custom_help_command
from mcp_proxy_adapter.core.errors import NotFoundError


class TestCustomHelpResult:
    """Test CustomHelpResult class."""

    def test_init_with_command_info(self):
        """Test CustomHelpResult initialization with command_info."""
        command_info = {
            "name": "test_command",
            "description": "Test command description",
            "summary": "Test summary",
            "params": {"param1": "string"},
            "examples": [{"command": "test_command", "params": {"param1": "value"}}]
        }
        
        result = custom_help_command.CustomHelpResult(command_info=command_info)
        
        assert result.command_info == command_info
        assert result.commands_info is None
        assert result.custom_info == {}

    def test_init_with_commands_info(self):
        """Test CustomHelpResult initialization with commands_info."""
        commands_info = {
            "commands": {
                "cmd1": {"name": "cmd1", "description": "Command 1"},
                "cmd2": {"name": "cmd2", "description": "Command 2"}
            }
        }
        custom_info = {"enhanced": True}
        
        result = custom_help_command.CustomHelpResult(
            commands_info=commands_info,
            custom_info=custom_info
        )
        
        assert result.commands_info == commands_info
        assert result.command_info is None
        assert result.custom_info == custom_info

    def test_init_with_none_values(self):
        """Test CustomHelpResult initialization with None values."""
        result = custom_help_command.CustomHelpResult()
        
        assert result.commands_info is None
        assert result.command_info is None
        assert result.custom_info == {}

    def test_to_dict_with_command_info(self):
        """Test to_dict method with command_info."""
        command_info = {
            "name": "test_command",
            "description": "Test command description",
            "summary": "Test summary",
            "params": {"param1": "string"},
            "examples": [{"command": "test_command", "params": {"param1": "value"}}]
        }
        
        result = custom_help_command.CustomHelpResult(command_info=command_info)
        result_dict = result.to_dict()
        
        assert result_dict["cmdname"] == "test_command"
        assert result_dict["info"]["description"] == "Test command description"
        assert result_dict["info"]["summary"] == "Test summary"
        assert result_dict["info"]["params"] == {"param1": "string"}
        assert result_dict["info"]["examples"] == [{"command": "test_command", "params": {"param1": "value"}}]
        assert result_dict["info"]["custom_help"] is True

    def test_to_dict_with_commands_info(self):
        """Test to_dict method with commands_info."""
        commands_info = {
            "commands": {
                "cmd1": {"name": "cmd1", "description": "Command 1"},
                "cmd2": {"name": "cmd2", "description": "Command 2"}
            }
        }
        custom_info = {"enhanced": True, "total_commands": 2}
        
        result = custom_help_command.CustomHelpResult(
            commands_info=commands_info,
            custom_info=custom_info
        )
        result_dict = result.to_dict()
        
        assert result_dict["commands"] == commands_info["commands"]
        assert result_dict["total"] == 2
        assert result_dict["custom_help"] is True
        assert result_dict["custom_features"] == custom_info

    def test_to_dict_with_none_commands_info(self):
        """Test to_dict method with None commands_info."""
        result = custom_help_command.CustomHelpResult()
        result_dict = result.to_dict()
        
        assert "tool_info" in result_dict
        assert result_dict["tool_info"]["name"] == "Custom MCP-Proxy API Service"
        assert result_dict["tool_info"]["description"] == "Enhanced JSON-RPC API with custom commands"
        assert result_dict["tool_info"]["version"] == "2.0.0"
        assert result_dict["tool_info"]["custom_help"] is True
        assert "help_usage" in result_dict
        assert result_dict["commands"] == {}
        assert result_dict["total"] == 0
        assert result_dict["custom_features"] == {}

    def test_to_dict_with_command_info_missing_fields(self):
        """Test to_dict method with command_info missing fields."""
        command_info = {"name": "test_command"}
        
        result = custom_help_command.CustomHelpResult(command_info=command_info)
        result_dict = result.to_dict()
        
        assert result_dict["cmdname"] == "test_command"
        assert result_dict["info"]["description"] == ""
        assert result_dict["info"]["summary"] == ""
        assert result_dict["info"]["params"] == {}
        assert result_dict["info"]["examples"] == []
        assert result_dict["info"]["custom_help"] is True

    def test_get_schema(self):
        """Test get_schema method."""
        result = custom_help_command.CustomHelpResult()
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "cmdname" in schema["properties"]
        assert "info" in schema["properties"]
        assert "tool_info" in schema["properties"]
        assert "help_usage" in schema["properties"]
        assert "commands" in schema["properties"]
        assert "total" in schema["properties"]
        assert "custom_features" in schema["properties"]


class TestCustomHelpCommand:
    """Test CustomHelpCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = custom_help_command.CustomHelpCommand()
        
        assert command.name == "help"
        assert command.result_class == custom_help_command.CustomHelpResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = custom_help_command.CustomHelpCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "cmdname" in schema["properties"]
        assert schema["properties"]["cmdname"]["type"] == "string"
        assert "description" in schema["properties"]["cmdname"]

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_with_cmdname_success(self, mock_registry):
        """Test execute method with specific command name."""
        command_info = {
            "name": "test_command",
            "description": "Test command description",
            "summary": "Test summary",
            "params": {"param1": "string"},
            "examples": [{"command": "test_command", "params": {"param1": "value"}}]
        }
        mock_registry.get_command_info.return_value = command_info
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(cmdname="test_command", request_id="123", hook_processed=True)
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.command_info == command_info
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["command_specific"] is True
        assert result.custom_info["request_id"] == "123"
        assert result.custom_info["hook_processed"] is True
        
        mock_registry.get_command_info.assert_called_once_with("test_command")

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_with_cmdname_not_found(self, mock_registry):
        """Test execute method with non-existent command name."""
        mock_registry.get_command_info.return_value = None
        
        command = custom_help_command.CustomHelpCommand()
        
        # The command should return a result with error info instead of raising
        result = await command.execute(cmdname="nonexistent")
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.command_info is None
        assert result.custom_info["error"] == "Command 'nonexistent' not found"
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["error_handling"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_without_cmdname(self, mock_registry):
        """Test execute method without command name."""
        commands_info = {
            "commands": {
                "cmd1": {"name": "cmd1", "description": "Command 1"},
                "cmd2": {"name": "cmd2", "description": "Command 2"}
            }
        }
        mock_registry.get_all_commands_info.return_value = commands_info
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(request_id="123", hook_processed=True)
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.commands_info == commands_info
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["total_commands"] == 2
        assert result.custom_info["custom_commands"] == ["echo", "help", "health"]
        assert result.custom_info["request_id"] == "123"
        assert result.custom_info["hook_processed"] is True
        
        mock_registry.get_all_commands_info.assert_called_once()

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_without_cmdname_empty_commands(self, mock_registry):
        """Test execute method without command name and empty commands."""
        commands_info = {"commands": {}}
        mock_registry.get_all_commands_info.return_value = commands_info
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute()
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.commands_info == commands_info
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["total_commands"] == 0
        assert result.custom_info["custom_commands"] == ["echo", "help", "health"]

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_with_registry_error(self, mock_registry):
        """Test execute method with registry error."""
        mock_registry.get_all_commands_info.side_effect = Exception("Registry error")
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(request_id="123", hook_processed=True)
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.command_info is None
        assert result.commands_info is None
        assert result.custom_info["error"] == "Registry error"
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["error_handling"] is True
        assert result.custom_info["request_id"] == "123"
        assert result.custom_info["hook_processed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_with_additional_kwargs(self, mock_registry):
        """Test execute method with additional kwargs."""
        commands_info = {"commands": {"cmd1": {"name": "cmd1"}}}
        mock_registry.get_all_commands_info.return_value = commands_info
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(
            extra_param="value",
            another_param=123,
            request_id="456",
            hook_processed=False
        )
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["request_id"] == "456"
        assert result.custom_info["hook_processed"] is False

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_execute_with_none_cmdname(self, mock_registry):
        """Test execute method with None cmdname."""
        commands_info = {"commands": {"cmd1": {"name": "cmd1"}}}
        mock_registry.get_all_commands_info.return_value = commands_info
        
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(cmdname=None)
        
        assert isinstance(result, custom_help_command.CustomHelpResult)
        assert result.commands_info == commands_info
        assert result.command_info is None


class TestCustomHelpCommandIntegration:
    """Test custom help command integration."""

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_command_execution_flow(self, mock_registry):
        """Test complete command execution flow."""
        # Setup mocks
        command_info = {
            "name": "echo",
            "description": "Echo command",
            "summary": "Echoes input",
            "params": {"message": "string"},
            "examples": [{"command": "echo", "params": {"message": "Hello"}}]
        }
        mock_registry.get_command_info.return_value = command_info
        
        # Execute command
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(cmdname="echo", request_id="test_123")
        
        # Verify result
        assert isinstance(result, custom_help_command.CustomHelpResult)
        result_dict = result.to_dict()
        
        assert result_dict["cmdname"] == "echo"
        assert result_dict["info"]["description"] == "Echo command"
        assert result_dict["info"]["custom_help"] is True
        
        # Verify custom info
        assert result.custom_info["enhanced"] is True
        assert result.custom_info["command_specific"] is True
        assert result.custom_info["request_id"] == "test_123"

    @patch('mcp_proxy_adapter.examples.custom_commands.custom_help_command.registry')
    async def test_all_commands_execution_flow(self, mock_registry):
        """Test complete all commands execution flow."""
        # Setup mocks
        commands_info = {
            "commands": {
                "help": {"name": "help", "description": "Help command"},
                "echo": {"name": "echo", "description": "Echo command"},
                "health": {"name": "health", "description": "Health command"}
            }
        }
        mock_registry.get_all_commands_info.return_value = commands_info
        
        # Execute command
        command = custom_help_command.CustomHelpCommand()
        result = await command.execute(hook_processed=True)
        
        # Verify result
        assert isinstance(result, custom_help_command.CustomHelpResult)
        result_dict = result.to_dict()
        
        assert result_dict["commands"] == commands_info["commands"]
        assert result_dict["total"] == 3
        assert result_dict["custom_help"] is True
        assert result_dict["custom_features"]["enhanced"] is True
        assert result_dict["custom_features"]["hook_processed"] is True
        assert result_dict["custom_features"]["custom_commands"] == ["echo", "help", "health"] 