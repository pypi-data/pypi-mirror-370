"""
Tests for protocol middleware.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.protocol_middleware import ProtocolMiddleware, setup_protocol_middleware


class TestProtocolMiddleware:
    """Test cases for ProtocolMiddleware class."""
    
    def setup_method(self):
        """Setup test method."""
        self.mock_app = MagicMock()
        self.protocol_manager = MagicMock()
        self.middleware = ProtocolMiddleware(self.mock_app, self.protocol_manager)
    
    def test_init(self):
        """Test middleware initialization."""
        assert self.middleware.protocol_manager == self.protocol_manager
    
    def test_init_default_manager(self):
        """Test middleware initialization with default protocol manager."""
        middleware = ProtocolMiddleware(self.mock_app)
        assert middleware.protocol_manager is not None
    
    def test_get_request_protocol_from_url(self):
        """Test getting protocol from request URL."""
        mock_request = MagicMock()
        mock_request.url.scheme = "https"
        mock_request.headers = {}
        
        protocol = self.middleware._get_request_protocol(mock_request)
        assert protocol == "https"
    
    def test_get_request_protocol_from_headers(self):
        """Test getting protocol from request headers."""
        mock_request = MagicMock()
        mock_request.url.scheme = None
        mock_request.headers = {"x-forwarded-proto": "https"}
        
        protocol = self.middleware._get_request_protocol(mock_request)
        assert protocol == "https"
    
    def test_get_request_protocol_default(self):
        """Test getting protocol with default fallback."""
        mock_request = MagicMock()
        mock_request.url.scheme = None
        mock_request.headers = {}
        
        protocol = self.middleware._get_request_protocol(mock_request)
        assert protocol == "http"
    
    @pytest.mark.asyncio
    async def test_dispatch_protocol_allowed(self):
        """Test dispatch with allowed protocol."""
        mock_request = MagicMock()
        mock_request.url.scheme = "http"
        mock_request.url.path = "/test"
        mock_request.headers = {}
        
        mock_response = MagicMock()
        mock_call_next = AsyncMock(return_value=mock_response)
        
        self.protocol_manager.is_protocol_allowed.return_value = True
        
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
    
    @pytest.mark.asyncio
    async def test_dispatch_protocol_not_allowed(self):
        """Test dispatch with not allowed protocol."""
        mock_request = MagicMock()
        mock_request.url.scheme = "https"
        mock_request.url.path = "/test"
        mock_request.headers = {}
        
        mock_call_next = AsyncMock()
        
        self.protocol_manager.is_protocol_allowed.return_value = False
        self.protocol_manager.get_allowed_protocols.return_value = ["http"]
        
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 403
        
        content = response.body.decode()
        assert "Protocol not allowed" in content
        assert "https" in content
        assert "http" in content
        
        mock_call_next.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_dispatch_exception_handling(self):
        """Test dispatch with exception handling."""
        mock_request = MagicMock()
        mock_call_next = AsyncMock(side_effect=Exception("Test error"))
        
        response = await self.middleware.dispatch(mock_request, mock_call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = response.body.decode()
        assert "Protocol validation error" in content
        assert "Test error" in content


class TestSetupProtocolMiddleware:
    """Test cases for setup_protocol_middleware function."""
    
    def test_setup_protocol_middleware_enabled(self):
        """Test setup protocol middleware when enabled."""
        mock_app = MagicMock()
        mock_protocol_manager = MagicMock()
        mock_protocol_manager.enabled = True
        
        setup_protocol_middleware(mock_app, mock_protocol_manager)
        
        # Check that middleware was added
        mock_app.add_middleware.assert_called_once()
        args, kwargs = mock_app.add_middleware.call_args
        assert args[0] == ProtocolMiddleware
    
    def test_setup_protocol_middleware_disabled(self):
        """Test setup protocol middleware when disabled."""
        mock_app = MagicMock()
        mock_protocol_manager = MagicMock()
        mock_protocol_manager.enabled = False
        
        with patch('mcp_proxy_adapter.api.middleware.protocol_middleware.logger') as mock_logger:
            setup_protocol_middleware(mock_app, mock_protocol_manager)
            
            # Check that middleware was not added
            mock_app.add_middleware.assert_not_called()
            mock_logger.debug.assert_called_with("Protocol management is disabled, skipping protocol middleware")
    
    def test_setup_protocol_middleware_default_manager(self):
        """Test setup protocol middleware with default manager."""
        mock_app = MagicMock()
        
        with patch('mcp_proxy_adapter.api.middleware.protocol_middleware.protocol_manager') as mock_default_manager:
            mock_default_manager.enabled = True
            
            setup_protocol_middleware(mock_app)
            
            # Check that middleware was added with default manager
            mock_app.add_middleware.assert_called_once()
            args, kwargs = mock_app.add_middleware.call_args
            assert args[0] == ProtocolMiddleware 