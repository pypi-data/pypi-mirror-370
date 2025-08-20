"""
Unit tests for SecurityConfigManager.

Tests for configuration management functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from mcp_security.config import SecurityConfigManager, get_config_manager, get_config
from mcp_security.schemas.models import SecurityConfig, RolesSchema


class TestSecurityConfigManager:
    """Test cases for SecurityConfigManager."""
    
    def test_init_with_path(self, temp_dir):
        """Test SecurityConfigManager initialization with explicit path."""
        config_file = temp_dir / "security_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        manager = SecurityConfigManager(str(config_file))
        
        assert manager.config_path == str(config_file)
        assert manager.config is not None
        assert manager.config.auth.enabled is True
    
    def test_init_without_path(self, temp_dir):
        """Test SecurityConfigManager initialization without path."""
        # Set environment variable
        os.environ['MCP_SECURITY_CONFIG'] = str(temp_dir / "env_config.json")
        
        config_file = temp_dir / "env_config.json"
        config_file.write_text('{"auth": {"enabled": false}}')
        
        manager = SecurityConfigManager()
        
        assert manager.config_path == str(config_file)
        assert manager.config.auth.enabled is False
        
        # Clean up
        del os.environ['MCP_SECURITY_CONFIG']
    
    def test_resolve_config_path_explicit(self, temp_dir):
        """Test resolving explicit config path."""
        config_file = temp_dir / "explicit_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        manager = SecurityConfigManager(str(config_file))
        resolved_path = manager._resolve_config_path(str(config_file))
        
        assert resolved_path == str(config_file)
    
    def test_resolve_config_path_env_var(self, temp_dir):
        """Test resolving config path from environment variable."""
        config_file = temp_dir / "env_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        os.environ['MCP_SECURITY_CONFIG'] = str(config_file)
        
        manager = SecurityConfigManager()
        resolved_path = manager._resolve_config_path(None)
        
        assert resolved_path == str(config_file)
        
        # Clean up
        del os.environ['MCP_SECURITY_CONFIG']
    
    def test_resolve_config_path_common_locations(self, temp_dir):
        """Test resolving config path from common locations."""
        # Create config in common location
        common_config = temp_dir / "config" / "security.json"
        common_config.parent.mkdir(exist_ok=True)
        common_config.write_text('{"auth": {"enabled": true}}')
        
        with patch('mcp_security.config.Path.home') as mock_home:
            mock_home.return_value = temp_dir
            
            manager = SecurityConfigManager()
            resolved_path = manager._resolve_config_path(None)
            
            assert resolved_path == str(common_config)
    
    def test_resolve_config_path_not_found(self, temp_dir):
        """Test resolving config path when not found."""
        manager = SecurityConfigManager()
        
        with pytest.raises(FileNotFoundError):
            manager._resolve_config_path("nonexistent.json")
    
    def test_load_config_success(self, temp_dir):
        """Test successful config loading."""
        config_data = {
            "auth": {"enabled": True},
            "ssl": {"enabled": False},
            "roles": {"enabled": True}
        }
        
        config_file = temp_dir / "test_config.json"
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
        
        manager = SecurityConfigManager(str(config_file))
        
        assert manager.config is not None
        assert manager.config.auth.enabled is True
        assert manager.config.ssl.enabled is False
        assert manager.config.roles.enabled is True
    
    def test_load_config_invalid_json(self, temp_dir):
        """Test loading config with invalid JSON."""
        config_file = temp_dir / "invalid_config.json"
        config_file.write_text("{ invalid json }")
        
        with pytest.raises(Exception):
            SecurityConfigManager(str(config_file))
    
    def test_load_config_file_not_found(self, temp_dir):
        """Test loading config when file not found."""
        config_file = temp_dir / "nonexistent.json"
        
        with pytest.raises(FileNotFoundError):
            SecurityConfigManager(str(config_file))
    
    def test_reload_config(self, temp_dir):
        """Test reloading configuration."""
        # Create initial config
        config_file = temp_dir / "reload_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        manager = SecurityConfigManager(str(config_file))
        assert manager.config.auth.enabled is True
        
        # Update config file
        config_file.write_text('{"auth": {"enabled": false}}')
        
        # Reload
        success = manager.reload_config()
        assert success is True
        assert manager.config.auth.enabled is False
    
    def test_reload_config_file_deleted(self, temp_dir):
        """Test reloading when config file is deleted."""
        config_file = temp_dir / "delete_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        manager = SecurityConfigManager(str(config_file))
        
        # Delete file
        config_file.unlink()
        
        # Reload should fail
        success = manager.reload_config()
        assert success is False
    
    def test_validate_config_valid(self, temp_dir):
        """Test validating valid configuration."""
        config_data = {
            "auth": {"enabled": True},
            "ssl": {"enabled": False},
            "roles": {"enabled": True}
        }
        
        config_file = temp_dir / "valid_config.json"
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
        
        manager = SecurityConfigManager(str(config_file))
        
        is_valid = manager.validate_config()
        assert is_valid is True
    
    def test_validate_config_invalid(self, temp_dir):
        """Test validating invalid configuration."""
        config_data = {
            "auth": {"enabled": "invalid"},  # Should be boolean
            "ssl": {"enabled": False}
        }
        
        config_file = temp_dir / "invalid_config.json"
        with open(config_file, 'w') as f:
            import json
            json.dump(config_data, f)
        
        manager = SecurityConfigManager(str(config_file))
        
        is_valid = manager.validate_config()
        assert is_valid is False
    
    def test_create_default_config(self, temp_dir):
        """Test creating default configuration."""
        config_file = temp_dir / "default_config.json"
        
        manager = SecurityConfigManager(str(config_file))
        success = manager.create_default_config()
        
        assert success is True
        assert config_file.exists()
        
        # Verify default values
        assert manager.config.auth.enabled is False
        assert manager.config.ssl.enabled is False
        assert manager.config.roles.enabled is False
        assert manager.config.rate_limit.enabled is False
    
    def test_create_default_roles_schema(self, temp_dir):
        """Test creating default roles schema."""
        schema_file = temp_dir / "default_roles.json"
        
        manager = SecurityConfigManager()
        success = manager.create_default_roles_schema(str(schema_file))
        
        assert success is True
        assert schema_file.exists()
        
        # Verify schema structure
        schema = manager._load_roles_schema(str(schema_file))
        assert schema is not None
        assert "admin" in schema.roles
        assert "user" in schema.roles
        assert "guest" in schema.roles
    
    def test_load_roles_schema_success(self, temp_dir):
        """Test loading roles schema successfully."""
        schema_data = {
            "roles": {
                "admin": {
                    "name": "Administrator",
                    "description": "Full system access",
                    "permissions": ["read", "write", "delete"],
                    "priority": 100
                }
            },
            "permissions": {
                "read": {"name": "Read", "description": "Read access"},
                "write": {"name": "Write", "description": "Write access"}
            },
            "role_hierarchy": {"roles": {}},
            "default_policy": {
                "deny_by_default": True,
                "require_role_match": True,
                "case_sensitive": False,
                "allow_wildcard": True
            },
            "server_roles": {}
        }
        
        schema_file = temp_dir / "test_roles.json"
        with open(schema_file, 'w') as f:
            import json
            json.dump(schema_data, f)
        
        manager = SecurityConfigManager()
        schema = manager._load_roles_schema(str(schema_file))
        
        assert schema is not None
        assert "admin" in schema.roles
        assert schema.roles["admin"].permissions == ["read", "write", "delete"]
    
    def test_load_roles_schema_file_not_found(self, temp_dir):
        """Test loading roles schema when file not found."""
        manager = SecurityConfigManager()
        
        schema = manager._load_roles_schema("nonexistent.json")
        assert schema is None
    
    def test_load_roles_schema_invalid_json(self, temp_dir):
        """Test loading roles schema with invalid JSON."""
        schema_file = temp_dir / "invalid_roles.json"
        schema_file.write_text("{ invalid json }")
        
        manager = SecurityConfigManager()
        schema = manager._load_roles_schema(str(schema_file))
        
        assert schema is None


class TestGlobalFunctions:
    """Test cases for global configuration functions."""
    
    def test_get_config_manager(self, temp_dir):
        """Test get_config_manager function."""
        config_file = temp_dir / "global_config.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        manager = get_config_manager(str(config_file))
        
        assert isinstance(manager, SecurityConfigManager)
        assert manager.config.auth.enabled is True
    
    def test_get_config(self, temp_dir):
        """Test get_config function."""
        config_file = temp_dir / "get_config.json"
        config_file.write_text('{"auth": {"enabled": false}}')
        
        config = get_config(str(config_file))
        
        assert isinstance(config, SecurityConfig)
        assert config.auth.enabled is False
    
    def test_reload_config_function(self, temp_dir):
        """Test reload_config function."""
        config_file = temp_dir / "reload_func.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        # Initial load
        manager = get_config_manager(str(config_file))
        assert manager.config.auth.enabled is True
        
        # Update file
        config_file.write_text('{"auth": {"enabled": false}}')
        
        # Reload
        from mcp_security.config import reload_config
        success = reload_config(str(config_file))
        assert success is True
        
        # Verify reload
        config = get_config(str(config_file))
        assert config.auth.enabled is False
    
    def test_validate_config_function(self, temp_dir):
        """Test validate_config function."""
        config_file = temp_dir / "validate_func.json"
        config_file.write_text('{"auth": {"enabled": true}}')
        
        from mcp_security.config import validate_config
        is_valid = validate_config(str(config_file))
        assert is_valid is True
