"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

from mcp_security.schemas.models import (
    Permission, Role, RoleHierarchy, DefaultPolicy, RolesSchema,
    SSLConfig, TokenAuthConfig, RoleConfig, RateLimitConfig,
    AuthConfig, SecurityConfig, PermissionLevel, SSLMode
)


class TestPermission:
    """Test cases for Permission model."""
    
    def test_valid_permission(self):
        """Test creating valid permission."""
        permission = Permission(
            name="read",
            description="Read access",
            level=PermissionLevel.READ
        )
        assert permission.name == "read"
        assert permission.description == "Read access"
        assert permission.level == PermissionLevel.READ
    
    def test_invalid_level(self):
        """Test invalid permission level."""
        with pytest.raises(ValidationError):
            Permission(
                name="read",
                description="Read access",
                level="invalid"
            )


class TestRole:
    """Test cases for Role model."""
    
    def test_valid_role(self):
        """Test creating valid role."""
        role = Role(
            name="admin",
            description="Administrator",
            permissions=["read", "write"],
            priority=100
        )
        assert role.name == "admin"
        assert role.description == "Administrator"
        assert role.permissions == ["read", "write"]
        assert role.priority == 100
    
    def test_default_priority(self):
        """Test default priority value."""
        role = Role(
            name="user",
            description="User",
            permissions=["read"]
        )
        assert role.priority == 50


class TestRoleHierarchy:
    """Test cases for RoleHierarchy model."""
    
    def test_valid_hierarchy(self):
        """Test creating valid hierarchy."""
        hierarchy = RoleHierarchy(
            roles={
                "admin": ["user"],
                "user": ["guest"]
            }
        )
        assert "admin" in hierarchy.roles
        assert "user" in hierarchy.roles["admin"]


class TestDefaultPolicy:
    """Test cases for DefaultPolicy model."""
    
    def test_valid_policy(self):
        """Test creating valid policy."""
        policy = DefaultPolicy(
            deny_by_default=True,
            require_role_match=True,
            case_sensitive=False,
            allow_wildcard=True
        )
        assert policy.deny_by_default is True
        assert policy.require_role_match is True
        assert policy.case_sensitive is False
        assert policy.allow_wildcard is True


class TestRolesSchema:
    """Test cases for RolesSchema model."""
    
    def test_valid_schema(self):
        """Test creating valid schema."""
        schema = RolesSchema(
            roles={
                "admin": Role(
                    name="admin",
                    description="Administrator",
                    permissions=["read", "write"]
                )
            },
            permissions={
                "read": Permission(
                    name="read",
                    description="Read access",
                    level=PermissionLevel.READ
                )
            },
            role_hierarchy=RoleHierarchy(roles={}),
            default_policy=DefaultPolicy(),
            server_roles={}
        )
        assert "admin" in schema.roles
        assert "read" in schema.permissions
    
    def test_get_role(self):
        """Test getting role from schema."""
        schema = RolesSchema(
            roles={
                "admin": Role(
                    name="admin",
                    description="Administrator",
                    permissions=["read", "write"]
                )
            },
            permissions={},
            role_hierarchy=RoleHierarchy(roles={}),
            default_policy=DefaultPolicy(),
            server_roles={}
        )
        
        role = schema.get_role("admin")
        assert role is not None
        assert role.name == "admin"
        
        # Test non-existent role
        role = schema.get_role("nonexistent")
        assert role is None
    
    def test_has_role(self):
        """Test checking if role exists."""
        schema = RolesSchema(
            roles={
                "admin": Role(
                    name="admin",
                    description="Administrator",
                    permissions=["read", "write"]
                )
            },
            permissions={},
            role_hierarchy=RoleHierarchy(roles={}),
            default_policy=DefaultPolicy(),
            server_roles={}
        )
        
        assert schema.has_role("admin") is True
        assert schema.has_role("nonexistent") is False
    
    def test_has_permission(self):
        """Test checking if permission exists."""
        schema = RolesSchema(
            roles={},
            permissions={
                "read": Permission(
                    name="read",
                    description="Read access",
                    level=PermissionLevel.READ
                )
            },
            role_hierarchy=RoleHierarchy(roles={}),
            default_policy=DefaultPolicy(),
            server_roles={}
        )
        
        assert schema.has_permission("read") is True
        assert schema.has_permission("nonexistent") is False


class TestSSLConfig:
    """Test cases for SSLConfig model."""
    
    def test_valid_ssl_config(self):
        """Test creating valid SSL config."""
        config = SSLConfig(
            enabled=True,
            cert_file="cert.pem",
            key_file="key.pem",
            ca_cert_file="ca.pem",
            mode=SSLMode.REQUIRED
        )
        assert config.enabled is True
        assert config.cert_file == "cert.pem"
        assert config.key_file == "key.pem"
        assert config.ca_cert_file == "ca.pem"
        assert config.mode == SSLMode.REQUIRED


class TestTokenAuthConfig:
    """Test cases for TokenAuthConfig model."""
    
    def test_valid_token_config(self):
        """Test creating valid token config."""
        config = TokenAuthConfig(
            enabled=True,
            header_name="Authorization",
            token_prefix="Bearer",
            tokens_file="tokens.json",
            jwt_secret="secret123"
        )
        assert config.enabled is True
        assert config.header_name == "Authorization"
        assert config.token_prefix == "Bearer"
        assert config.tokens_file == "tokens.json"
        assert config.jwt_secret == "secret123"
    
    def test_jwt_secret_validation(self):
        """Test JWT secret validation."""
        # Valid secret
        config = TokenAuthConfig(
            enabled=True,
            jwt_secret="secret123"
        )
        assert config.jwt_secret == "secret123"
        
        # Invalid secret (too short)
        with pytest.raises(ValidationError):
            TokenAuthConfig(
                enabled=True,
                jwt_secret="123"
            )


class TestRoleConfig:
    """Test cases for RoleConfig model."""
    
    def test_valid_role_config(self):
        """Test creating valid role config."""
        config = RoleConfig(
            enabled=True,
            config_file="roles.json",
            default_policy=DefaultPolicy()
        )
        assert config.enabled is True
        assert config.config_file == "roles.json"


class TestRateLimitConfig:
    """Test cases for RateLimitConfig model."""
    
    def test_valid_rate_limit_config(self):
        """Test creating valid rate limit config."""
        config = RateLimitConfig(
            enabled=True,
            rate_limit=100,
            time_window=60,
            by_ip=True,
            by_user=True
        )
        assert config.enabled is True
        assert config.rate_limit == 100
        assert config.time_window == 60
        assert config.by_ip is True
        assert config.by_user is True


class TestAuthConfig:
    """Test cases for AuthConfig model."""
    
    def test_valid_auth_config(self):
        """Test creating valid auth config."""
        config = AuthConfig(
            enabled=True,
            api_keys={"key1": "user1"},
            jwt_secret="secret123"
        )
        assert config.enabled is True
        assert config.api_keys == {"key1": "user1"}
        assert config.jwt_secret == "secret123"


class TestSecurityConfig:
    """Test cases for SecurityConfig model."""
    
    def test_valid_security_config(self):
        """Test creating valid security config."""
        config = SecurityConfig(
            auth=AuthConfig(enabled=True),
            ssl=SSLConfig(enabled=False),
            roles=RoleConfig(enabled=True),
            rate_limit=RateLimitConfig(enabled=False)
        )
        assert config.auth.enabled is True
        assert config.ssl.enabled is False
        assert config.roles.enabled is True
        assert config.rate_limit.enabled is False
    
    def test_legacy_compatibility(self):
        """Test legacy compatibility fields."""
        config = SecurityConfig(
            auth_enabled=True,
            rate_limit_enabled=False
        )
        assert config.auth_enabled is True
        assert config.rate_limit_enabled is False
        assert config.auth.enabled is True
        assert config.rate_limit.enabled is False
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        config = SecurityConfig(
            auth=AuthConfig(enabled=True),
            ssl=SSLConfig(enabled=False)
        )
        config_dict = config.to_dict()
        assert "auth" in config_dict
        assert "ssl" in config_dict
        assert config_dict["auth"]["enabled"] is True
        assert config_dict["ssl"]["enabled"] is False
    
    def test_from_dict(self):
        """Test creating from dictionary."""
        config_dict = {
            "auth": {"enabled": True},
            "ssl": {"enabled": False}
        }
        config = SecurityConfig.from_dict(config_dict)
        assert config.auth.enabled is True
        assert config.ssl.enabled is False


class TestEnums:
    """Test cases for enums."""
    
    def test_permission_level_enum(self):
        """Test PermissionLevel enum."""
        assert PermissionLevel.READ == "read"
        assert PermissionLevel.WRITE == "write"
        assert PermissionLevel.ADMIN == "admin"
    
    def test_ssl_mode_enum(self):
        """Test SSLMode enum."""
        assert SSLMode.REQUIRED == "required"
        assert SSLMode.OPTIONAL == "optional"
        assert SSLMode.DISABLED == "disabled"
