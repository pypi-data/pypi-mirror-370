"""
Tests for error handling middleware.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.error_handling import ErrorHandlingMiddleware
from mcp_proxy_adapter.core.errors import MicroserviceError, CommandError, ValidationError


class TestErrorHandlingMiddleware:
    """Tests for ErrorHandlingMiddleware."""

    def setup_method(self):
        """Set up test method."""
        # Create a mock app for middleware initialization
        mock_app = MagicMock()
        self.middleware = ErrorHandlingMiddleware(mock_app)

    def test_is_json_rpc_request_true(self):
        """Test _is_json_rpc_request with JSON-RPC path."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        
        result = self.middleware._is_json_rpc_request(request)
        
        assert result is True

    def test_is_json_rpc_request_false(self):
        """Test _is_json_rpc_request with non-JSON-RPC path."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/health"
        
        result = self.middleware._is_json_rpc_request(request)
        
        assert result is False

    @pytest.mark.asyncio
    async def test_get_json_rpc_id_from_state(self):
        """Test _get_json_rpc_id when ID is already in request state."""
        request = MagicMock(spec=Request)
        request.state.json_rpc_id = "test-id"
        
        result = await self.middleware._get_json_rpc_id(request)
        
        assert result == "test-id"

    @pytest.mark.asyncio
    async def test_get_json_rpc_id_from_body(self):
        """Test _get_json_rpc_id when parsing from request body."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        delattr(request.state, 'json_rpc_id')
        
        # Mock request body
        body_data = {"jsonrpc": "2.0", "method": "test", "id": "body-id"}
        request.body = AsyncMock(return_value=json.dumps(body_data).encode())
        
        result = await self.middleware._get_json_rpc_id(request)
        
        assert result == "body-id"
        assert request.state.json_rpc_id == "body-id"

    @pytest.mark.asyncio
    async def test_get_json_rpc_id_no_body(self):
        """Test _get_json_rpc_id with empty body."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        delattr(request.state, 'json_rpc_id')
        request.body = AsyncMock(return_value=b"")
        
        result = await self.middleware._get_json_rpc_id(request)
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_json_rpc_id_parse_error(self, caplog):
        """Test _get_json_rpc_id with JSON parse error."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        delattr(request.state, 'json_rpc_id')
        request.body = AsyncMock(return_value=b"invalid json")
        
        result = await self.middleware._get_json_rpc_id(request)
        
        assert result is None
        assert "Error parsing JSON-RPC ID: Expecting value: line 1 column 1 (char 0)" in caplog.text

    @pytest.mark.asyncio
    async def test_dispatch_success(self):
        """Test dispatch with successful request."""
        request = MagicMock(spec=Request)
        response = JSONResponse(content={"success": True})
        call_next = AsyncMock(return_value=response)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result == response
        call_next.assert_called_once_with(request)

    @pytest.mark.asyncio
    async def test_dispatch_command_error_jsonrpc(self, caplog):
        """Test dispatch with CommandError in JSON-RPC context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = CommandError("Test command error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000
        assert "Test command error" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_command_error_regular(self, caplog):
        """Test dispatch with CommandError in regular context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/health"
        request.state.json_rpc_id = "test-request"
        
        error = CommandError("Test command error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["code"] == -32000
        assert "Test command error" in data["message"]

    @pytest.mark.asyncio
    async def test_dispatch_validation_error_jsonrpc(self, caplog):
        """Test dispatch with ValidationError in JSON-RPC context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = ValidationError("Test validation error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32602
        assert "Invalid params" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_validation_error_regular(self, caplog):
        """Test dispatch with ValidationError in regular context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/health"
        request.state.json_rpc_id = "test-request"
        
        error = ValidationError("Test validation error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["code"] == -32602
        assert "Test validation error" in data["message"]

    @pytest.mark.asyncio
    async def test_dispatch_microservice_error_jsonrpc(self, caplog):
        """Test dispatch with MicroserviceError in JSON-RPC context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = MicroserviceError("Test microservice error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000
        assert "Test microservice error" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_microservice_error_regular(self, caplog):
        """Test dispatch with MicroserviceError in regular context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/health"
        request.state.json_rpc_id = "test-request"
        
        error = MicroserviceError("Test microservice error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["code"] == -32000
        assert "Test microservice error" in data["message"]

    @pytest.mark.asyncio
    async def test_dispatch_unexpected_error_jsonrpc(self, caplog):
        """Test dispatch with unexpected error in JSON-RPC context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = Exception("Unexpected error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 500
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32603
        assert "Internal error" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_unexpected_error_regular(self, caplog):
        """Test dispatch with unexpected error in regular context."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/health"
        request.state.json_rpc_id = "test-request"
        
        error = Exception("Unexpected error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 500
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == 500
        assert "Internal server error" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_dispatch_command_error_with_details(self, caplog):
        """Test dispatch with CommandError that has details."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = CommandError("Test command error", data={"key": "value"})
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000
        assert "Test command error" in data["error"]["message"]
        assert data["error"]["data"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_dispatch_validation_error_with_details(self, caplog):
        """Test dispatch with ValidationError that has details."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = ValidationError("Test validation error", data={"key": "value"})
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32602
        assert "Invalid params" in data["error"]["message"]
        assert data["error"]["data"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_dispatch_microservice_error_with_details(self, caplog):
        """Test dispatch with MicroserviceError that has details."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = "test-request"
        
        error = MicroserviceError("Test microservice error", data={"key": "value"})
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000
        assert "Test microservice error" in data["error"]["message"]
        assert data["error"]["data"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_dispatch_no_request_id(self, caplog):
        """Test dispatch when no request ID is available."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state = MagicMock()
        delattr(request.state, 'json_rpc_id')
        request.body = AsyncMock(return_value=b"")
        
        error = CommandError("Test command error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000

    @pytest.mark.asyncio
    async def test_dispatch_no_jsonrpc_id(self, caplog):
        """Test dispatch when JSON-RPC ID is not available."""
        request = MagicMock(spec=Request)
        request.url.path = "/api/jsonrpc"
        request.state.json_rpc_id = None
        
        error = CommandError("Test command error")
        call_next = AsyncMock(side_effect=error)
        
        result = await self.middleware.dispatch(request, call_next)
        
        assert result.status_code == 400
        data = json.loads(result.body.decode())
        assert data["error"]["code"] == -32000 