"""
Integration tests for MCP Security Framework.

Tests for complete security flow and component interactions.
"""

import pytest
import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp_security.middleware.security_middleware import setup_security
from mcp_security.schemas.models import SecurityConfig, RolesSchema
from mcp_security.utils.schema_loader import SchemaLoader
from mcp_security.utils.permission_validator import PermissionValidator


class TestSecurityIntegration:
    """Integration tests for complete security flow."""
    
    def test_complete_security_setup(self, temp_dir):
        """Test complete security setup with all components."""
        # Create FastAPI app
        app = FastAPI()
        
        # Create security configuration
        security_config = SecurityConfig(
            auth_enabled=True,
            auth={
                "enabled": True,
                "api_keys": {"user1": "key1", "admin": "admin_key"},
                "public_paths": ["/docs", "/health"]
            },
            ssl={
                "enabled": False
            },
            roles={
                "enabled": True,
                "config_file": str(temp_dir / "roles_schema.json")
            },
            rate_limit={
                "enabled": True,
                "requests_per_minute": 100,
                "time_window": 60
            }
        )
        
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        SchemaLoader.save_roles_schema(roles_schema, temp_dir / "roles_schema.json")
        
        # Setup security middleware
        setup_security(app, security_config.to_dict())
        
        # Create test client
        client = TestClient(app)
        
        # Test public path access
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test protected path without auth
        response = client.get("/api/data")
        assert response.status_code == 401
        
        # Test protected path with valid API key
        response = client.get("/api/data", headers={"X-API-Key": "key1"})
        # Should work if no specific endpoint exists, or return 404
        assert response.status_code in [200, 404]
    
    def test_roles_integration_with_auth(self, temp_dir):
        """Test integration of roles with authentication."""
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        SchemaLoader.save_roles_schema(roles_schema, temp_dir / "roles_schema.json")
        
        # Create permission validator
        validator = PermissionValidator(roles_schema)
        
        # Test admin access
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read", "write"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "write" in result.effective_permissions
        assert "admin" in result.matched_roles
        
        # Test user access (should be limited)
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "user" in result.matched_roles
        
        # Test user access to admin-only permissions
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["admin"],
            server_role="admin_panel"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007
    
    def test_serialization_integration(self, temp_dir):
        """Test integration of serialization with validation."""
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        
        # Save to file
        schema_file = temp_dir / "test_roles_schema.json"
        SchemaLoader.save_roles_schema(roles_schema, schema_file)
        
        # Load from file
        loaded_schema = SchemaLoader.load_roles_schema(schema_file)
        
        assert loaded_schema is not None
        
        # Create permission validator with loaded schema
        validator = PermissionValidator(loaded_schema)
        
        # Test validation with loaded schema
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
    
    def test_security_config_integration(self, temp_dir):
        """Test integration of security configuration."""
        # Create security config
        config = SecurityConfig(
            auth_enabled=True,
            rate_limit_enabled=True,
            auth={
                "enabled": True,
                "api_keys": {"user1": "key1"}
            },
            rate_limit={
                "enabled": True,
                "requests_per_minute": 100
            }
        )
        
        # Save to file
        config_file = temp_dir / "security_config.json"
        SchemaLoader.save_security_config(config, config_file)
        
        # Load from file
        loaded_config = SchemaLoader.load_security_config(config_file)
        
        assert loaded_config is not None
        assert loaded_config.auth_enabled == config.auth_enabled
        assert loaded_config.rate_limit_enabled == config.rate_limit_enabled
        assert loaded_config.auth.enabled == config.auth.enabled
        assert loaded_config.rate_limit.enabled == config.rate_limit.enabled
        
        # Convert to dict and back
        config_dict = loaded_config.to_dict()
        restored_config = SecurityConfig.from_dict(config_dict)
        
        assert restored_config.auth_enabled == config.auth_enabled
        assert restored_config.rate_limit_enabled == config.rate_limit_enabled
    
    def test_middleware_integration(self, temp_dir):
        """Test integration of multiple middleware components."""
        # Create FastAPI app
        app = FastAPI()
        
        # Create security configuration with multiple components
        security_config = SecurityConfig(
            auth_enabled=True,
            auth={
                "enabled": True,
                "api_keys": {"user1": "key1", "admin": "admin_key"},
                "public_paths": ["/docs", "/health"]
            },
            ssl={
                "enabled": False
            },
            roles={
                "enabled": True,
                "config_file": str(temp_dir / "roles_schema.json")
            },
            rate_limit={
                "enabled": True,
                "requests_per_minute": 100,
                "time_window": 60
            }
        )
        
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        SchemaLoader.save_roles_schema(roles_schema, temp_dir / "roles_schema.json")
        
        # Setup security middleware
        setup_security(app, security_config.to_dict())
        
        # Verify middleware was added
        assert len(app.user_middleware) > 0
        
        # Create test client
        client = TestClient(app)
        
        # Test that public paths are accessible
        response = client.get("/docs")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_error_handling_integration(self, temp_dir):
        """Test integration of error handling across components."""
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        SchemaLoader.save_roles_schema(roles_schema, temp_dir / "roles_schema.json")
        
        # Create permission validator
        validator = PermissionValidator(roles_schema)
        
        # Test various error scenarios
        test_cases = [
            # No roles
            {
                "user_roles": [],
                "required_permissions": ["read"],
                "server_role": "basic_commands",
                "expected_valid": False,
                "expected_error_code": -32007
            },
            # Unknown role
            {
                "user_roles": ["unknown_role"],
                "required_permissions": ["read"],
                "server_role": "basic_commands",
                "expected_valid": False,
                "expected_error_code": -32007
            },
            # Unknown permission
            {
                "user_roles": ["admin"],
                "required_permissions": ["unknown_permission"],
                "server_role": "kubernetes_manager",
                "expected_valid": False,
                "expected_error_code": -32007
            },
            # Server role restriction
            {
                "user_roles": ["user"],
                "required_permissions": ["read"],
                "server_role": "kubernetes_manager",
                "expected_valid": False,
                "expected_error_code": -32007
            }
        ]
        
        for case in test_cases:
            result = validator.validate_access(
                user_roles=case["user_roles"],
                required_permissions=case["required_permissions"],
                server_role=case["server_role"]
            )
            
            assert result.is_valid == case["expected_valid"]
            if not case["expected_valid"]:
                assert result.error_code == case["expected_error_code"]
    
    def test_performance_integration(self, temp_dir):
        """Test integration performance with multiple validations."""
        # Create roles schema
        roles_schema = SchemaLoader.create_default_roles_schema()
        SchemaLoader.save_roles_schema(roles_schema, temp_dir / "roles_schema.json")
        
        # Create permission validator
        validator = PermissionValidator(roles_schema)
        
        # Test multiple validations
        import time
        
        start_time = time.time()
        
        for i in range(100):
            result = validator.validate_access(
                user_roles=["admin"],
                required_permissions=["read", "write"],
                server_role="kubernetes_manager"
            )
            assert result.is_valid is True
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 validations in reasonable time (< 1 second)
        assert duration < 1.0
        
        # Test with different roles
        start_time = time.time()
        
        roles_to_test = ["admin", "user", "operator", "guest"]
        for role in roles_to_test:
            for i in range(25):
                result = validator.validate_access(
                    user_roles=[role],
                    required_permissions=["read"],
                    server_role="basic_commands"
                )
                # Some should be valid, some not
                assert isinstance(result.is_valid, bool)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete 100 validations in reasonable time (< 1 second)
        assert duration < 1.0


class TestConfigurationIntegration:
    """Integration tests for configuration management."""
    
    def test_configuration_validation_integration(self, temp_dir):
        """Test integration of configuration validation."""
        # Test valid configuration
        valid_config = SecurityConfig(
            auth_enabled=True,
            rate_limit_enabled=True,
            auth={
                "enabled": True,
                "api_keys": {"user1": "key1"}
            },
            rate_limit={
                "enabled": True,
                "requests_per_minute": 100
            }
        )
        
        # Should not raise any validation errors
        config_dict = valid_config.to_dict()
        restored_config = SecurityConfig.from_dict(config_dict)
        
        assert restored_config.auth_enabled == valid_config.auth_enabled
        assert restored_config.rate_limit_enabled == valid_config.rate_limit_enabled
    
    def test_configuration_file_integration(self, temp_dir):
        """Test integration of configuration file operations."""
        # Create configuration
        config = SecurityConfig(
            auth_enabled=True,
            rate_limit_enabled=True
        )
        
        # Save to file
        config_file = temp_dir / "config.json"
        SchemaLoader.save_security_config(config, config_file)
        
        # Load from file
        loaded_config = SchemaLoader.load_security_config(config_file)
        
        assert loaded_config is not None
        assert loaded_config.auth_enabled == config.auth_enabled
        assert loaded_config.rate_limit_enabled == config.rate_limit_enabled
        
        # Modify and save again
        loaded_config.auth_enabled = False
        SchemaLoader.save_security_config(loaded_config, config_file)
        
        # Load again and verify changes
        updated_config = SchemaLoader.load_security_config(config_file)
        assert updated_config.auth_enabled is False
    
    def test_legacy_configuration_integration(self, temp_dir):
        """Test integration with legacy configuration format."""
        # Create legacy configuration data
        legacy_config_data = {
            "auth_enabled": True,
            "rate_limit_enabled": True
        }
        
        # Convert to new format
        config = SecurityConfig.from_dict(legacy_config_data)
        
        assert config.auth_enabled is True
        assert config.rate_limit_enabled is True
        assert config.auth.enabled is True
        assert config.rate_limit.enabled is True
        
        # Convert back to dict
        config_dict = config.to_dict()
        
        assert config_dict["auth_enabled"] is True
        assert config_dict["rate_limit_enabled"] is True
        assert "auth" in config_dict
        assert "rate_limit" in config_dict


class TestSchemaIntegration:
    """Integration tests for schema management."""
    
    def test_schema_creation_integration(self, temp_dir):
        """Test integration of schema creation and validation."""
        # Create default schema
        schema = SchemaLoader.create_default_roles_schema()
        
        # Validate schema structure
        assert len(schema.roles) > 0
        assert len(schema.permissions) > 0
        assert len(schema.role_hierarchy.roles) > 0
        
        # Test schema methods
        assert schema.has_role("admin") is True
        assert schema.has_role("unknown_role") is False
        assert schema.has_permission("read") is True
        assert schema.has_permission("unknown_permission") is False
        
        # Test role retrieval
        admin_role = schema.get_role("admin")
        assert admin_role is not None
        assert admin_role.description == "Administrator"
        
        # Test permission retrieval
        read_perm = schema.get_permission("read")
        assert read_perm is not None
        assert read_perm.description == "Read access"
    
    def test_schema_persistence_integration(self, temp_dir):
        """Test integration of schema persistence."""
        # Create schema
        schema = SchemaLoader.create_default_roles_schema()
        
        # Save to file
        schema_file = temp_dir / "schema.json"
        SchemaLoader.save_roles_schema(schema, schema_file)
        
        # Load from file
        loaded_schema = SchemaLoader.load_roles_schema(schema_file)
        
        assert loaded_schema is not None
        
        # Compare schemas
        assert len(loaded_schema.roles) == len(schema.roles)
        assert len(loaded_schema.permissions) == len(schema.permissions)
        
        # Test that loaded schema works with validator
        validator = PermissionValidator(loaded_schema)
        
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is True
    
    def test_schema_modification_integration(self, temp_dir):
        """Test integration of schema modification."""
        # Create schema
        schema = SchemaLoader.create_default_roles_schema()
        
        # Modify schema
        from mcp_security.schemas.models import Role, Permission
        
        # Add new role
        schema.roles["custom_role"] = Role(
            description="Custom role",
            permissions=["read"],
            priority=50
        )
        
        # Add new permission
        schema.permissions["custom_permission"] = Permission(
            description="Custom permission",
            level=5
        )
        
        # Save modified schema
        schema_file = temp_dir / "modified_schema.json"
        SchemaLoader.save_roles_schema(schema, schema_file)
        
        # Load modified schema
        loaded_schema = SchemaLoader.load_roles_schema(schema_file)
        
        assert loaded_schema is not None
        assert "custom_role" in loaded_schema.roles
        assert "custom_permission" in loaded_schema.permissions
        
        # Test with validator
        validator = PermissionValidator(loaded_schema)
        
        result = validator.validate_access(
            user_roles=["custom_role"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is True
