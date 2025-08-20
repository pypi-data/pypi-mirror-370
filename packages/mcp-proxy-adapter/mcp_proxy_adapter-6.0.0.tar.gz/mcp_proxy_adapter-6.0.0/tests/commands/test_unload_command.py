"""
Tests for unload command.
"""

import pytest
from unittest.mock import patch

from mcp_proxy_adapter.commands.unload_command import UnloadCommand, UnloadResult
from mcp_proxy_adapter.commands.command_registry import registry


class TestUnloadCommand:
    """Test cases for UnloadCommand."""
    
    def setup_method(self):
        """Setup test method."""
        self.command = UnloadCommand()
    
    def test_command_name(self):
        """Test command name."""
        assert UnloadCommand.name == "unload"
    
    def test_result_class(self):
        """Test result class."""
        assert UnloadCommand.result_class == UnloadResult
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful execution."""
        # Mock registry.unload_command to return success
        with patch.object(registry, 'unload_command') as mock_unload:
            mock_unload.return_value = {
                "success": True,
                "command_name": "test_command",
                "message": "Command 'test_command' unloaded successfully"
            }
            
            result = await self.command.execute(command_name="test_command")
            
            # Verify result
            assert isinstance(result, UnloadResult)
            assert result.data["success"] is True
            assert result.data["command_name"] == "test_command"
            assert "unloaded successfully" in result.message
            
            # Verify mock was called
            mock_unload.assert_called_once_with("test_command")
    
    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test failed execution."""
        # Mock registry.unload_command to return failure
        with patch.object(registry, 'unload_command') as mock_unload:
            mock_unload.return_value = {
                "success": False,
                "command_name": "test_command",
                "error": "Command not found"
            }
            
            result = await self.command.execute(command_name="test_command")
            
            # Verify result
            assert isinstance(result, UnloadResult)
            assert result.data["success"] is False
            assert result.data["command_name"] == "test_command"
            assert result.data["error"] == "Command not found"
            
            # Verify mock was called
            mock_unload.assert_called_once_with("test_command")
    
    def test_get_schema(self):
        """Test command schema."""
        schema = UnloadCommand.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "command_name" in schema["properties"]
        assert "required" in schema
        assert "command_name" in schema["required"]


class TestUnloadResult:
    """Test cases for UnloadResult."""
    
    def test_success_result(self):
        """Test successful result creation."""
        result = UnloadResult(
            success=True,
            command_name="test_command",
            message="Command unloaded successfully"
        )
        
        assert result.data["success"] is True
        assert result.data["command_name"] == "test_command"
        assert result.message == "Command unloaded successfully"
        assert "error" not in result.data
    
    def test_error_result(self):
        """Test error result creation."""
        result = UnloadResult(
            success=False,
            command_name="test_command",
            message="Failed to unload command",
            error="Command not found"
        )
        
        assert result.data["success"] is False
        assert result.data["command_name"] == "test_command"
        assert result.message == "Failed to unload command"
        assert result.data["error"] == "Command not found"
    
    def test_get_schema(self):
        """Test result schema."""
        schema = UnloadResult.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "data" in schema["properties"] 