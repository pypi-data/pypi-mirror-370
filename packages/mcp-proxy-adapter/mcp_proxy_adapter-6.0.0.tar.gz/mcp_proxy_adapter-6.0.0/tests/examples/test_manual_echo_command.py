"""
Tests for manual echo command example.

This module tests the manual echo command functionality including:
- ManualEchoResult class
- ManualEchoCommand class
- Result serialization
- Command execution
"""

import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.examples.custom_commands import manual_echo_command


class TestManualEchoResult:
    """Test ManualEchoResult class."""

    def test_init_with_message(self):
        """Test ManualEchoResult initialization with message."""
        message = "Test message"
        
        result = manual_echo_command.ManualEchoResult(message=message)
        
        assert result.message == message
        assert result.manually_registered is True

    def test_init_with_custom_manually_registered(self):
        """Test ManualEchoResult initialization with custom manually_registered."""
        message = "Test message"
        manually_registered = False
        
        result = manual_echo_command.ManualEchoResult(
            message=message,
            manually_registered=manually_registered
        )
        
        assert result.message == message
        assert result.manually_registered == manually_registered

    def test_to_dict(self):
        """Test to_dict method."""
        message = "Test message"
        
        result = manual_echo_command.ManualEchoResult(message=message)
        result_dict = result.to_dict()
        
        assert result_dict["message"] == message
        assert result_dict["manually_registered"] is True
        assert result_dict["command_type"] == "manual_echo"

    def test_get_schema(self):
        """Test get_schema method."""
        result = manual_echo_command.ManualEchoResult(message="test")
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert "manually_registered" in schema["properties"]
        assert "command_type" in schema["properties"]


class TestManualEchoCommand:
    """Test ManualEchoCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = manual_echo_command.ManualEchoCommand()
        
        assert command.name == "manual_echo"
        assert command.result_class == manual_echo_command.ManualEchoResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = manual_echo_command.ManualEchoCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert schema["properties"]["message"]["type"] == "string"
        assert "description" in schema["properties"]["message"]
        assert "default" in schema["properties"]["message"]

    async def test_execute_with_message(self):
        """Test execute method with message."""
        command = manual_echo_command.ManualEchoCommand()
        message = "Custom message"
        
        result = await command.execute(message=message)
        
        assert isinstance(result, manual_echo_command.ManualEchoResult)
        assert result.message == message
        assert result.manually_registered is True

    async def test_execute_without_message(self):
        """Test execute method without message."""
        command = manual_echo_command.ManualEchoCommand()
        
        result = await command.execute()
        
        assert isinstance(result, manual_echo_command.ManualEchoResult)
        assert result.message == "Hello from manually registered command!"
        assert result.manually_registered is True

    async def test_execute_with_none_message(self):
        """Test execute method with None message."""
        command = manual_echo_command.ManualEchoCommand()
        
        result = await command.execute(message=None)
        
        assert isinstance(result, manual_echo_command.ManualEchoResult)
        assert result.message == "Hello from manually registered command!"
        assert result.manually_registered is True

    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        command = manual_echo_command.ManualEchoCommand()
        extra_param = "extra_value"
        
        result = await command.execute(
            message="test",
            extra_param=extra_param,
            another_param=123
        )
        
        assert isinstance(result, manual_echo_command.ManualEchoResult)
        assert result.message == "test"
        assert result.manually_registered is True


class TestManualEchoCommandIntegration:
    """Test manual echo command integration."""

    async def test_command_execution_flow(self):
        """Test complete command execution flow."""
        command = manual_echo_command.ManualEchoCommand()
        
        result = await command.execute(message="Hello World")
        
        # Verify result structure
        assert isinstance(result, manual_echo_command.ManualEchoResult)
        result_dict = result.to_dict()
        
        assert result_dict["command_type"] == "manual_echo"
        assert result_dict["message"] == "Hello World"
        assert result_dict["manually_registered"] is True

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = manual_echo_command.ManualEchoCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify message property
        message_prop = schema["properties"]["message"]
        assert message_prop["type"] == "string"
        assert "description" in message_prop
        assert "default" in message_prop
        assert message_prop["default"] == "Hello from manually registered command!"

    async def test_result_serialization(self):
        """Test result serialization."""
        result = manual_echo_command.ManualEchoResult(
            message="Test message",
            manually_registered=True
        )
        
        result_dict = result.to_dict()
        
        # Verify all fields are present
        assert "message" in result_dict
        assert "manually_registered" in result_dict
        assert "command_type" in result_dict
        
        # Verify data types
        assert isinstance(result_dict["message"], str)
        assert isinstance(result_dict["manually_registered"], bool)
        assert isinstance(result_dict["command_type"], str)

    async def test_default_message_behavior(self):
        """Test default message behavior."""
        command = manual_echo_command.ManualEchoCommand()
        
        # Test with empty string
        result = await command.execute(message="")
        assert result.message == ""
        
        # Test with None
        result = await command.execute(message=None)
        assert result.message == "Hello from manually registered command!"
        
        # Test without parameter
        result = await command.execute()
        assert result.message == "Hello from manually registered command!"

    async def test_manual_registration_flag(self):
        """Test manual registration flag behavior."""
        command = manual_echo_command.ManualEchoCommand()
        
        # Test with default manually_registered
        result = await command.execute(message="test")
        assert result.manually_registered is True
        
        # Test with custom manually_registered in result creation
        custom_result = manual_echo_command.ManualEchoResult(
            message="test",
            manually_registered=False
        )
        assert custom_result.manually_registered is False 