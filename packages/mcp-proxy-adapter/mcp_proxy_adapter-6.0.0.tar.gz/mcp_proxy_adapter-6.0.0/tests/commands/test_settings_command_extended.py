"""
Extended tests for settings command.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.settings_command import SettingsResult, SettingsCommand


class TestSettingsResultExtended:
    """Extended tests for SettingsResult class."""
    
    def test_init_with_all_parameters(self):
        """Test SettingsResult initialization with all parameters."""
        result = SettingsResult(
            success=True,
            operation="get",
            key="test_key",
            value="test_value",
            all_settings={"test": "value"},
            error_message=None
        )
        
        assert result.to_dict()["success"] is True
        assert result.operation == "get"
        assert result.key == "test_key"
        assert result.value == "test_value"
        assert result.all_settings == {"test": "value"}
        assert result.error_message is None
    
    def test_to_dict_with_all_fields(self):
        """Test to_dict method with all fields."""
        result = SettingsResult(
            success=True,
            operation="get",
            key="test_key",
            value="test_value",
            all_settings={"test": "value"},
            error_message=None
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["operation"] == "get"
        assert data["key"] == "test_key"
        assert data["value"] == "test_value"
        assert data["all_settings"] == {"test": "value"}
        assert "error_message" not in data
    
    def test_to_dict_with_minimal_fields(self):
        """Test to_dict method with minimal fields."""
        result = SettingsResult(
            success=False,
            operation="unknown",
            error_message="Test error"
        )
        
        data = result.to_dict()
        assert data["success"] is False
        assert data["operation"] == "unknown"
        assert data["error_message"] == "Test error"
        assert "key" not in data
        assert "value" not in data
        assert "all_settings" not in data
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = SettingsResult(
            success=True,
            operation="get"
        ).get_schema()
        
        assert schema["type"] == "object"
        assert "success" in schema["properties"]
        assert "operation" in schema["properties"]
        assert "key" in schema["properties"]
        assert "value" in schema["properties"]
        assert "all_settings" in schema["properties"]
        assert "error_message" in schema["properties"]


class TestSettingsCommandExtended:
    """Extended tests for SettingsCommand class."""
    
    def test_name_and_description(self):
        """Test command name and description."""
        assert SettingsCommand.name == "settings"
        assert SettingsCommand.description == "Manage framework settings and configuration"
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = SettingsCommand.get_schema()
        
        assert schema["type"] == "object"
        assert "operation" in schema["properties"]
        assert "key" in schema["properties"]
        assert "value" in schema["properties"]
        assert schema["additionalProperties"] is False
    
    @patch('mcp_proxy_adapter.commands.settings_command.get_setting')
    async def test_execute_get_operation_success(self, mock_get_setting):
        """Test execute method with successful get operation."""
        mock_get_setting.return_value = "test_value"
        
        command = SettingsCommand()
        result = await command.execute(operation="get", key="test_key")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "get"
        assert result.key == "test_key"
        assert result.value == "test_value"
        assert result.error_message is None
        
        mock_get_setting.assert_called_once_with("test_key")
    
    @patch('mcp_proxy_adapter.commands.settings_command.get_setting')
    async def test_execute_get_operation_with_default(self, mock_get_setting):
        """Test execute method with get operation and default value."""
        mock_get_setting.return_value = "default_value"
        
        command = SettingsCommand()
        result = await command.execute(operation="get", key="test_key")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "get"
        assert result.key == "test_key"
        assert result.value == "default_value"
        
        mock_get_setting.assert_called_once_with("test_key")
    
    @patch('mcp_proxy_adapter.commands.settings_command.set_setting')
    async def test_execute_set_operation_success(self, mock_set_setting):
        """Test execute method with successful set operation."""
        command = SettingsCommand()
        result = await command.execute(operation="set", key="test_key", value="test_value")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "set"
        assert result.key == "test_key"
        assert result.value == "test_value"
        assert result.error_message is None
        
        mock_set_setting.assert_called_once_with("test_key", "test_value")
    
    @patch('mcp_proxy_adapter.commands.settings_command.set_setting')
    async def test_execute_set_operation_failure(self, mock_set_setting):
        """Test execute method with set operation failure."""
        mock_set_setting.side_effect = Exception("Set failed")
        
        command = SettingsCommand()
        result = await command.execute(operation="set", key="test_key", value="test_value")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "set"
        assert result.error_message == "Set failed"
    
    @patch('mcp_proxy_adapter.commands.settings_command.Settings')
    async def test_execute_get_all_operation_success(self, mock_settings):
        """Test execute method with successful get_all operation."""
        mock_settings.get_all_settings.return_value = {"test": "value", "app": {"version": "1.0.0"}}
        
        command = SettingsCommand()
        result = await command.execute(operation="get_all")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "get_all"
        assert result.all_settings == {"test": "value", "app": {"version": "1.0.0"}}
        assert result.error_message is None
        
        mock_settings.get_all_settings.assert_called_once()
    
    @patch('mcp_proxy_adapter.commands.settings_command.reload_settings')
    async def test_execute_reload_operation_success(self, mock_reload_settings):
        """Test execute method with successful reload operation."""
        command = SettingsCommand()
        result = await command.execute(operation="reload")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "reload"
        assert result.error_message is None
        
        mock_reload_settings.assert_called_once()
    
    @patch('mcp_proxy_adapter.commands.settings_command.reload_settings')
    async def test_execute_reload_operation_failure(self, mock_reload_settings):
        """Test execute method with reload operation failure."""
        mock_reload_settings.side_effect = Exception("Reload failed")
        
        command = SettingsCommand()
        result = await command.execute(operation="reload")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "reload"
        assert result.error_message == "Reload failed"
    
    async def test_execute_invalid_operation(self):
        """Test execute method with invalid operation."""
        command = SettingsCommand()
        result = await command.execute(operation="invalid")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "invalid"
        assert result.error_message == "Unknown operation: invalid. Supported operations: get, set, get_all, reload"
    
    async def test_execute_get_operation_missing_key(self):
        """Test execute method with get operation missing key."""
        command = SettingsCommand()
        result = await command.execute(operation="get")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "get"
        assert result.error_message == "Key is required for 'get' operation"
    
    async def test_execute_set_operation_missing_key(self):
        """Test execute method with set operation missing key."""
        command = SettingsCommand()
        result = await command.execute(operation="set", value="test_value")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "set"
        assert result.error_message == "Key is required for 'set' operation"
    
    async def test_execute_set_operation_missing_value(self):
        """Test execute method with set operation missing value."""
        command = SettingsCommand()
        result = await command.execute(operation="set", key="test_key")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is True
        assert result.operation == "set"
        assert result.key == "test_key"
        assert result.value is None
    
    @patch('mcp_proxy_adapter.commands.settings_command.get_setting')
    async def test_execute_get_operation_exception(self, mock_get_setting):
        """Test execute method with get operation exception."""
        mock_get_setting.side_effect = Exception("Get failed")
        
        command = SettingsCommand()
        result = await command.execute(operation="get", key="test_key")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "get"
        assert result.error_message == "Get failed"
    
    @patch('mcp_proxy_adapter.commands.settings_command.set_setting')
    async def test_execute_set_operation_exception(self, mock_set_setting):
        """Test execute method with set operation exception."""
        mock_set_setting.side_effect = Exception("Set failed")
        
        command = SettingsCommand()
        result = await command.execute(operation="set", key="test_key", value="test_value")
        
        assert isinstance(result, SettingsResult)
        assert result.to_dict()["success"] is False
        assert result.operation == "set"
        assert result.error_message == "Set failed"
    
    async def test_execute_default_operation(self):
        """Test execute method with default operation (get_all)."""
        with patch('mcp_proxy_adapter.commands.settings_command.Settings') as mock_settings:
            mock_settings.get_all_settings.return_value = {"default": "settings"}
            
            command = SettingsCommand()
            result = await command.execute()
            
            assert isinstance(result, SettingsResult)
            assert result.to_dict()["success"] is True
            assert result.operation == "get_all"
            assert result.all_settings == {"default": "settings"}
    
    async def test_execute_with_additional_kwargs(self):
        """Test execute method with additional kwargs."""
        with patch('mcp_proxy_adapter.commands.settings_command.get_setting') as mock_get_setting:
            mock_get_setting.return_value = "test_value"
            
            command = SettingsCommand()
            result = await command.execute(
                operation="get",
                key="test_key",
                extra_param="extra_value"
            )
            
            assert isinstance(result, SettingsResult)
            assert result.to_dict()["success"] is True
            assert result.operation == "get"
            assert result.key == "test_key"
            assert result.value == "test_value" 