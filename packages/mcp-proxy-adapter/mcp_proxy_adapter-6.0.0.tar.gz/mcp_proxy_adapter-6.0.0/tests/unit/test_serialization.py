"""
Unit tests for serialization and deserialization.

Tests for SchemaLoader and SecuritySerializer.
"""

import pytest
import json
import tempfile
from pathlib import Path

from mcp_security.utils.schema_loader import SchemaLoader
from mcp_security.schemas.models import (
    RolesSchema, SecurityConfig, Permission, Role, RoleHierarchy, DefaultPolicy
)


class TestSchemaLoader:
    """Test cases for SchemaLoader."""
    
    def test_load_roles_schema_success(self, temp_dir, sample_roles_schema):
        """Test successful loading of roles schema."""
        # Save schema to file
        schema_file = temp_dir / "test_roles_schema.json"
        SchemaLoader.save_roles_schema(sample_roles_schema, schema_file)
        
        # Load schema from file
        loaded_schema = SchemaLoader.load_roles_schema(schema_file)
        
        assert loaded_schema is not None
        assert len(loaded_schema.roles) == len(sample_roles_schema.roles)
        assert len(loaded_schema.permissions) == len(sample_roles_schema.permissions)
        
        # Check specific roles
        assert "admin" in loaded_schema.roles
        assert "user" in loaded_schema.roles
        assert loaded_schema.roles["admin"].description == "Administrator"
        assert loaded_schema.roles["user"].description == "Regular user"
        
        # Check permissions
        assert "read" in loaded_schema.permissions
        assert "write" in loaded_schema.permissions
        assert loaded_schema.permissions["read"].description == "Read access"
    
    def test_load_roles_schema_file_not_found(self, temp_dir):
        """Test loading roles schema from non-existent file."""
        non_existent_file = temp_dir / "non_existent.json"
        
        loaded_schema = SchemaLoader.load_roles_schema(non_existent_file)
        
        assert loaded_schema is None
    
    def test_load_roles_schema_invalid_json(self, temp_dir):
        """Test loading roles schema from invalid JSON file."""
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("{ invalid json }")
        
        loaded_schema = SchemaLoader.load_roles_schema(invalid_file)
        
        assert loaded_schema is None
    
    def test_save_roles_schema_success(self, temp_dir, sample_roles_schema):
        """Test successful saving of roles schema."""
        schema_file = temp_dir / "test_save_roles_schema.json"
        
        success = SchemaLoader.save_roles_schema(sample_roles_schema, schema_file)
        
        assert success is True
        assert schema_file.exists()
        
        # Verify file content
        with open(schema_file, 'r') as f:
            data = json.load(f)
        
        assert "roles" in data
        assert "permissions" in data
        assert "role_hierarchy" in data
        assert "default_policy" in data
        assert "server_roles" in data
        
        # Check specific content
        assert "admin" in data["roles"]
        assert "read" in data["permissions"]
        assert data["roles"]["admin"]["description"] == "Administrator"
    
    def test_save_roles_schema_directory_creation(self, temp_dir, sample_roles_schema):
        """Test that save_roles_schema creates directories if needed."""
        schema_file = temp_dir / "nested" / "deep" / "roles_schema.json"
        
        success = SchemaLoader.save_roles_schema(sample_roles_schema, schema_file)
        
        assert success is True
        assert schema_file.exists()
        assert schema_file.parent.exists()
    
    def test_load_security_config_success(self, temp_dir, sample_security_config):
        """Test successful loading of security config."""
        # Save config to file
        config_file = temp_dir / "test_security_config.json"
        SchemaLoader.save_security_config(sample_security_config, config_file)
        
        # Load config from file
        loaded_config = SchemaLoader.load_security_config(config_file)
        
        assert loaded_config is not None
        assert loaded_config.auth_enabled == sample_security_config.auth_enabled
        assert loaded_config.rate_limit_enabled == sample_security_config.rate_limit_enabled
        assert loaded_config.auth.enabled == sample_security_config.auth.enabled
        assert loaded_config.rate_limit.enabled == sample_security_config.rate_limit.enabled
    
    def test_load_security_config_file_not_found(self, temp_dir):
        """Test loading security config from non-existent file."""
        non_existent_file = temp_dir / "non_existent_config.json"
        
        loaded_config = SchemaLoader.load_security_config(non_existent_file)
        
        assert loaded_config is None
    
    def test_save_security_config_success(self, temp_dir, sample_security_config):
        """Test successful saving of security config."""
        config_file = temp_dir / "test_save_security_config.json"
        
        success = SchemaLoader.save_security_config(sample_security_config, config_file)
        
        assert success is True
        assert config_file.exists()
        
        # Verify file content
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        assert "auth_enabled" in data
        assert "rate_limit_enabled" in data
        assert "auth" in data
        assert "ssl" in data
        assert "roles" in data
        assert "rate_limit" in data
    
    def test_create_default_roles_schema(self):
        """Test creation of default roles schema."""
        schema = SchemaLoader.create_default_roles_schema()
        
        assert schema is not None
        assert len(schema.roles) > 0
        assert len(schema.permissions) > 0
        
        # Check default roles
        assert "super-admin" in schema.roles
        assert "admin" in schema.roles
        assert "operator" in schema.roles
        assert "user" in schema.roles
        assert "guest" in schema.roles
        
        # Check default permissions
        assert "read" in schema.permissions
        assert "write" in schema.permissions
        assert "delete" in schema.permissions
        assert "admin" in schema.permissions
        assert "system" in schema.permissions
        
        # Check role hierarchy
        assert "super-admin" in schema.role_hierarchy.roles
        assert "admin" in schema.role_hierarchy.roles
        assert "operator" in schema.role_hierarchy.roles
        assert "user" in schema.role_hierarchy.roles
        
        # Check default policy
        assert schema.default_policy.deny_by_default is True
        assert schema.default_policy.require_role_match is True
        assert schema.default_policy.case_sensitive is False
        assert schema.default_policy.allow_wildcard is True


class TestSerializationDeserialization:
    """Test cases for serialization and deserialization logic."""
    
    def test_deserialize_roles_schema(self, sample_json_data):
        """Test deserialization of JSON data to RolesSchema."""
        schema = SchemaLoader._deserialize_roles_schema(sample_json_data)
        
        assert schema is not None
        assert "admin" in schema.roles
        assert "user" in schema.roles
        assert "read" in schema.permissions
        assert "write" in schema.permissions
        
        # Check role details
        admin_role = schema.roles["admin"]
        assert admin_role.description == "Administrator"
        assert admin_role.allowed_servers == ["*"]
        assert admin_role.allowed_clients == ["*"]
        assert "read" in admin_role.permissions
        assert "write" in admin_role.permissions
        assert "delete" in admin_role.permissions
        assert "admin" in admin_role.permissions
        assert admin_role.priority == 100
        
        # Check permission details
        read_perm = schema.permissions["read"]
        assert read_perm.description == "Read access"
        assert read_perm.level == 1
        
        # Check role hierarchy
        assert "admin" in schema.role_hierarchy.roles
        assert schema.role_hierarchy.roles["admin"] == ["user"]
        
        # Check default policy
        assert schema.default_policy.deny_by_default is True
        assert schema.default_policy.require_role_match is True
        assert schema.default_policy.case_sensitive is False
        assert schema.default_policy.allow_wildcard is True
    
    def test_serialize_roles_schema(self, sample_roles_schema):
        """Test serialization of RolesSchema to JSON data."""
        data = SchemaLoader._serialize_roles_schema(sample_roles_schema)
        
        assert "roles" in data
        assert "permissions" in data
        assert "role_hierarchy" in data
        assert "default_policy" in data
        assert "server_roles" in data
        
        # Check roles serialization
        assert "admin" in data["roles"]
        assert "user" in data["roles"]
        assert data["roles"]["admin"]["description"] == "Administrator"
        assert data["roles"]["admin"]["allowed_servers"] == ["*"]
        assert data["roles"]["admin"]["allowed_clients"] == ["*"]
        assert "read" in data["roles"]["admin"]["permissions"]
        assert "write" in data["roles"]["admin"]["permissions"]
        assert data["roles"]["admin"]["priority"] == 100
        
        # Check permissions serialization
        assert "read" in data["permissions"]
        assert "write" in data["permissions"]
        assert data["permissions"]["read"]["description"] == "Read access"
        assert data["permissions"]["read"]["level"] == 1
        
        # Check role hierarchy serialization
        assert "admin" in data["role_hierarchy"]
        assert data["role_hierarchy"]["admin"] == ["operator", "user"]
        
        # Check default policy serialization
        assert data["default_policy"]["deny_by_default"] is True
        assert data["default_policy"]["require_role_match"] is True
        assert data["default_policy"]["case_sensitive"] is False
        assert data["default_policy"]["allow_wildcard"] is True
    
    def test_round_trip_serialization(self, sample_roles_schema):
        """Test round-trip serialization and deserialization."""
        # Serialize
        data = SchemaLoader._serialize_roles_schema(sample_roles_schema)
        
        # Deserialize
        deserialized_schema = SchemaLoader._deserialize_roles_schema(data)
        
        # Compare
        assert len(deserialized_schema.roles) == len(sample_roles_schema.roles)
        assert len(deserialized_schema.permissions) == len(sample_roles_schema.permissions)
        
        # Check specific roles
        for role_name in sample_roles_schema.roles:
            original_role = sample_roles_schema.roles[role_name]
            deserialized_role = deserialized_schema.roles[role_name]
            
            assert original_role.description == deserialized_role.description
            assert original_role.allowed_servers == deserialized_role.allowed_servers
            assert original_role.allowed_clients == deserialized_role.allowed_clients
            assert original_role.permissions == deserialized_role.permissions
            assert original_role.priority == deserialized_role.priority
        
        # Check permissions
        for perm_name in sample_roles_schema.permissions:
            original_perm = sample_roles_schema.permissions[perm_name]
            deserialized_perm = deserialized_schema.permissions[perm_name]
            
            assert original_perm.description == deserialized_perm.description
            assert original_perm.level == deserialized_perm.level
    
    def test_deserialize_with_missing_fields(self):
        """Test deserialization with missing optional fields."""
        minimal_data = {
            "roles": {
                "admin": {
                    "description": "Administrator",
                    "allowed_servers": ["*"],
                    "allowed_clients": ["*"],
                    "permissions": ["read", "write"],
                    "priority": 100
                }
            },
            "permissions": {
                "read": {
                    "description": "Read access",
                    "level": 1
                }
            }
        }
        
        schema = SchemaLoader._deserialize_roles_schema(minimal_data)
        
        assert schema is not None
        assert "admin" in schema.roles
        assert "read" in schema.permissions
        
        # Check that missing fields have defaults
        assert schema.role_hierarchy.roles == {}
        assert schema.default_policy.deny_by_default is True
        assert schema.server_roles == {}
    
    def test_serialize_with_empty_fields(self):
        """Test serialization with empty fields."""
        schema = RolesSchema(
            roles={
                "admin": Role(
                    description="Administrator",
                    permissions=["read"],
                    priority=100
                )
            },
            permissions={
                "read": Permission(description="Read access", level=1)
            },
            role_hierarchy=RoleHierarchy(roles={}),
            default_policy=DefaultPolicy(),
            server_roles={}
        )
        
        data = SchemaLoader._serialize_roles_schema(schema)
        
        assert "roles" in data
        assert "permissions" in data
        assert "role_hierarchy" in data
        assert "default_policy" in data
        assert "server_roles" in data
        
        # Check that empty fields are preserved
        assert data["role_hierarchy"] == {}
        assert data["server_roles"] == {}


class TestSecurityConfigSerialization:
    """Test cases for SecurityConfig serialization."""
    
    def test_security_config_to_dict(self, sample_security_config):
        """Test SecurityConfig.to_dict method."""
        config_dict = sample_security_config.to_dict()
        
        assert "auth_enabled" in config_dict
        assert "rate_limit_enabled" in config_dict
        assert "auth" in config_dict
        assert "ssl" in config_dict
        assert "roles" in config_dict
        assert "rate_limit" in config_dict
        
        assert config_dict["auth_enabled"] == sample_security_config.auth_enabled
        assert config_dict["rate_limit_enabled"] == sample_security_config.rate_limit_enabled
    
    def test_security_config_from_dict(self):
        """Test SecurityConfig.from_dict method."""
        config_data = {
            "auth_enabled": True,
            "rate_limit_enabled": True,
            "auth": {
                "enabled": True,
                "api_keys": {"user1": "key1"},
                "public_paths": ["/docs"]
            },
            "ssl": {
                "enabled": True,
                "mode": "https_only"
            },
            "roles": {
                "enabled": True,
                "config_file": "roles.json"
            },
            "rate_limit": {
                "enabled": True,
                "requests_per_minute": 100
            }
        }
        
        config = SecurityConfig.from_dict(config_data)
        
        assert config.auth_enabled is True
        assert config.rate_limit_enabled is True
        assert config.auth.enabled is True
        assert config.auth.api_keys["user1"] == "key1"
        assert config.ssl.enabled is True
        assert config.roles.enabled is True
        assert config.rate_limit.enabled is True
    
    def test_security_config_from_dict_legacy(self):
        """Test SecurityConfig.from_dict with legacy format."""
        config_data = {
            "auth_enabled": True,
            "rate_limit_enabled": True
        }
        
        config = SecurityConfig.from_dict(config_data)
        
        assert config.auth_enabled is True
        assert config.rate_limit_enabled is True
        assert config.auth.enabled is True
        assert config.rate_limit.enabled is True
    
    def test_security_config_round_trip(self, sample_security_config):
        """Test round-trip serialization of SecurityConfig."""
        # Convert to dict
        config_dict = sample_security_config.to_dict()
        
        # Convert back from dict
        restored_config = SecurityConfig.from_dict(config_dict)
        
        # Compare
        assert restored_config.auth_enabled == sample_security_config.auth_enabled
        assert restored_config.rate_limit_enabled == sample_security_config.rate_limit_enabled
        assert restored_config.auth.enabled == sample_security_config.auth.enabled
        assert restored_config.rate_limit.enabled == sample_security_config.rate_limit.enabled
