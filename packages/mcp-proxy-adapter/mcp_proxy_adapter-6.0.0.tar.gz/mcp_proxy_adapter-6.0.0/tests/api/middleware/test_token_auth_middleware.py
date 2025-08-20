"""
Tests for Token Authentication Middleware

This module contains tests for the TokenAuthMiddleware class.
Tests cover token validation, JWT handling, API token handling, and error scenarios.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.token_auth_middleware import TokenAuthMiddleware


class TestTokenAuthMiddleware:
    """Test cases for TokenAuthMiddleware."""
    
    @pytest.fixture
    def app(self):
        """Create test FastAPI application."""
        app = FastAPI()
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}
        
        return app
    
    @pytest.fixture
    def token_config(self):
        """Create test token configuration."""
        return {
            "enabled": True,
            "header_name": "Authorization",
            "token_prefix": "Bearer",
            "tokens_file": "test_tokens.json",
            "token_expiry": 3600,
            "jwt_secret": "test-secret",
            "jwt_algorithm": "HS256"
        }
    
    @pytest.fixture
    def middleware(self, app, token_config):
        """Create TokenAuthMiddleware instance."""
        return TokenAuthMiddleware(app, token_config)
    
    @pytest.fixture
    def temp_tokens_file(self):
        """Create temporary tokens file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tokens_data = {
                "test-api-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": True,
                    "created_at": time.time(),
                    "expires_at": time.time() + 3600,
                    "description": "Test API token",
                    "user_id": "test-user"
                },
                "expired-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": True,
                    "created_at": time.time() - 7200,
                    "expires_at": time.time() - 3600,
                    "description": "Expired token",
                    "user_id": "test-user"
                },
                "revoked-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": False,
                    "created_at": time.time(),
                    "expires_at": time.time() + 3600,
                    "description": "Revoked token",
                    "user_id": "test-user"
                }
            }
            json.dump(tokens_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    def test_init_disabled(self, app):
        """Test middleware initialization with disabled config."""
        config = {"enabled": False}
        middleware = TokenAuthMiddleware(app, config)
        
        assert middleware.enabled is False
        assert middleware.header_name == "Authorization"
        assert middleware.token_prefix == "Bearer"
    
    def test_init_enabled(self, app, token_config):
        """Test middleware initialization with enabled config."""
        middleware = TokenAuthMiddleware(app, token_config)
        
        assert middleware.enabled is True
        assert middleware.header_name == "Authorization"
        assert middleware.token_prefix == "Bearer"
        assert middleware.tokens_file == "test_tokens.json"
        assert middleware.token_expiry == 3600
        assert middleware.jwt_secret == "test-secret"
        assert middleware.jwt_algorithm == "HS256"
    
    def test_load_tokens_file_exists(self, app, token_config, temp_tokens_file):
        """Test loading tokens from existing file."""
        token_config["tokens_file"] = temp_tokens_file
        middleware = TokenAuthMiddleware(app, token_config)
        
        assert len(middleware.tokens) == 3
        assert "test-api-token" in middleware.tokens
        assert "expired-token" in middleware.tokens
        assert "revoked-token" in middleware.tokens
    
    def test_load_tokens_file_not_exists(self, app, token_config):
        """Test loading tokens when file doesn't exist."""
        token_config["tokens_file"] = "nonexistent.json"
        middleware = TokenAuthMiddleware(app, token_config)
        
        assert middleware.tokens == {}
    
    def test_load_tokens_invalid_json(self, app, token_config):
        """Test loading tokens from invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            token_config["tokens_file"] = temp_file
            middleware = TokenAuthMiddleware(app, token_config)
            
            assert middleware.tokens == {}
        finally:
            Path(temp_file).unlink(missing_ok=True)
    
    def test_is_jwt_token_valid(self, middleware):
        """Test JWT token format detection with valid token."""
        token = "header.payload.signature"
        assert middleware._is_jwt_token(token) is True
    
    def test_is_jwt_token_invalid(self, middleware):
        """Test JWT token format detection with invalid token."""
        token = "invalid.token"
        assert middleware._is_jwt_token(token) is False
    
    def test_is_jwt_token_empty(self, middleware):
        """Test JWT token format detection with empty token."""
        token = ""
        assert middleware._is_jwt_token(token) is False
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_validate_jwt_token_success(self, mock_auth_validator, middleware):
        """Test JWT token validation success."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_validator.validate_token.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        # Patch the middleware's auth_validator
        middleware.auth_validator = mock_validator
        
        token = "header.payload.signature"
        result = middleware._validate_jwt_token(token)
        
        assert result is True
        mock_validator.validate_token.assert_called_once_with(token, "jwt")
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_validate_jwt_token_failure(self, mock_auth_validator, middleware):
        """Test JWT token validation failure."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = False
        mock_validator.validate_token.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        # Patch the middleware's auth_validator
        middleware.auth_validator = mock_validator
        
        token = "header.payload.signature"
        result = middleware._validate_jwt_token(token)
        
        assert result is False
        mock_validator.validate_token.assert_called_once_with(token, "jwt")
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_validate_jwt_token_exception(self, mock_auth_validator, middleware):
        """Test JWT token validation with exception."""
        mock_validator = Mock()
        mock_validator.validate_token.side_effect = Exception("Test error")
        mock_auth_validator.return_value = mock_validator
        
        # Patch the middleware's auth_validator
        middleware.auth_validator = mock_validator
        
        token = "header.payload.signature"
        result = middleware._validate_jwt_token(token)
        
        assert result is False
    
    def test_validate_api_token_success(self, app, token_config, temp_tokens_file):
        """Test API token validation success."""
        token_config["tokens_file"] = temp_tokens_file
        middleware = TokenAuthMiddleware(app, token_config)
        
        result = middleware._validate_api_token("test-api-token")
        assert result is True
    
    def test_validate_api_token_not_found(self, app, token_config, temp_tokens_file):
        """Test API token validation with non-existent token."""
        token_config["tokens_file"] = temp_tokens_file
        middleware = TokenAuthMiddleware(app, token_config)
        
        with patch.object(middleware.auth_validator, 'validate_token') as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = False
            mock_validate.return_value = mock_result
            
            result = middleware._validate_api_token("non-existent-token")
            assert result is False
    
    def test_validate_api_token_revoked(self, app, token_config, temp_tokens_file):
        """Test API token validation with revoked token."""
        token_config["tokens_file"] = temp_tokens_file
        middleware = TokenAuthMiddleware(app, token_config)
        
        result = middleware._validate_api_token("revoked-token")
        assert result is False
    
    def test_validate_api_token_expired(self, app, token_config, temp_tokens_file):
        """Test API token validation with expired token."""
        token_config["tokens_file"] = temp_tokens_file
        middleware = TokenAuthMiddleware(app, token_config)
        
        result = middleware._validate_api_token("expired-token")
        assert result is False
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_validate_api_token_fallback(self, mock_auth_validator, app, token_config):
        """Test API token validation fallback to AuthValidator."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_validator.validate_token.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        middleware = TokenAuthMiddleware(app, token_config)
        
        result = middleware._validate_api_token("fallback-token")
        assert result is True
        mock_validator.validate_token.assert_called_once_with("fallback-token", "api")
    
    def test_validate_token_jwt(self, middleware):
        """Test token validation with JWT token."""
        with patch.object(middleware, '_validate_jwt_token', return_value=True):
            result = middleware._validate_token("Bearer header.payload.signature")
            assert result is True
    
    def test_validate_token_api(self, middleware):
        """Test token validation with API token."""
        with patch.object(middleware, '_validate_api_token', return_value=True):
            result = middleware._validate_token("Bearer api-token")
            assert result is True
    
    def test_validate_token_invalid_prefix(self, middleware):
        """Test token validation with invalid prefix."""
        result = middleware._validate_token("Invalid token")
        assert result is False
    
    def test_validate_token_empty_token(self, middleware):
        """Test token validation with empty token."""
        result = middleware._validate_token("Bearer ")
        assert result is False
    
    def test_create_auth_error(self, middleware):
        """Test creating authentication error response."""
        response = middleware._create_auth_error("Test error", 401)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        
        content = response.body.decode()
        error_data = json.loads(content)
        
        assert "error" in error_data
        assert error_data["error"]["code"] == -32004
        assert error_data["error"]["message"] == "Test error"
        assert error_data["error"]["type"] == "token_authentication_error"
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_get_roles_from_token_jwt(self, mock_auth_validator, middleware):
        """Test extracting roles from JWT token."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_result.roles = ["admin", "user"]
        mock_validator.validate_token.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        # Patch the middleware's auth_validator
        middleware.auth_validator = mock_validator
        
        roles = middleware.get_roles_from_token("Bearer header.payload.signature")
        
        assert roles == ["admin", "user"]
        mock_validator.validate_token.assert_called_once_with("header.payload.signature", "jwt")
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_get_roles_from_token_api(self, mock_auth_validator, middleware):
        """Test extracting roles from API token."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_result.roles = ["user"]
        mock_validator.validate_token.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        # Patch the middleware's auth_validator
        middleware.auth_validator = mock_validator
        
        roles = middleware.get_roles_from_token("Bearer api-token")
        
        assert roles == ["user"]
        mock_validator.validate_token.assert_called_once_with("api-token", "api")
    
    def test_get_roles_from_token_invalid_header(self, middleware):
        """Test extracting roles from invalid header."""
        roles = middleware.get_roles_from_token("Invalid header")
        assert roles == []
    
    def test_get_roles_from_token_empty(self, middleware):
        """Test extracting roles from empty token."""
        roles = middleware.get_roles_from_token("Bearer ")
        assert roles == []
    
    @patch('mcp_proxy_adapter.api.middleware.token_auth_middleware.AuthValidator')
    def test_get_roles_from_token_exception(self, mock_auth_validator, middleware):
        """Test extracting roles with exception."""
        mock_validator = Mock()
        mock_validator.validate_token.side_effect = Exception("Test error")
        mock_auth_validator.return_value = mock_validator
        
        roles = middleware.get_roles_from_token("Bearer token")
        assert roles == []
    
    @pytest.mark.asyncio
    async def test_dispatch_disabled(self, app, token_config):
        """Test dispatch when middleware is disabled."""
        token_config["enabled"] = False
        middleware = TokenAuthMiddleware(app, token_config)
        
        request = Mock()
        
        async def mock_call_next(req):
            return {"message": "success"}
        
        call_next = mock_call_next
        
        response = await middleware.dispatch(request, call_next)
        
        assert response == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_dispatch_no_header(self, app, token_config):
        """Test dispatch without authorization header."""
        middleware = TokenAuthMiddleware(app, token_config)
        
        request = Mock()
        request.headers = {}
        call_next = Mock()
        
        response = await middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 401
        
        content = response.body.decode()
        error_data = json.loads(content)
        assert error_data["error"]["message"] == "Authorization header required"
    
    @pytest.mark.asyncio
    async def test_dispatch_invalid_token(self, app, token_config):
        """Test dispatch with invalid token."""
        middleware = TokenAuthMiddleware(app, token_config)
        
        with patch.object(middleware, '_validate_token', return_value=False):
            request = Mock()
            request.headers = {"Authorization": "Bearer invalid-token"}
            call_next = Mock()
            
            response = await middleware.dispatch(request, call_next)
            
            assert isinstance(response, JSONResponse)
            assert response.status_code == 401
            
            content = response.body.decode()
            error_data = json.loads(content)
            assert error_data["error"]["message"] == "Invalid or expired token"
    
    @pytest.mark.asyncio
    async def test_dispatch_valid_token(self, app, token_config):
        """Test dispatch with valid token."""
        middleware = TokenAuthMiddleware(app, token_config)
        
        with patch.object(middleware, '_validate_token', return_value=True):
            request = Mock()
            request.headers = {"Authorization": "Bearer valid-token"}
            
            async def mock_call_next(req):
                return {"message": "success"}
            
            call_next = mock_call_next
            
            response = await middleware.dispatch(request, call_next)
            
            assert response == {"message": "success"}
    
    @pytest.mark.asyncio
    async def test_dispatch_exception(self, app, token_config):
        """Test dispatch with exception."""
        middleware = TokenAuthMiddleware(app, token_config)
        
        request = Mock()
        request.headers = {"Authorization": "Bearer token"}
        call_next = Mock()
        call_next.side_effect = Exception("Test error")
        
        response = await middleware.dispatch(request, call_next)
        
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        
        content = response.body.decode()
        error_data = json.loads(content)
        assert error_data["error"]["message"] == "Token authentication failed" 