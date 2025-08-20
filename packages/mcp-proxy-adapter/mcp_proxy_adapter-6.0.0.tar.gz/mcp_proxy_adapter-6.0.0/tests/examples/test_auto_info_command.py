"""
Tests for auto info command example.

This module tests the auto info command functionality including:
- AutoInfoResult class
- AutoInfoCommand class
- Result serialization
- Command execution
"""

import pytest
from unittest.mock import MagicMock

from mcp_proxy_adapter.examples.custom_commands.auto_commands import auto_info_command


class TestAutoInfoResult:
    """Test AutoInfoResult class."""

    def test_init_with_info(self):
        """Test AutoInfoResult initialization with info."""
        info = {"topic": "test", "data": "value"}
        
        result = auto_info_command.AutoInfoResult(info=info)
        
        assert result.info == info
        assert result.auto_registered is True

    def test_init_with_custom_auto_registered(self):
        """Test AutoInfoResult initialization with custom auto_registered."""
        info = {"topic": "test"}
        auto_registered = False
        
        result = auto_info_command.AutoInfoResult(
            info=info,
            auto_registered=auto_registered
        )
        
        assert result.info == info
        assert result.auto_registered == auto_registered

    def test_to_dict(self):
        """Test to_dict method."""
        info = {"topic": "test", "data": "value"}
        
        result = auto_info_command.AutoInfoResult(info=info)
        result_dict = result.to_dict()
        
        assert result_dict["info"] == info
        assert result_dict["auto_registered"] is True
        assert result_dict["command_type"] == "auto_info"

    def test_get_schema(self):
        """Test get_schema method."""
        result = auto_info_command.AutoInfoResult(info={"test": "data"})
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "info" in schema["properties"]
        assert "auto_registered" in schema["properties"]
        assert "command_type" in schema["properties"]


class TestAutoInfoCommand:
    """Test AutoInfoCommand class."""

    def test_name_and_result_class(self):
        """Test command name and result class."""
        command = auto_info_command.AutoInfoCommand()
        
        assert command.name == "auto_info"
        assert command.result_class == auto_info_command.AutoInfoResult

    def test_get_schema(self):
        """Test get_schema class method."""
        schema = auto_info_command.AutoInfoCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "topic" in schema["properties"]
        assert schema["properties"]["topic"]["type"] == "string"
        assert "description" in schema["properties"]["topic"]
        assert "default" in schema["properties"]["topic"]

    async def test_execute_with_topic(self):
        """Test execute method with topic."""
        command = auto_info_command.AutoInfoCommand()
        topic = "custom_topic"
        
        result = await command.execute(topic=topic)
        
        assert isinstance(result, auto_info_command.AutoInfoResult)
        assert result.info["topic"] == topic
        assert result.info["auto_registered"] is True
        assert result.info["discovery_method"] == "automatic"
        assert result.info["registration_time"] == "startup"
        assert result.info["command_type"] == "auto_info"
        assert result.auto_registered is True

    async def test_execute_without_topic(self):
        """Test execute method without topic."""
        command = auto_info_command.AutoInfoCommand()
        
        result = await command.execute()
        
        assert isinstance(result, auto_info_command.AutoInfoResult)
        assert result.info["topic"] == "general"
        assert result.info["auto_registered"] is True
        assert result.auto_registered is True

    async def test_execute_with_none_topic(self):
        """Test execute method with None topic."""
        command = auto_info_command.AutoInfoCommand()
        
        result = await command.execute(topic=None)
        
        assert isinstance(result, auto_info_command.AutoInfoResult)
        assert result.info["topic"] == "general"
        assert result.info["auto_registered"] is True
        assert result.auto_registered is True

    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        command = auto_info_command.AutoInfoCommand()
        extra_param = "extra_value"
        
        result = await command.execute(
            topic="test",
            extra_param=extra_param,
            another_param=123
        )
        
        assert isinstance(result, auto_info_command.AutoInfoResult)
        assert result.info["topic"] == "test"
        assert result.info["auto_registered"] is True
        assert result.auto_registered is True


class TestAutoInfoCommandIntegration:
    """Test auto info command integration."""

    async def test_command_execution_flow(self):
        """Test complete command execution flow."""
        command = auto_info_command.AutoInfoCommand()
        
        result = await command.execute(topic="system_info")
        
        # Verify result structure
        assert isinstance(result, auto_info_command.AutoInfoResult)
        result_dict = result.to_dict()
        
        assert result_dict["command_type"] == "auto_info"
        assert result_dict["info"]["topic"] == "system_info"
        assert result_dict["info"]["auto_registered"] is True
        assert result_dict["info"]["discovery_method"] == "automatic"
        assert result_dict["info"]["registration_time"] == "startup"
        assert result_dict["info"]["command_type"] == "auto_info"
        assert result_dict["auto_registered"] is True

    async def test_schema_validation(self):
        """Test schema validation."""
        schema = auto_info_command.AutoInfoCommand.get_schema()
        
        # Verify schema structure
        assert schema["type"] == "object"
        assert "properties" in schema
        
        # Verify topic property
        topic_prop = schema["properties"]["topic"]
        assert topic_prop["type"] == "string"
        assert "description" in topic_prop
        assert "default" in topic_prop
        assert topic_prop["default"] == "general"

    async def test_result_serialization(self):
        """Test result serialization."""
        info_data = {
            "topic": "test",
            "data": "value",
            "auto_registered": True
        }
        
        result = auto_info_command.AutoInfoResult(
            info=info_data,
            auto_registered=True
        )
        
        result_dict = result.to_dict()
        
        # Verify all fields are present
        assert "info" in result_dict
        assert "auto_registered" in result_dict
        assert "command_type" in result_dict
        
        # Verify data types
        assert isinstance(result_dict["info"], dict)
        assert isinstance(result_dict["auto_registered"], bool)
        assert isinstance(result_dict["command_type"], str)

    async def test_default_topic_behavior(self):
        """Test default topic behavior."""
        command = auto_info_command.AutoInfoCommand()
        
        # Test with empty string
        result = await command.execute(topic="")
        assert result.info["topic"] == ""
        
        # Test with None
        result = await command.execute(topic=None)
        assert result.info["topic"] == "general"
        
        # Test without parameter
        result = await command.execute()
        assert result.info["topic"] == "general"

    async def test_info_data_structure(self):
        """Test info data structure."""
        command = auto_info_command.AutoInfoCommand()
        
        result = await command.execute(topic="custom_topic")
        
        # Verify all expected fields are present
        expected_fields = ["topic", "auto_registered", "discovery_method", "registration_time", "command_type"]
        for field in expected_fields:
            assert field in result.info
        
        # Verify field values
        assert result.info["topic"] == "custom_topic"
        assert result.info["auto_registered"] is True
        assert result.info["discovery_method"] == "automatic"
        assert result.info["registration_time"] == "startup"
        assert result.info["command_type"] == "auto_info" 