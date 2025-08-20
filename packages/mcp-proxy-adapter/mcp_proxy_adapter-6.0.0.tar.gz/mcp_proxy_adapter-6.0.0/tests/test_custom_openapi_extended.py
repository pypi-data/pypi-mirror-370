"""
Extended tests for custom OpenAPI functionality.

This module contains additional tests for custom_openapi.py
to improve code coverage.
"""

import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from mcp_proxy_adapter.custom_openapi import (
    CustomOpenAPIGenerator,
    custom_openapi,
    register_openapi_generator,
    get_openapi_generator,
    list_openapi_generators,
    custom_openapi_with_fallback
)
from mcp_proxy_adapter.commands.base import Command


class TestCustomOpenAPIGeneratorExtended:
    """Extended tests for CustomOpenAPIGenerator."""
    
    def test_load_base_schema_file_not_found(self):
        """Test _load_base_schema when file is not found."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                generator = CustomOpenAPIGenerator()
    
    def test_load_base_schema_invalid_json(self):
        """Test _load_base_schema with invalid JSON."""
        with patch('builtins.open', mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                generator = CustomOpenAPIGenerator()
    
    def test_add_commands_to_schema_no_commands(self):
        """Test _add_commands_to_schema with no commands."""
        generator = CustomOpenAPIGenerator()
        schema = {
            "components": {
                "schemas": {
                    "CommandRequest": {
                        "properties": {
                            "command": {"type": "string", "enum": []},
                            "params": {"type": "object", "oneOf": []}
                        }
                    }
                }
            }
        }
        
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            generator._add_commands_to_schema(schema)
            
            # Verify CommandRequest enum is empty
            assert schema["components"]["schemas"]["CommandRequest"]["properties"]["command"]["enum"] == []
            # Verify oneOf contains only null option
            assert len(schema["components"]["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"]) == 1
            assert schema["components"]["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"][0] == {"type": "null"}
    
    def test_add_commands_to_schema_missing_command_request(self):
        """Test _add_commands_to_schema when CommandRequest doesn't exist."""
        generator = CustomOpenAPIGenerator()
        schema = {
            "components": {
                "schemas": {}
            }
        }
        
        with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
            mock_registry.get_all_commands.return_value = {}
            
            generator._add_commands_to_schema(schema)
            
            # Verify CommandRequest was created
            assert "CommandRequest" in schema["components"]["schemas"]
    
    def test_create_params_schema_with_complex_schema(self):
        """Test _create_params_schema with complex command schema."""
        generator = CustomOpenAPIGenerator()
        
        # Mock command class with complex schema
        mock_cmd_class = MagicMock()
        mock_cmd_class.get_schema.return_value = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"},
                "param2": {"type": "integer"},
                "param3": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["param1"]
        }
        
        result = generator._create_params_schema(mock_cmd_class)
        
        assert result["type"] == "object"
        assert "param1" in result["properties"]
        assert "param2" in result["properties"]
        assert "param3" in result["properties"]
        assert "param1" in result["required"]
    
    def test_create_params_schema_with_empty_schema(self):
        """Test _create_params_schema with empty schema."""
        generator = CustomOpenAPIGenerator()
        
        mock_cmd_class = MagicMock()
        mock_cmd_class.get_schema.return_value = {}
        mock_cmd_class.name = "mock"
        
        result = generator._create_params_schema(mock_cmd_class)
        
        # Even empty schema gets title and description added
        assert result["title"] == "Parameters for mock"
        assert result["description"] == "Parameters for the mock command"
    
    def test_generate_with_custom_values(self):
        """Test generate method with custom title, description, and version."""
        generator = CustomOpenAPIGenerator()
        
        with patch.object(generator, '_load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "Default Title",
                    "description": "Default Description",
                    "version": "1.0.0"
                },
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            
            with patch.object(generator, '_add_commands_to_schema') as mock_add:
                result = generator.generate(
                    title="Custom Title",
                    description="Custom Description",
                    version="2.0.0"
                )
                
                assert result["info"]["title"] == "Custom Title"
                assert result["info"]["description"] == "Custom Description"
                assert result["info"]["version"] == "2.0.0"
                mock_add.assert_called_once()
    
    def test_generate_with_none_values(self):
        """Test generate method with None values (should use defaults)."""
        generator = CustomOpenAPIGenerator()
        
        with patch.object(generator, '_load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {
                    "title": "MCP Microservice API",
                    "description": "API для выполнения команд микросервиса",
                    "version": "1.0.0"
                },
                "components": {
                    "schemas": {
                        "CommandRequest": {
                            "properties": {
                                "command": {"type": "string", "enum": []},
                                "params": {"type": "object", "oneOf": []}
                            }
                        }
                    }
                }
            }
            
            with patch.object(generator, '_add_commands_to_schema') as mock_add:
                result = generator.generate()
                
                assert result["info"]["title"] == "MCP Microservice API"
                assert "API для выполнения команд микросервиса" in result["info"]["description"]
                assert result["info"]["version"] == "1.0.0"
                mock_add.assert_called_once()


class TestCustomOpenAPIFunctions:
    """Test custom OpenAPI functions."""
    
    def test_custom_openapi_function(self):
        """Test custom_openapi function."""
        mock_app = MagicMock()
        
        with patch('mcp_proxy_adapter.custom_openapi.CustomOpenAPIGenerator') as mock_generator_class:
            mock_generator = MagicMock()
            mock_generator_class.return_value = mock_generator
            mock_generator.generate.return_value = {"test": "schema"}
            
            result = custom_openapi(mock_app)
            
            assert result == {"test": "schema"}
            mock_generator.generate.assert_called_once()
    
    def test_register_openapi_generator(self):
        """Test register_openapi_generator function."""
        mock_generator_func = MagicMock()
        
        # Clear any existing generators
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {}):
            register_openapi_generator("test_generator", mock_generator_func)
            
            # Verify generator was registered
            from mcp_proxy_adapter.custom_openapi import _openapi_generators
            assert "test_generator" in _openapi_generators
            assert _openapi_generators["test_generator"] == mock_generator_func
    
    def test_get_openapi_generator_existing(self):
        """Test get_openapi_generator with existing generator."""
        mock_generator_func = MagicMock()
        
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {"test": mock_generator_func}):
            result = get_openapi_generator("test")
            
            assert result == mock_generator_func
    
    def test_get_openapi_generator_nonexistent(self):
        """Test get_openapi_generator with non-existent generator."""
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {}):
            result = get_openapi_generator("nonexistent")
            
            assert result is None
    
    def test_list_openapi_generators(self):
        """Test list_openapi_generators function."""
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {"gen1": None, "gen2": None}):
            result = list_openapi_generators()
            
            assert "gen1" in result
            assert "gen2" in result
            assert len(result) == 2
    
    def test_custom_openapi_with_fallback_success(self):
        """Test custom_openapi_with_fallback with successful generator."""
        mock_app = MagicMock()
        mock_generator_func = MagicMock()
        mock_generator_func.return_value = {"custom": "schema"}
        
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {"test_generator": mock_generator_func}):
            result = custom_openapi_with_fallback(mock_app)
            
            assert result == {"custom": "schema"}
            mock_generator_func.assert_called_once_with(mock_app)
    
    def test_custom_openapi_with_fallback_no_generator(self):
        """Test custom_openapi_with_fallback with no generator available."""
        mock_app = MagicMock()
        
        with patch('mcp_proxy_adapter.custom_openapi._openapi_generators', {}):
            with patch('mcp_proxy_adapter.custom_openapi.custom_openapi') as mock_custom_openapi:
                mock_custom_openapi.return_value = {"fallback": "schema"}
                
                result = custom_openapi_with_fallback(mock_app)
                
                assert result == {"fallback": "schema"}
                mock_custom_openapi.assert_called_once_with(mock_app)


class TestCustomOpenAPIErrorHandling:
    """Test error handling in custom OpenAPI functionality."""
    
    def test_generate_with_registry_error(self):
        """Test generate method when registry raises an error."""
        generator = CustomOpenAPIGenerator()
        
        with patch.object(generator, '_load_base_schema') as mock_load:
            mock_load.return_value = {
                "info": {},
                "components": {"schemas": {}}
            }
            
            with patch('mcp_proxy_adapter.custom_openapi.registry') as mock_registry:
                mock_registry.get_all_commands.side_effect = Exception("Registry error")
                
                with pytest.raises(Exception, match="Registry error"):
                    generator.generate()
    
    def test_create_params_schema_with_schema_error(self):
        """Test _create_params_schema when command.get_schema() raises an error."""
        generator = CustomOpenAPIGenerator()
        
        mock_cmd_class = MagicMock()
        mock_cmd_class.get_schema.side_effect = Exception("Schema error")
        
        with pytest.raises(Exception, match="Schema error"):
            generator._create_params_schema(mock_cmd_class) 