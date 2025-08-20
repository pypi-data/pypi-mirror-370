"""
Tests for echo command example.

This module tests the echo command functionality including:
- EchoResult class
- EchoCommand class
- Result serialization
- Command execution
- Hook integration
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from mcp_proxy_adapter.examples.custom_commands import echo_command


class TestEchoResult:
    """Test EchoResult class."""

    def test_init_with_message_and_timestamp(self):
        """Test EchoResult initialization with message and timestamp."""
        message = "Test message"
        timestamp = "2023-01-01T12:00:00"
        
        result = echo_command.EchoResult(message=message, timestamp=timestamp)
        
        assert result.data["message"] == message
        assert result.data["timestamp"] == timestamp
        assert result.data["echoed"] is True

    def test_get_schema(self):
        """Test get_schema method."""
        schema = echo_command.EchoResult.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"]
        assert "required" in schema
        
        data_properties = schema["properties"]["data"]["properties"]
        assert "message" in data_properties
        assert "timestamp" in data_properties
        assert "echoed" in data_properties
        
        required_fields = schema["properties"]["data"]["required"]
        assert "message" in required_fields
        assert "timestamp" in required_fields
        assert "echoed" in required_fields


class TestEchoCommand:
    """Test EchoCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = echo_command.EchoCommand()
        
        assert command.name == "echo"
        assert command.result_class == echo_command.EchoResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = echo_command.EchoCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "message" in schema["properties"]
        assert "text" in schema["properties"]
        assert schema["properties"]["message"]["type"] == "string"
        assert schema["properties"]["text"]["type"] == "string"

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_message(self, mock_datetime):
        """Test execute method with message."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        message = "Custom message"
        
        result = await command.execute(message=message)
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == message
        assert result.data["timestamp"] == "2023-01-01T12:00:00"
        assert result.data["echoed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_without_message(self, mock_datetime):
        """Test execute method without message."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        
        result = await command.execute()
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == "Hello, World!"
        assert result.data["timestamp"] == "2023-01-01T12:00:00"
        assert result.data["echoed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_text_parameter(self, mock_datetime):
        """Test execute method with text parameter."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        text = "Text message"
        
        result = await command.execute(text=text)
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == text
        assert result.data["timestamp"] == "2023-01-01T12:00:00"
        assert result.data["echoed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_hook_timestamp(self, mock_datetime):
        """Test execute method with hook timestamp."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        hook_timestamp = "2023-01-01T11:00:00"
        
        result = await command.execute(
            message="test",
            hook_timestamp=hook_timestamp
        )
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == "test"
        assert result.data["timestamp"] == hook_timestamp
        assert result.data["echoed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_hook_processed(self, mock_datetime):
        """Test execute method with hook processed."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        hook_timestamp = "2023-01-01T11:00:00"
        
        result = await command.execute(
            message="test",
            hook_processed=True,
            hook_timestamp=hook_timestamp
        )
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["hook_processed"] is True
        assert result.data["hook_timestamp"] == hook_timestamp

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_none_message(self, mock_datetime):
        """Test execute method with None message."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        
        result = await command.execute(message=None)
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == "Hello, World!"
        assert result.data["timestamp"] == "2023-01-01T12:00:00"
        assert result.data["echoed"] is True

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_execute_with_additional_kwargs(self, mock_datetime):
        """Test execute method with additional kwargs."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        extra_param = "extra_value"
        
        result = await command.execute(
            message="test",
            extra_param=extra_param,
            another_param=123
        )
        
        assert isinstance(result, echo_command.EchoResult)
        assert result.data["message"] == "test"
        assert result.data["timestamp"] == "2023-01-01T12:00:00"
        assert result.data["echoed"] is True


class TestEchoCommandIntegration:
    """Test echo command integration."""

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_command_execution_flow(self, mock_datetime):
        """Test complete command execution flow."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        
        result = await command.execute(message="Hello World")
        
        # Verify result structure
        assert isinstance(result, echo_command.EchoResult)
        result_dict = result.to_dict()
        
        assert result_dict["data"]["message"] == "Hello World"
        assert result_dict["data"]["timestamp"] == "2023-01-01T12:00:00"
        assert result_dict["data"]["echoed"] is True

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = echo_command.EchoCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify message property
        message_prop = schema["properties"]["message"]
        assert message_prop["type"] == "string"
        assert "description" in message_prop
        assert "default" in message_prop
        assert message_prop["default"] == "Hello, World!"
        
        # Verify text property
        text_prop = schema["properties"]["text"]
        assert text_prop["type"] == "string"
        assert "description" in text_prop

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_result_serialization(self, mock_datetime):
        """Test result serialization."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        result = echo_command.EchoResult(
            message="Test message",
            timestamp="2023-01-01T12:00:00"
        )
        
        result_dict = result.to_dict()
        
        # Verify all fields are present
        assert "data" in result_dict
        assert "message" in result_dict["data"]
        assert "timestamp" in result_dict["data"]
        assert "echoed" in result_dict["data"]
        
        # Verify data types
        assert isinstance(result_dict["data"]["message"], str)
        assert isinstance(result_dict["data"]["timestamp"], str)
        assert isinstance(result_dict["data"]["echoed"], bool)

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_hook_integration(self, mock_datetime):
        """Test hook integration."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        
        # Test with hook timestamp
        result = await command.execute(
            message="test",
            hook_timestamp="2023-01-01T11:00:00",
            hook_processed=True
        )
        
        assert result.data["timestamp"] == "2023-01-01T11:00:00"
        assert result.data["hook_processed"] is True
        assert result.data["hook_timestamp"] == "2023-01-01T11:00:00"

    @patch('mcp_proxy_adapter.examples.custom_commands.echo_command.datetime')
    async def test_default_message_behavior(self, mock_datetime):
        """Test default message behavior."""
        mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        command = echo_command.EchoCommand()
        
        # Test with empty string
        result = await command.execute(message="")
        assert result.data["message"] == ""
        
        # Test with None
        result = await command.execute(message=None)
        assert result.data["message"] == "Hello, World!"
        
        # Test without parameter
        result = await command.execute()
        assert result.data["message"] == "Hello, World!"
        
        # Test with text parameter
        result = await command.execute(text="Text message")
        assert result.data["message"] == "Text message" 