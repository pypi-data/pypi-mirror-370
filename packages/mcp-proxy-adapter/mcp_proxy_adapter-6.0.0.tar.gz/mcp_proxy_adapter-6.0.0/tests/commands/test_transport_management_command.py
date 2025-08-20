"""
Unit tests for TransportManagementCommand.

This module contains unit tests for the transport management command functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from mcp_proxy_adapter.commands.transport_management_command import (
    TransportManagementCommand,
    TransportManagementResult
)
from mcp_proxy_adapter.core.transport_manager import TransportType


class TestTransportManagementCommand:
    """Test cases for TransportManagementCommand."""
    
    def setup_method(self):
        """Setup test method."""
        self.command = TransportManagementCommand()
    
    def test_get_schema(self):
        """Test command schema."""
        schema = self.command.get_schema()
        
        assert schema["type"] == "object"
        assert "action" in schema["properties"]
        assert schema["properties"]["action"]["type"] == "string"
        assert "get_info" in schema["properties"]["action"]["enum"]
        assert "validate" in schema["properties"]["action"]["enum"]
        assert "reload" in schema["properties"]["action"]["enum"]
        assert "action" in schema["required"]
    
    @pytest.mark.asyncio
    async def test_execute_get_info(self):
        """Test execute with get_info action."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.get_transport_info.return_value = {
                "type": "https",
                "port": 8443,
                "ssl_enabled": True
            }
            
            result = await self.command.execute(action="get_info")
            
            assert isinstance(result, TransportManagementResult)
            assert result.data["transport_info"]["type"] == "https"
            assert result.data["transport_info"]["port"] == 8443
            assert result.data["transport_info"]["ssl_enabled"] == True
            assert "Transport information retrieved successfully" in result.message
            mock_manager.get_transport_info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_validate(self):
        """Test execute with validate action."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.validate_config.return_value = True
            mock_manager.get_transport_info.return_value = {
                "type": "https",
                "port": 8443,
                "ssl_enabled": True
            }
            
            result = await self.command.execute(action="validate")
            
            assert isinstance(result, TransportManagementResult)
            assert result.data["transport_info"]["validation"]["is_valid"] == True
            assert "Transport configuration validated successfully" in result.message
            mock_manager.validate_config.assert_called_once()
            mock_manager.get_transport_info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_validate_failed(self):
        """Test execute with validate action when validation fails."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.validate_config.return_value = False
            mock_manager.get_transport_info.return_value = {
                "type": "https",
                "port": 8443,
                "ssl_enabled": True
            }
            
            result = await self.command.execute(action="validate")
            
            assert isinstance(result, TransportManagementResult)
            assert result.data["transport_info"]["validation"]["is_valid"] == False
            assert "Transport configuration validation failed" in result.message
            mock_manager.validate_config.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_reload(self):
        """Test execute with reload action."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.get_transport_info.return_value = {
                "type": "https",
                "port": 8443,
                "ssl_enabled": True
            }
            
            result = await self.command.execute(action="reload")
            
            assert isinstance(result, TransportManagementResult)
            assert result.data["transport_info"]["reload"]["status"] == "completed"
            assert "Transport configuration reload completed" in result.message
            mock_manager.get_transport_info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_unknown_action(self):
        """Test execute with unknown action."""
        result = await self.command.execute(action="unknown")
        
        assert isinstance(result, TransportManagementResult)
        assert "error" in result.data["transport_info"]
        assert result.data["transport_info"]["error"] == "Unknown action: unknown"
        assert "Unknown action: unknown" in result.message
    
    @pytest.mark.asyncio
    async def test_execute_default_action(self):
        """Test execute with default action (get_info)."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.get_transport_info.return_value = {
                "type": "http",
                "port": 8000,
                "ssl_enabled": False
            }
            
            result = await self.command.execute()
            
            assert isinstance(result, TransportManagementResult)
            assert result.data["transport_info"]["type"] == "http"
            assert "Transport information retrieved successfully" in result.message
            mock_manager.get_transport_info.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_exception_handling(self):
        """Test execute with exception handling."""
        with patch('mcp_proxy_adapter.commands.transport_management_command.transport_manager') as mock_manager:
            mock_manager.get_transport_info.side_effect = Exception("Test error")
            
            result = await self.command.execute(action="get_info")
            
            assert isinstance(result, TransportManagementResult)
            assert "error" in result.data["transport_info"]
            assert result.data["transport_info"]["error"] == "Test error"
            assert "Transport management failed: Test error" in result.message


class TestTransportManagementResult:
    """Test cases for TransportManagementResult."""
    
    def test_init(self):
        """Test TransportManagementResult initialization."""
        transport_info = {
            "type": "https",
            "port": 8443,
            "ssl_enabled": True
        }
        
        result = TransportManagementResult(transport_info, "Test message")
        
        assert result.data["transport_info"] == transport_info
        assert result.message == "Test message"
    
    def test_init_default_message(self):
        """Test TransportManagementResult initialization with default message."""
        transport_info = {
            "type": "http",
            "port": 8000,
            "ssl_enabled": False
        }
        
        result = TransportManagementResult(transport_info)
        
        assert result.data["transport_info"] == transport_info
        assert "Transport management operation completed" in result.message
    
    def test_to_dict(self):
        """Test TransportManagementResult to_dict method."""
        transport_info = {
            "type": "mtls",
            "port": 9443,
            "ssl_enabled": True
        }
        
        result = TransportManagementResult(transport_info, "MTLS configured")
        result_dict = result.to_dict()
        
        assert result_dict["success"] == True
        assert result_dict["data"]["transport_info"] == transport_info
        assert result_dict["message"] == "MTLS configured" 