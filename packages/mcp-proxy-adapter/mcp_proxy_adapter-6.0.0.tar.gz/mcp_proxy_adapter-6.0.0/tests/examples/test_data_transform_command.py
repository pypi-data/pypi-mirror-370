"""
Tests for data transform command example.

This module tests the data transform command functionality including:
- DataTransformResult class
- DataTransformCommand class
- Result serialization
- Command execution
- Different transformation types
"""

import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.examples.custom_commands import data_transform_command


class TestDataTransformResult:
    """Test DataTransformResult class."""

    def test_init_with_all_parameters(self):
        """Test DataTransformResult initialization with all parameters."""
        original_data = {"name": "test", "value": 123}
        transformed_data = {"name": "TEST", "value": "123"}
        processing_info = {"transform_type": "uppercase", "input_keys": ["name", "value"]}
        
        result = data_transform_command.DataTransformResult(
            original_data=original_data,
            transformed_data=transformed_data,
            processing_info=processing_info
        )
        
        assert result.original_data == original_data
        assert result.transformed_data == transformed_data
        assert result.processing_info == processing_info

    def test_to_dict(self):
        """Test to_dict method."""
        original_data = {"name": "test"}
        transformed_data = {"name": "TEST"}
        processing_info = {"transform_type": "uppercase"}
        
        result = data_transform_command.DataTransformResult(
            original_data=original_data,
            transformed_data=transformed_data,
            processing_info=processing_info
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["original_data"] == original_data
        assert result_dict["transformed_data"] == transformed_data
        assert result_dict["processing_info"] == processing_info
        assert result_dict["command_type"] == "data_transform"

    def test_get_schema(self):
        """Test get_schema method."""
        result = data_transform_command.DataTransformResult(
            original_data={},
            transformed_data={},
            processing_info={}
        )
        
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "original_data" in schema["properties"]
        assert "transformed_data" in schema["properties"]
        assert "processing_info" in schema["properties"]
        assert "command_type" in schema["properties"]


class TestDataTransformCommand:
    """Test DataTransformCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = data_transform_command.DataTransformCommand()
        
        assert command.name == "data_transform"
        assert command.result_class == data_transform_command.DataTransformResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = data_transform_command.DataTransformCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"]
        assert "transform_type" in schema["properties"]
        assert schema["properties"]["transform_type"]["type"] == "string"
        assert "enum" in schema["properties"]["transform_type"]

    async def test_execute_with_uppercase_transformation(self):
        """Test execute method with uppercase transformation."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "test", "value": "hello"}
        
        result = await command.execute(data=data, transform_type="uppercase")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == data
        assert result.transformed_data["name"] == "TEST"
        assert result.transformed_data["value"] == "HELLO"
        assert result.processing_info["transform_type"] == "uppercase"
        assert result.processing_info["input_keys"] == ["name", "value"]
        assert result.processing_info["output_keys"] == ["name", "value"]

    async def test_execute_with_lowercase_transformation(self):
        """Test execute method with lowercase transformation."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "TEST", "value": "HELLO"}
        
        result = await command.execute(data=data, transform_type="lowercase")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == data
        assert result.transformed_data["name"] == "test"
        assert result.transformed_data["value"] == "hello"
        assert result.processing_info["transform_type"] == "lowercase"

    async def test_execute_with_reverse_transformation(self):
        """Test execute method with reverse transformation."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "test", "value": "hello"}
        
        result = await command.execute(data=data, transform_type="reverse")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == data
        assert result.transformed_data["name"] == "tset"
        assert result.transformed_data["value"] == "olleh"
        assert result.processing_info["transform_type"] == "reverse"

    async def test_execute_with_default_transformation(self):
        """Test execute method with default transformation."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "test", "value": "hello"}
        
        result = await command.execute(data=data, transform_type="default")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == data
        assert result.transformed_data == data.copy()
        assert result.processing_info["transform_type"] == "default"

    async def test_execute_without_data(self):
        """Test execute method without data."""
        command = data_transform_command.DataTransformCommand()
        
        result = await command.execute()
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == {}
        assert result.transformed_data == {}
        assert result.processing_info["transform_type"] == "default"

    async def test_execute_without_transform_type(self):
        """Test execute method without transform_type."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "test"}
        
        result = await command.execute(data=data)
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == data
        assert result.transformed_data == data.copy()
        assert result.processing_info["transform_type"] == "default"

    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        command = data_transform_command.DataTransformCommand()
        data = {"name": "test"}
        
        result = await command.execute(
            data=data,
            transform_type="uppercase",
            hook_enhanced=True,
            data_modified=True,
            extra_param="value"
        )
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.processing_info["hook_enhanced"] is True
        assert result.processing_info["data_modified"] is True

    async def test_execute_with_numeric_data(self):
        """Test execute method with numeric data."""
        command = data_transform_command.DataTransformCommand()
        data = {"count": 123, "price": 45.67}
        
        result = await command.execute(data=data, transform_type="uppercase")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.transformed_data["count"] == "123"
        assert result.transformed_data["price"] == "45.67"

    async def test_execute_with_boolean_data(self):
        """Test execute method with boolean data."""
        command = data_transform_command.DataTransformCommand()
        data = {"active": True, "enabled": False}
        
        result = await command.execute(data=data, transform_type="uppercase")
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.transformed_data["active"] == "TRUE"
        assert result.transformed_data["enabled"] == "FALSE"

    async def test_execute_with_none_data(self):
        """Test execute method with None data."""
        command = data_transform_command.DataTransformCommand()
        
        result = await command.execute(data=None)
        
        assert isinstance(result, data_transform_command.DataTransformResult)
        assert result.original_data == {}
        assert result.transformed_data == {}


class TestDataTransformCommandIntegration:
    """Test data transform command integration."""

    async def test_command_execution_flow(self):
        """Test complete command execution flow."""
        command = data_transform_command.DataTransformCommand()
        data = {"message": "Hello World", "number": 42}
        
        result = await command.execute(
            data=data,
            transform_type="uppercase",
            hook_enhanced=True
        )
        
        # Verify result structure
        assert isinstance(result, data_transform_command.DataTransformResult)
        result_dict = result.to_dict()
        
        assert result_dict["command_type"] == "data_transform"
        assert result_dict["original_data"] == data
        assert result_dict["transformed_data"]["message"] == "HELLO WORLD"
        assert result_dict["transformed_data"]["number"] == "42"
        assert result_dict["processing_info"]["hook_enhanced"] is True
        assert result_dict["processing_info"]["transform_type"] == "uppercase"

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = data_transform_command.DataTransformCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify data property
        data_prop = schema["properties"]["data"]
        assert data_prop["type"] == "object"
        assert "description" in data_prop
        
        # Verify transform_type property
        transform_prop = schema["properties"]["transform_type"]
        assert transform_prop["type"] == "string"
        assert "enum" in transform_prop
        assert "description" in transform_prop
        assert "uppercase" in transform_prop["enum"]
        assert "lowercase" in transform_prop["enum"]
        assert "reverse" in transform_prop["enum"]
        assert "default" in transform_prop["enum"] 