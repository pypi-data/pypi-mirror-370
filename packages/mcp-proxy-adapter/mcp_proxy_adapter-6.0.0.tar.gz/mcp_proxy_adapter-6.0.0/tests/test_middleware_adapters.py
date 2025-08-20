"""
Tests for Middleware Adapters.

This module contains tests for the middleware adapters that provide backward compatibility
while using the new SecurityMiddleware internally.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response

from mcp_proxy_adapter.api.middleware.auth_adapter import AuthMiddlewareAdapter
from mcp_proxy_adapter.api.middleware.rate_limit_adapter import RateLimitMiddlewareAdapter
from mcp_proxy_adapter.api.middleware.mtls_adapter import MTLSMiddlewareAdapter
from mcp_proxy_adapter.api.middleware.roles_adapter import RolesMiddlewareAdapter


class TestAuthMiddlewareAdapter:
    """Tests for AuthMiddlewareAdapter class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "api_keys": {"admin": "admin_key_123", "user": "user_key_456"},
            "public_paths": ["/docs", "/health"],
            "auth_enabled": True
        }
    
    @pytest.fixture
    def adapter(self, app, config):
        """Create AuthMiddlewareAdapter instance."""
        return AuthMiddlewareAdapter(
            app, 
            api_keys=config["api_keys"],
            public_paths=config["public_paths"],
            auth_enabled=config["auth_enabled"]
        )
    
    def test_init(self, app, config):
        """Test AuthMiddlewareAdapter initialization."""
        adapter = AuthMiddlewareAdapter(
            app, 
            api_keys=config["api_keys"],
            public_paths=config["public_paths"],
            auth_enabled=config["auth_enabled"]
        )
        
        assert adapter.api_keys == config["api_keys"]
        assert adapter.public_paths == config["public_paths"]
        assert adapter.auth_enabled == config["auth_enabled"]
        assert adapter.security_middleware is not None
    
    def test_is_public_path(self, adapter):
        """Test public path detection."""
        assert adapter._is_public_path("/docs") is True
        assert adapter._is_public_path("/health") is True
        assert adapter._is_public_path("/api/jsonrpc") is False
    
    def test_validate_api_key(self, adapter):
        """Test API key validation."""
        assert adapter._validate_api_key("admin_key_123") == "admin"
        assert adapter._validate_api_key("user_key_456") == "user"
        assert adapter._validate_api_key("invalid_key") is None
    
    def test_get_username(self, adapter):
        """Test username extraction from request state."""
        request = Mock()
        request.state.username = "admin"
        
        username = adapter.get_username(request)
        assert username == "admin"
        
        # Test when no username
        request.state.username = None
        username = adapter.get_username(request)
        assert username is None
    
    def test_is_authenticated(self, adapter):
        """Test authentication status check."""
        request = Mock()
        request.state.username = "admin"
        
        assert adapter.is_authenticated(request) is True
        
        request.state.username = None
        assert adapter.is_authenticated(request) is False


class TestRateLimitMiddlewareAdapter:
    """Tests for RateLimitMiddlewareAdapter class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def adapter(self, app):
        """Create RateLimitMiddlewareAdapter instance."""
        return RateLimitMiddlewareAdapter(
            app,
            rate_limit=10,
            time_window=60,
            by_ip=True,
            by_user=True
        )
    
    def test_init(self, app):
        """Test RateLimitMiddlewareAdapter initialization."""
        adapter = RateLimitMiddlewareAdapter(
            app,
            rate_limit=10,
            time_window=60,
            by_ip=True,
            by_user=True
        )
        
        assert adapter.rate_limit == 10
        assert adapter.time_window == 60
        assert adapter.by_ip is True
        assert adapter.by_user is True
        assert adapter.security_middleware is not None
    
    def test_is_public_path(self, adapter):
        """Test public path detection."""
        assert adapter._is_public_path("/docs") is True
        assert adapter._is_public_path("/health") is True
        assert adapter._is_public_path("/api/jsonrpc") is False
    
    def test_clean_old_requests(self, adapter):
        """Test cleaning old requests."""
        import time
        current_time = time.time()
        
        requests_list = [current_time - 120, current_time - 30, current_time - 10]
        adapter._clean_old_requests(requests_list, current_time)
        
        # Should keep only requests within time window (60 seconds)
        assert len(requests_list) == 2
        assert current_time - 30 in requests_list
        assert current_time - 10 in requests_list
    
    def test_get_rate_limit_info(self, adapter):
        """Test rate limit information retrieval."""
        request = Mock()
        request.client.host = "192.168.1.1"
        request.state.username = "admin"
        
        # Add some requests
        adapter.ip_requests["192.168.1.1"] = [1, 2, 3]
        adapter.user_requests["admin"] = [1, 2]
        
        info = adapter.get_rate_limit_info(request)
        
        assert info["rate_limit"] == 10
        assert info["time_window"] == 60
        assert info["by_ip"] is True
        assert info["by_user"] is True
        assert info["ip_requests"] == 3
        assert info["ip_remaining"] == 7
        assert info["user_requests"] == 2
        assert info["user_remaining"] == 8


class TestMTLSMiddlewareAdapter:
    """Tests for MTLSMiddlewareAdapter class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def mtls_config(self):
        """Create test mTLS configuration."""
        return {
            "enabled": True,
            "ca_cert": "/path/to/ca.crt",
            "verify_client": True,
            "client_cert_required": True,
            "allowed_roles": ["admin", "user"],
            "require_roles": True
        }
    
    @pytest.fixture
    def adapter(self, app, mtls_config):
        """Create MTLSMiddlewareAdapter instance."""
        return MTLSMiddlewareAdapter(app, mtls_config)
    
    def test_init(self, app, mtls_config):
        """Test MTLSMiddlewareAdapter initialization."""
        adapter = MTLSMiddlewareAdapter(app, mtls_config)
        
        assert adapter.enabled == mtls_config["enabled"]
        assert adapter.ca_cert_path == mtls_config["ca_cert"]
        assert adapter.verify_client == mtls_config["verify_client"]
        assert adapter.client_cert_required == mtls_config["client_cert_required"]
        assert adapter.allowed_roles == mtls_config["allowed_roles"]
        assert adapter.require_roles == mtls_config["require_roles"]
        assert adapter.security_middleware is not None
    
    def test_get_common_name(self, adapter):
        """Test common name extraction from certificate."""
        # Mock certificate
        cert = Mock()
        cert.subject = [Mock(oid=Mock(dotted_string="2.5.4.3"), value="CN=test.example.com")]
        
        common_name = adapter._get_common_name(cert)
        assert common_name == "test.example.com"
    
    def test_validate_access(self, adapter):
        """Test access validation based on roles."""
        # Test with allowed role
        assert adapter._validate_access(["admin"]) is True
        assert adapter._validate_access(["user"]) is True
        
        # Test with disallowed role
        assert adapter._validate_access(["guest"]) is False
        
        # Test with empty roles
        assert adapter._validate_access([]) is False
    
    def test_get_client_certificate(self, adapter):
        """Test client certificate retrieval."""
        request = Mock()
        request.state.client_certificate = "mock_cert"
        
        cert = adapter.get_client_certificate(request)
        assert cert == "mock_cert"
    
    def test_get_client_roles(self, adapter):
        """Test client roles retrieval."""
        request = Mock()
        request.state.client_roles = ["admin", "user"]
        
        roles = adapter.get_client_roles(request)
        assert roles == ["admin", "user"]
    
    def test_get_client_common_name(self, adapter):
        """Test client common name retrieval."""
        request = Mock()
        request.state.client_common_name = "test.example.com"
        
        common_name = adapter.get_client_common_name(request)
        assert common_name == "test.example.com"
    
    def test_is_mtls_authenticated(self, adapter):
        """Test mTLS authentication status check."""
        request = Mock()
        request.state.client_certificate = "mock_cert"
        
        assert adapter.is_mtls_authenticated(request) is True
        
        request.state.client_certificate = None
        assert adapter.is_mtls_authenticated(request) is False


class TestRolesMiddlewareAdapter:
    """Tests for RolesMiddlewareAdapter class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def roles_config_path(self, tmp_path):
        """Create test roles configuration file."""
        config = {
            "enabled": True,
            "default_policy": {
                "deny_by_default": True,
                "require_role_match": True,
                "case_sensitive": False,
                "allow_wildcard": True,
                "allow_empty_roles": False,
                "default_role": "user"
            },
            "roles": {
                "admin": {
                    "description": "Administrator",
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                },
                "user": {
                    "description": "Regular user",
                    "permissions": ["read", "write"],
                    "priority": 10
                }
            },
            "server_roles": ["admin", "user"],
            "role_hierarchy": {
                "admin": ["user"]
            }
        }
        
        config_file = tmp_path / "roles.json"
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        return str(config_file)
    
    @pytest.fixture
    def adapter(self, app, roles_config_path):
        """Create RolesMiddlewareAdapter instance."""
        return RolesMiddlewareAdapter(app, roles_config_path)
    
    def test_init(self, app, roles_config_path):
        """Test RolesMiddlewareAdapter initialization."""
        adapter = RolesMiddlewareAdapter(app, roles_config_path)
        
        assert adapter.enabled is True
        assert adapter.roles_config_path == roles_config_path
        assert len(adapter.roles) == 2
        assert len(adapter.server_roles) == 2
        assert adapter.security_middleware is not None
    
    def test_get_client_roles(self, adapter):
        """Test client roles extraction."""
        request = Mock()
        request.state.client_roles = ["admin"]
        request.headers = {"X-Client-Roles": '["user", "guest"]'}
        
        roles = adapter._get_client_roles(request)
        assert "admin" in roles
        assert "user" in roles
        assert "guest" in roles
    
    def test_validate_roles(self, adapter):
        """Test role validation."""
        # Test with valid roles
        assert adapter._validate_roles(["admin"]) is True
        assert adapter._validate_roles(["user"]) is True
        
        # Test with invalid roles
        assert adapter._validate_roles(["guest"]) is False
        
        # Test with empty roles
        assert adapter._validate_roles([]) is False
    
    def test_get_client_roles_backward_compat(self, adapter):
        """Test backward compatibility client roles retrieval."""
        request = Mock()
        request.state.client_roles = ["admin", "user"]
        
        roles = adapter.get_client_roles(request)
        assert roles == ["admin", "user"]
    
    def test_is_role_validation_passed(self, adapter):
        """Test role validation status check."""
        request = Mock()
        request.state.role_validation_passed = True
        
        assert adapter.is_role_validation_passed(request) is True
        
        request.state.role_validation_passed = False
        assert adapter.is_role_validation_passed(request) is False
    
    def test_has_role(self, adapter):
        """Test role checking."""
        request = Mock()
        request.state.client_roles = ["admin", "user"]
        
        assert adapter.has_role(request, "admin") is True
        assert adapter.has_role(request, "user") is True
        assert adapter.has_role(request, "guest") is False
    
    def test_has_any_role(self, adapter):
        """Test multiple role checking."""
        request = Mock()
        request.state.client_roles = ["admin", "user"]
        
        assert adapter.has_any_role(request, ["admin", "guest"]) is True
        assert adapter.has_any_role(request, ["guest", "visitor"]) is False
    
    def test_get_server_roles(self, adapter):
        """Test server roles retrieval."""
        roles = adapter.get_server_roles()
        assert "admin" in roles
        assert "user" in roles
    
    def test_get_role_hierarchy(self, adapter):
        """Test role hierarchy retrieval."""
        hierarchy = adapter.get_role_hierarchy()
        assert "admin" in hierarchy
        assert "user" in hierarchy["admin"]


@pytest.mark.asyncio
class TestMiddlewareAdaptersIntegration:
    """Integration tests for middleware adapters."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application with adapters."""
        app = FastAPI()
        
        # Add test endpoint
        @app.post("/api/test")
        async def test_endpoint(request: Request):
            return {
                "message": "success",
                "username": getattr(request.state, 'username', None),
                "roles": getattr(request.state, 'client_roles', [])
            }
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_auth_adapter_integration(self, app, client):
        """Test AuthMiddlewareAdapter integration."""
        # Add auth adapter
        adapter = AuthMiddlewareAdapter(
            app,
            api_keys={"admin": "admin_key_123"},
            auth_enabled=True
        )
        app.add_middleware(adapter.__class__, **adapter.__dict__)
        
        # Test without auth
        response = client.post("/api/test", json={"test": "data"})
        assert response.status_code == 401
        
        # Test with auth
        headers = {"X-API-Key": "admin_key_123"}
        response = client.post("/api/test", json={"test": "data"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "success"
        assert response.json()["username"] == "admin"
    
    def test_public_path_access(self, app, client):
        """Test access to public paths."""
        # Add auth adapter
        adapter = AuthMiddlewareAdapter(
            app,
            api_keys={"admin": "admin_key_123"},
            auth_enabled=True
        )
        app.add_middleware(adapter.__class__, **adapter.__dict__)
        
        # Test public path access
        response = client.get("/docs")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__])
