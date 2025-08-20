"""
Tests for tools module.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json

from mcp_proxy_adapter.api.tools import (
    TSTCommandExecutor, 
    get_tool_description, 
    execute_tool,
    available_tools,
    registry
)
from mcp_proxy_adapter.core.errors import NotFoundError, InvalidParamsError


class TestTSTCommandExecutor:
    """Tests for TSTCommandExecutor class."""

    def setup_method(self):
        """Set up test method."""
        self.mock_registry = MagicMock()
        
        # Mock command metadata
        self.mock_metadata = {
            "test_command": {
                "summary": "Test command",
                "params": {"param1": {"type": "строка", "required": True}},
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"param1": "value1"}
                    }
                ]
            },
            "simple_command": {
                "summary": "Simple command",
                "params": {},
                "examples": [
                    {
                        "command": "simple_command", 
                        "params": {}
                    }
                ]
            }
        }

    def test_tst_command_executor_attributes(self):
        """Test TSTCommandExecutor class attributes."""
        assert TSTCommandExecutor.name == "tst_execute_command"
        assert "JSON-RPC" in TSTCommandExecutor.description

    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test execute method with successful command execution."""
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            # Mock command exists and execution
            mock_registry.command_exists.return_value = True
            mock_command_class = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"success": True, "data": "test"}
            mock_command_class.execute = AsyncMock(return_value=mock_result)
            mock_registry.get_command_with_priority.return_value = mock_command_class
            
            result = await TSTCommandExecutor.execute("test_command", {"param1": "value1"})
            
            assert result == {"success": True, "data": "test"}
            mock_registry.command_exists_with_priority.assert_called_once_with("test_command")
            mock_registry.get_command_with_priority.assert_called_once_with("test_command")
            mock_command_class.execute.assert_called_once_with(param1="value1")

    @pytest.mark.asyncio
    async def test_execute_command_no_params(self):
        """Test execute method with no parameters."""
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            mock_registry.command_exists.return_value = True
            mock_command_class = MagicMock()
            mock_result = MagicMock()
            mock_result.to_dict.return_value = {"success": True}
            mock_command_class.execute = AsyncMock(return_value=mock_result)
            mock_registry.get_command_with_priority.return_value = mock_command_class
            
            result = await TSTCommandExecutor.execute("test_command")
            
            assert result == {"success": True}
            mock_command_class.execute.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_execute_command_not_found(self, caplog):
        """Test execute method with non-existent command."""
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            mock_registry.command_exists_with_priority.return_value = False
            
            with pytest.raises(NotFoundError, match="Команда 'nonexistent' не найдена"):
                await TSTCommandExecutor.execute("nonexistent")
            assert "Command not found: nonexistent" in caplog.text

    @pytest.mark.asyncio
    async def test_execute_command_execution_error(self, caplog):
        """Test execute method with command execution error."""
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            mock_registry.command_exists_with_priority.return_value = True
            mock_command_class = MagicMock()
            mock_command_class.execute = AsyncMock(side_effect=Exception("Test error"))
            mock_registry.get_command_with_priority.return_value = mock_command_class
            
            with pytest.raises(Exception, match="Test error"):
                await TSTCommandExecutor.execute("test_command")
            assert "Error executing command test_command: Test error" in caplog.text

    def test_get_schema(self):
        """Test get_schema method."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_schema.return_value = {
                "name": "tst_execute_command",
                "description": "Test description"
            }
            
            result = TSTCommandExecutor.get_schema()
            
            assert result["name"] == "tst_execute_command"
            mock_tool_integration.generate_tool_schema.assert_called_once_with(
                TSTCommandExecutor.name, 
                registry, 
                TSTCommandExecutor.description
            )

    def test_get_description_json_format(self):
        """Test get_description with JSON format."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_schema.return_value = {
                "name": "tst_execute_command",
                "description": "Test description"
            }
            
            # Mock registry for examples and error codes
            with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
                mock_registry.get_all_metadata.return_value = self.mock_metadata
                
                result = TSTCommandExecutor.get_description("json")
                
                assert "name" in result
                assert "examples" in result
                assert "error_codes" in result

    def test_get_description_markdown_format(self):
        """Test get_description with markdown format."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_documentation.return_value = "# Test Tool\n\nDescription"
            
            result = TSTCommandExecutor.get_description("markdown")
            
            assert result == "# Test Tool\n\nDescription"
            mock_tool_integration.generate_tool_documentation.assert_called_once_with(
                TSTCommandExecutor.name, 
                registry, 
                "markdown"
            )

    def test_get_description_text_format(self):
        """Test get_description with text format."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_documentation.return_value = "Test Tool Description"
            
            result = TSTCommandExecutor.get_description("text")
            
            assert result == "Test Tool Description"

    def test_get_description_html_format(self):
        """Test get_description with html format."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_documentation.return_value = "<html>Test</html>"
            
            result = TSTCommandExecutor.get_description("html")
            
            assert result == "<html>Test</html>"

    def test_get_description_unknown_format(self):
        """Test get_description with unknown format."""
        with patch('mcp_proxy_adapter.api.tools.ToolIntegration') as mock_tool_integration:
            mock_tool_integration.generate_tool_schema.return_value = {
                "name": "tst_execute_command",
                "description": "Test description"
            }
            
            result = TSTCommandExecutor.get_description("unknown_format")
            
            assert "name" in result

    def test_generate_examples(self):
        """Test _generate_examples method."""
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            mock_registry.get_all_metadata.return_value = self.mock_metadata
            
            examples = TSTCommandExecutor._generate_examples()
            
            assert len(examples) == 2
            assert examples[0]["command"] == "tst_execute_command"
            assert "command" in examples[0]["params"]
            assert "params" in examples[0]["params"]

    def test_generate_examples_no_examples(self):
        """Test _generate_examples with commands without examples."""
        metadata_without_examples = {
            "cmd1": {"summary": "Command 1", "params": {}, "examples": []},
            "cmd2": {"summary": "Command 2", "params": {}}
        }
        
        with patch('mcp_proxy_adapter.api.tools.registry') as mock_registry:
            mock_registry.get_all_metadata.return_value = metadata_without_examples
            
            examples = TSTCommandExecutor._generate_examples()
            
            assert len(examples) == 0

    def test_generate_error_codes(self):
        """Test _generate_error_codes method."""
        error_codes = TSTCommandExecutor._generate_error_codes()
        
        assert "-32600" in error_codes
        assert "-32601" in error_codes
        assert "-32602" in error_codes
        assert "-32603" in error_codes
        assert "-32000" in error_codes
        assert "Некорректный запрос" in error_codes.values()
        assert "Команда не найдена" in error_codes.values()


class TestAvailableTools:
    """Tests for available_tools dictionary."""

    def test_available_tools_contains_tst_executor(self):
        """Test that available_tools contains TSTCommandExecutor."""
        assert "tst_execute_command" in available_tools
        assert available_tools["tst_execute_command"] == TSTCommandExecutor


class TestGetToolDescription:
    """Tests for get_tool_description function."""

    def test_get_tool_description_existing_tool(self):
        """Test get_tool_description with existing tool."""
        with patch.object(TSTCommandExecutor, 'get_description') as mock_get_desc:
            mock_get_desc.return_value = {"name": "tst_execute_command", "description": "Test"}
            
            result = get_tool_description("tst_execute_command", "json")
            
            assert result == {"name": "tst_execute_command", "description": "Test"}
            mock_get_desc.assert_called_once_with("json")

    def test_get_tool_description_nonexistent_tool(self):
        """Test get_tool_description with non-existent tool."""
        with pytest.raises(NotFoundError, match="Инструмент 'nonexistent' не найден"):
            get_tool_description("nonexistent")

    def test_get_tool_description_default_format(self):
        """Test get_tool_description with default format."""
        with patch.object(TSTCommandExecutor, 'get_description') as mock_get_desc:
            mock_get_desc.return_value = {"name": "tst_execute_command"}
            
            result = get_tool_description("tst_execute_command")
            
            assert result == {"name": "tst_execute_command"}
            mock_get_desc.assert_called_once_with("json")


class TestExecuteTool:
    """Tests for execute_tool function."""

    @pytest.mark.asyncio
    async def test_execute_tool_existing_tool(self):
        """Test execute_tool with existing tool."""
        with patch.object(TSTCommandExecutor, 'execute') as mock_execute:
            mock_execute.return_value = {"success": True, "data": "test"}
            
            result = await execute_tool("tst_execute_command", command="test_command")
            
            assert result == {"success": True, "data": "test"}
            mock_execute.assert_called_once_with(command="test_command")

    @pytest.mark.asyncio
    async def test_execute_tool_nonexistent_tool(self):
        """Test execute_tool with non-existent tool."""
        with pytest.raises(NotFoundError, match="Инструмент 'nonexistent' не найден"):
            await execute_tool("nonexistent")

    @pytest.mark.asyncio
    async def test_execute_tool_with_params(self):
        """Test execute_tool with parameters."""
        with patch.object(TSTCommandExecutor, 'execute') as mock_execute:
            mock_execute.return_value = {"success": True}
            
            result = await execute_tool("tst_execute_command", command="test", param1="value1")
            
            assert result == {"success": True}
            mock_execute.assert_called_once_with(command="test", param1="value1")

    @pytest.mark.asyncio
    async def test_execute_tool_no_params(self):
        """Test execute_tool without parameters."""
        with patch.object(TSTCommandExecutor, 'execute') as mock_execute:
            mock_execute.return_value = {"success": True}
            
            result = await execute_tool("tst_execute_command")
            
            assert result == {"success": True}
            mock_execute.assert_called_once_with() 