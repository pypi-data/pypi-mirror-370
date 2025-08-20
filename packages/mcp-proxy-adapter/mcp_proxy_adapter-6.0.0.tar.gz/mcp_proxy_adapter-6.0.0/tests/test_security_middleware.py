"""
Tests for SecurityMiddleware.

This module contains tests for the unified SecurityMiddleware that replaces
AuthMiddleware, RateLimitMiddleware, MTLSMiddleware, and RolesMiddleware.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response

from mcp_proxy_adapter.api.middleware.security import SecurityMiddleware, SecurityValidationError
from mcp_proxy_adapter.api.middleware.factory import MiddlewareFactory


class TestSecurityMiddleware:
    """Tests for SecurityMiddleware class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {"admin": "admin_key_123"}
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "roles.json"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
    
    @pytest.fixture
    def middleware(self, app, config):
        """Create SecurityMiddleware instance."""
        return SecurityMiddleware(app, config)
    
    def test_init(self, app, config):
        """Test SecurityMiddleware initialization."""
        middleware = SecurityMiddleware(app, config)
        
        assert middleware.config == config
        assert middleware.security_config == config["security"]
        assert len(middleware.public_paths) >= 5  # Default public paths
        assert "/docs" in middleware.public_paths
        assert "/health" in middleware.public_paths
    
    def test_is_public_path(self, middleware):
        """Test public path detection."""
        assert middleware._is_public_path("/docs") is True
        assert middleware._is_public_path("/health") is True
        assert middleware._is_public_path("/api/jsonrpc") is False
        assert middleware._is_public_path("/some/private/path") is False
    
    def test_get_client_ip(self, middleware):
        """Test client IP extraction."""
        # Test X-Forwarded-For header
        request = Mock()
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        request.client = None
        
        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.1"
        
        # Test X-Real-IP header
        request.headers = {"X-Real-IP": "192.168.1.2"}
        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.2"
        
        # Test client host
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.3"
        
        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.3"
        
        # Test unknown
        request.client = None
        ip = middleware._get_client_ip(request)
        assert ip == "unknown"
    
    def test_prepare_request_data_sync(self, middleware):
        """Test synchronous request data preparation."""
        request = Mock()
        request.method = "GET"
        request.url.path = "/api/test"
        request.headers = {"Content-Type": "application/json"}
        request.query_params = {"param": "value"}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        data = middleware._prepare_request_data(request)
        
        assert data["method"] == "GET"
        assert data["path"] == "/api/test"
        assert data["headers"]["Content-Type"] == "application/json"
        assert data["query_params"]["param"] == "value"
        assert data["client_ip"] == "192.168.1.1"
        assert data["body"] == {}
    
    @pytest.mark.asyncio
    async def test_prepare_request_data_async(self, middleware):
        """Test asynchronous request data preparation."""
        request = Mock()
        request.method = "POST"
        request.url.path = "/api/test"
        request.headers = {"Content-Type": "application/json"}
        request.query_params = {}
        request.client = Mock()
        request.client.host = "192.168.1.1"
        
        # Mock async body method
        request.body = AsyncMock(return_value=json.dumps({"test": "data"}).encode())
        
        data = await middleware._prepare_request_data_async(request)
        
        assert data["method"] == "POST"
        assert data["path"] == "/api/test"
        assert data["body"]["test"] == "data"
    
    def test_get_status_code_for_error(self, middleware):
        """Test error code to status code mapping."""
        assert middleware._get_status_code_for_error(-32000) == 401  # Authentication failed
        assert middleware._get_status_code_for_error(-32007) == 403  # Role validation failed
        assert middleware._get_status_code_for_error(-32603) == 500  # Internal error
        assert middleware._get_status_code_for_error(-99999) == 500  # Unknown error
    
    def test_get_user_roles(self, middleware):
        """Test user roles extraction from request state."""
        request = Mock()
        request.state.user_roles = ["admin", "user"]
        
        roles = middleware.get_user_roles(request)
        assert roles == ["admin", "user"]
        
        # Test when no roles
        request.state.user_roles = None
        roles = middleware.get_user_roles(request)
        assert roles == []
    
    def test_get_user_id(self, middleware):
        """Test user ID extraction from request state."""
        request = Mock()
        request.state.user_id = "admin"
        
        user_id = middleware.get_user_id(request)
        assert user_id == "admin"
        
        # Test when no user ID
        request.state.user_id = None
        user_id = middleware.get_user_id(request)
        assert user_id is None
    
    def test_is_security_validated(self, middleware):
        """Test security validation status check."""
        request = Mock()
        request.state.security_validated = True
        
        assert middleware.is_security_validated(request) is True
        
        request.state.security_validated = False
        assert middleware.is_security_validated(request) is False
    
    def test_has_role(self, middleware):
        """Test role checking."""
        request = Mock()
        request.state.user_roles = ["admin", "user"]
        
        assert middleware.has_role(request, "admin") is True
        assert middleware.has_role(request, "user") is True
        assert middleware.has_role(request, "guest") is False
        
        # Test wildcard role
        request.state.user_roles = ["*"]
        assert middleware.has_role(request, "any_role") is True
    
    def test_has_any_role(self, middleware):
        """Test multiple role checking."""
        request = Mock()
        request.state.user_roles = ["admin", "user"]
        
        assert middleware.has_any_role(request, ["admin", "guest"]) is True
        assert middleware.has_any_role(request, ["guest", "visitor"]) is False
        
        # Test wildcard role
        request.state.user_roles = ["*"]
        assert middleware.has_any_role(request, ["any_role", "another_role"]) is True


class TestSecurityValidationError:
    """Tests for SecurityValidationError class."""
    
    def test_init(self):
        """Test SecurityValidationError initialization."""
        error = SecurityValidationError("Test error", -32000)
        
        assert error.message == "Test error"
        assert error.error_code == -32000
        assert str(error) == "Test error"


class TestMiddlewareFactory:
    """Tests for MiddlewareFactory class."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        return FastAPI()
    
    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {}
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": True,
                    "roles_file": "roles.json"
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": 60
                }
            }
        }
    
    @pytest.fixture
    def factory(self, app, config):
        """Create MiddlewareFactory instance."""
        return MiddlewareFactory(app, config)
    
    def test_init(self, app, config):
        """Test MiddlewareFactory initialization."""
        factory = MiddlewareFactory(app, config)
        
        assert factory.app == app
        assert factory.config == config
        assert len(factory.middleware_stack) == 0
    
    def test_create_security_middleware(self, factory):
        """Test security middleware creation."""
        middleware = factory.create_security_middleware()
        
        assert middleware is not None
        assert isinstance(middleware, SecurityMiddleware)
        assert len(factory.middleware_stack) == 1
    
    def test_create_security_middleware_disabled(self, app):
        """Test security middleware creation when disabled."""
        config = {
            "security": {
                "enabled": False
            }
        }
        factory = MiddlewareFactory(app, config)
        
        middleware = factory.create_security_middleware()
        assert middleware is None
    
    def test_validate_middleware_config_valid(self, factory):
        """Test middleware configuration validation with valid config."""
        assert factory.validate_middleware_config() is True
    
    def test_validate_middleware_config_invalid(self, app):
        """Test middleware configuration validation with invalid config."""
        config = {
            "security": {
                "auth": "invalid"  # Should be dict
            }
        }
        factory = MiddlewareFactory(app, config)
        
        assert factory.validate_middleware_config() is False
    
    def test_get_middleware_info(self, factory):
        """Test middleware information retrieval."""
        # Create some middleware
        factory.create_security_middleware()
        
        info = factory.get_middleware_info()
        
        assert info["total_middleware"] == 1
        assert "SecurityMiddleware" in info["middleware_types"]
        assert info["security_enabled"] is True
        assert info["legacy_mode"] is False
    
    def test_get_middleware_by_type(self, factory):
        """Test middleware retrieval by type."""
        middleware = factory.create_security_middleware()
        
        found = factory.get_middleware_by_type(SecurityMiddleware)
        assert found == middleware
        
        # Test with non-existent type
        from mcp_proxy_adapter.api.middleware.logging import LoggingMiddleware
        found = factory.get_middleware_by_type(LoggingMiddleware)
        assert found is None
    
    def test_get_security_middleware(self, factory):
        """Test security middleware retrieval."""
        middleware = factory.create_security_middleware()
        
        found = factory.get_security_middleware()
        assert found == middleware


@pytest.mark.asyncio
class TestSecurityMiddlewareIntegration:
    """Integration tests for SecurityMiddleware."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application with middleware."""
        app = FastAPI()
        
        config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": True,
                    "methods": ["api_key"],
                    "api_keys": {"admin": "admin_key_123"}
                },
                "ssl": {"enabled": False},
                "permissions": {"enabled": True},
                "rate_limit": {"enabled": True}
            }
        }
        
        # Add middleware
        middleware = SecurityMiddleware(app, config)
        app.add_middleware(middleware.__class__, **middleware.__dict__)
        
        # Add test endpoint
        @app.post("/api/test")
        async def test_endpoint(request: Request):
            return {"message": "success", "user_id": getattr(request.state, 'user_id', None)}
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)
    
    def test_public_path_access(self, client):
        """Test access to public paths."""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_protected_path_without_auth(self, client):
        """Test access to protected path without authentication."""
        response = client.post("/api/test", json={"test": "data"})
        assert response.status_code == 401
    
    def test_protected_path_with_auth(self, client):
        """Test access to protected path with authentication."""
        headers = {"X-API-Key": "admin_key_123"}
        response = client.post("/api/test", json={"test": "data"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "success"
        assert response.json()["user_id"] == "admin"


if __name__ == "__main__":
    pytest.main([__file__])
