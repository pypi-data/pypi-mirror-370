"""
Tests for help command.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.commands.help_command import HelpCommand, HelpResult
from mcp_proxy_adapter.core.errors import NotFoundError


class TestHelpResult:
    """Tests for HelpResult class."""

    def test_init_with_commands_info(self):
        """Test HelpResult initialization with commands_info."""
        commands_info = {
            "commands": {"cmd1": {"summary": "Test command"}},
            "total": 1
        }
        
        result = HelpResult(commands_info=commands_info)
        
        assert result.commands_info == commands_info
        assert result.command_info is None

    def test_init_with_command_info(self):
        """Test HelpResult initialization with command_info."""
        command_info = {
            "name": "test_command",
            "summary": "Test command summary",
            "params": {"param1": {"type": "string"}},
            "examples": [{"command": "test_command", "params": {}}]
        }
        
        result = HelpResult(command_info=command_info)
        
        assert result.command_info == command_info
        assert result.commands_info is None

    def test_init_with_both_none(self):
        """Test HelpResult initialization with both parameters None."""
        result = HelpResult()
        
        assert result.commands_info is None
        assert result.command_info is None

    def test_to_dict_with_command_info(self):
        """Test to_dict method with command_info."""
        command_info = {
            "name": "test_command",
            "summary": "Test command summary",
            "params": {"param1": {"type": "string"}},
            "examples": [{"command": "test_command", "params": {}}]
        }
        
        result = HelpResult(command_info=command_info)
        data = result.to_dict()
        
        assert data["cmdname"] == "test_command"
        assert data["info"]["summary"] == "Test command summary"
        assert data["info"]["params"] == {"param1": {"type": "string"}}
        assert data["info"]["examples"] == [{"command": "test_command", "params": {}}]

    def test_to_dict_with_command_info_missing_fields(self):
        """Test to_dict method with command_info missing some fields."""
        command_info = {
            "name": "test_command"
            # Missing other fields
        }
        
        result = HelpResult(command_info=command_info)
        data = result.to_dict()
        
        assert data["cmdname"] == "test_command"
        assert data["info"]["summary"] == ""
        assert data["info"]["params"] == {}
        assert data["info"]["examples"] == []

    def test_to_dict_with_commands_info(self):
        """Test to_dict method with commands_info."""
        commands_info = {
            "tool_info": {
                "name": "Test Tool",
                "description": "Test description",
                "version": "1.0.0"
            },
            "commands": {
                "cmd1": {"summary": "Command 1", "params_count": 2},
                "cmd2": {"summary": "Command 2", "params_count": 0}
            }
        }
        
        result = HelpResult(commands_info=commands_info)
        data = result.to_dict()
        
        assert data["tool_info"]["name"] == "Test Tool"
        assert data["total"] == 2
        assert "note" in data
        assert "cmd1" in data["commands"]
        assert "cmd2" in data["commands"]

    def test_to_dict_with_commands_info_missing_commands(self):
        """Test to_dict method with commands_info missing commands."""
        commands_info = {
            "tool_info": {"name": "Test Tool"},
            "commands": {}
        }
        
        result = HelpResult(commands_info=commands_info)
        data = result.to_dict()
        
        assert data["total"] == 0
        assert data["commands"] == {}

    def test_to_dict_with_none_commands_info(self):
        """Test to_dict method with None commands_info."""
        result = HelpResult(commands_info=None)
        data = result.to_dict()
        
        assert data["tool_info"]["name"] == "MCP-Proxy API Service"
        assert data["total"] == 0
        assert "note" in data

    def test_get_schema(self):
        """Test get_schema method."""
        schema = HelpResult.get_schema()
        
        assert schema["type"] == "object"
        assert "oneOf" in schema
        assert len(schema["oneOf"]) == 2
        
        # Check first schema (for commands list)
        first_schema = schema["oneOf"][0]
        assert "commands" in first_schema["properties"]
        assert "tool_info" in first_schema["properties"]
        assert "total" in first_schema["properties"]
        
        # Check second schema (for single command)
        second_schema = schema["oneOf"][1]
        assert "cmdname" in second_schema["properties"]
        assert "info" in second_schema["properties"]


class TestHelpCommand:
    """Tests for HelpCommand class."""

    def setup_method(self):
        """Set up test method."""
        self.command = HelpCommand()

    def test_name_and_result_class(self):
        """Test command name and result class."""
        assert HelpCommand.name == "help"
        assert HelpCommand.result_class == HelpResult

    def test_get_schema(self):
        """Test get_schema method."""
        schema = HelpCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "cmdname" in schema["properties"]
        assert schema["properties"]["cmdname"]["type"] == "string"
        assert schema["additionalProperties"] is False

    @pytest.mark.asyncio
    async def test_execute_with_cmdname_success(self):
        """Test execute method with valid cmdname."""
        command_info = {
            "name": "test_command",
            "summary": "Test command summary",
            "params": {"param1": {"type": "string"}},
            "examples": [{"command": "test_command", "params": {}}]
        }
        
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_command_metadata.return_value = command_info
            
            result = await self.command.execute(cmdname="test_command")
            
            assert isinstance(result, HelpResult)
            assert result.command_info == command_info
            assert result.commands_info is None

    @pytest.mark.asyncio
    async def test_execute_with_cmdname_not_found(self):
        """Test execute method with non-existent cmdname."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_command_metadata.side_effect = NotFoundError("Command not found")
            mock_registry.get_all_metadata.return_value = {"cmd1": {}, "cmd2": {}}
            
            result = await self.command.execute(cmdname="nonexistent")
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "error" in result.commands_info
            assert "Command 'nonexistent' not found" in result.commands_info["error"]

    @pytest.mark.asyncio
    async def test_execute_with_cmdname_not_found_no_commands(self):
        """Test execute method with non-existent cmdname when no commands exist."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_command_metadata.side_effect = NotFoundError("Command not found")
            mock_registry.get_all_metadata.return_value = {}
            
            result = await self.command.execute(cmdname="nonexistent")
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "error" in result.commands_info
            assert "note" in result.commands_info

    @pytest.mark.asyncio
    async def test_execute_with_empty_cmdname(self):
        """Test execute method with empty cmdname."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_all_metadata.return_value = {
                "cmd1": {"summary": "Command 1"},
                "cmd2": {"summary": "Command 2"}
            }
            
            result = await self.command.execute(cmdname="")
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "tool_info" in result.commands_info
            assert "commands" in result.commands_info

    @pytest.mark.asyncio
    async def test_execute_with_none_cmdname(self):
        """Test execute method with None cmdname."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_all_metadata.return_value = {
                "cmd1": {"summary": "Command 1", "params": {"param1": {"type": "string"}}},
                "cmd2": {"summary": "Command 2", "params": {}}
            }
            
            result = await self.command.execute(cmdname=None)
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "tool_info" in result.commands_info
            assert "commands" in result.commands_info
            assert "cmd1" in result.commands_info["commands"]
            assert "cmd2" in result.commands_info["commands"]

    @pytest.mark.asyncio
    async def test_execute_with_registry_error(self):
        """Test execute method when registry.get_all_metadata fails."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_all_metadata.side_effect = Exception("Registry error")
            
            result = await self.command.execute()
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "error" in result.commands_info
            assert "Registry error" in result.commands_info["error"]

    @pytest.mark.asyncio
    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs (should be ignored)."""
        with patch('mcp_proxy_adapter.commands.help_command.registry') as mock_registry:
            mock_registry.get_all_metadata.return_value = {
                "cmd1": {"summary": "Command 1"}
            }
            
            result = await self.command.execute(
                cmdname=None,
                extra_param="ignored",
                another_param=123
            )
            
            assert isinstance(result, HelpResult)
            assert result.commands_info is not None
            assert "commands" in result.commands_info

    def test_command_metadata_structure(self):
        """Test that command returns proper metadata structure."""
        commands_info = {
            "tool_info": {
                "name": "MCP-Proxy API Service",
                "description": "JSON-RPC API for microservice command execution",
                "version": "1.0.0"
            },
            "help_usage": {
                "description": "Get information about commands",
                "examples": [
                    {"command": "help", "description": "List of all available commands"},
                    {"command": "help", "params": {"cmdname": "command_name"}, "description": "Get detailed information about a specific command"}
                ]
            },
            "commands": {
                "cmd1": {"summary": "Command 1", "params_count": 1},
                "cmd2": {"summary": "Command 2", "params_count": 0}
            }
        }
        
        result = HelpResult(commands_info=commands_info)
        data = result.to_dict()
        
        # Check tool_info structure
        assert "name" in data["tool_info"]
        assert "description" in data["tool_info"]
        assert "version" in data["tool_info"]
        
        # Check help_usage structure
        assert "description" in data["help_usage"]
        assert "examples" in data["help_usage"]
        
        # Check commands structure
        assert "cmd1" in data["commands"]
        assert "cmd2" in data["commands"]
        assert "summary" in data["commands"]["cmd1"]
        assert "params_count" in data["commands"]["cmd1"] 