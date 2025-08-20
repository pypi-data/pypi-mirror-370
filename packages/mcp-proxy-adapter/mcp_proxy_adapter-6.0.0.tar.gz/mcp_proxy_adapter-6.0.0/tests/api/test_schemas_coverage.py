"""
Additional tests for schemas.py to achieve 100% coverage.
"""

import pytest
from unittest.mock import MagicMock
from mcp_proxy_adapter.api.schemas import APIToolDescription


class TestAPIToolDescriptionCoverage:
    """Additional tests to cover missing lines in APIToolDescription."""
    
    def test_generate_tool_description_with_empty_metadata(self):
        """Test generate_tool_description with empty metadata."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {}
        
        result = APIToolDescription.generate_tool_description("test_tool", mock_registry)
        
        assert result["name"] == "test_tool"
        assert result["description"] == "Выполняет команды через JSON-RPC протокол на сервере проекта."
        assert result["supported_commands"] == {}
        assert result["examples"] == []
    
    def test_generate_tool_description_with_metadata_no_params(self):
        """Test generate_tool_description with metadata but no params."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {},
                "examples": []
            }
        }
        
        result = APIToolDescription.generate_tool_description("test_tool", mock_registry)
        
        assert "test_command" in result["supported_commands"]
        assert result["supported_commands"]["test_command"]["params"] == {}
        assert result["supported_commands"]["test_command"]["required_params"] == []
    
    def test_generate_tool_description_with_required_params(self):
        """Test generate_tool_description with required parameters."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {
                    "required_param": {
                        "type": "str",
                        "required": True
                    },
                    "optional_param": {
                        "type": "int",
                        "required": False
                    }
                },
                "examples": []
            }
        }
        
        result = APIToolDescription.generate_tool_description("test_tool", mock_registry)
        
        cmd_info = result["supported_commands"]["test_command"]
        assert "required_param" in cmd_info["required_params"]
        assert "optional_param" not in cmd_info["required_params"]
        assert cmd_info["params"]["required_param"]["required"] is True
        assert cmd_info["params"]["optional_param"]["required"] is False
    
    def test_generate_tool_description_with_examples(self):
        """Test generate_tool_description with examples."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {},
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"param1": "value1"},
                        "description": "Test example"
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description("test_tool", mock_registry)
        
        assert len(result["examples"]) == 1
        assert result["examples"][0]["command"] == "test_command"
        assert result["examples"][0]["params"] == {"param1": "value1"}
        assert result["examples"][0]["description"] == "Test example"
    
    def test_generate_tool_description_with_example_defaults(self):
        """Test generate_tool_description with example defaults."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {},
                "examples": [
                    {
                        "command": "test_command"
                        # Missing params and description
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description("test_tool", mock_registry)
        
        assert len(result["examples"]) == 1
        assert result["examples"][0]["command"] == "test_command"
        assert result["examples"][0]["params"] == {}
        assert result["examples"][0]["description"] == "Пример использования команды test_command"
    
    def test_generate_tool_description_text_with_params_and_examples(self):
        """Test generate_tool_description_text with params and examples."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
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
                        "params": {"param1": "value1"},
                        "description": "Test example"
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description_text("test_tool", mock_registry)
        
        assert "# Инструмент test_tool" in result
        assert "## Доступные команды" in result
        assert "### test_command" in result
        assert "#### Параметры:" in result
        assert "**обязательный**" in result
        assert "#### Примеры:" in result
        assert "**Пример 1**" in result
        assert '"param1": "value1"' in result
    
    def test_generate_tool_description_text_with_string_params(self):
        """Test generate_tool_description_text with string parameters."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {
                    "string_param": {
                        "type": "строка",
                        "description": "String parameter",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"string_param": "test_value"},
                        "description": "String example"
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description_text("test_tool", mock_registry)
        
        assert '"string_param": "test_value"' in result
    
    def test_generate_tool_description_text_with_numeric_params(self):
        """Test generate_tool_description_text with numeric parameters."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {
                    "numeric_param": {
                        "type": "число",
                        "description": "Numeric parameter",
                        "required": False
                    }
                },
                "examples": [
                    {
                        "command": "test_command",
                        "params": {"numeric_param": 42},
                        "description": "Numeric example"
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description_text("test_tool", mock_registry)
        
        assert '"numeric_param": 42' in result
    
    def test_generate_tool_description_text_with_empty_params(self):
        """Test generate_tool_description_text with empty parameters."""
        mock_registry = MagicMock()
        mock_registry.get_all_metadata.return_value = {
            "test_command": {
                "summary": "Test command",
                "description": "Test command description",
                "params": {},
                "examples": [
                    {
                        "command": "test_command",
                        "params": {},
                        "description": "Empty params example"
                    }
                ]
            }
        }
        
        result = APIToolDescription.generate_tool_description_text("test_tool", mock_registry)
        
        assert '"params": {}' in result
    
    def test_simplify_type_with_float(self):
        """Test _simplify_type with float type."""
        result = APIToolDescription._simplify_type("float")
        assert result == "число"
    
    def test_simplify_type_with_bool(self):
        """Test _simplify_type with bool type."""
        result = APIToolDescription._simplify_type("bool")
        assert result == "логическое значение"
    
    def test_simplify_type_with_optional_complex(self):
        """Test _simplify_type with Optional[Dict[str, Any]]."""
        result = APIToolDescription._simplify_type("Optional[Dict[str, Any]]")
        assert result == "строка"
    
    def test_simplify_type_with_optional_list(self):
        """Test _simplify_type with Optional[List[str]]."""
        result = APIToolDescription._simplify_type("Optional[List[str]]")
        assert result == "строка"
    
    def test_simplify_type_with_class_prefix(self):
        """Test _simplify_type with class prefix."""
        result = APIToolDescription._simplify_type("<class 'str'>")
        assert result == "строка"
    
    def test_simplify_type_with_unknown_type(self):
        """Test _simplify_type with unknown type."""
        result = APIToolDescription._simplify_type("CustomType")
        assert result == "значение"
    
    def test_simplify_type_with_optional_dict(self):
        """Test _simplify_type with Optional[Dict]."""
        result = APIToolDescription._simplify_type("Optional[Dict[str, Any]]")
        assert result == "строка"
    
    def test_simplify_type_with_optional_list(self):
        """Test _simplify_type with Optional[List]."""
        result = APIToolDescription._simplify_type("Optional[List[str]]")
        assert result == "строка"
    
    def test_simplify_type_with_optional_dict_recursive(self):
        """Test _simplify_type with Optional[Dict] that should return object."""
        result = APIToolDescription._simplify_type("Optional[Dict]")
        assert result == "объект"
    
    def test_simplify_type_with_optional_list_recursive(self):
        """Test _simplify_type with Optional[List] that should return list."""
        result = APIToolDescription._simplify_type("Optional[List]")
        assert result == "список"
    
    def test_extract_param_description_with_multiple_sections(self):
        """Test _extract_param_description with multiple sections."""
        doc_string = """
        Test function.
        
        Args:
            param1: First parameter description
            param2: Second parameter description
            
        Returns:
            Some return value
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == "First parameter description"
        
        result = APIToolDescription._extract_param_description(doc_string, "param2")
        assert result == "Second parameter description"
    
    def test_extract_param_description_with_no_colon(self):
        """Test _extract_param_description with parameter without colon."""
        doc_string = """
        Test function.
        
        Args:
            param1: First parameter description
            param2 Second parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param2")
        assert result == ""
    
    def test_extract_param_description_with_empty_line(self):
        """Test _extract_param_description with empty line in args section."""
        doc_string = """
        Test function.
        
        Args:
            param1: First parameter description
            
            param2: Second parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param2")
        assert result == "Second parameter description"
    
    def test_extract_param_description_with_parameters_section(self):
        """Test _extract_param_description with Parameters section."""
        doc_string = """
        Test function.
        
        Parameters:
            param1: First parameter description
            param2: Second parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == "First parameter description"
    
    def test_extract_param_description_without_sections(self):
        """Test _extract_param_description without Args or Parameters sections."""
        doc_string = """
        Test function.
        
        This is a test function without Args or Parameters sections.
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == ""
    
    def test_extract_param_description_param_not_found(self):
        """Test _extract_param_description with parameter not found."""
        doc_string = """
        Test function.
        
        Args:
            param1: First parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "nonexistent_param")
        assert result == ""
    
    def test_extract_param_description_with_colon_spacing(self):
        """Test _extract_param_description with different colon spacing."""
        doc_string = """
        Test function.
        
        Args:
            param1 : First parameter description
            param2:Second parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == "First parameter description"
        
        result = APIToolDescription._extract_param_description(doc_string, "param2")
        assert result == "Second parameter description"
    
    def test_extract_param_description_with_no_matching_param(self):
        """Test _extract_param_description when parameter is not found in args section."""
        doc_string = """
        Test function.
        
        Args:
            param1: First parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "nonexistent_param")
        assert result == ""
    
    def test_extract_param_description_with_empty_args_section(self):
        """Test _extract_param_description with empty args section."""
        doc_string = """
        Test function.
        
        Args:
            
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == ""
    
    def test_extract_param_description_with_non_matching_lines(self):
        """Test _extract_param_description with lines that don't match the parameter."""
        doc_string = """
        Test function.
        
        Args:
            other_param: Other parameter description
            another_param: Another parameter description
        """
        
        result = APIToolDescription._extract_param_description(doc_string, "param1")
        assert result == "" 