"""
Tests for reload command.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mcp_proxy_adapter.commands.reload_command import ReloadCommand, ReloadResult
from mcp_proxy_adapter.commands.command_registry import registry


class TestReloadCommand:
    """Test reload command."""
    
    def setup_method(self):
        """Setup test method."""
        self.command = ReloadCommand()
    
    def test_get_schema(self):
        """Test command schema."""
        schema = self.command.get_schema()
        
        assert schema["type"] == "object"
        assert "config_path" in schema["properties"]
        assert schema["properties"]["config_path"]["type"] == "string"
        assert schema["properties"]["config_path"]["description"] == "Path to configuration file to reload"
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful reload execution."""
        mock_result = {
            "config_reloaded": True,
            "builtin_commands": 5,
            "custom_commands": 2,
            "loaded_commands": 3,
            "total_commands": 10
        }
        
        with patch.object(registry, 'reload_system', return_value=mock_result):
            result = await self.command.execute(config_path="/path/to/config.json")
        
        assert isinstance(result, ReloadResult)
        assert result.to_dict()["success"] is True
        assert result.config_reloaded is True
        assert result.builtin_commands == 5
        assert result.custom_commands == 2
        assert result.loaded_commands == 3
        assert result.total_commands == 10
        assert result.server_restart_required is True
        assert result.error_message is None
    
    @pytest.mark.asyncio
    async def test_execute_without_config_path(self):
        """Test reload execution without config path."""
        mock_result = {
            "config_reloaded": True,
            "builtin_commands": 5,
            "custom_commands": 0,
            "loaded_commands": 0,
            "total_commands": 5
        }
        
        with patch.object(registry, 'reload_system', return_value=mock_result):
            result = await self.command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.to_dict()["success"] is True
        assert result.config_reloaded is True
    
    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test reload execution failure."""
        with patch.object(registry, 'reload_system', side_effect=Exception("Test error")):
            result = await self.command.execute(config_path="/path/to/config.json")
        
        assert isinstance(result, ReloadResult)
        assert result.to_dict()["success"] is False
        assert result.config_reloaded is False
        assert result.builtin_commands == 0
        assert result.custom_commands == 0
        assert result.loaded_commands == 0
        assert result.total_commands == 0
        assert result.server_restart_required is False
        assert result.error_message == "Test error"
    
    @pytest.mark.asyncio
    async def test_execute_with_missing_result_fields(self):
        """Test reload execution with missing result fields."""
        mock_result = {
            "config_reloaded": True
            # Missing other fields
        }
        
        with patch.object(registry, 'reload_system', return_value=mock_result):
            result = await self.command.execute()
        
        assert isinstance(result, ReloadResult)
        assert result.to_dict()["success"] is True
        assert result.config_reloaded is True
        assert result.builtin_commands == 0  # Default value
        assert result.custom_commands == 0   # Default value
        assert result.loaded_commands == 0   # Default value
        assert result.total_commands == 0    # Default value


class TestReloadResult:
    """Test reload result."""
    
    def test_to_dict(self):
        """Test result to dictionary conversion."""
        result = ReloadResult(
            config_reloaded=True,
            builtin_commands=5,
            custom_commands=2,
            loaded_commands=3,
            total_commands=10,
            server_restart_required=True,
            success=True
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is True
        assert result_dict["config_reloaded"] is True
        assert result_dict["builtin_commands"] == 5
        assert result_dict["custom_commands"] == 2
        assert result_dict["loaded_commands"] == 3
        assert result_dict["total_commands"] == 10
        assert result_dict["server_restart_required"] is True
        assert result_dict["message"] == "Server restart required to apply configuration changes"
        assert result_dict["error_message"] is None
    
    def test_to_dict_with_error(self):
        """Test result to dictionary conversion with error."""
        result = ReloadResult(
            config_reloaded=False,
            builtin_commands=0,
            custom_commands=0,
            loaded_commands=0,
            total_commands=0,
            server_restart_required=False,
            success=False,
            error_message="Test error"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["success"] is False
        assert result_dict["config_reloaded"] is False
        assert result_dict["error_message"] == "Test error"
    
    def test_get_schema(self):
        """Test result schema."""
        result = ReloadResult(
            config_reloaded=True,
            builtin_commands=5,
            custom_commands=2,
            loaded_commands=3,
            total_commands=10,
            server_restart_required=True,
            success=True
        )
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        required_fields = [
            "success", "config_reloaded", "builtin_commands", "custom_commands",
            "loaded_commands", "total_commands", "server_restart_required"
        ]
        
        for field in required_fields:
            assert field in schema["required"]
        
        # Check specific field types
        assert schema["properties"]["success"]["type"] == "boolean"
        assert schema["properties"]["config_reloaded"]["type"] == "boolean"
        assert schema["properties"]["builtin_commands"]["type"] == "integer"
        assert schema["properties"]["custom_commands"]["type"] == "integer"
        assert schema["properties"]["loaded_commands"]["type"] == "integer"
        assert schema["properties"]["total_commands"]["type"] == "integer"
        assert schema["properties"]["server_restart_required"]["type"] == "boolean"
        assert schema["properties"]["error_message"]["type"] == ["string", "null"] 