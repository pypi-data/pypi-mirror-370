"""
Tests for auto echo command example.

This module tests the auto echo command functionality including:
- AutoEchoResult class
- AutoEchoCommand class
- Result serialization
- Command execution
"""

import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.examples.custom_commands.auto_commands import auto_echo_command


class TestAutoEchoResult:
    """Test AutoEchoResult class."""

    def test_init_with_message(self):
        """Test AutoEchoResult initialization with message."""
        message = "Test message"
        
        result = auto_echo_command.AutoEchoResult(message=message)
        
        assert result.message == message
        assert result.auto_registered is True

    def test_init_with_custom_auto_registered(self):
        """Test AutoEchoResult initialization with custom auto_registered."""
        message = "Test message"
        auto_registered = False
        
        result = auto_echo_command.AutoEchoResult(
            message=message,
            auto_registered=auto_registered
        )
        
        assert result.message == message
        assert result.auto_registered == auto_registered

    def test_to_dict(self):
        """Test to_dict method."""
        message = "Test message"
        
        result = auto_echo_command.AutoEchoResult(message=message)
        result_dict = result.to_dict()
        
        assert result_dict["message"] == message
        assert result_dict["auto_registered"] is True
        assert result_dict["command_type"] == "auto_echo"

    def test_get_schema(self):
        """Test get_schema method."""
        result = auto_echo_command.AutoEchoResult(message="test")
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert "auto_registered" in schema["properties"]
        assert "command_type" in schema["properties"]


class TestAutoEchoCommand:
    """Test AutoEchoCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = auto_echo_command.AutoEchoCommand()
        
        assert command.name == "auto_echo"
        assert command.result_class == auto_echo_command.AutoEchoResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = auto_echo_command.AutoEchoCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert schema["properties"]["message"]["type"] == "string"
        assert "description" in schema["properties"]["message"]
        assert "default" in schema["properties"]["message"]

    async def test_execute_with_message(self):
        """Test execute method with message."""
        command = auto_echo_command.AutoEchoCommand()
        message = "Custom message"
        
        result = await command.execute(message=message)
        
        assert isinstance(result, auto_echo_command.AutoEchoResult)
        assert result.message == message
        assert result.auto_registered is True

    async def test_execute_without_message(self):
        """Test execute method without message."""
        command = auto_echo_command.AutoEchoCommand()
        
        result = await command.execute()
        
        assert isinstance(result, auto_echo_command.AutoEchoResult)
        assert result.message == "Hello from auto-registered command!"
        assert result.auto_registered is True

    async def test_execute_with_none_message(self):
        """Test execute method with None message."""
        command = auto_echo_command.AutoEchoCommand()
        
        result = await command.execute(message=None)
        
        assert isinstance(result, auto_echo_command.AutoEchoResult)
        assert result.message == "Hello from auto-registered command!"
        assert result.auto_registered is True

    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        command = auto_echo_command.AutoEchoCommand()
        extra_param = "extra_value"
        
        result = await command.execute(
            message="test",
            extra_param=extra_param,
            another_param=123
        )
        
        assert isinstance(result, auto_echo_command.AutoEchoResult)
        assert result.message == "test"
        assert result.auto_registered is True


class TestAutoEchoCommandIntegration:
    """Test auto echo command integration."""

    async def test_command_execution_flow(self):
        """Test complete command execution flow."""
        command = auto_echo_command.AutoEchoCommand()
        
        result = await command.execute(message="Hello World")
        
        # Verify result structure
        assert isinstance(result, auto_echo_command.AutoEchoResult)
        result_dict = result.to_dict()
        
        assert result_dict["command_type"] == "auto_echo"
        assert result_dict["message"] == "Hello World"
        assert result_dict["auto_registered"] is True

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = auto_echo_command.AutoEchoCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify message property
        message_prop = schema["properties"]["message"]
        assert message_prop["type"] == "string"
        assert "description" in message_prop
        assert "default" in message_prop
        assert message_prop["default"] == "Hello from auto-registered command!"

    async def test_result_serialization(self):
        """Test result serialization."""
        result = auto_echo_command.AutoEchoResult(
            message="Test message",
            auto_registered=True
        )
        
        result_dict = result.to_dict()
        
        # Verify all fields are present
        assert "message" in result_dict
        assert "auto_registered" in result_dict
        assert "command_type" in result_dict
        
        # Verify data types
        assert isinstance(result_dict["message"], str)
        assert isinstance(result_dict["auto_registered"], bool)
        assert isinstance(result_dict["command_type"], str)

    async def test_default_message_behavior(self):
        """Test default message behavior."""
        command = auto_echo_command.AutoEchoCommand()
        
        # Test with empty string
        result = await command.execute(message="")
        assert result.message == ""
        
        # Test with None
        result = await command.execute(message=None)
        assert result.message == "Hello from auto-registered command!"
        
        # Test without parameter
        result = await command.execute()
        assert result.message == "Hello from auto-registered command!" 