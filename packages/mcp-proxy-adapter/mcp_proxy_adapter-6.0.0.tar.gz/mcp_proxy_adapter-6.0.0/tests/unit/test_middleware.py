"""
Unit tests for middleware components.

Tests for SecurityMiddleware, AuthMiddleware, and other middleware.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient

from mcp_security.middleware.security_middleware import SecurityMiddleware
from mcp_security.middleware.auth_middleware import AuthMiddleware
from mcp_security.middleware.roles_middleware import RolesMiddleware
from mcp_security.middleware.token_auth_middleware import TokenAuthMiddleware
from mcp_security.middleware.rate_limit_middleware import RateLimitMiddleware


class TestSecurityMiddleware:
    """Test cases for SecurityMiddleware."""
    
    def test_security_middleware_init(self, fastapi_app):
        """Test SecurityMiddleware initialization."""
        config = {
            "auth_enabled": True,
            "ssl": {"enabled": False},
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        middleware = SecurityMiddleware(fastapi_app, config)
        
        assert middleware.app == fastapi_app
        assert middleware.config == config
    
    def test_security_middleware_setup_class_method(self, fastapi_app):
        """Test SecurityMiddleware.setup class method."""
        config = {
            "auth_enabled": False,
            "ssl": {"enabled": False},
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        SecurityMiddleware.setup(fastapi_app, config)
        
        # Check that middleware was added to app
        assert len(fastapi_app.user_middleware) > 0
    
    def test_security_middleware_setup_function(self, fastapi_app):
        """Test setup_security function."""
        from mcp_security.middleware.security_middleware import setup_security
        
        config = {
            "auth_enabled": False,
            "ssl": {"enabled": False},
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        setup_security(fastapi_app, config)
        
        # Check that middleware was added to app
        assert len(fastapi_app.user_middleware) > 0
    
    @patch('mcp_security.middleware.security_middleware.RateLimitMiddleware')
    def test_security_middleware_rate_limit_enabled(self, mock_rate_limit, fastapi_app):
        """Test that rate limiting middleware is added when enabled."""
        config = {
            "auth_enabled": False,
            "ssl": {"enabled": False},
            "roles": {"enabled": False},
            "rate_limit": {
                "enabled": True,
                "requests_per_minute": 100,
                "time_window": 60
            }
        }
        
        SecurityMiddleware(fastapi_app, config)
        
        # Check that RateLimitMiddleware was called
        mock_rate_limit.assert_called_once()
    
    @patch('mcp_security.middleware.security_middleware.AuthMiddleware')
    def test_security_middleware_auth_enabled(self, mock_auth, fastapi_app):
        """Test that auth middleware is added when enabled."""
        config = {
            "auth_enabled": True,
            "auth": {
                "enabled": True,
                "api_keys": {"user1": "key1"},
                "public_paths": ["/docs"]
            },
            "ssl": {"enabled": False},
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        SecurityMiddleware(fastapi_app, config)
        
        # Check that AuthMiddleware was called
        mock_auth.assert_called_once()
    
    @patch('mcp_security.middleware.security_middleware.MTLSMiddleware')
    def test_security_middleware_mtls_enabled(self, mock_mtls, fastapi_app):
        """Test that mTLS middleware is added when enabled."""
        config = {
            "auth_enabled": False,
            "ssl": {
                "enabled": True,
                "mode": "mtls",
                "cert_file": "./certs/server.crt",
                "key_file": "./certs/server.key"
            },
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        SecurityMiddleware(fastapi_app, config)
        
        # Check that MTLSMiddleware was called
        mock_mtls.assert_called_once()
    
    @patch('mcp_security.middleware.security_middleware.TokenAuthMiddleware')
    def test_security_middleware_token_auth_enabled(self, mock_token_auth, fastapi_app):
        """Test that token auth middleware is added when enabled."""
        config = {
            "auth_enabled": False,
            "ssl": {
                "enabled": True,
                "mode": "https_only",
                "token_auth": {
                    "enabled": True,
                    "jwt_secret": "test_secret"
                }
            },
            "roles": {"enabled": False},
            "rate_limit": {"enabled": False}
        }
        
        SecurityMiddleware(fastapi_app, config)
        
        # Check that TokenAuthMiddleware was called
        mock_token_auth.assert_called_once()
    
    @patch('mcp_security.middleware.security_middleware.RolesMiddleware')
    def test_security_middleware_roles_enabled(self, mock_roles, fastapi_app):
        """Test that roles middleware is added when enabled."""
        config = {
            "auth_enabled": False,
            "ssl": {"enabled": False},
            "roles": {
                "enabled": True,
                "config_file": "roles_schema.json"
            },
            "rate_limit": {"enabled": False}
        }
        
        SecurityMiddleware(fastapi_app, config)
        
        # Check that RolesMiddleware was called
        mock_roles.assert_called_once()


class TestAuthMiddleware:
    """Test cases for AuthMiddleware."""
    
    def test_auth_middleware_init(self, fastapi_app):
        """Test AuthMiddleware initialization."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        public_paths = ["/docs", "/health"]
        
        middleware = AuthMiddleware(
            fastapi_app,
            api_keys=api_keys,
            public_paths=public_paths,
            auth_enabled=True
        )
        
        assert middleware.api_keys == api_keys
        assert middleware.public_paths == public_paths
        assert middleware.auth_enabled is True
    
    def test_auth_middleware_init_defaults(self, fastapi_app):
        """Test AuthMiddleware initialization with defaults."""
        middleware = AuthMiddleware(fastapi_app)
        
        assert middleware.api_keys == {}
        assert "/docs" in middleware.public_paths
        assert "/redoc" in middleware.public_paths
        assert "/openapi.json" in middleware.public_paths
        assert "/health" in middleware.public_paths
        assert middleware.auth_enabled is True
    
    @pytest.mark.asyncio
    async def test_auth_middleware_disabled(self, fastapi_app):
        """Test AuthMiddleware when authentication is disabled."""
        middleware = AuthMiddleware(fastapi_app, auth_enabled=False)
        
        request = Mock(spec=Request)
        request.url.path = "/secure"
        request.headers = {}
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should call next middleware without authentication
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
    
    @pytest.mark.asyncio
    async def test_auth_middleware_public_path(self, fastapi_app):
        """Test AuthMiddleware with public path."""
        middleware = AuthMiddleware(fastapi_app)
        
        request = Mock(spec=Request)
        request.url.path = "/docs"
        request.headers = {}
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should allow access to public path
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
    
    @pytest.mark.asyncio
    async def test_auth_middleware_valid_api_key_header(self, fastapi_app):
        """Test AuthMiddleware with valid API key in header."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        middleware = AuthMiddleware(fastapi_app, api_keys=api_keys)
        
        request = Mock(spec=Request)
        request.url.path = "/secure"
        request.headers = {"X-API-Key": "key1"}
        request.state = Mock()
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should allow access with valid API key
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
        assert request.state.username == "user1"
    
    @pytest.mark.asyncio
    async def test_auth_middleware_valid_api_key_query(self, fastapi_app):
        """Test AuthMiddleware with valid API key in query parameters."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        middleware = AuthMiddleware(fastapi_app, api_keys=api_keys)
        
        request = Mock(spec=Request)
        request.url.path = "/secure"
        request.headers = {}
        request.query_params = {"api_key": "admin_key"}
        request.state = Mock()
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should allow access with valid API key
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
        assert request.state.username == "admin"
    
    @pytest.mark.asyncio
    async def test_auth_middleware_invalid_api_key(self, fastapi_app):
        """Test AuthMiddleware with invalid API key."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        middleware = AuthMiddleware(fastapi_app, api_keys=api_keys)
        
        request = Mock(spec=Request)
        request.url.path = "/secure"
        request.headers = {"X-API-Key": "invalid_key"}
        
        call_next = AsyncMock()
        
        response = await middleware.dispatch(request, call_next)
        
        # Should deny access with invalid API key
        call_next.assert_not_called()
        assert response.status_code == 401
        assert b"Invalid API key" in response.body
    
    @pytest.mark.asyncio
    async def test_auth_middleware_no_api_key(self, fastapi_app):
        """Test AuthMiddleware with no API key."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        middleware = AuthMiddleware(fastapi_app, api_keys=api_keys)
        
        request = Mock(spec=Request)
        request.url.path = "/secure"
        request.headers = {}
        request.query_params = {}
        
        call_next = AsyncMock()
        
        response = await middleware.dispatch(request, call_next)
        
        # Should deny access without API key
        call_next.assert_not_called()
        assert response.status_code == 401
        assert b"API key not provided" in response.body
    
    def test_auth_middleware_is_public_path(self, fastapi_app):
        """Test AuthMiddleware._is_public_path method."""
        middleware = AuthMiddleware(fastapi_app)
        
        assert middleware._is_public_path("/docs") is True
        assert middleware._is_public_path("/health") is True
        assert middleware._is_public_path("/secure") is False
        assert middleware._is_public_path("/api/data") is False
    
    def test_auth_middleware_validate_api_key(self, fastapi_app):
        """Test AuthMiddleware._validate_api_key method."""
        api_keys = {"user1": "key1", "admin": "admin_key"}
        middleware = AuthMiddleware(fastapi_app, api_keys=api_keys)
        
        assert middleware._validate_api_key("key1") == "user1"
        assert middleware._validate_api_key("admin_key") == "admin"
        assert middleware._validate_api_key("invalid_key") is None
        assert middleware._validate_api_key("") is None


class TestRateLimitMiddleware:
    """Test cases for RateLimitMiddleware."""
    
    def test_rate_limit_middleware_init(self, fastapi_app):
        """Test RateLimitMiddleware initialization."""
        middleware = RateLimitMiddleware(
            fastapi_app,
            rate_limit=100,
            time_window=60,
            by_ip=True,
            by_user=True
        )
        
        assert middleware.rate_limit == 100
        assert middleware.time_window == 60
        assert middleware.by_ip is True
        assert middleware.by_user is True
    
    def test_rate_limit_middleware_init_defaults(self, fastapi_app):
        """Test RateLimitMiddleware initialization with defaults."""
        middleware = RateLimitMiddleware(fastapi_app)
        
        assert middleware.rate_limit == 100
        assert middleware.time_window == 60
        assert middleware.by_ip is True
        assert middleware.by_user is True
        assert "/docs" in middleware.public_paths
    
    @pytest.mark.asyncio
    async def test_rate_limit_middleware_public_path(self, fastapi_app):
        """Test RateLimitMiddleware with public path."""
        middleware = RateLimitMiddleware(fastapi_app)
        
        request = Mock(spec=Request)
        request.url.path = "/docs"
        request.client.host = "127.0.0.1"
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should allow access to public path without rate limiting
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
    
    @pytest.mark.asyncio
    async def test_rate_limit_middleware_within_limit(self, fastapi_app):
        """Test RateLimitMiddleware within rate limit."""
        middleware = RateLimitMiddleware(fastapi_app, rate_limit=2, time_window=60)
        
        request = Mock(spec=Request)
        request.url.path = "/api/data"
        request.client.host = "127.0.0.1"
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        # First request
        response1 = await middleware.dispatch(request, call_next)
        assert response1.content == b"test"
        
        # Second request
        response2 = await middleware.dispatch(request, call_next)
        assert response2.content == b"test"
    
    @pytest.mark.asyncio
    async def test_rate_limit_middleware_exceed_limit(self, fastapi_app):
        """Test RateLimitMiddleware when rate limit is exceeded."""
        middleware = RateLimitMiddleware(fastapi_app, rate_limit=1, time_window=60)
        
        request = Mock(spec=Request)
        request.url.path = "/api/data"
        request.client.host = "127.0.0.1"
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        # First request - should succeed
        response1 = await middleware.dispatch(request, call_next)
        assert response1.content == b"test"
        
        # Second request - should be rate limited
        response2 = await middleware.dispatch(request, call_next)
        assert response2.status_code == 429
        assert b"Rate limit exceeded" in response2.body
    
    @pytest.mark.asyncio
    async def test_rate_limit_middleware_by_user(self, fastapi_app):
        """Test RateLimitMiddleware with user-based limiting."""
        middleware = RateLimitMiddleware(fastapi_app, rate_limit=1, time_window=60, by_user=True)
        
        request = Mock(spec=Request)
        request.url.path = "/api/data"
        request.client.host = "127.0.0.1"
        request.state = Mock()
        request.state.username = "user1"
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        # First request - should succeed
        response1 = await middleware.dispatch(request, call_next)
        assert response1.content == b"test"
        
        # Second request - should be rate limited
        response2 = await middleware.dispatch(request, call_next)
        assert response2.status_code == 429
        assert b"Rate limit exceeded" in response2.body
    
    def test_rate_limit_middleware_clean_old_requests(self, fastapi_app):
        """Test RateLimitMiddleware._clean_old_requests method."""
        import time
        
        middleware = RateLimitMiddleware(fastapi_app, time_window=60)
        
        # Create some old requests
        old_time = time.time() - 120  # 2 minutes ago
        current_time = time.time()
        
        requests = [old_time, old_time, current_time, current_time]
        
        middleware._clean_old_requests(requests, current_time)
        
        # Should only keep recent requests
        assert len(requests) == 2
        assert all(req >= current_time - 60 for req in requests)
    
    def test_rate_limit_middleware_is_public_path(self, fastapi_app):
        """Test RateLimitMiddleware._is_public_path method."""
        middleware = RateLimitMiddleware(fastapi_app)
        
        assert middleware._is_public_path("/docs") is True
        assert middleware._is_public_path("/health") is True
        assert middleware._is_public_path("/api/data") is False
        assert middleware._is_public_path("/secure") is False


class TestTokenAuthMiddleware:
    """Test cases for TokenAuthMiddleware."""
    
    def test_token_auth_middleware_init(self, fastapi_app):
        """Test TokenAuthMiddleware initialization."""
        token_config = {
            "enabled": True,
            "header_name": "Authorization",
            "token_prefix": "Bearer",
            "tokens_file": "tokens.json",
            "jwt_secret": "test_secret"
        }
        
        middleware = TokenAuthMiddleware(fastapi_app, token_config)
        
        assert middleware.enabled is True
        assert middleware.header_name == "Authorization"
        assert middleware.token_prefix == "Bearer"
        assert middleware.tokens_file == "tokens.json"
        assert middleware.jwt_secret == "test_secret"
    
    @pytest.mark.asyncio
    async def test_token_auth_middleware_disabled(self, fastapi_app):
        """Test TokenAuthMiddleware when disabled."""
        token_config = {"enabled": False}
        middleware = TokenAuthMiddleware(fastapi_app, token_config)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should call next middleware without token validation
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
    
    @pytest.mark.asyncio
    async def test_token_auth_middleware_no_header(self, fastapi_app):
        """Test TokenAuthMiddleware with no authorization header."""
        token_config = {"enabled": True}
        middleware = TokenAuthMiddleware(fastapi_app, token_config)
        
        request = Mock(spec=Request)
        request.headers = {}
        
        call_next = AsyncMock()
        
        response = await middleware.dispatch(request, call_next)
        
        # Should deny access without authorization header
        call_next.assert_not_called()
        assert response.status_code == 401
        assert b"Authorization header required" in response.body
    
    @pytest.mark.asyncio
    async def test_token_auth_middleware_invalid_token(self, fastapi_app):
        """Test TokenAuthMiddleware with invalid token."""
        token_config = {"enabled": True}
        middleware = TokenAuthMiddleware(fastapi_app, token_config)
        
        request = Mock(spec=Request)
        request.headers = {"Authorization": "Bearer invalid_token"}
        
        call_next = AsyncMock()
        
        response = await middleware.dispatch(request, call_next)
        
        # Should deny access with invalid token
        call_next.assert_not_called()
        assert response.status_code == 401
        assert b"Invalid or expired token" in response.body


class TestRolesMiddleware:
    """Test cases for RolesMiddleware."""
    
    def test_roles_middleware_init(self, fastapi_app, temp_dir):
        """Test RolesMiddleware initialization."""
        # Create a temporary roles schema file
        schema_file = temp_dir / "roles_schema.json"
        schema_file.write_text('{"roles": {}, "permissions": {}, "role_hierarchy": {"roles": {}}, "default_policy": {}}')
        
        middleware = RolesMiddleware(fastapi_app, str(schema_file))
        
        assert middleware.roles_config_path == str(schema_file)
    
    @pytest.mark.asyncio
    async def test_roles_middleware_dispatch(self, fastapi_app, temp_dir):
        """Test RolesMiddleware dispatch method."""
        # Create a temporary roles schema file
        schema_file = temp_dir / "roles_schema.json"
        schema_file.write_text('{"roles": {}, "permissions": {}, "role_hierarchy": {"roles": {}}, "default_policy": {}}')
        
        middleware = RolesMiddleware(fastapi_app, str(schema_file))
        
        request = Mock(spec=Request)
        request.url.path = "/api/data"
        request.headers = {}
        
        call_next = AsyncMock()
        call_next.return_value = Response(content="test")
        
        response = await middleware.dispatch(request, call_next)
        
        # Should call next middleware
        call_next.assert_called_once_with(request)
        assert response.content == b"test"
