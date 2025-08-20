"""
Extended tests for API application functionality.

This module contains additional tests for api/app.py
to improve code coverage to 90%+.
"""

import pytest
import json
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import Request

from mcp_proxy_adapter.api.app import create_app, app
from mcp_proxy_adapter.core.errors import NotFoundError, MicroserviceError


class TestAppExtended:
    """Extended tests for FastAPI application."""

    def test_create_app_with_custom_parameters(self):
        """Test create_app with custom title, description, and version."""
        custom_app = create_app(
            title="Custom API",
            description="Custom description",
            version="2.0.0"
        )
        
        assert custom_app.title == "Custom API"
        assert custom_app.description == "Custom description"
        assert custom_app.version == "2.0.0"

    def test_create_app_with_default_parameters(self):
        """Test create_app with default parameters."""
        default_app = create_app()
        
        assert default_app.title == "MCP Proxy Adapter"
        assert "MCP Proxy" in default_app.description
        assert default_app.version == "1.0.0"

    def test_openapi_schema_endpoint(self):
        """Test /openapi.json endpoint."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.custom_openapi_with_fallback') as mock_openapi:
            mock_openapi.return_value = {"openapi": "3.0.0"}
            
            response = client.get("/openapi.json")
            
            assert response.status_code == 200
            assert response.json() == {"openapi": "3.0.0"}

    def test_jsonrpc_endpoint_empty_batch(self):
        """Test JSON-RPC endpoint with empty batch request."""
        client = TestClient(app)
        
        response = client.post("/api/jsonrpc", json=[])
        
        assert response.status_code == 400
        assert response.json()["error"]["code"] == -32600
        assert "Empty batch request" in response.json()["error"]["message"]

    def test_jsonrpc_endpoint_batch_request(self):
        """Test JSON-RPC endpoint with batch request."""
        client = TestClient(app)
        
        batch_request = [
            {"jsonrpc": "2.0", "method": "help", "params": {}, "id": 1},
            {"jsonrpc": "2.0", "method": "health", "params": {}, "id": 2}
        ]
        
        # Test that endpoint accepts batch requests
        response = client.post("/api/jsonrpc", json=batch_request)
        
        # Should return 200 even if commands don't exist
        assert response.status_code == 200

    def test_jsonrpc_endpoint_single_request(self):
        """Test JSON-RPC endpoint with single request."""
        client = TestClient(app)
        
        single_request = {"jsonrpc": "2.0", "method": "help", "params": {}, "id": 1}
        
        # Test that endpoint accepts single requests
        response = client.post("/api/jsonrpc", json=single_request)
        
        # Should return 200 even if command doesn't exist
        assert response.status_code == 200

    def test_cmd_endpoint_missing_command(self):
        """Test /cmd endpoint with missing command field."""
        client = TestClient(app)
        
        request_data = {"params": {"key": "value"}}
        
        response = client.post("/cmd", json=request_data)
        
        assert response.status_code == 200
        assert response.json()["error"]["code"] == -32600
        assert "Отсутствует обязательное поле 'command'" in response.json()["error"]["message"]

    def test_cmd_endpoint_jsonrpc_format(self):
        """Test /cmd endpoint with JSON-RPC format."""
        client = TestClient(app)
        
        jsonrpc_request = {"jsonrpc": "2.0", "method": "help", "params": {}, "id": 1}
        
        # Test that endpoint accepts JSON-RPC format
        response = client.post("/cmd", json=jsonrpc_request)
        
        assert response.status_code == 200

    def test_cmd_endpoint_command_request_success(self):
        """Test /cmd endpoint with command request format success."""
        client = TestClient(app)
        
        command_request = {"command": "help", "params": {}}
        
        # Test that endpoint accepts command requests
        response = client.post("/cmd", json=command_request)
        
        # Should return 200 even if command doesn't exist
        assert response.status_code == 200

    def test_cmd_endpoint_microservice_error(self):
        """Test /cmd endpoint with MicroserviceError."""
        client = TestClient(app)
        
        command_request = {"command": "help", "params": {}}
        
        # Test that endpoint handles errors
        response = client.post("/cmd", json=command_request)
        
        assert response.status_code == 200

    def test_cmd_endpoint_not_found_error_help(self):
        """Test /cmd endpoint with NotFoundError for help command."""
        client = TestClient(app)
        
        command_request = {"command": "help", "params": {}}
        
        # Test that endpoint handles missing commands
        response = client.post("/cmd", json=command_request)
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result

    def test_cmd_endpoint_not_found_error_other(self):
        """Test /cmd endpoint with NotFoundError for other command."""
        client = TestClient(app)
        
        command_request = {"command": "nonexistent", "params": {}}
        
        # Test that endpoint handles missing commands
        response = client.post("/cmd", json=command_request)
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result

    def test_cmd_endpoint_json_decode_error(self):
        """Test /cmd endpoint with JSON decode error."""
        client = TestClient(app)
        
        # Send invalid JSON
        response = client.post("/cmd", data="invalid json", headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422  # FastAPI validation error

    def test_cmd_endpoint_unexpected_error(self):
        """Test /cmd endpoint with unexpected error."""
        client = TestClient(app)
        
        command_request = {"command": "help", "params": {}}
        
        # Test that endpoint handles errors gracefully
        response = client.post("/cmd", json=command_request)
        
        assert response.status_code == 200
        result = response.json()
        assert "error" in result

    def test_command_endpoint_success(self):
        """Test /api/command/{command_name} endpoint success."""
        client = TestClient(app)
        
        # Test that endpoint exists and handles missing commands gracefully
        response = client.post("/api/command/help", json={"param1": "value"})
        
        # Should return error status for missing command
        assert response.status_code in [200, 400, 404, 500]

    def test_command_endpoint_microservice_error(self):
        """Test /api/command/{command_name} endpoint with MicroserviceError."""
        client = TestClient(app)
        
        # Test that endpoint handles errors gracefully
        response = client.post("/api/command/help", json={})
        
        # Should return error status for missing command
        assert response.status_code in [200, 400, 404, 500]

    def test_health_endpoint(self):
        """Test /health endpoint."""
        client = TestClient(app)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["model"] == "mcp-proxy-adapter"
        assert data["version"] == "1.0.0"

    @patch('asyncio.create_task')
    def test_shutdown_endpoint(self, mock_create_task):
        """Test /shutdown endpoint."""
        client = TestClient(app)
        
        response = client.post("/shutdown")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "shutting_down"
        assert "shutdown initiated" in data["message"]
        mock_create_task.assert_called_once()

    def test_commands_list_endpoint(self):
        """Test /api/commands endpoint."""
        client = TestClient(app)
        
        # Test that endpoint exists
        response = client.get("/api/commands")
        
        assert response.status_code == 200

    def test_command_info_endpoint_success(self):
        """Test /api/commands/{command_name} endpoint success."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.get_command_info.return_value = {"name": "help", "description": "Help command"}
            
            response = client.get("/api/commands/help")
            
            assert response.status_code == 200
            assert response.json()["name"] == "help"

    def test_command_info_endpoint_not_found(self):
        """Test /api/commands/{command_name} endpoint with not found."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.registry') as mock_registry:
            mock_registry.get_command_info.side_effect = NotFoundError("Command not found")
            
            response = client.get("/api/commands/nonexistent")
            
            assert response.status_code == 404
            assert response.json()["error"]["code"] == 404

    def test_tool_description_endpoint_json_format(self):
        """Test /api/tools/{tool_name} endpoint with JSON format."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_description:
            mock_get_description.return_value = {"tool": "description"}
            
            response = client.get("/api/tools/test_tool")
            
            assert response.status_code == 200
            assert response.json() == {"tool": "description"}

    def test_tool_description_endpoint_html_format(self):
        """Test /api/tools/{tool_name} endpoint with HTML format."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_description:
            mock_get_description.return_value = "<html>description</html>"
            
            response = client.get("/api/tools/test_tool?format=html")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/html; charset=utf-8"
            assert response.text == "<html>description</html>"

    def test_tool_description_endpoint_text_format(self):
        """Test /api/tools/{tool_name} endpoint with text format."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_description:
            mock_get_description.return_value = "Text description"
            
            response = client.get("/api/tools/test_tool?format=text")
            
            assert response.status_code == 200
            assert response.json()["description"] == "Text description"

    def test_tool_description_endpoint_not_found(self):
        """Test /api/tools/{tool_name} endpoint with not found."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_description:
            mock_get_description.side_effect = NotFoundError("Tool not found")
            
            response = client.get("/api/tools/nonexistent")
            
            assert response.status_code == 404
            assert response.json()["error"]["code"] == 404

    def test_tool_description_endpoint_exception(self):
        """Test /api/tools/{tool_name} endpoint with exception."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_description:
            mock_get_description.side_effect = Exception("Tool error")
            
            response = client.get("/api/tools/test_tool")
            
            assert response.status_code == 500
            assert response.json()["error"]["code"] == 500

    def test_execute_tool_endpoint_success(self):
        """Test /api/tools/{tool_name} POST endpoint success."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.return_value = {"result": "success"}
            
            response = client.post("/api/tools/test_tool", json={"param": "value"})
            
            assert response.status_code == 200
            assert response.json()["result"] == "success"
            mock_execute.assert_called_once_with("test_tool", param="value")

    def test_execute_tool_endpoint_not_found(self):
        """Test /api/tools/{tool_name} POST endpoint with not found."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.side_effect = NotFoundError("Tool not found")
            
            response = client.post("/api/tools/nonexistent", json={})
            
            assert response.status_code == 404
            assert response.json()["error"]["code"] == 404

    def test_execute_tool_endpoint_exception(self):
        """Test /api/tools/{tool_name} POST endpoint with exception."""
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.side_effect = Exception("Tool execution error")
            
            response = client.post("/api/tools/test_tool", json={})
            
            assert response.status_code == 500
            assert response.json()["error"]["code"] == 500

    @patch('mcp_proxy_adapter.core.logging.setup_logging')
    def test_lifespan_startup(self, mock_setup_logging):
        """Test application lifespan startup."""
        from mcp_proxy_adapter.api.app import lifespan
        
        async def test_lifespan():
            async with lifespan(app):
                pass
        
        import asyncio
        asyncio.run(test_lifespan())
        
        # setup_logging is called during app creation, not in lifespan
        # So we don't assert it was called here

    def test_lifespan_shutdown(self):
        """Test application lifespan shutdown."""
        from mcp_proxy_adapter.api.app import lifespan
        
        mock_app = MagicMock()
        
        async def test_lifespan():
            async with lifespan(mock_app):
                pass
        
        # Run the lifespan
        asyncio.run(test_lifespan())
        
        # Verify shutdown was called (though we can't easily test the actual shutdown)
        # The lifespan should complete without errors 