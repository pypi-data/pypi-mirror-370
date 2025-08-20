"""
Unit tests for Transport Middleware.

This module contains unit tests for the transport middleware functionality.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request
from fastapi.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.transport_middleware import TransportMiddleware
from mcp_proxy_adapter.core.transport_manager import TransportType


class TestTransportMiddleware:
    """Test cases for TransportMiddleware."""
    
    def setup_method(self):
        """Setup test method."""
        self.app = MagicMock()
        self.transport_manager_mock = MagicMock()
        self.middleware = TransportMiddleware(self.app, self.transport_manager_mock)
    
    def test_init_with_custom_manager(self):
        """Test initialization with custom transport manager."""
        custom_manager = MagicMock()
        middleware = TransportMiddleware(self.app, custom_manager)
        
        assert middleware.transport_manager == custom_manager
    
    def test_init_with_default_manager(self):
        """Test initialization with default transport manager."""
        middleware = TransportMiddleware(self.app)
        
        assert middleware.transport_manager is not None
    
    @pytest.mark.asyncio
    async def test_dispatch_http_allowed(self):
        """Test dispatch with HTTP transport allowed."""
        # Setup transport manager
        self.transport_manager_mock.get_transport_type.return_value = TransportType.HTTP
        
        # Setup request
        request = MagicMock(spec=Request)
        request.url.scheme = "http"
        request.state = MagicMock()
        
        # Setup call_next
        call_next = AsyncMock()
        call_next.return_value = JSONResponse(content={"test": "response"})
        
        # Execute
        response = await self.middleware.dispatch(request, call_next)
        
        # Verify
        assert response.status_code == 200
        assert response.body == b'{"test":"response"}'
        assert request.state.transport_type == "http"
        assert request.state.transport_allowed == True
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_dispatch_https_allowed(self):
        """Test dispatch with HTTPS transport allowed."""
        # Setup transport manager
        self.transport_manager_mock.get_transport_type.return_value = TransportType.HTTPS
        self.transport_manager_mock.is_mtls.return_value = False
        
        # Setup request
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.headers = {}
        request.client = None
        request.state = MagicMock()
        
        # Setup call_next
        call_next = AsyncMock()
        call_next.return_value = JSONResponse(content={"test": "response"})
        
        # Execute
        response = await self.middleware.dispatch(request, call_next)
        
        # Verify
        assert response.status_code == 200
        assert response.body == b'{"test":"response"}'
        assert request.state.transport_type == "https"
        assert request.state.transport_allowed == True
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_dispatch_mtls_allowed(self):
        """Test dispatch with MTLS transport allowed."""
        # Setup transport manager
        self.transport_manager_mock.get_transport_type.return_value = TransportType.MTLS
        self.transport_manager_mock.is_mtls.return_value = True
        
        # Setup request
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.headers = {"ssl-client-cert": "test-cert"}
        request.state = MagicMock()
        
        # Setup call_next
        call_next = AsyncMock()
        call_next.return_value = JSONResponse(content={"test": "response"})
        
        # Execute
        response = await self.middleware.dispatch(request, call_next)
        
        # Verify
        assert response.status_code == 200
        assert response.body == b'{"test":"response"}'
        assert request.state.transport_type == "mtls"
        assert request.state.transport_allowed == True
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_dispatch_transport_not_allowed(self):
        """Test dispatch with transport not allowed."""
        # Setup transport manager
        self.transport_manager_mock.get_transport_type.return_value = TransportType.HTTP
        
        # Setup request
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.url.__str__ = MagicMock(return_value="https://localhost:8443/test")
        
        # Setup call_next
        call_next = AsyncMock()
        
        # Execute
        response = await self.middleware.dispatch(request, call_next)
        
        # Verify
        assert response.status_code == 403
        response_content = response.body.decode()
        assert "Transport not allowed" in response_content
        assert "https" in response_content
        assert "http" in response_content
        call_next.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_dispatch_transport_not_configured(self):
        """Test dispatch when transport is not configured."""
        # Setup transport manager
        self.transport_manager_mock.get_transport_type.return_value = None
        
        # Setup request
        request = MagicMock(spec=Request)
        request.url.scheme = "http"
        
        # Setup call_next
        call_next = AsyncMock()
        
        # Execute
        response = await self.middleware.dispatch(request, call_next)
        
        # Verify
        assert response.status_code == 403
        response_content = response.body.decode()
        assert "Transport not allowed" in response_content
        call_next.assert_not_called()
    
    def test_get_request_transport_type_http(self):
        """Test getting transport type for HTTP request."""
        request = MagicMock(spec=Request)
        request.url.scheme = "http"
        
        transport_type = self.middleware._get_request_transport_type(request)
        
        assert transport_type == "http"
    
    def test_get_request_transport_type_https(self):
        """Test getting transport type for HTTPS request."""
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.headers = {}
        request.client = None
        
        # Mock is_mtls to return False
        self.transport_manager_mock.is_mtls.return_value = False
        
        transport_type = self.middleware._get_request_transport_type(request)
        
        assert transport_type == "https"
    
    def test_get_request_transport_type_mtls_with_header(self):
        """Test getting transport type for MTLS request with header."""
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.headers = {"ssl-client-cert": "test-cert"}
        
        transport_type = self.middleware._get_request_transport_type(request)
        
        assert transport_type == "mtls"
    
    def test_get_request_transport_type_mtls_with_client(self):
        """Test getting transport type for MTLS request with client."""
        request = MagicMock(spec=Request)
        request.url.scheme = "https"
        request.headers = {}
        request.client = MagicMock()
        
        # Mock is_mtls to return True
        self.transport_manager_mock.is_mtls.return_value = True
        
        transport_type = self.middleware._get_request_transport_type(request)
        
        assert transport_type == "mtls"
    
    def test_has_client_certificate_with_header(self):
        """Test client certificate detection with header."""
        request = MagicMock(spec=Request)
        request.headers = {"ssl-client-cert": "test-cert"}
        
        has_cert = self.middleware._has_client_certificate(request)
        
        assert has_cert == True
    
    def test_has_client_certificate_with_client(self):
        """Test client certificate detection with client."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = MagicMock()
        
        # Mock is_mtls to return True
        self.transport_manager_mock.is_mtls.return_value = True
        
        has_cert = self.middleware._has_client_certificate(request)
        
        assert has_cert == True
    
    def test_has_client_certificate_no_cert(self):
        """Test client certificate detection without certificate."""
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None
        
        has_cert = self.middleware._has_client_certificate(request)
        
        assert has_cert == False
    
    def test_is_transport_allowed_same_type(self):
        """Test transport allowed check with same type."""
        self.transport_manager_mock.get_transport_type.return_value = TransportType.HTTPS
        
        is_allowed = self.middleware._is_transport_allowed("https")
        
        assert is_allowed == True
    
    def test_is_transport_allowed_different_type(self):
        """Test transport allowed check with different type."""
        self.transport_manager_mock.get_transport_type.return_value = TransportType.HTTP
        
        is_allowed = self.middleware._is_transport_allowed("https")
        
        assert is_allowed == False
    
    def test_is_transport_allowed_not_configured(self):
        """Test transport allowed check when not configured."""
        self.transport_manager_mock.get_transport_type.return_value = None
        
        is_allowed = self.middleware._is_transport_allowed("http")
        
        assert is_allowed == False 