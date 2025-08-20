"""
Tests for proxy registration functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from mcp_proxy_adapter.core.proxy_registration import (
    ProxyRegistrationManager,
    register_with_proxy,
    unregister_from_proxy,
    get_proxy_registration_status,
    proxy_registration_manager
)
from mcp_proxy_adapter.config import config


class TestProxyRegistrationManager:
    """Test cases for ProxyRegistrationManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ProxyRegistrationManager()
        self.manager.registration_config = {
            "enabled": True,
            "proxy_url": "http://localhost:3004",
            "server_id": "test_server",
            "server_name": "Test Server",
            "description": "Test server for proxy registration",
            "registration_timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 5,
            "auto_register_on_startup": True,
            "auto_unregister_on_shutdown": True
        }
    
    def test_is_enabled(self):
        """Test is_enabled method."""
        assert self.manager.is_enabled() is True
        
        self.manager.registration_config["enabled"] = False
        assert self.manager.is_enabled() is False
    
    def test_set_server_url(self):
        """Test set_server_url method."""
        test_url = "http://localhost:8000"
        self.manager.set_server_url(test_url)
        assert self.manager.server_url == test_url
    
    @pytest.mark.asyncio
    async def test_register_server_success(self):
        """Test successful server registration."""
        self.manager.server_url = "http://localhost:8000"
        
        with patch('mcp_proxy_adapter.core.proxy_registration.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"success": True, "server_key": "test_server_1"})
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await self.manager.register_server()
            
            assert result is True
            assert self.manager.registered is True
            assert self.manager.server_key == "test_server_1"
    
    @pytest.mark.asyncio
    async def test_register_server_failure(self):
        """Test failed server registration."""
        self.manager.server_url = "http://localhost:8000"
        
        with patch('mcp_proxy_adapter.core.proxy_registration.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 400
            mock_response.json = AsyncMock(return_value={
                "success": False, 
                "error": {"message": "Server unavailable"}
            })
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await self.manager.register_server()
            
            assert result is False
            assert self.manager.registered is False
            assert self.manager.server_key is None
    
    @pytest.mark.asyncio
    async def test_register_server_disabled(self):
        """Test registration when disabled."""
        self.manager.registration_config["enabled"] = False
        result = await self.manager.register_server()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_register_server_no_url(self):
        """Test registration without server URL."""
        result = await self.manager.register_server()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_unregister_server_success(self):
        """Test successful server unregistration."""
        self.manager.registered = True
        self.manager.server_key = "test_server_1"
        
        with patch('mcp_proxy_adapter.core.proxy_registration.aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"success": True, "unregistered": True})
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
            
            result = await self.manager.unregister_server()
            
            assert result is True
            assert self.manager.registered is False
            assert self.manager.server_key is None
    
    @pytest.mark.asyncio
    async def test_unregister_server_not_registered(self):
        """Test unregistration when not registered."""
        result = await self.manager.unregister_server()
        assert result is True  # Should succeed even if not registered
    
    def test_get_registration_status(self):
        """Test get_registration_status method."""
        self.manager.registered = True
        self.manager.server_key = "test_server_1"
        self.manager.server_url = "http://localhost:8000"
        
        status = self.manager.get_registration_status()
        
        assert status["enabled"] is True
        assert status["registered"] is True
        assert status["server_key"] == "test_server_1"
        assert status["server_url"] == "http://localhost:8000"
        assert status["proxy_url"] == "http://localhost:3004"
        assert status["server_id"] == "test_server"


class TestProxyRegistrationFunctions:
    """Test cases for proxy registration functions."""
    
    @pytest.mark.asyncio
    async def test_register_with_proxy(self):
        """Test register_with_proxy function."""
        with patch.object(proxy_registration_manager, 'set_server_url') as mock_set_url, \
             patch.object(proxy_registration_manager, 'register_server', return_value=True) as mock_register:
            
            result = await register_with_proxy("http://localhost:8000")
            
            mock_set_url.assert_called_once_with("http://localhost:8000")
            mock_register.assert_called_once()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_unregister_from_proxy(self):
        """Test unregister_from_proxy function."""
        with patch.object(proxy_registration_manager, 'unregister_server', return_value=True) as mock_unregister:
            result = await unregister_from_proxy()
            
            mock_unregister.assert_called_once()
            assert result is True
    
    def test_get_proxy_registration_status(self):
        """Test get_proxy_registration_status function."""
        with patch.object(proxy_registration_manager, 'get_registration_status') as mock_get_status:
            mock_get_status.return_value = {"enabled": True, "registered": False}
            
            status = get_proxy_registration_status()
            
            mock_get_status.assert_called_once()
            assert status["enabled"] is True
            assert status["registered"] is False


class TestProxyRegistrationIntegration:
    """Integration tests for proxy registration."""
    
    @pytest.mark.asyncio
    async def test_full_registration_cycle(self):
        """Test complete registration cycle."""
        manager = ProxyRegistrationManager()
        manager.registration_config["enabled"] = True
        manager.server_url = "http://localhost:8000"
        
        # Mock successful registration
        with patch('mcp_proxy_adapter.core.proxy_registration.aiohttp.ClientSession') as mock_session:
            # Registration response
            mock_reg_response = AsyncMock()
            mock_reg_response.status = 200
            mock_reg_response.json = AsyncMock(return_value={"success": True, "server_key": "test_server_1"})
            
            # Unregistration response
            mock_unreg_response = AsyncMock()
            mock_unreg_response.status = 200
            mock_unreg_response.json = AsyncMock(return_value={"success": True, "unregistered": True})
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.side_effect = [
                mock_reg_response, mock_unreg_response
            ]
            
            # Register
            reg_result = await manager.register_server()
            assert reg_result is True
            assert manager.registered is True
            assert manager.server_key == "test_server_1"
            
            # Unregister
            unreg_result = await manager.unregister_server()
            assert unreg_result is True
            assert manager.registered is False
            assert manager.server_key is None 