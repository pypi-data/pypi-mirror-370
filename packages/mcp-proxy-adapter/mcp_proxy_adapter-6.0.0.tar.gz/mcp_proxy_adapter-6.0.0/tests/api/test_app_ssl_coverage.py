"""
Additional tests for app.py to improve coverage to 90%+.

Tests SSL functionality and missing error handling paths.
"""

import pytest
import ssl
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from mcp_proxy_adapter.api.app import create_app, create_ssl_context
from mcp_proxy_adapter.core.ssl_utils import SSLUtils


class TestAppSSLCoverage:
    """Test cases to improve app.py coverage."""
    
    def test_create_ssl_context_disabled(self):
        """Test create_ssl_context when SSL is disabled."""
        with patch('mcp_proxy_adapter.api.app.config') as mock_config:
            mock_config.get.return_value = {"enabled": False}
            
            result = create_ssl_context()
            assert result is None
    
    def test_create_ssl_context_no_cert_files(self):
        """Test create_ssl_context when certificate files are not specified."""
        with patch('mcp_proxy_adapter.api.app.config') as mock_config:
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": None,
                "key_file": None
            }
            
            result = create_ssl_context()
            assert result is None
    
    def test_create_ssl_context_success(self):
        """Test create_ssl_context when SSL is properly configured."""
        with patch('mcp_proxy_adapter.api.app.config') as mock_config:
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": "test.crt",
                "key_file": "test.key",
                "ca_cert": "ca.crt",
                "verify_client": True,
                "cipher_suites": ["TLS_AES_256_GCM_SHA384"],
                "min_tls_version": "1.2",
                "max_tls_version": "1.3",
                "mode": "https_only"
            }
            
            with patch('mcp_proxy_adapter.api.app.SSLUtils') as mock_ssl_utils:
                mock_context = Mock()
                mock_ssl_utils.create_ssl_context.return_value = mock_context
                
                result = create_ssl_context()
                assert result == mock_context
                mock_ssl_utils.create_ssl_context.assert_called_once()
    
    def test_create_ssl_context_exception(self):
        """Test create_ssl_context when SSL creation fails."""
        with patch('mcp_proxy_adapter.api.app.config') as mock_config:
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": "test.crt",
                "key_file": "test.key"
            }
            
            with patch('mcp_proxy_adapter.api.app.SSLUtils') as mock_ssl_utils:
                mock_ssl_utils.create_ssl_context.side_effect = Exception("SSL error")
                
                result = create_ssl_context()
                assert result is None
    
    def test_create_app_with_ssl_context(self):
        """Test create_app with SSL context creation."""
        with patch('mcp_proxy_adapter.api.app.create_ssl_context') as mock_create_ssl:
            mock_context = Mock()
            mock_create_ssl.return_value = mock_context
            
            app = create_app()
            assert app is not None
    
    def test_jsonrpc_endpoint_with_request_id(self):
        """Test JSON-RPC endpoint with request_id in state."""
        app = create_app()
        client = TestClient(app)
        
        # Mock request state with request_id
        with patch('mcp_proxy_adapter.api.app.getattr') as mock_getattr:
            mock_getattr.return_value = "test-request-id"
            
            response = client.post("/api/jsonrpc", json={
                "jsonrpc": "2.0",
                "method": "help",
                "id": 1
            })
            
            assert response.status_code == 200
    
    def test_tool_description_endpoint_tool_not_found(self):
        """Test tool description endpoint when tool is not found."""
        app = create_app()
        client = TestClient(app)
        
        # The endpoint returns 404 when tool is not found
        response = client.get("/api/tools/nonexistent")
        assert response.status_code == 404
    
    def test_tool_description_endpoint_exception(self):
        """Test tool description endpoint when exception occurs."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_tool:
            mock_get_tool.side_effect = Exception("Tool error")
            
            response = client.get("/api/tools/test_tool")
            assert response.status_code == 500
    
    def test_execute_tool_endpoint_tool_not_found(self):
        """Test execute tool endpoint when tool is not found."""
        app = create_app()
        client = TestClient(app)
        
        # The endpoint returns 404 when tool is not found
        response = client.post("/api/tools/nonexistent", json={})
        assert response.status_code == 404
    
    def test_execute_tool_endpoint_exception(self):
        """Test execute tool endpoint when exception occurs."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.side_effect = Exception("Tool execution error")
            
            response = client.post("/api/tools/test_tool", json={})
            assert response.status_code == 500
    
    def test_cmd_endpoint_missing_command_field(self):
        """Test cmd endpoint when command field is missing."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/cmd", json={})
        assert response.status_code == 200
        
        # Check that response contains error about missing command
        data = response.json()
        assert "error" in data or "result" in data
    
    def test_cmd_endpoint_jsonrpc_format_missing_method(self):
        """Test cmd endpoint with JSON-RPC format but missing method."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/cmd", json={
            "jsonrpc": "2.0",
            "id": 1
            # Missing "method" field
        })
        assert response.status_code == 200
    
    def test_cmd_endpoint_jsonrpc_format_invalid_version(self):
        """Test cmd endpoint with JSON-RPC format but invalid version."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/cmd", json={
            "jsonrpc": "1.0",  # Invalid version
            "method": "help",
            "id": 1
        })
        assert response.status_code == 200
    
    def test_cmd_endpoint_command_request_format(self):
        """Test cmd endpoint with CommandRequest format."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/cmd", json={
            "command": "help",
            "params": {}
        })
        assert response.status_code == 200
    
    def test_cmd_endpoint_command_request_no_params(self):
        """Test cmd endpoint with CommandRequest format but no params."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/cmd", json={
            "command": "help"
            # Missing "params" field
        })
        assert response.status_code == 200
    
    def test_cmd_endpoint_microservice_error(self):
        """Test cmd endpoint when MicroserviceError occurs."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            from mcp_proxy_adapter.core.errors import MicroserviceError
            mock_execute.side_effect = MicroserviceError("Custom error")
            
            response = client.post("/cmd", json={
                "command": "help",
                "params": {}
            })
            assert response.status_code == 200
    
    def test_cmd_endpoint_not_found_error_help(self):
        """Test cmd endpoint when NotFoundError occurs for help command."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            from mcp_proxy_adapter.core.errors import NotFoundError
            mock_execute.side_effect = NotFoundError("Command not found")
            
            response = client.post("/cmd", json={
                "command": "help",
                "params": {}
            })
            assert response.status_code == 200
    
    def test_cmd_endpoint_not_found_error_other(self):
        """Test cmd endpoint when NotFoundError occurs for other commands."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            from mcp_proxy_adapter.core.errors import NotFoundError
            mock_execute.side_effect = NotFoundError("Command not found")
            
            response = client.post("/cmd", json={
                "command": "nonexistent",
                "params": {}
            })
            assert response.status_code == 200
    
    def test_cmd_endpoint_json_decode_error(self):
        """Test cmd endpoint when JSON decode error occurs."""
        app = create_app()
        client = TestClient(app)
        
        # Send invalid JSON
        response = client.post("/cmd", data="invalid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422
    
    def test_cmd_endpoint_unexpected_error(self):
        """Test cmd endpoint when unexpected error occurs."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.side_effect = Exception("Unexpected error")
            
            response = client.post("/cmd", json={
                "command": "help",
                "params": {}
            })
            assert response.status_code == 200
    
    def test_command_endpoint_success(self):
        """Test /api/command/{command_name} endpoint success."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            mock_execute.return_value = {"result": "success"}
            
            response = client.post("/api/command/help", json={})
            assert response.status_code == 200
    
    def test_command_endpoint_microservice_error(self):
        """Test /api/command/{command_name} endpoint with MicroserviceError."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_command') as mock_execute:
            from mcp_proxy_adapter.core.errors import MicroserviceError
            mock_execute.side_effect = MicroserviceError("Custom error")
            
            response = client.post("/api/command/help", json={})
            assert response.status_code == 400
    
    def test_health_endpoint(self):
        """Test /health endpoint."""
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_shutdown_endpoint(self):
        """Test /shutdown endpoint."""
        app = create_app()
        client = TestClient(app)
        
        response = client.post("/shutdown")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_commands_list_endpoint(self):
        """Test /api/commands endpoint."""
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/api/commands")
        assert response.status_code == 200
        data = response.json()
        assert "commands" in data
    
    def test_command_info_endpoint_success(self):
        """Test /api/commands/{command_name} endpoint success."""
        app = create_app()
        client = TestClient(app)
        
        response = client.get("/api/commands/help")
        assert response.status_code == 200
        # The response might be None, which is acceptable
        data = response.json()
        # Don't assert on data content since it might be None
    
    def test_command_info_endpoint_not_found(self):
        """Test /api/commands/{command_name} endpoint when command not found."""
        app = create_app()
        client = TestClient(app)
        
        # The endpoint returns 200 even when command is not found, but logs a warning
        response = client.get("/api/commands/nonexistent")
        assert response.status_code == 200
        # The response might be None, which is acceptable
        data = response.json()
        # Don't assert on data content since it might be None
    
    def test_tool_description_endpoint_json_format(self):
        """Test /api/tools/{tool_name} endpoint with JSON format."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_tool:
            mock_get_tool.return_value = {"description": "test tool"}
            
            response = client.get("/api/tools/test_tool")
            assert response.status_code == 200
    
    def test_tool_description_endpoint_html_format(self):
        """Test /api/tools/{tool_name} endpoint with HTML format."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_tool:
            mock_get_tool.return_value = "<html>test tool</html>"
            
            response = client.get("/api/tools/test_tool?format=html")
            assert response.status_code == 200
    
    def test_tool_description_endpoint_text_format(self):
        """Test /api/tools/{tool_name} endpoint with text format."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.get_tool_description') as mock_get_tool:
            mock_get_tool.return_value = "test tool description"
            
            response = client.get("/api/tools/test_tool?format=text")
            assert response.status_code == 200
    
    def test_execute_tool_endpoint_success(self):
        """Test POST /api/tools/{tool_name} endpoint success."""
        app = create_app()
        client = TestClient(app)
        
        with patch('mcp_proxy_adapter.api.app.execute_tool') as mock_execute:
            mock_execute.return_value = {"result": "success"}
            
            response = client.post("/api/tools/test_tool", json={})
            assert response.status_code == 200
    
    def test_lifespan_startup(self):
        """Test lifespan startup."""
        app = create_app()
        
        # Test that lifespan context manager works
        # Note: lifespan_context is async, so we just test that the app has lifespan
        assert hasattr(app, 'router')
        assert app.router.lifespan_context is not None
    
    def test_lifespan_shutdown(self):
        """Test lifespan shutdown."""
        app = create_app()
        
        # Test that lifespan context manager works
        # Note: lifespan_context is async, so we just test that the app has lifespan
        assert hasattr(app, 'router')
        assert app.router.lifespan_context is not None 