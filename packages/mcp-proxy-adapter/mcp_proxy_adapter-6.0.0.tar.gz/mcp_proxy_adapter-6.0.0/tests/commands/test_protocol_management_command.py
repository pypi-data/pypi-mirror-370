"""
Tests for protocol management command.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from mcp_proxy_adapter.commands.protocol_management_command import ProtocolManagementCommand


class TestProtocolManagementCommand:
    """Test cases for ProtocolManagementCommand class."""
    
    def setup_method(self):
        """Setup test method."""
        self.command = ProtocolManagementCommand()
    
    def test_init(self):
        """Test command initialization."""
        assert self.command.name == "protocol_management"
        assert "protocol" in self.command.description.lower()
    
    def test_get_schema(self):
        """Test command schema."""
        schema = self.command.get_schema()
        
        assert schema["type"] == "object"
        assert "action" in schema["properties"]
        assert "protocol" in schema["properties"]
        assert "action" in schema["required"]
        
        action_enum = schema["properties"]["action"]["enum"]
        assert "get_info" in action_enum
        assert "validate_config" in action_enum
        assert "get_allowed" in action_enum
        assert "check_protocol" in action_enum
    
    @pytest.mark.asyncio
    async def test_execute_get_info_success(self):
        """Test execute with get_info action."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_protocol_info.return_value = {
                "http": {"enabled": True, "port": 8000}
            }
            mock_manager.get_allowed_protocols.return_value = ["http", "https"]
            mock_manager.validate_protocol_configuration.return_value = []
            mock_manager.enabled = True
            
            result = await self.command.execute(action="get_info")
            
            assert result.to_dict()["success"] is True
            assert "protocol_info" in result.data
            assert "allowed_protocols" in result.data
            assert "validation_errors" in result.data
    
    @pytest.mark.asyncio
    async def test_execute_validate_config_success(self):
        """Test execute with validate_config action."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.validate_protocol_configuration.return_value = []
            
            result = await self.command.execute(action="validate_config")
            
            assert result.to_dict()["success"] is True
            assert result.data["is_valid"] is True
            assert result.data["error_count"] == 0
    
    @pytest.mark.asyncio
    async def test_execute_validate_config_with_errors(self):
        """Test execute with validate_config action and errors."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.validate_protocol_configuration.return_value = ["Error 1", "Error 2"]
            
            result = await self.command.execute(action="validate_config")
            
            assert result.to_dict()["success"] is True
            assert result.data["is_valid"] is False
            assert result.data["error_count"] == 2
            assert len(result.data["validation_errors"]) == 2
    
    @pytest.mark.asyncio
    async def test_execute_get_allowed_success(self):
        """Test execute with get_allowed action."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_allowed_protocols.return_value = ["http", "https", "mtls"]
            
            result = await self.command.execute(action="get_allowed")
            
            assert result.to_dict()["success"] is True
            assert result.data["allowed_protocols"] == ["http", "https", "mtls"]
            assert result.data["count"] == 3
    
    @pytest.mark.asyncio
    async def test_execute_check_protocol_success(self):
        """Test execute with check_protocol action."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.is_protocol_allowed.return_value = True
            mock_manager.get_protocol_port.return_value = 8000
            mock_manager.get_protocol_config.return_value = {"enabled": True, "port": 8000}
            mock_manager.get_ssl_context_for_protocol.return_value = None
            
            result = await self.command.execute(action="check_protocol", protocol="http")
            
            assert result.to_dict()["success"] is True
            assert result.data["protocol"] == "http"
            assert result.data["is_allowed"] is True
            assert result.data["port"] == 8000
            assert result.data["enabled"] is True
            assert result.data["requires_ssl"] is False
    
    @pytest.mark.asyncio
    async def test_execute_check_protocol_https(self):
        """Test execute with check_protocol action for HTTPS."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.is_protocol_allowed.return_value = True
            mock_manager.get_protocol_port.return_value = 8443
            mock_manager.get_protocol_config.return_value = {"enabled": True, "port": 8443}
            mock_manager.get_ssl_context_for_protocol.return_value = MagicMock()
            
            result = await self.command.execute(action="check_protocol", protocol="https")
            
            assert result.to_dict()["success"] is True
            assert result.data["protocol"] == "https"
            assert result.data["requires_ssl"] is True
            assert result.data["ssl_context_available"] is True
    
    @pytest.mark.asyncio
    async def test_execute_check_protocol_missing_protocol(self):
        """Test execute with check_protocol action without protocol parameter."""
        result = await self.command.execute(action="check_protocol")
        
        assert result.to_dict()["success"] is False
        assert "Protocol parameter required" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_check_protocol_unknown(self):
        """Test execute with check_protocol action for unknown protocol."""
        result = await self.command.execute(action="check_protocol", protocol="unknown")
        
        assert result.to_dict()["success"] is False
        assert "Unknown protocol" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        """Test execute with unknown action."""
        result = await self.command.execute(action="unknown_action")
        
        assert result.to_dict()["success"] is False
        assert "Unknown action" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_exception_handling(self):
        """Test execute with exception handling."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_protocol_info.side_effect = Exception("Test error")
            
            result = await self.command.execute(action="get_info")
            
            assert result.to_dict()["success"] is False
            assert "Failed to get protocol info" in result.message
            assert "Test error" in result.message
    
    @pytest.mark.asyncio
    async def test_get_protocol_info_success(self):
        """Test _get_protocol_info method success."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_protocol_info.return_value = {
                "http": {"enabled": True, "port": 8000},
                "https": {"enabled": False, "port": 8443}
            }
            mock_manager.get_allowed_protocols.return_value = ["http"]
            mock_manager.validate_protocol_configuration.return_value = []
            mock_manager.enabled = True
            
            result = await self.command._get_protocol_info()
            
            assert result.to_dict()["success"] is True
            assert result.data["total_protocols"] == 2
            assert result.data["enabled_protocols"] == 1
            assert result.data["protocols_enabled"] is True
    
    @pytest.mark.asyncio
    async def test_get_protocol_info_exception(self):
        """Test _get_protocol_info method with exception."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_protocol_info.side_effect = Exception("Test error")
            
            result = await self.command._get_protocol_info()
            
            assert result.to_dict()["success"] is False
            assert "Failed to get protocol info" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_configuration_success(self):
        """Test _validate_configuration method success."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.validate_protocol_configuration.return_value = []
            
            result = await self.command._validate_configuration()
            
            assert result.to_dict()["success"] is True
            assert result.data["is_valid"] is True
            assert "passed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_configuration_with_errors(self):
        """Test _validate_configuration method with errors."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.validate_protocol_configuration.return_value = ["Error 1"]
            
            result = await self.command._validate_configuration()
            
            assert result.to_dict()["success"] is True
            assert result.data["is_valid"] is False
            assert "failed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_configuration_exception(self):
        """Test _validate_configuration method with exception."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.validate_protocol_configuration.side_effect = Exception("Test error")
            
            result = await self.command._validate_configuration()
            
            assert result.to_dict()["success"] is False
            assert "Failed to validate configuration" in result.message
    
    @pytest.mark.asyncio
    async def test_get_allowed_protocols_success(self):
        """Test _get_allowed_protocols method success."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_allowed_protocols.return_value = ["http", "https"]
            
            result = await self.command._get_allowed_protocols()
            
            assert result.to_dict()["success"] is True
            assert result.data["allowed_protocols"] == ["http", "https"]
            assert result.data["count"] == 2
    
    @pytest.mark.asyncio
    async def test_get_allowed_protocols_exception(self):
        """Test _get_allowed_protocols method with exception."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.get_allowed_protocols.side_effect = Exception("Test error")
            
            result = await self.command._get_allowed_protocols()
            
            assert result.to_dict()["success"] is False
            assert "Failed to get allowed protocols" in result.message
    
    @pytest.mark.asyncio
    async def test_check_protocol_success(self):
        """Test _check_protocol method success."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.is_protocol_allowed.return_value = True
            mock_manager.get_protocol_port.return_value = 8000
            mock_manager.get_protocol_config.return_value = {"enabled": True, "port": 8000}
            mock_manager.get_ssl_context_for_protocol.return_value = None
            
            result = await self.command._check_protocol("http")
            
            assert result.to_dict()["success"] is True
            assert result.data["protocol"] == "http"
            assert result.data["is_allowed"] is True
            assert result.data["port"] == 8000
            assert result.data["enabled"] is True
            assert result.data["requires_ssl"] is False
            assert result.data["ssl_context_available"] is None
    
    @pytest.mark.asyncio
    async def test_check_protocol_https_with_ssl(self):
        """Test _check_protocol method for HTTPS with SSL context."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.is_protocol_allowed.return_value = True
            mock_manager.get_protocol_port.return_value = 8443
            mock_manager.get_protocol_config.return_value = {"enabled": True, "port": 8443}
            mock_manager.get_ssl_context_for_protocol.return_value = MagicMock()
            
            result = await self.command._check_protocol("https")
            
            assert result.to_dict()["success"] is True
            assert result.data["protocol"] == "https"
            assert result.data["requires_ssl"] is True
            assert result.data["ssl_context_available"] is True
    
    @pytest.mark.asyncio
    async def test_check_protocol_exception(self):
        """Test _check_protocol method with exception."""
        with patch('mcp_proxy_adapter.commands.protocol_management_command.protocol_manager') as mock_manager:
            mock_manager.is_protocol_allowed.side_effect = Exception("Test error")
            
            result = await self.command._check_protocol("http")
            
            assert result.to_dict()["success"] is False
            assert "Failed to check protocol" in result.message 