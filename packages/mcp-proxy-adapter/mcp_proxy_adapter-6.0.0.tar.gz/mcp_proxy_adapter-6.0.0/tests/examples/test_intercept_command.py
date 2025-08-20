"""
Tests for intercept command example.

This module tests the intercept command functionality including:
- InterceptResult class
- InterceptCommand class
- Result serialization
- Command execution
- Different execution scenarios
"""

import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.examples.custom_commands import intercept_command


class TestInterceptResult:
    """Test InterceptResult class."""

    def test_init_with_all_parameters(self):
        """Test InterceptResult initialization with all parameters."""
        message = "Test message"
        executed = True
        intercept_reason = "test_reason"
        hook_data = {"hook": "data"}
        
        result = intercept_command.InterceptResult(
            message=message,
            executed=executed,
            intercept_reason=intercept_reason,
            hook_data=hook_data
        )
        
        assert result.message == message
        assert result.executed == executed
        assert result.intercept_reason == intercept_reason
        assert result.hook_data == hook_data

    def test_init_with_default_values(self):
        """Test InterceptResult initialization with default values."""
        message = "Test message"
        executed = False
        
        result = intercept_command.InterceptResult(
            message=message,
            executed=executed
        )
        
        assert result.message == message
        assert result.executed == executed
        assert result.intercept_reason is None
        assert result.hook_data == {}

    def test_init_with_none_hook_data(self):
        """Test InterceptResult initialization with None hook_data."""
        message = "Test message"
        executed = True
        
        result = intercept_command.InterceptResult(
            message=message,
            executed=executed,
            hook_data=None
        )
        
        assert result.message == message
        assert result.executed == executed
        assert result.hook_data == {}

    def test_to_dict(self):
        """Test to_dict method."""
        message = "Test message"
        executed = True
        intercept_reason = "test_reason"
        hook_data = {"hook": "data"}
        
        result = intercept_command.InterceptResult(
            message=message,
            executed=executed,
            intercept_reason=intercept_reason,
            hook_data=hook_data
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["message"] == message
        assert result_dict["executed"] == executed
        assert result_dict["intercept_reason"] == intercept_reason
        assert result_dict["hook_data"] == hook_data
        assert result_dict["command_type"] == "intercept"

    def test_get_schema(self):
        """Test get_schema method."""
        result = intercept_command.InterceptResult(
            message="test",
            executed=True
        )
        
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert "executed" in schema["properties"]
        assert "intercept_reason" in schema["properties"]
        assert "hook_data" in schema["properties"]
        assert "command_type" in schema["properties"]


class TestInterceptCommand:
    """Test InterceptCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = intercept_command.InterceptCommand()
        
        assert command.name == "intercept"
        assert command.result_class == intercept_command.InterceptResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = intercept_command.InterceptCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "action" in schema["properties"]
        assert "bypass_flag" in schema["properties"]
        assert schema["properties"]["action"]["type"] == "string"
        assert schema["properties"]["bypass_flag"]["type"] == "integer"
        assert "enum" in schema["properties"]["bypass_flag"]

    async def test_execute_with_all_parameters(self):
        """Test execute method with all parameters."""
        command = intercept_command.InterceptCommand()
        action = "test_action"
        bypass_flag = 1
        
        result = await command.execute(action=action, bypass_flag=bypass_flag)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == f"Command executed with action: {action}"
        assert result.executed is True
        assert result.intercept_reason is None
        assert result.hook_data == {}

    async def test_execute_without_parameters(self):
        """Test execute method without parameters."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute()
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == "Command executed with action: default"
        assert result.executed is True
        assert result.intercept_reason is None
        assert result.hook_data == {}

    async def test_execute_with_bypass_flag_zero(self):
        """Test execute method with bypass_flag = 0."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute(bypass_flag=0)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == "Command executed with action: default"
        assert result.executed is True
        assert result.intercept_reason is None
        assert result.hook_data == {}

    async def test_execute_with_bypass_flag_one(self):
        """Test execute method with bypass_flag = 1."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute(bypass_flag=1)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == "Command executed with action: default"
        assert result.executed is True
        assert result.intercept_reason is None
        assert result.hook_data == {}

    async def test_execute_with_custom_action(self):
        """Test execute method with custom action."""
        command = intercept_command.InterceptCommand()
        action = "custom_action"
        
        result = await command.execute(action=action)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == f"Command executed with action: {action}"
        assert result.executed is True

    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        command = intercept_command.InterceptCommand()
        extra_param = "extra_value"
        
        result = await command.execute(
            action="test",
            bypass_flag=1,
            extra_param=extra_param,
            another_param=123
        )
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.hook_data["extra_param"] == extra_param
        assert result.hook_data["another_param"] == 123

    async def test_execute_with_none_bypass_flag(self):
        """Test execute method with None bypass_flag."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute(bypass_flag=None)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == "Command executed with action: default"
        assert result.executed is True

    async def test_execute_with_none_action(self):
        """Test execute method with None action."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute(action=None)
        
        assert isinstance(result, intercept_command.InterceptResult)
        assert result.message == "Command executed with action: default"
        assert result.executed is True


class TestInterceptCommandIntegration:
    """Test intercept command integration."""

    async def test_command_execution_flow(self):
        """Test complete command execution flow."""
        command = intercept_command.InterceptCommand()
        
        result = await command.execute(
            action="test_action",
            bypass_flag=1,
            test="data"
        )
        
        # Verify result structure
        assert isinstance(result, intercept_command.InterceptResult)
        result_dict = result.to_dict()
        
        assert result_dict["command_type"] == "intercept"
        assert result_dict["message"] == "Command executed with action: test_action"
        assert result_dict["executed"] is True
        assert result_dict["intercept_reason"] is None
        assert result_dict["hook_data"]["test"] == "data"

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = intercept_command.InterceptCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify action property
        action_prop = schema["properties"]["action"]
        assert action_prop["type"] == "string"
        assert "description" in action_prop
        
        # Verify bypass_flag property
        bypass_prop = schema["properties"]["bypass_flag"]
        assert bypass_prop["type"] == "integer"
        assert "enum" in bypass_prop
        assert "description" in bypass_prop
        assert 0 in bypass_prop["enum"]
        assert 1 in bypass_prop["enum"]

    async def test_result_serialization(self):
        """Test result serialization."""
        result = intercept_command.InterceptResult(
            message="Test message",
            executed=True,
            intercept_reason="test_reason",
            hook_data={"key": "value"}
        )
        
        result_dict = result.to_dict()
        
        # Verify all fields are present
        assert "message" in result_dict
        assert "executed" in result_dict
        assert "intercept_reason" in result_dict
        assert "hook_data" in result_dict
        assert "command_type" in result_dict
        
        # Verify data types
        assert isinstance(result_dict["message"], str)
        assert isinstance(result_dict["executed"], bool)
        assert isinstance(result_dict["intercept_reason"], str)
        assert isinstance(result_dict["hook_data"], dict)
        assert isinstance(result_dict["command_type"], str) 