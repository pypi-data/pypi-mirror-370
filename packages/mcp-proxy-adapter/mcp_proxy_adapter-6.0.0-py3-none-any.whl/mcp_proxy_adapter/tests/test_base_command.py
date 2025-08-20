"""
Tests for command base classes.
"""

import pytest
from typing import Dict, Any

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult, SuccessResult, ErrorResult


class MockResultClass(CommandResult):
    """Test result class for testing."""
    
    def __init__(self, value: str):
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value}
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "string"}
            },
            "required": ["value"]
        }


class MockCommand(Command):
    """Test command for testing."""
    
    name = "test_command"
    result_class = MockResultClass
    
    async def execute(self, value: str = "default") -> MockResultClass:
        return MockResultClass(value)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "value": {"type": "string"}
            },
            "additionalProperties": False
        }


def test_success_result():
    """Test success result class."""
    result = SuccessResult(data={"key": "value"}, message="success message")
    
    # Test to_dict method
    result_dict = result.to_dict()
    assert result_dict["success"] is True
    assert result_dict["data"] == {"key": "value"}
    assert result_dict["message"] == "success message"
    
    # Test from_dict method
    result2 = SuccessResult.from_dict(result_dict)
    assert result2.data == {"key": "value"}
    assert result2.message == "success message"


def test_error_result():
    """Test error result class."""
    result = ErrorResult(message="error message", code=400, details={"field": "invalid"})
    
    # Test to_dict method
    result_dict = result.to_dict()
    assert result_dict["success"] is False
    assert result_dict["error"]["code"] == 400
    assert result_dict["error"]["message"] == "error message"
    assert result_dict["error"]["data"] == {"field": "invalid"}
    
    # Test from_dict method
    result2 = ErrorResult.from_dict(result_dict)
    assert result2.message == "error message"
    assert result2.code == 400
    assert result2.details == {"field": "invalid"}


class CommandClassTests:
    """Test command class."""
    
    @pytest.mark.asyncio
    async def test_execute(self):
        """Test execute method."""
        command = MockCommand()
        result = await command.execute(value="test_value")
        assert isinstance(result, MockResultClass)
        assert result.value == "test_value"
    
    @pytest.mark.asyncio
    async def test_run(self):
        """Test run method (with validation)."""
        result = await MockCommand.run(value="test_value")
        assert isinstance(result, MockResultClass)
        assert result.value == "test_value"
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = MockCommand.get_schema()
        assert schema["type"] == "object"
        assert "value" in schema["properties"]
        assert schema["additionalProperties"] is False
    
    def test_get_result_schema(self):
        """Test get_result_schema method."""
        schema = MockCommand.get_result_schema()
        assert schema["type"] == "object"
        assert "value" in schema["properties"]
        assert "value" in schema["required"]
    
    def test_get_param_info(self):
        """Test get_param_info method."""
        params = MockCommand.get_param_info()
        assert "value" in params
        assert params["value"]["required"] is False
        assert params["value"]["default"] == "default" 