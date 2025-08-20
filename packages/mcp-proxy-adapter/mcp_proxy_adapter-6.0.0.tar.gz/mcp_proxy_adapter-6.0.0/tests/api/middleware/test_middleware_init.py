"""
Tests for middleware initialization module.

Tests middleware setup with mTLS integration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from fastapi import FastAPI

from mcp_proxy_adapter.api.middleware import setup_middleware


class TestMiddlewareSetup:
    """Test cases for middleware setup."""
    
    @pytest.fixture
    def mock_app(self):
        """Create mock FastAPI application."""
        app = Mock(spec=FastAPI)
        app.add_middleware = Mock()
        return app
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_basic(self, mock_config, mock_app):
        """Test basic middleware setup without mTLS."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {"enabled": False}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify middleware were added
        assert mock_app.add_middleware.call_count >= 4  # At least 4 middleware
        
        # Verify specific middleware calls
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        
        # Should have error handling, logging, auth, and performance middleware
        from mcp_proxy_adapter.api.middleware.error_handling import ErrorHandlingMiddleware
        from mcp_proxy_adapter.api.middleware.logging import LoggingMiddleware
        from mcp_proxy_adapter.api.middleware.auth import AuthMiddleware
        from mcp_proxy_adapter.api.middleware.performance import PerformanceMiddleware
        
        assert ErrorHandlingMiddleware in middleware_calls
        assert LoggingMiddleware in middleware_calls
        assert AuthMiddleware in middleware_calls
        assert PerformanceMiddleware in middleware_calls
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_with_rate_limit(self, mock_config, mock_app):
        """Test middleware setup with rate limiting enabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": True,
            "rate_limit": 100,
            "rate_limit_window": 60,
            "auth_enabled": False,
            "ssl": {"enabled": False}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify rate limit middleware was added
        from mcp_proxy_adapter.api.middleware.rate_limit import RateLimitMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert RateLimitMiddleware in middleware_calls
        
        # Verify rate limit parameters
        rate_limit_call = None
        for call in mock_app.add_middleware.call_args_list:
            if call[0][0] == RateLimitMiddleware:
                rate_limit_call = call
                break
        
        assert rate_limit_call is not None
        assert rate_limit_call[1]["rate_limit"] == 100
        assert rate_limit_call[1]["time_window"] == 60
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_with_mtls_enabled(self, mock_config, mock_app):
        """Test middleware setup with mTLS enabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {
                "enabled": True,
                "mode": "mtls",
                "ca_cert": "/path/to/ca.crt",
                "verify_client": True,
                "client_cert_required": True,
                "allowed_roles": ["admin", "user"],
                "require_roles": True,
                "token_auth": {"enabled": False}
            },
            "roles": {"enabled": True}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify mTLS middleware was added
        from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert MTLSMiddleware in middleware_calls
        
        # Verify mTLS configuration
        mtls_call = None
        for call in mock_app.add_middleware.call_args_list:
            if call[0][0] == MTLSMiddleware:
                mtls_call = call
                break
        
        assert mtls_call is not None
        mtls_config = mtls_call[1]["mtls_config"]
        assert mtls_config["enabled"] is True
        assert mtls_config["ca_cert"] == "/path/to/ca.crt"
        assert mtls_config["verify_client"] is True
        assert mtls_config["client_cert_required"] is True
        assert mtls_config["allowed_roles"] == ["admin", "user"]
        assert mtls_config["require_roles"] is True
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_with_token_auth_enabled(self, mock_config, mock_app):
        """Test middleware setup with token authentication enabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {
                "enabled": True,
                "mode": "https_only",
                "cert_file": "/path/to/cert.crt",
                "key_file": "/path/to/key.key",
                "token_auth": {
                    "enabled": True,
                    "header_name": "Authorization",
                    "token_prefix": "Bearer",
                    "tokens_file": "tokens.json",
                    "token_expiry": 3600,
                    "jwt_secret": "test-secret",
                    "jwt_algorithm": "HS256"
                }
            },
            "roles": {"enabled": True}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify token authentication middleware was added
        from mcp_proxy_adapter.api.middleware.token_auth_middleware import TokenAuthMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert TokenAuthMiddleware in middleware_calls
        
        # Verify token authentication configuration
        token_auth_call = None
        for call in mock_app.add_middleware.call_args_list:
            if call[0][0] == TokenAuthMiddleware:
                token_auth_call = call
                break
        
        assert token_auth_call is not None
        token_config = token_auth_call[1]["token_config"]
        assert token_config["enabled"] is True
        assert token_config["header_name"] == "Authorization"
        assert token_config["token_prefix"] == "Bearer"
        assert token_config["tokens_file"] == "tokens.json"
        assert token_config["token_expiry"] == 3600
        assert token_config["jwt_secret"] == "test-secret"
        assert token_config["jwt_algorithm"] == "HS256"
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_with_token_auth_disabled(self, mock_config, mock_app):
        """Test middleware setup with token authentication disabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {
                "enabled": True,
                "mode": "https_only",
                "cert_file": "/path/to/cert.crt",
                "key_file": "/path/to/key.key",
                "token_auth": {"enabled": False}
            },
            "roles": {"enabled": True}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify token authentication middleware was NOT added
        from mcp_proxy_adapter.api.middleware.token_auth_middleware import TokenAuthMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert TokenAuthMiddleware not in middleware_calls
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_ssl_enabled_but_not_mtls(self, mock_config, mock_app):
        """Test middleware setup with SSL enabled but not mTLS mode."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {
                "enabled": True,
                "mode": "ssl",  # Not mTLS
                "cert_file": "/path/to/cert.crt",
                "key_file": "/path/to/key.key",
                "token_auth": {"enabled": False}
            }
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify mTLS middleware was NOT added
        from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert MTLSMiddleware not in middleware_calls
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_ssl_disabled(self, mock_config, mock_app):
        """Test middleware setup with SSL disabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "api_keys": {"test-key": "test-value"},
            "ssl": {"enabled": False}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify mTLS middleware was NOT added
        from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert MTLSMiddleware not in middleware_calls
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_mtls_default_config(self, mock_config, mock_app):
        """Test middleware setup with mTLS using default configuration."""
        # Setup mock config with minimal mTLS settings
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": False,
            "ssl": {
                "enabled": True,
                "mode": "mtls",
                "ca_cert": "/path/to/ca.crt"
                # Other settings will use defaults
            }
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify mTLS middleware was added with default values
        from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert MTLSMiddleware in middleware_calls
        
        # Verify default mTLS configuration
        mtls_call = None
        for call in mock_app.add_middleware.call_args_list:
            if call[0][0] == MTLSMiddleware:
                mtls_call = call
                break
        
        assert mtls_call is not None
        mtls_config = mtls_call[1]["mtls_config"]
        assert mtls_config["enabled"] is True
        assert mtls_config["ca_cert"] == "/path/to/ca.crt"
        assert mtls_config["verify_client"] is True  # Default
        assert mtls_config["client_cert_required"] is True  # Default
        assert mtls_config["allowed_roles"] == []  # Default
        assert mtls_config["require_roles"] is False  # Default
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_complete_config(self, mock_config, mock_app):
        """Test middleware setup with complete configuration."""
        # Setup mock config with all features enabled
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": True,
            "rate_limit": 200,
            "rate_limit_window": 120,
            "auth_enabled": True,
            "api_keys": {"key1": "value1", "key2": "value2"},
            "ssl": {
                "enabled": True,
                "mode": "mtls",
                "ca_cert": "/path/to/ca.crt",
                "verify_client": True,
                "client_cert_required": True,
                "allowed_roles": ["admin", "user", "guest"],
                "require_roles": True
            }
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify all middleware were added
        from mcp_proxy_adapter.api.middleware.error_handling import ErrorHandlingMiddleware
        from mcp_proxy_adapter.api.middleware.logging import LoggingMiddleware
        from mcp_proxy_adapter.api.middleware.auth import AuthMiddleware
        from mcp_proxy_adapter.api.middleware.rate_limit import RateLimitMiddleware
        from mcp_proxy_adapter.api.middleware.performance import PerformanceMiddleware
        from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        
        assert ErrorHandlingMiddleware in middleware_calls
        assert LoggingMiddleware in middleware_calls
        assert AuthMiddleware in middleware_calls
        assert RateLimitMiddleware in middleware_calls
        assert PerformanceMiddleware in middleware_calls
        assert MTLSMiddleware in middleware_calls
        
        # Verify all required middleware are present
        # Note: Order may vary depending on configuration
    
    @patch('mcp_proxy_adapter.config.config')
    def test_setup_middleware_auth_disabled(self, mock_config, mock_app):
        """Test middleware setup with authentication disabled."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": False,
            "ssl": {"enabled": False}
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify auth middleware was still added but with auth_enabled=False
        from mcp_proxy_adapter.api.middleware.auth import AuthMiddleware
        
        middleware_calls = [call[0][0] for call in mock_app.add_middleware.call_args_list]
        assert AuthMiddleware in middleware_calls
        
        # Verify auth configuration
        auth_call = None
        for call in mock_app.add_middleware.call_args_list:
            if call[0][0] == AuthMiddleware:
                auth_call = call
                break
        
        assert auth_call is not None
        assert auth_call[1]["auth_enabled"] is False
    
    @patch('mcp_proxy_adapter.config.config')
    @patch('mcp_proxy_adapter.api.middleware.logger')
    def test_setup_middleware_logging(self, mock_logger, mock_config, mock_app):
        """Test middleware setup logging."""
        # Setup mock config
        mock_config.get.side_effect = lambda key, default=None: {
            "rate_limit_enabled": False,
            "auth_enabled": True,
            "ssl": {
                "enabled": True,
                "mode": "mtls",
                "ca_cert": "/path/to/ca.crt"
            }
        }.get(key, default)
        
        setup_middleware(mock_app)
        
        # Verify logging calls
        mock_logger.info.assert_called()
        
        # Check for specific log messages
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("mTLS middleware added" in call for call in log_calls)
        assert any("Auth enabled: True" in call for call in log_calls) 