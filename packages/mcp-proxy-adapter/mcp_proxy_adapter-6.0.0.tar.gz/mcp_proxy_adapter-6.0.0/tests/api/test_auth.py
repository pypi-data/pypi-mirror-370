"""
Tests for authentication middleware.
"""

import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.auth import AuthMiddleware


class TestAuthMiddleware:
    """Tests for AuthMiddleware."""

    def setup_method(self):
        """Set up test method."""
        self.app = MagicMock()
        self.api_keys = {"test-key": "test-user", "admin-key": "admin"}
        self.public_paths = ["/docs", "/health", "/public"]
        self.middleware = AuthMiddleware(
            app=self.app,
            api_keys=self.api_keys,
            public_paths=self.public_paths,
            auth_enabled=True
        )

    def test_init_default_values(self):
        """Test AuthMiddleware initialization with default values."""
        middleware = AuthMiddleware(self.app)
        
        assert middleware.api_keys == {}
        assert "/docs" in middleware.public_paths
        assert "/redoc" in middleware.public_paths
        assert "/openapi.json" in middleware.public_paths
        assert "/health" in middleware.public_paths
        assert middleware.auth_enabled is True

    def test_init_custom_values(self):
        """Test AuthMiddleware initialization with custom values."""
        custom_api_keys = {"key1": "user1", "key2": "user2"}
        custom_public_paths = ["/custom1", "/custom2"]
        
        middleware = AuthMiddleware(
            app=self.app,
            api_keys=custom_api_keys,
            public_paths=custom_public_paths,
            auth_enabled=False
        )
        
        assert middleware.api_keys == custom_api_keys
        assert middleware.public_paths == custom_public_paths
        assert middleware.auth_enabled is False

    @pytest.mark.asyncio
    async def test_dispatch_auth_disabled(self):
        """Test dispatch when authentication is disabled."""
        self.middleware.auth_enabled = False
        
        request = MagicMock(spec=Request)
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert response.body == b"success"

    @pytest.mark.asyncio
    async def test_dispatch_public_path(self):
        """Test dispatch for public paths."""
        request = MagicMock(spec=Request)
        request.url.path = "/docs"
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert response.body == b"success"

    @pytest.mark.asyncio
    async def test_dispatch_api_key_header(self):
        """Test dispatch with API key in header."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {"X-API-Key": "test-key"}
        request.state = MagicMock()
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert request.state.username == "test-user"
        assert response.body == b"success"

    @pytest.mark.asyncio
    async def test_dispatch_api_key_query(self):
        """Test dispatch with API key in query parameters."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {"api_key": "admin-key"}
        request.state = MagicMock()
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert request.state.username == "admin"
        assert response.body == b"success"

    @pytest.mark.asyncio
    async def test_dispatch_api_key_json_body(self):
        """Test dispatch with API key in JSON-RPC request body."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        request.state = MagicMock()
        
        # Mock request.body() to return JSON with API key
        body_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"api_key": "test-key"}
        }).encode("utf-8")
        request.body = AsyncMock(return_value=body_data)
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert request.state.username == "test-user"
        assert response.body == b"success"

    @pytest.mark.asyncio
    async def test_dispatch_api_key_json_body_invalid_json(self):
        """Test dispatch with invalid JSON in body."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return invalid JSON
        request.body = AsyncMock(return_value=b"invalid json")
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_api_key_json_body_exception(self):
        """Test dispatch when body reading raises exception."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to raise exception
        request.body = AsyncMock(side_effect=Exception("Body read error"))
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_no_api_key(self):
        """Test dispatch when no API key is provided."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "GET"
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_invalid_api_key(self):
        """Test dispatch with invalid API key."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {"X-API-Key": "invalid-key"}
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "Invalid API key" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_api_key_json_body_no_params(self):
        """Test dispatch with JSON body but no params."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return JSON without params
        body_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "test"
        }).encode("utf-8")
        request.body = AsyncMock(return_value=body_data)
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_api_key_json_body_params_no_api_key(self):
        """Test dispatch with JSON body with params but no API key."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return JSON with params but no API key
        body_data = json.dumps({
            "jsonrpc": "2.0",
            "method": "test",
            "params": {"other_param": "value"}
        }).encode("utf-8")
        request.body = AsyncMock(return_value=body_data)
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    def test_is_public_path_true(self):
        """Test _is_public_path returns True for public paths."""
        assert self.middleware._is_public_path("/docs") is True
        assert self.middleware._is_public_path("/health") is True
        assert self.middleware._is_public_path("/public") is True

    def test_is_public_path_false(self):
        """Test _is_public_path returns False for private paths."""
        assert self.middleware._is_public_path("/api/test") is False
        assert self.middleware._is_public_path("/private") is False

    def test_validate_api_key_valid(self):
        """Test _validate_api_key with valid API key."""
        username = self.middleware._validate_api_key("test-key")
        assert username == "test-user"

    def test_validate_api_key_invalid(self):
        """Test _validate_api_key with invalid API key."""
        username = self.middleware._validate_api_key("invalid-key")
        assert username is None

    def test_validate_api_key_empty(self):
        """Test _validate_api_key with empty API key."""
        username = self.middleware._validate_api_key("")
        assert username is None

    def test_validate_api_key_none(self):
        """Test _validate_api_key with None API key."""
        username = self.middleware._validate_api_key(None)
        assert username is None

    def test_create_error_response(self):
        """Test _create_error_response creates proper error response."""
        response = self.middleware._create_error_response("Test error", 401)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        
        content = json.loads(response.body.decode())
        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == -32000
        assert content["error"]["message"] == "Test error"
        assert content["id"] is None

    def test_create_error_response_different_status(self):
        """Test _create_error_response with different status code."""
        response = self.middleware._create_error_response("Forbidden", 403)
        
        assert response.status_code == 403
        
        content = json.loads(response.body.decode())
        assert content["jsonrpc"] == "2.0"
        assert content["error"]["code"] == -32000
        assert content["error"]["message"] == "Forbidden"
        assert content["id"] is None

    @pytest.mark.asyncio
    async def test_dispatch_successful_auth_logs_username(self):
        """Test that successful authentication logs the username."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {"X-API-Key": "test-key"}
        request.state = MagicMock()
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        with patch('mcp_proxy_adapter.api.middleware.auth.logger') as mock_logger:
            await self.middleware.dispatch(request, call_next)
            
            # Check that info log was called with username
            mock_logger.info.assert_called()
            call_args = mock_logger.info.call_args[0][0]
            assert "test-user" in call_args
            assert "/api/test" in call_args

    @pytest.mark.asyncio
    async def test_dispatch_failed_auth_logs_warning(self):
        """Test that failed authentication logs a warning."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {"X-API-Key": "invalid-key"}
        
        call_next = AsyncMock()
        
        with patch('mcp_proxy_adapter.api.middleware.auth.logger') as mock_logger:
            await self.middleware.dispatch(request, call_next)
            
            # Check that warning log was called
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "Invalid API key" in call_args
            assert "/api/test" in call_args

    @pytest.mark.asyncio
    async def test_dispatch_no_api_key_logs_warning(self):
        """Test that missing API key logs a warning."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "GET"
        
        call_next = AsyncMock()
        
        with patch('mcp_proxy_adapter.api.middleware.auth.logger') as mock_logger:
            await self.middleware.dispatch(request, call_next)
            
            # Check that warning log was called
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "API key not provided" in call_args
            assert "/api/test" in call_args

    @pytest.mark.asyncio
    async def test_dispatch_auth_disabled_logs_debug(self):
        """Test that disabled authentication logs debug message."""
        self.middleware.auth_enabled = False
        
        request = MagicMock(spec=Request)
        call_next = AsyncMock()
        call_next.return_value = Response(content="success")
        
        with patch('mcp_proxy_adapter.api.middleware.auth.logger') as mock_logger:
            await self.middleware.dispatch(request, call_next)
            
            # Check that debug log was called
            mock_logger.debug.assert_called()
            call_args = mock_logger.debug.call_args[0][0]
            assert "Authentication is disabled" in call_args

    def test_public_paths_contains_default_paths(self):
        """Test that default public paths are included."""
        middleware = AuthMiddleware(self.app)
        
        assert "/docs" in middleware.public_paths
        assert "/redoc" in middleware.public_paths
        assert "/openapi.json" in middleware.public_paths
        assert "/health" in middleware.public_paths

    def test_public_paths_custom_override(self):
        """Test that custom public paths override defaults."""
        custom_paths = ["/custom1", "/custom2"]
        middleware = AuthMiddleware(self.app, public_paths=custom_paths)
        
        assert middleware.public_paths == custom_paths
        assert "/docs" not in middleware.public_paths
        assert "/health" not in middleware.public_paths

    @pytest.mark.asyncio
    async def test_dispatch_json_body_not_dict(self):
        """Test dispatch with JSON body that is not a dict."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return JSON array
        body_data = json.dumps([1, 2, 3]).encode("utf-8")
        request.body = AsyncMock(return_value=body_data)
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_json_body_empty(self):
        """Test dispatch with empty JSON body."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return empty body
        request.body = AsyncMock(return_value=b"")
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode()

    @pytest.mark.asyncio
    async def test_dispatch_json_body_none(self):
        """Test dispatch with None body."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.headers = {}
        request.query_params = {}
        request.method = "POST"
        
        # Mock request.body() to return None
        request.body = AsyncMock(return_value=None)
        
        call_next = AsyncMock()
        
        response = await self.middleware.dispatch(request, call_next)
        
        call_next.assert_not_called()
        assert response.status_code == 401
        assert "API key not provided" in response.body.decode() 