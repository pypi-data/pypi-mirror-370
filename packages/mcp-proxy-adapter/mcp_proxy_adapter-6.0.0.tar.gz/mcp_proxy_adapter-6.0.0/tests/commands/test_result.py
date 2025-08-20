"""
Tests for command result classes.
"""

import json
import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult


class TestCommandResult:
    """Tests for base CommandResult class."""

    def test_to_json_with_indent(self):
        """Test to_json method with indentation."""
        # Create a real SuccessResult instead of mock
        result_obj = SuccessResult(data={"test": "value", "number": 123})
        
        result = result_obj.to_json(indent=2)
        
        # Should be valid JSON with indentation
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["test"] == "value"
        assert parsed["data"]["number"] == 123
        assert "\n" in result  # Should have newlines for indentation

    def test_to_json_without_indent(self):
        """Test to_json method without indentation."""
        # Create a real SuccessResult instead of mock
        result_obj = SuccessResult(data={"test": "value"})
        
        result = result_obj.to_json()
        
        # Should be valid JSON without indentation
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["test"] == "value"
        assert "\n" not in result  # Should not have newlines

    def test_to_json_with_unicode(self):
        """Test to_json method with unicode characters."""
        # Create a real SuccessResult instead of mock
        result_obj = SuccessResult(data={"message": "Привет мир", "key": "значение"})
        
        result = result_obj.to_json()
        
        # Should preserve unicode characters
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["message"] == "Привет мир"
        assert parsed["data"]["key"] == "значение"

    def test_from_dict_not_implemented(self):
        """Test that from_dict raises NotImplementedError in base class."""
        with pytest.raises(NotImplementedError, match="Method from_dict must be implemented in subclasses"):
            CommandResult.from_dict({"test": "value"})


class TestSuccessResult:
    """Tests for SuccessResult class."""

    def test_init_with_data_and_message(self):
        """Test SuccessResult initialization with data and message."""
        data = {"key": "value", "number": 42}
        message = "Operation completed successfully"
        
        result = SuccessResult(data=data, message=message)
        
        assert result.data == data
        assert result.message == message

    def test_init_with_none_values(self):
        """Test SuccessResult initialization with None values."""
        result = SuccessResult()
        
        assert result.data == {}
        assert result.message is None

    def test_init_with_empty_data(self):
        """Test SuccessResult initialization with empty data."""
        result = SuccessResult(data={})
        
        assert result.data == {}
        assert result.message is None

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields populated."""
        data = {"result": "success", "items": [1, 2, 3]}
        message = "Operation completed"
        
        result = SuccessResult(data=data, message=message)
        dict_result = result.to_dict()
        
        assert dict_result["success"] is True
        assert dict_result["data"] == data
        assert dict_result["message"] == message

    def test_to_dict_without_message(self):
        """Test to_dict method without message."""
        data = {"key": "value"}
        
        result = SuccessResult(data=data)
        dict_result = result.to_dict()
        
        assert dict_result["success"] is True
        assert dict_result["data"] == data
        assert "message" not in dict_result

    def test_to_dict_without_data(self):
        """Test to_dict method without data."""
        message = "Success"
        
        result = SuccessResult(message=message)
        dict_result = result.to_dict()
        
        assert dict_result["success"] is True
        assert dict_result["message"] == message
        assert "data" not in dict_result

    def test_to_dict_with_empty_data(self):
        """Test to_dict method with empty data."""
        result = SuccessResult(data={})
        dict_result = result.to_dict()
        
        assert dict_result["success"] is True
        assert "data" not in dict_result  # Empty data should not be included

    def test_get_schema(self):
        """Test get_schema method."""
        schema = SuccessResult.get_schema()
        
        assert schema["type"] == "object"
        assert "success" in schema["properties"]
        assert "data" in schema["properties"]
        assert "message" in schema["properties"]
        assert schema["properties"]["success"]["type"] == "boolean"
        assert "success" in schema["required"]

    def test_from_dict_with_all_fields(self):
        """Test from_dict method with all fields."""
        data = {"key": "value", "number": 42}
        message = "Success message"
        
        input_data = {
            "success": True,
            "data": data,
            "message": message
        }
        
        result = SuccessResult.from_dict(input_data)
        
        assert result.data == data
        assert result.message == message

    def test_from_dict_without_optional_fields(self):
        """Test from_dict method without optional fields."""
        input_data = {"success": True}
        
        result = SuccessResult.from_dict(input_data)
        
        # data should be empty dict when not provided
        assert result.data == {}
        assert result.message is None

    def test_from_dict_with_partial_fields(self):
        """Test from_dict method with partial fields."""
        data = {"key": "value"}
        
        input_data = {
            "success": True,
            "data": data
        }
        
        result = SuccessResult.from_dict(input_data)
        
        assert result.data == data
        assert result.message is None


class TestErrorResult:
    """Tests for ErrorResult class."""

    def test_init_with_all_parameters(self):
        """Test ErrorResult initialization with all parameters."""
        message = "Something went wrong"
        code = -32601
        details = {"param": "value", "line": 42}
        
        result = ErrorResult(message=message, code=code, details=details)
        
        assert result.message == message
        assert result.code == code
        assert result.details == details

    def test_init_with_default_values(self):
        """Test ErrorResult initialization with default values."""
        message = "Error occurred"
        
        result = ErrorResult(message=message)
        
        assert result.message == message
        assert result.code == -32000  # Default code
        assert result.details == {}  # Default empty dict

    def test_init_with_none_details(self):
        """Test ErrorResult initialization with None details."""
        message = "Error message"
        code = -32000
        
        result = ErrorResult(message=message, code=code, details=None)
        
        assert result.message == message
        assert result.code == code
        assert result.details == {}  # Should be converted to empty dict

    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        message = "Invalid parameter"
        code = -32602
        details = {"param": "value", "expected": "string"}
        
        result = ErrorResult(message=message, code=code, details=details)
        dict_result = result.to_dict()
        
        assert dict_result["success"] is False
        assert dict_result["error"]["code"] == code
        assert dict_result["error"]["message"] == message
        assert dict_result["error"]["data"] == details

    def test_to_dict_without_details(self):
        """Test to_dict method without details."""
        message = "Simple error"
        code = -32000
        
        result = ErrorResult(message=message, code=code)
        dict_result = result.to_dict()
        
        assert dict_result["success"] is False
        assert dict_result["error"]["code"] == code
        assert dict_result["error"]["message"] == message
        assert "data" not in dict_result["error"]

    def test_to_dict_with_empty_details(self):
        """Test to_dict method with empty details."""
        message = "Error with empty details"
        
        result = ErrorResult(message=message, details={})
        dict_result = result.to_dict()
        
        assert dict_result["success"] is False
        assert dict_result["error"]["message"] == message
        assert "data" not in dict_result["error"]  # Empty details should not be included

    def test_get_schema(self):
        """Test get_schema method."""
        schema = ErrorResult.get_schema()
        
        assert schema["type"] == "object"
        assert "success" in schema["properties"]
        assert "error" in schema["properties"]
        assert schema["properties"]["success"]["type"] == "boolean"
        assert schema["properties"]["error"]["type"] == "object"
        assert "success" in schema["required"]
        assert "error" in schema["required"]
        
        # Check error object schema
        error_schema = schema["properties"]["error"]
        assert "code" in error_schema["properties"]
        assert "message" in error_schema["properties"]
        assert "data" in error_schema["properties"]
        assert "code" in error_schema["required"]
        assert "message" in error_schema["required"]

    def test_from_dict_with_all_fields(self):
        """Test from_dict method with all fields."""
        input_data = {
            "success": False,
            "error": {
                "code": -32601,
                "message": "Method not found",
                "data": {"method": "nonexistent", "available": ["help", "config"]}
            }
        }
        
        result = ErrorResult.from_dict(input_data)
        
        assert result.message == "Method not found"
        assert result.code == -32601
        assert result.details == {"method": "nonexistent", "available": ["help", "config"]}

    def test_from_dict_without_details(self):
        """Test from_dict method without details."""
        input_data = {
            "success": False,
            "error": {
                "code": -32000,
                "message": "Internal error"
            }
        }
        
        result = ErrorResult.from_dict(input_data)
        
        assert result.message == "Internal error"
        assert result.code == -32000
        # details should be empty dict when not provided in error object
        assert result.details == {}

    def test_from_dict_with_missing_error_fields(self):
        """Test from_dict method with missing error fields."""
        input_data = {
            "success": False,
            "error": {}
        }
        
        result = ErrorResult.from_dict(input_data)
        
        assert result.message == "Unknown error"  # Default message
        assert result.code == -32000  # Default code
        # details should be empty dict when not provided in error object
        assert result.details == {}

    def test_from_dict_with_missing_error(self):
        """Test from_dict method with missing error object."""
        input_data = {
            "success": False
        }
        
        result = ErrorResult.from_dict(input_data)
        
        assert result.message == "Unknown error"  # Default message
        assert result.code == -32000  # Default code
        # details should be empty dict when not provided in error object
        assert result.details == {}

    def test_json_rpc_compliance(self):
        """Test that ErrorResult follows JSON-RPC 2.0 specification."""
        message = "Parse error"
        code = -32700
        details = {"line": 10, "column": 5}
        
        result = ErrorResult(message=message, code=code, details=details)
        dict_result = result.to_dict()
        
        # Check JSON-RPC 2.0 error object structure
        assert "error" in dict_result
        error_obj = dict_result["error"]
        assert "code" in error_obj
        assert "message" in error_obj
        assert "data" in error_obj  # Additional data field
        
        # Check data types
        assert isinstance(error_obj["code"], int)
        assert isinstance(error_obj["message"], str)
        assert isinstance(error_obj["data"], dict)

    def test_standard_error_codes(self):
        """Test standard JSON-RPC 2.0 error codes."""
        # Parse error
        parse_error = ErrorResult("Parse error", -32700)
        assert parse_error.code == -32700
        
        # Invalid request
        invalid_request = ErrorResult("Invalid request", -32600)
        assert invalid_request.code == -32600
        
        # Method not found
        method_not_found = ErrorResult("Method not found", -32601)
        assert method_not_found.code == -32601
        
        # Invalid params
        invalid_params = ErrorResult("Invalid params", -32602)
        assert invalid_params.code == -32602
        
        # Internal error
        internal_error = ErrorResult("Internal error", -32603)
        assert internal_error.code == -32603

    def test_custom_error_codes(self):
        """Test custom error codes outside JSON-RPC 2.0 range."""
        # Custom error codes should work
        custom_error = ErrorResult("Custom error", -32001)
        assert custom_error.code == -32001
        
        # Positive error codes should work
        positive_error = ErrorResult("Positive error", 1001)
        assert positive_error.code == 1001

    def test_error_result_serialization(self):
        """Test that ErrorResult can be properly serialized to JSON."""
        message = "Test error message"
        code = -32000
        details = {"key": "value", "number": 42}
        
        result = ErrorResult(message=message, code=code, details=details)
        json_str = result.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["success"] is False
        assert parsed["error"]["message"] == message
        assert parsed["error"]["code"] == code
        assert parsed["error"]["data"] == details 