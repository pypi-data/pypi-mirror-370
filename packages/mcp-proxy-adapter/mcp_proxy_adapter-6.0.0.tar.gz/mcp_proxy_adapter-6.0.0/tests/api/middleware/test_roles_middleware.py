"""
Tests for Roles Middleware.

Tests role-based access control functionality including role validation,
access control, and integration with other middleware components.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from fastapi import Request
from starlette.testclient import TestClient

from mcp_proxy_adapter.api.middleware.roles_middleware import RolesMiddleware
from mcp_proxy_adapter.core.role_utils import RoleUtils


class TestRolesMiddleware:
    """Test cases for RolesMiddleware."""
    
    @pytest.fixture
    def mock_roles_config(self):
        """Mock roles configuration."""
        return {
            "enabled": True,
            "default_policy": {
                "deny_by_default": True,
                "require_role_match": True,
                "case_sensitive": False,
                "allow_wildcard": True
            },
            "roles": {
                "admin": {
                    "description": "Administrator with full access",
                    "allowed_servers": ["*"],
                    "allowed_clients": ["*"],
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                },
                "operator": {
                    "description": "Operator with limited access",
                    "allowed_servers": ["kubernetes_manager", "docker_manager"],
                    "allowed_clients": ["admin", "operator"],
                    "permissions": ["read", "write"],
                    "priority": 50
                },
                "user": {
                    "description": "Regular user",
                    "allowed_servers": ["basic_commands"],
                    "allowed_clients": ["admin", "operator", "user"],
                    "permissions": ["read"],
                    "priority": 10
                }
            },
            "server_roles": {
                "kubernetes_manager": {
                    "description": "Kubernetes management server",
                    "required_roles": ["admin", "operator"],
                    "allowed_commands": ["k8s_*"]
                },
                "docker_manager": {
                    "description": "Docker management server",
                    "required_roles": ["admin", "operator"],
                    "allowed_commands": ["docker_*"]
                },
                "basic_commands": {
                    "description": "Basic command server",
                    "required_roles": ["user", "admin", "operator"],
                    "allowed_commands": ["help", "config"]
                }
            },
            "role_hierarchy": {
                "admin": ["operator", "user"],
                "operator": ["user"]
            }
        }
    
    @pytest.fixture
    def mock_app(self):
        """Mock FastAPI application."""
        return Mock()
    
    @pytest.fixture
    def roles_middleware(self, mock_app, mock_roles_config, tmp_path):
        """Create RolesMiddleware instance with mock configuration."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        with patch('mcp_proxy_adapter.api.middleware.roles_middleware.RolesMiddleware._load_roles_config') as mock_load:
            mock_load.return_value = mock_roles_config
            middleware = RolesMiddleware(mock_app, str(config_file))
            return middleware
    
    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request."""
        request = Mock(spec=Request)
        request.state = Mock()
        request.url.path = "/api/basic_commands/help"
        request.headers = {}
        return request
    
    @pytest.fixture
    def mock_certificate(self):
        """Mock X.509 certificate."""
        # Create a mock certificate
        cert = Mock(spec=x509.Certificate)
        cert.extensions = []
        return cert
    
    def test_init(self, mock_app, mock_roles_config, tmp_path):
        """Test middleware initialization."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        with patch('mcp_proxy_adapter.api.middleware.roles_middleware.RolesMiddleware._load_roles_config') as mock_load:
            mock_load.return_value = mock_roles_config
            middleware = RolesMiddleware(mock_app, str(config_file))
            
            assert middleware.enabled is True
            assert middleware.roles == mock_roles_config["roles"]
            assert middleware.server_roles == mock_roles_config["server_roles"]
            assert middleware.role_hierarchy == mock_roles_config["role_hierarchy"]
    
    def test_load_roles_config_file_exists(self, mock_app, mock_roles_config, tmp_path):
        """Test loading roles configuration from existing file."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        middleware = RolesMiddleware(mock_app, str(config_file))
        assert middleware.roles_config == mock_roles_config
    
    def test_load_roles_config_file_not_exists(self, mock_app):
        """Test loading roles configuration when file doesn't exist."""
        middleware = RolesMiddleware(mock_app, "nonexistent_file.json")
        assert middleware.roles_config["enabled"] is True
        assert "admin" in middleware.roles_config["roles"]
    
    def test_extract_roles_from_certificate(self, roles_middleware, mock_certificate):
        """Test extracting roles from certificate."""
        with patch.object(RoleUtils, 'extract_roles_from_certificate_object') as mock_extract:
            mock_extract.return_value = ["admin", "operator"]
            roles = roles_middleware._extract_roles_from_certificate(mock_certificate)
            assert roles == ["admin", "operator"]
    
    def test_extract_roles_from_certificate_error(self, roles_middleware, mock_certificate):
        """Test extracting roles from certificate with error."""
        with patch.object(RoleUtils, 'extract_roles_from_certificate_object') as mock_extract:
            mock_extract.side_effect = Exception("Certificate error")
            roles = roles_middleware._extract_roles_from_certificate(mock_certificate)
            assert roles == []
    
    def test_extract_server_role_from_path(self, roles_middleware, mock_request):
        """Test extracting server role from request path."""
        mock_request.url.path = "/api/kubernetes_manager/pods"
        server_role = roles_middleware._extract_server_role(mock_request)
        assert server_role == "kubernetes_manager"
    
    def test_extract_server_role_from_header(self, roles_middleware, mock_request):
        """Test extracting server role from request header."""
        # Create middleware with proper mock config
        mock_app = Mock()
        mock_config = {
            "enabled": True,
            "default_policy": {"deny_by_default": True},
            "roles": {},
            "server_roles": {
                "docker_manager": {
                    "description": "Docker management server",
                    "required_roles": ["admin", "operator"],
                    "allowed_commands": ["docker_*"]
                }
            },
            "role_hierarchy": {}
        }
        
        with patch('mcp_proxy_adapter.api.middleware.roles_middleware.RolesMiddleware._load_roles_config') as mock_load:
            mock_load.return_value = mock_config
            middleware = RolesMiddleware(mock_app, "test_config.json")
            
            mock_request.headers = {"X-Server-Role": "docker_manager"}
            server_role = middleware._extract_server_role(mock_request)
            assert server_role == "docker_manager"
    
    def test_extract_server_role_default(self, roles_middleware, mock_request):
        """Test extracting default server role."""
        mock_request.url.path = "/api/unknown/path"
        server_role = roles_middleware._extract_server_role(mock_request)
        assert server_role == "basic_commands"
    
    def test_validate_access_with_matching_roles(self, roles_middleware, mock_request):
        """Test access validation with matching roles."""
        client_roles = ["admin"]
        server_role = "kubernetes_manager"
        
        result = roles_middleware._validate_access(client_roles, server_role, mock_request)
        assert result is True
    
    def test_validate_access_with_hierarchy(self, roles_middleware, mock_request):
        """Test access validation with role hierarchy."""
        client_roles = ["operator"]
        server_role = "basic_commands"
        
        result = roles_middleware._validate_access(client_roles, server_role, mock_request)
        assert result is True
    
    def test_validate_access_denied(self, roles_middleware, mock_request):
        """Test access validation denied."""
        client_roles = ["user"]
        server_role = "kubernetes_manager"
        
        result = roles_middleware._validate_access(client_roles, server_role, mock_request)
        assert result is False
    
    def test_validate_access_no_client_roles_deny_default(self, roles_middleware, mock_request):
        """Test access validation with no client roles and deny by default."""
        client_roles = []
        server_role = "basic_commands"
        
        result = roles_middleware._validate_access(client_roles, server_role, mock_request)
        assert result is False
    
    def test_validate_access_no_server_role_allow(self, roles_middleware, mock_request):
        """Test access validation with no server role and not requiring match."""
        roles_middleware.default_policy["require_role_match"] = False
        client_roles = ["admin"]
        server_role = ""
        
        result = roles_middleware._validate_access(client_roles, server_role, mock_request)
        assert result is True
    
    def test_has_required_role_case_insensitive(self, roles_middleware):
        """Test role comparison case insensitive."""
        client_role = "ADMIN"
        required_roles = ["admin", "operator"]
        
        with patch.object(RoleUtils, 'compare_roles') as mock_compare:
            mock_compare.return_value = True
            result = roles_middleware._has_required_role(client_role, required_roles)
            assert result is True
    
    def test_has_required_role_wildcard(self, roles_middleware):
        """Test role comparison with wildcard."""
        client_role = "admin"
        required_roles = ["*"]
        
        result = roles_middleware._has_required_role(client_role, required_roles)
        assert result is True
    
    def test_has_role_in_hierarchy(self, roles_middleware):
        """Test role hierarchy validation."""
        client_role = "admin"
        required_roles = ["user"]
        
        with patch.object(roles_middleware, '_get_role_hierarchy') as mock_hierarchy:
            mock_hierarchy.return_value = ["operator", "user"]
            with patch.object(roles_middleware, '_has_required_role') as mock_has:
                mock_has.return_value = True
                result = roles_middleware._has_role_in_hierarchy(client_role, required_roles)
                assert result is True
    
    def test_get_role_hierarchy(self, roles_middleware):
        """Test getting role hierarchy."""
        role = "admin"
        hierarchy = roles_middleware._get_role_hierarchy(role)
        assert hierarchy == ["operator", "user"]
    
    def test_validate_permissions(self, roles_middleware):
        """Test permission validation."""
        client_roles = ["admin"]
        required_permissions = ["read", "write"]
        
        result = roles_middleware._validate_permissions(client_roles, required_permissions)
        assert result is True
    
    def test_validate_permissions_insufficient(self, roles_middleware):
        """Test permission validation with insufficient permissions."""
        client_roles = ["user"]
        required_permissions = ["read", "write", "delete"]
        
        result = roles_middleware._validate_permissions(client_roles, required_permissions)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_before_request_success(self, roles_middleware, mock_request):
        """Test successful before_request processing."""
        mock_request.state.client_roles = ["admin"]
        mock_request.state.client_certificate = None
        
        await roles_middleware.before_request(mock_request)
        
        assert mock_request.state.role_validation_passed is True
        assert hasattr(mock_request.state, 'server_role')
    
    @pytest.mark.asyncio
    async def test_before_request_with_certificate(self, roles_middleware, mock_request, mock_certificate):
        """Test before_request processing with certificate."""
        mock_request.state.client_roles = []
        mock_request.state.client_certificate = mock_certificate
        
        with patch.object(roles_middleware, '_extract_roles_from_certificate') as mock_extract:
            mock_extract.return_value = ["admin"]
            await roles_middleware.before_request(mock_request)
            
            assert mock_request.state.role_validation_passed is True
    
    @pytest.mark.asyncio
    async def test_before_request_access_denied(self, roles_middleware, mock_request):
        """Test before_request processing with access denied."""
        mock_request.state.client_roles = ["user"]
        mock_request.state.client_certificate = None
        
        # Mock _extract_server_role to return a role that requires admin
        with patch.object(roles_middleware, '_extract_server_role') as mock_extract:
            mock_extract.return_value = "kubernetes_manager"
            await roles_middleware.before_request(mock_request)
            
            assert mock_request.state.role_validation_passed is False
            assert hasattr(mock_request.state, 'role_validation_error')
    
    @pytest.mark.asyncio
    async def test_before_request_disabled(self, roles_middleware, mock_request):
        """Test before_request processing when middleware is disabled."""
        roles_middleware.enabled = False
        # Create completely fresh mock request
        fresh_request = Mock(spec=Request)
        fresh_request.state = Mock()
        fresh_request.state.client_roles = ["user"]
        fresh_request.url.path = "/api/test"
        fresh_request.headers = {}
        
        # Mock the _extract_server_role method to verify it's not called
        with patch.object(roles_middleware, '_extract_server_role') as mock_extract:
            await roles_middleware.before_request(fresh_request)
            
            # When disabled, middleware should return early and not call _extract_server_role
            mock_extract.assert_not_called()
            
            # client_roles should remain unchanged
            assert fresh_request.state.client_roles == ["user"]
    
    def test_get_client_roles(self, roles_middleware, mock_request):
        """Test getting client roles from request."""
        mock_request.state.client_roles = ["admin", "operator"]
        roles = roles_middleware.get_client_roles(mock_request)
        assert roles == ["admin", "operator"]
    
    def test_get_server_role(self, roles_middleware, mock_request):
        """Test getting server role from request."""
        mock_request.state.server_role = "kubernetes_manager"
        role = roles_middleware.get_server_role(mock_request)
        assert role == "kubernetes_manager"
    
    def test_is_role_validation_passed(self, roles_middleware, mock_request):
        """Test checking if role validation passed."""
        mock_request.state.role_validation_passed = True
        result = roles_middleware.is_role_validation_passed(mock_request)
        assert result is True
    
    def test_get_role_validation_error(self, roles_middleware, mock_request):
        """Test getting role validation error."""
        mock_request.state.role_validation_error = "Access denied"
        error = roles_middleware.get_role_validation_error(mock_request)
        assert error == "Access denied"
    
    def test_get_default_config(self, roles_middleware):
        """Test getting default configuration."""
        config = roles_middleware._get_default_config()
        assert config["enabled"] is True
        assert "admin" in config["roles"]
        assert config["default_policy"]["deny_by_default"] is True


class TestRolesMiddlewareIntegration:
    """Integration tests for RolesMiddleware."""
    
    @pytest.fixture
    def test_app(self):
        """Create test FastAPI application."""
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/api/basic_commands/help")
        async def help_endpoint():
            return {"message": "Help endpoint"}
        
        @app.get("/api/kubernetes_manager/pods")
        async def pods_endpoint():
            return {"message": "Pods endpoint"}
        
        return app
    
    @pytest.fixture
    def roles_config(self):
        """Roles configuration for integration tests."""
        return {
            "enabled": True,
            "default_policy": {
                "deny_by_default": True,
                "require_role_match": True,
                "case_sensitive": False,
                "allow_wildcard": True
            },
            "roles": {
                "admin": {
                    "description": "Administrator",
                    "allowed_servers": ["*"],
                    "allowed_clients": ["*"],
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                },
                "user": {
                    "description": "User",
                    "allowed_servers": ["basic_commands"],
                    "allowed_clients": ["admin", "user"],
                    "permissions": ["read"],
                    "priority": 10
                }
            },
            "server_roles": {
                "basic_commands": {
                    "description": "Basic commands",
                    "required_roles": ["user", "admin"],
                    "allowed_commands": ["help"]
                },
                "kubernetes_manager": {
                    "description": "Kubernetes manager",
                    "required_roles": ["admin"],
                    "allowed_commands": ["k8s_*"]
                }
            },
            "role_hierarchy": {
                "admin": ["user"]
            }
        }
    
    def test_middleware_integration_with_app(self, test_app, roles_config, tmp_path):
        """Test middleware integration with FastAPI application."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(roles_config, f)
        
        # Add middleware to app
        middleware = RolesMiddleware(test_app, str(config_file))
        test_app.add_middleware(RolesMiddleware, roles_config_path=str(config_file))
        
        client = TestClient(test_app)
        
        # Test with admin role (should work for all endpoints)
        with patch.object(RolesMiddleware, '_extract_server_role') as mock_extract:
            mock_extract.return_value = "basic_commands"
            
            # Mock request state
            with patch.object(client, 'get') as mock_get:
                mock_get.return_value.status_code = 200
                response = client.get("/api/basic_commands/help")
                assert response.status_code == 200
    
    def test_middleware_with_mtls_integration(self, test_app, roles_config, tmp_path):
        """Test middleware integration with mTLS."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(roles_config, f)
        
        middleware = RolesMiddleware(test_app, str(config_file))
        
        # Mock request with mTLS certificate
        request = Mock(spec=Request)
        request.state = Mock()
        request.state.client_roles = ["admin"]
        request.state.client_certificate = Mock()
        request.url.path = "/api/kubernetes_manager/pods"
        request.headers = {}
        
        # Test role validation
        with patch.object(middleware, '_extract_roles_from_certificate') as mock_extract:
            mock_extract.return_value = ["admin"]
            
            # Should pass validation
            result = middleware._validate_access(["admin"], "kubernetes_manager", request)
            assert result is True
            
            # Should fail for user role
            result = middleware._validate_access(["user"], "kubernetes_manager", request)
            assert result is False 