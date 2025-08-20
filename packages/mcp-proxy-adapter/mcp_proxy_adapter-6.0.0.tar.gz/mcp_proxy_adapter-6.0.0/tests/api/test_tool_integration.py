"""
Tests for tool integration module.
"""

import pytest
from unittest.mock import MagicMock, patch
import json

from mcp_proxy_adapter.api.tool_integration import ToolIntegration, generate_tool_help
from mcp_proxy_adapter.commands.command_registry import CommandRegistry


class TestToolIntegration:
    """Tests for ToolIntegration class."""

    def setup_method(self):
        """Set up test method."""
        self.mock_registry = MagicMock(spec=CommandRegistry)
        
        # Mock command metadata
        self.mock_metadata = {
            "test_command": {
                "summary": "Test command summary",
                "params": {
                    "param1": {
                        "type": "строка",
                        "description": "Test parameter",
                        "required": True
                    },
                    "param2": {
                        "type": "целое число", 
                        "description": "Number parameter",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"param1": "value1"}
                    }
                ]
            }
        }
        
        self.mock_registry.get_all_metadata.return_value = self.mock_metadata

    def test_generate_tool_schema_basic(self):
        """Test generate_tool_schema with basic parameters."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description.return_value = {
                "description": "Test tool description",
                "supported_commands": {
                    "test_command": {
                        "params": {
                            "param1": {"type": "строка", "description": "Test param"}
                        }
                    }
                }
            }
            
            result = ToolIntegration.generate_tool_schema("test_tool", self.mock_registry)
            
            assert result["name"] == "test_tool"
            assert result["description"] == "Test tool description"
            assert "command" in result["parameters"]["properties"]
            assert "params" in result["parameters"]["properties"]
            assert result["parameters"]["required"] == ["command"]

    def test_generate_tool_schema_with_custom_description(self):
        """Test generate_tool_schema with custom description."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description.return_value = {
                "description": "Default description",
                "supported_commands": {}
            }
            
            result = ToolIntegration.generate_tool_schema(
                "test_tool", 
                self.mock_registry, 
                "Custom description"
            )
            
            assert result["description"] == "Custom description"

    def test_generate_tool_schema_parameter_types(self):
        """Test generate_tool_schema parameter type extraction."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description.return_value = {
                "description": "Test description",
                "supported_commands": {
                    "cmd1": {
                        "params": {
                            "str_param": {"type": "строка", "description": "String param"},
                            "int_param": {"type": "целое число", "description": "Integer param"},
                            "num_param": {"type": "число", "description": "Number param"},
                            "bool_param": {"type": "логическое значение", "description": "Boolean param"},
                            "arr_param": {"type": "список", "description": "Array param"},
                            "obj_param": {"type": "объект", "description": "Object param"},
                            "unknown_param": {"type": "неизвестный", "description": "Unknown param"}
                        }
                    }
                }
            }
            
            result = ToolIntegration.generate_tool_schema("test_tool", self.mock_registry)
            param_props = result["parameters"]["properties"]["params"]["properties"]
            
            assert param_props["str_param"]["type"] == "string"
            assert param_props["int_param"]["type"] == "integer"
            assert param_props["num_param"]["type"] == "number"
            assert param_props["bool_param"]["type"] == "boolean"
            assert param_props["arr_param"]["type"] == "array"
            assert param_props["obj_param"]["type"] == "object"
            assert param_props["unknown_param"]["type"] == "string"

    def test_generate_tool_documentation_markdown(self):
        """Test generate_tool_documentation with markdown format."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description_text.return_value = "# Test Tool\n\nTool description"
            
            result = ToolIntegration.generate_tool_documentation(
                "test_tool", 
                self.mock_registry, 
                "markdown"
            )
            
            assert result == "# Test Tool\n\nTool description"
            mock_api.generate_tool_description_text.assert_called_once_with("test_tool", self.mock_registry)

    def test_generate_tool_documentation_html(self):
        """Test generate_tool_documentation with html format."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description_text.return_value = "# Test Tool\n\nTool description"
            
            result = ToolIntegration.generate_tool_documentation(
                "test_tool", 
                self.mock_registry, 
                "html"
            )
            
            assert "<html>" in result
            assert "<body>" in result
            assert "<h1> Test Tool" in result

    def test_generate_tool_documentation_default_format(self):
        """Test generate_tool_documentation with default format."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description_text.return_value = "# Test Tool\n\nTool description"
            
            result = ToolIntegration.generate_tool_documentation(
                "test_tool", 
                self.mock_registry, 
                "unknown_format"
            )
            
            assert result == "# Test Tool\n\nTool description"

    def test_register_external_tools_success(self):
        """Test register_external_tools with successful registration."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description.return_value = {
                "description": "Test description",
                "supported_commands": {}
            }
            
            result = ToolIntegration.register_external_tools(
                self.mock_registry, 
                ["tool1", "tool2"]
            )
            
            assert len(result) == 2
            assert result["tool1"]["status"] == "success"
            assert result["tool2"]["status"] == "success"
            assert "schema" in result["tool1"]

    def test_register_external_tools_with_error(self, caplog):
        """Test register_external_tools with error during registration."""
        with patch('mcp_proxy_adapter.api.tool_integration.APIToolDescription') as mock_api:
            mock_api.generate_tool_description.side_effect = Exception("Test error")
            
            result = ToolIntegration.register_external_tools(
                self.mock_registry,
                ["error_tool"]
            )
            
            assert "error_tool" in result
            assert result["error_tool"]["status"] == "error"
            assert result["error_tool"]["error"] == "Test error"

    def test_extract_parameter_types_empty_commands(self):
        """Test _extract_parameter_types with empty commands."""
        result = ToolIntegration._extract_parameter_types({})
        assert result == {}

    def test_extract_parameter_types_no_params(self):
        """Test _extract_parameter_types with commands without params."""
        commands = {
            "cmd1": {"summary": "Test command"},
            "cmd2": {"params": {}}
        }
        
        result = ToolIntegration._extract_parameter_types(commands)
        assert result == {}

    def test_extract_parameter_types_with_params(self):
        """Test _extract_parameter_types with commands having params."""
        commands = {
            "cmd1": {
                "params": {
                    "param1": {"type": "строка", "description": "String param"},
                    "param2": {"type": "целое число", "description": "Integer param"}
                }
            }
        }
        
        result = ToolIntegration._extract_parameter_types(commands)
        
        assert "param1" in result
        assert "param2" in result
        assert result["param1"]["type"] == "string"
        assert result["param2"]["type"] == "integer"
        assert result["param1"]["description"] == "String param"

    def test_extract_parameter_types_duplicate_params(self):
        """Test _extract_parameter_types with duplicate parameter names."""
        commands = {
            "cmd1": {
                "params": {
                    "param1": {"type": "строка", "description": "String param"}
                }
            },
            "cmd2": {
                "params": {
                    "param1": {"type": "целое число", "description": "Integer param"}
                }
            }
        }
        
        result = ToolIntegration._extract_parameter_types(commands)
        
        # Last occurrence should be used
        assert result["param1"]["type"] == "integer"
        assert result["param1"]["description"] == "Integer param"


class TestGenerateToolHelp:
    """Tests for generate_tool_help function."""

    def test_generate_tool_help_basic(self):
        """Test generate_tool_help with basic metadata."""
        mock_registry = MagicMock(spec=CommandRegistry)
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command summary",
                "params": {
                    "param1": {
                        "type": "строка",
                        "description": "Test parameter",
                        "required": True
                    }
                },
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"param1": "value1"}
                    }
                ]
            }
        }
        
        result = generate_tool_help("test_tool", mock_registry)
        
        assert "# Инструмент test_tool" in result
        assert "## Доступные команды:" in result
        assert "### test_command" in result
        assert "Test command summary" in result
        assert "param1: обязательный" in result

    def test_generate_tool_help_no_params(self):
        """Test generate_tool_help with command without parameters."""
        mock_registry = MagicMock(spec=CommandRegistry)
        mock_registry.get_all_metadata.return_value = {
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
        
        result = generate_tool_help("test_tool", mock_registry)
        
        assert "### simple_command" in result
        assert "Simple command" in result
        # Should not contain parameter information
        assert "Параметры:" not in result

    def test_generate_tool_help_no_examples(self):
        """Test generate_tool_help with command without examples."""
        mock_registry = MagicMock(spec=CommandRegistry)
        mock_registry.get_all_metadata.return_value = {
            "no_example_command": {
                "summary": "Command without examples",
                "params": {},
                "examples": []
            }
        }
        
        result = generate_tool_help("test_tool", mock_registry)
        
        assert "### no_example_command" in result
        assert "Command without examples" in result
        # Should not contain example section
        assert "Пример:" not in result

    def test_generate_tool_help_multiple_commands(self):
        """Test generate_tool_help with multiple commands."""
        mock_registry = MagicMock(spec=CommandRegistry)
        mock_registry.get_all_metadata.return_value = {
            "cmd1": {
                "summary": "First command",
                "params": {"param1": {"type": "строка", "required": True}},
                "examples": [{"command": "cmd1", "params": {"param1": "value1"}}]
            },
            "cmd2": {
                "summary": "Second command", 
                "params": {"param2": {"type": "целое число", "required": False}},
                "examples": [{"command": "cmd2", "params": {"param2": 42}}]
            }
        }
        
        result = generate_tool_help("test_tool", mock_registry)
        
        assert "### cmd1" in result
        assert "### cmd2" in result
        assert "First command" in result
        assert "Second command" in result
        assert "param1: обязательный" in result
        assert "param2: опциональный" in result

    def test_generate_tool_help_json_example_format(self):
        """Test generate_tool_help JSON example formatting."""
        mock_registry = MagicMock(spec=CommandRegistry)
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "params": {},
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"key": "value", "number": 123}
                    }
                ]
            }
        }
        
        result = generate_tool_help("test_tool", mock_registry)
        
        # Check that JSON example is properly formatted
        assert "```json" in result
        assert '"command": "test_command"' in result
        assert '"params": {' in result
        assert '"key": "value"' in result
        assert '"number": 123' in result 