"""
Test configuration and fixtures for MCP Security Framework.

This module provides common fixtures and configuration for all tests.
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any

# Import from mcp_security_framework if available, otherwise use mock objects
try:
    from mcp_security_framework.schemas.models import (
        RolesSchema, Role, Permission, RoleHierarchy, DefaultPolicy,
        SecurityConfig, SSLConfig, AuthConfig, RoleConfig, RateLimitConfig
    )
    from mcp_security_framework.utils import SchemaLoader
    SECURITY_FRAMEWORK_AVAILABLE = True
except ImportError:
    # Create mock classes for testing when framework is not available
    class MockBase:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class RolesSchema(MockBase): pass
    class Role(MockBase): pass
    class Permission(MockBase): pass
    class RoleHierarchy(MockBase): pass
    class DefaultPolicy(MockBase): pass
    class SecurityConfig(MockBase): pass
    class SSLConfig(MockBase): pass
    class AuthConfig(MockBase): pass
    class RoleConfig(MockBase): pass
    class RateLimitConfig(MockBase): pass
    class SchemaLoader(MockBase): pass
    SECURITY_FRAMEWORK_AVAILABLE = False


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_permissions():
    """Sample permissions for testing."""
    return {
        "read": Permission(description="Read access", level=1),
        "write": Permission(description="Write access", level=2),
        "delete": Permission(description="Delete access", level=3),
        "admin": Permission(description="Admin access", level=4),
        "system": Permission(description="System access", level=5)
    }


@pytest.fixture
def sample_roles():
    """Sample roles for testing."""
    return {
        "super-admin": Role(
            description="Super administrator",
            allowed_servers=["*"],
            allowed_clients=["*"],
            permissions=["read", "write", "delete", "admin", "system"],
            priority=200
        ),
        "admin": Role(
            description="Administrator",
            allowed_servers=["*"],
            allowed_clients=["*"],
            permissions=["read", "write", "delete", "admin"],
            priority=100
        ),
        "operator": Role(
            description="Operator",
            allowed_servers=["kubernetes_manager", "docker_manager"],
            allowed_clients=["admin", "super-admin", "operator"],
            permissions=["read", "write"],
            priority=50
        ),
        "user": Role(
            description="Regular user",
            allowed_servers=["basic_commands"],
            allowed_clients=["admin", "super-admin", "operator", "user"],
            permissions=["read"],
            priority=10
        ),
        "guest": Role(
            description="Guest user",
            allowed_servers=["help", "info"],
            allowed_clients=["admin", "super-admin", "operator", "user", "guest"],
            permissions=["read"],
            priority=1
        )
    }


@pytest.fixture
def sample_role_hierarchy():
    """Sample role hierarchy for testing."""
    return RoleHierarchy(roles={
        "super-admin": ["admin", "user"],
        "admin": ["operator", "user"],
        "operator": ["user"],
        "user": ["guest"]
    })


@pytest.fixture
def sample_default_policy():
    """Sample default policy for testing."""
    return DefaultPolicy(
        deny_by_default=True,
        require_role_match=True,
        case_sensitive=False,
        allow_wildcard=True
    )


@pytest.fixture
def sample_roles_schema(sample_roles, sample_permissions, sample_role_hierarchy, sample_default_policy):
    """Sample roles schema for testing."""
    return RolesSchema(
        roles=sample_roles,
        permissions=sample_permissions,
        role_hierarchy=sample_role_hierarchy,
        default_policy=sample_default_policy,
        server_roles={
            "kubernetes_manager": {
                "required_roles": ["admin", "operator"],
                "allowed_commands": ["k8s_*", "system_monitor"]
            },
            "basic_commands": {
                "required_roles": ["user", "admin"],
                "allowed_commands": ["help", "info", "echo"]
            }
        }
    )


@pytest.fixture
def sample_security_config():
    """Sample security configuration for testing."""
    return SecurityConfig(
        auth=AuthConfig(
            enabled=True,
            api_keys={"user1": "key1", "admin": "admin_key"},
            public_paths=["/docs", "/health"]
        ),
        ssl=SSLConfig(
            enabled=True,
            mode="https_only",
            cert_file="./certs/server.crt",
            key_file="./certs/server.key"
        ),
        roles=RoleConfig(
            enabled=True,
            config_file="schemas/roles_schema.json"
        ),
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_minute=100,
            time_window=60
        )
    )


@pytest.fixture
def roles_schema_file(temp_dir, sample_roles_schema):
    """Create a temporary roles schema file."""
    schema_file = temp_dir / "roles_schema.json"
    SchemaLoader.save_roles_schema(sample_roles_schema, schema_file)
    return schema_file


@pytest.fixture
def security_config_file(temp_dir, sample_security_config):
    """Create a temporary security config file."""
    config_file = temp_dir / "security_config.json"
    SchemaLoader.save_security_config(sample_security_config, config_file)
    return config_file


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing serialization."""
    return {
        "roles": {
            "admin": {
                "description": "Administrator",
                "allowed_servers": ["*"],
                "allowed_clients": ["*"],
                "permissions": ["read", "write", "delete", "admin"],
                "priority": 100
            },
            "user": {
                "description": "Regular user",
                "allowed_servers": ["basic_commands"],
                "allowed_clients": ["admin", "user"],
                "permissions": ["read"],
                "priority": 10
            }
        },
        "permissions": {
            "read": {
                "description": "Read access",
                "level": 1
            },
            "write": {
                "description": "Write access",
                "level": 2
            }
        },
        "role_hierarchy": {
            "admin": ["user"]
        },
        "default_policy": {
            "deny_by_default": True,
            "require_role_match": True,
            "case_sensitive": False,
            "allow_wildcard": True
        },
        "server_roles": {}
    }


@pytest.fixture
def test_certificates(temp_dir):
    """Create test certificates for testing."""
    cert_dir = temp_dir / "certs"
    cert_dir.mkdir()
    
    # Create dummy certificate files
    (cert_dir / "ca.crt").write_text("-----BEGIN CERTIFICATE-----\nDUMMY CA CERT\n-----END CERTIFICATE-----")
    (cert_dir / "ca.key").write_text("-----BEGIN PRIVATE KEY-----\nDUMMY CA KEY\n-----END PRIVATE KEY-----")
    (cert_dir / "server.crt").write_text("-----BEGIN CERTIFICATE-----\nDUMMY SERVER CERT\n-----END CERTIFICATE-----")
    (cert_dir / "server.key").write_text("-----BEGIN PRIVATE KEY-----\nDUMMY SERVER KEY\n-----END PRIVATE KEY-----")
    (cert_dir / "client.crt").write_text("-----BEGIN CERTIFICATE-----\nDUMMY CLIENT CERT\n-----END CERTIFICATE-----")
    (cert_dir / "client.key").write_text("-----BEGIN PRIVATE KEY-----\nDUMMY CLIENT KEY\n-----END PRIVATE KEY-----")
    
    return cert_dir


@pytest.fixture
def sample_tokens_file(temp_dir):
    """Create a sample tokens file for testing."""
    tokens_file = temp_dir / "tokens.json"
    tokens_data = {
        "tokens": {
            "user_token_1": {
                "user": "user1",
                "roles": ["user"],
                "expires": "2025-12-31T23:59:59Z"
            },
            "admin_token_1": {
                "user": "admin",
                "roles": ["admin"],
                "expires": "2025-12-31T23:59:59Z"
            }
        }
    }
    tokens_file.write_text(json.dumps(tokens_data, indent=2))
    return tokens_file


@pytest.fixture
def fastapi_app():
    """Create a FastAPI app for testing."""
    from fastapi import FastAPI
    return FastAPI(title="Test Security API", version="1.0.0")


@pytest.fixture
def test_client(fastapi_app):
    """Create a test client for FastAPI app."""
    from fastapi.testclient import TestClient
    return TestClient(fastapi_app)


@pytest.fixture
def mock_request():
    """Create a mock request object for testing."""
    from unittest.mock import Mock
    from fastapi import Request
    
    request = Mock(spec=Request)
    request.headers = {}
    request.url.path = "/test"
    request.method = "GET"
    request.client.host = "127.0.0.1"
    request.state = Mock()
    
    return request


@pytest.fixture
def mock_response():
    """Create a mock response object for testing."""
    from unittest.mock import Mock
    from fastapi import Response
    
    response = Mock(spec=Response)
    response.status_code = 200
    response.headers = {}
    
    return response


@pytest.fixture
def sample_validation_cases():
    """Sample validation test cases."""
    return [
        {
            "name": "admin_has_full_access",
            "user_roles": ["admin"],
            "required_permissions": ["read", "write", "delete"],
            "server_role": "kubernetes_manager",
            "expected": True,
            "description": "Admin should have full access to kubernetes manager"
        },
        {
            "name": "user_limited_access",
            "user_roles": ["user"],
            "required_permissions": ["read"],
            "server_role": "basic_commands",
            "expected": True,
            "description": "User should have read access to basic commands"
        },
        {
            "name": "user_no_admin_access",
            "user_roles": ["user"],
            "required_permissions": ["admin"],
            "server_role": "admin_panel",
            "expected": False,
            "description": "User should not have admin access"
        },
        {
            "name": "guest_limited_access",
            "user_roles": ["guest"],
            "required_permissions": ["read"],
            "server_role": "help",
            "expected": True,
            "description": "Guest should have read access to help"
        },
        {
            "name": "guest_no_write_access",
            "user_roles": ["guest"],
            "required_permissions": ["write"],
            "server_role": "basic_commands",
            "expected": False,
            "description": "Guest should not have write access"
        },
        {
            "name": "super_admin_inheritance",
            "user_roles": ["super-admin"],
            "required_permissions": ["read"],
            "server_role": "basic_commands",
            "expected": True,
            "description": "Super admin should inherit user permissions"
        }
    ]


@pytest.fixture
def sample_error_codes():
    """Sample error codes for testing."""
    return {
        "invalid_request": -32600,
        "method_not_found": -32601,
        "invalid_params": -32602,
        "internal_error": -32603,
        "auth_disabled": -32001,
        "invalid_config": -32002,
        "cert_validation_failed": -32003,
        "token_validation_failed": -32004,
        "mtls_validation_failed": -32005,
        "ssl_validation_failed": -32006,
        "role_validation_failed": -32007,
        "cert_expired": -32008,
        "cert_not_found": -32009,
        "token_expired": -32010,
        "token_not_found": -32011
    } 