"""
Unit tests for permission validation.

Tests for PermissionValidator and related validation logic.
"""

import pytest
from typing import List, Set

from mcp_security.utils.permission_validator import PermissionValidator
from mcp_security.schemas.models import RolesSchema, ValidationResult


class TestPermissionValidator:
    """Test cases for PermissionValidator."""
    
    def test_validate_access_admin_full_access(self, sample_roles_schema):
        """Test that admin has full access."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read", "write", "delete"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "write" in result.effective_permissions
        assert "delete" in result.effective_permissions
        assert "admin" in result.matched_roles
    
    def test_validate_access_user_limited_access(self, sample_roles_schema):
        """Test that user has limited access."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "user" in result.matched_roles
    
    def test_validate_access_user_no_admin_access(self, sample_roles_schema):
        """Test that user cannot access admin permissions."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["admin"],
            server_role="admin_panel"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007  # Role validation failed
        assert "admin" not in result.effective_permissions
    
    def test_validate_access_guest_limited_access(self, sample_roles_schema):
        """Test that guest has very limited access."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["guest"],
            required_permissions=["read"],
            server_role="help"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "guest" in result.matched_roles
    
    def test_validate_access_guest_no_write_access(self, sample_roles_schema):
        """Test that guest cannot write."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["guest"],
            required_permissions=["write"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is False
        assert "write" not in result.effective_permissions
    
    def test_validate_access_super_admin_inheritance(self, sample_roles_schema):
        """Test that super-admin inherits permissions from admin."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["super-admin"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "super-admin" in result.matched_roles
    
    def test_validate_access_multiple_roles(self, sample_roles_schema):
        """Test validation with multiple user roles."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["admin", "operator"],
            required_permissions=["read", "write"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is True
        assert "read" in result.effective_permissions
        assert "write" in result.effective_permissions
        assert "admin" in result.matched_roles
        assert "operator" in result.matched_roles
    
    def test_validate_access_no_roles(self, sample_roles_schema):
        """Test validation with no user roles."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=[],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007  # Role validation failed
        assert len(result.effective_permissions) == 0
    
    def test_validate_access_unknown_role(self, sample_roles_schema):
        """Test validation with unknown user role."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["unknown_role"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007  # Role validation failed
    
    def test_validate_access_unknown_permission(self, sample_roles_schema):
        """Test validation with unknown required permission."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["unknown_permission"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007  # Role validation failed
    
    def test_validate_access_server_role_restriction(self, sample_roles_schema):
        """Test that server role restrictions are enforced."""
        validator = PermissionValidator(sample_roles_schema)
        
        # User should not have access to kubernetes_manager
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["read"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007  # Role validation failed
    
    def test_check_role_hierarchy(self, sample_roles_schema):
        """Test role hierarchy checking."""
        validator = PermissionValidator(sample_roles_schema)
        
        # Admin should be able to access user permissions
        assert validator.check_role_hierarchy("admin", "user") is True
        
        # User should not be able to access admin permissions
        assert validator.check_role_hierarchy("user", "admin") is False
        
        # Super-admin should be able to access admin permissions
        assert validator.check_role_hierarchy("super-admin", "admin") is True
        
        # Admin should be able to access operator permissions
        assert validator.check_role_hierarchy("admin", "operator") is True
    
    def test_get_effective_permissions(self, sample_roles_schema):
        """Test getting effective permissions for roles."""
        validator = PermissionValidator(sample_roles_schema)
        
        # Admin permissions
        admin_perms = validator.get_effective_permissions(["admin"])
        assert "read" in admin_perms
        assert "write" in admin_perms
        assert "delete" in admin_perms
        assert "admin" in admin_perms
        
        # User permissions
        user_perms = validator.get_effective_permissions(["user"])
        assert "read" in user_perms
        assert "write" not in user_perms
        assert "delete" not in user_perms
        assert "admin" not in user_perms
        
        # Guest permissions
        guest_perms = validator.get_effective_permissions(["guest"])
        assert "read" in guest_perms
        assert "write" not in guest_perms
        assert "delete" not in guest_perms
        assert "admin" not in guest_perms
        
        # Super-admin permissions (should include all)
        super_admin_perms = validator.get_effective_permissions(["super-admin"])
        assert "read" in super_admin_perms
        assert "write" in super_admin_perms
        assert "delete" in super_admin_perms
        assert "admin" in super_admin_perms
        assert "system" in super_admin_perms
    
    def test_get_effective_permissions_multiple_roles(self, sample_roles_schema):
        """Test getting effective permissions for multiple roles."""
        validator = PermissionValidator(sample_roles_schema)
        
        # Admin + User permissions
        combined_perms = validator.get_effective_permissions(["admin", "user"])
        assert "read" in combined_perms
        assert "write" in combined_perms
        assert "delete" in combined_perms
        assert "admin" in combined_perms
        
        # Operator + User permissions
        operator_user_perms = validator.get_effective_permissions(["operator", "user"])
        assert "read" in operator_user_perms
        assert "write" in operator_user_perms
        assert "delete" not in operator_user_perms
        assert "admin" not in operator_user_perms
    
    def test_get_effective_permissions_empty_roles(self, sample_roles_schema):
        """Test getting effective permissions for empty roles list."""
        validator = PermissionValidator(sample_roles_schema)
        
        perms = validator.get_effective_permissions([])
        assert len(perms) == 0
    
    def test_get_effective_permissions_unknown_role(self, sample_roles_schema):
        """Test getting effective permissions for unknown role."""
        validator = PermissionValidator(sample_roles_schema)
        
        perms = validator.get_effective_permissions(["unknown_role"])
        assert len(perms) == 0
    
    def test_validate_access_case_insensitive(self, sample_roles_schema):
        """Test that role validation is case insensitive by default."""
        validator = PermissionValidator(sample_roles_schema)
        
        # Test with different case
        result = validator.validate_access(
            user_roles=["ADMIN"],  # Uppercase
            required_permissions=["READ"],  # Uppercase
            server_role="KUBERNETES_MANAGER"  # Uppercase
        )
        
        # Should work if case insensitive
        if sample_roles_schema.default_policy.case_sensitive:
            assert result.is_valid is False
        else:
            assert result.is_valid is True
    
    def test_validate_access_wildcard_matching(self, sample_roles_schema):
        """Test wildcard matching in server roles."""
        validator = PermissionValidator(sample_roles_schema)
        
        # Admin should have access to any server (allowed_servers: ["*"])
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read"],
            server_role="any_server_name"
        )
        
        assert result.is_valid is True
    
    def test_validate_access_specific_server_restriction(self, sample_roles_schema):
        """Test specific server restrictions."""
        validator = PermissionValidator(sample_roles_schema)
        
        # User should only have access to basic_commands
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["read"],
            server_role="basic_commands"
        )
        
        assert result.is_valid is True
        
        # User should not have access to kubernetes_manager
        result = validator.validate_access(
            user_roles=["user"],
            required_permissions=["read"],
            server_role="kubernetes_manager"
        )
        
        assert result.is_valid is False
    
    def test_validate_access_no_server_role(self, sample_roles_schema):
        """Test validation without server role."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=["read"],
            server_role=None
        )
        
        # Should still validate permissions even without server role
        assert result.is_valid is True
        assert "read" in result.effective_permissions
    
    def test_validate_access_empty_permissions(self, sample_roles_schema):
        """Test validation with empty required permissions."""
        validator = PermissionValidator(sample_roles_schema)
        
        result = validator.validate_access(
            user_roles=["admin"],
            required_permissions=[],
            server_role="kubernetes_manager"
        )
        
        # Should be valid if no permissions required
        assert result.is_valid is True
        assert len(result.effective_permissions) > 0  # Admin has permissions


class TestValidationResult:
    """Test cases for ValidationResult."""
    
    def test_validation_result_success(self):
        """Test successful validation result."""
        result = ValidationResult(
            is_valid=True,
            effective_permissions=["read", "write"],
            matched_roles=["admin"]
        )
        
        assert result.is_valid is True
        assert result.error_code is None
        assert result.error_message is None
        assert result.effective_permissions == ["read", "write"]
        assert result.matched_roles == ["admin"]
    
    def test_validation_result_failure(self):
        """Test failed validation result."""
        result = ValidationResult(
            is_valid=False,
            error_code=-32007,
            error_message="Role validation failed",
            effective_permissions=["read"],
            matched_roles=["user"]
        )
        
        assert result.is_valid is False
        assert result.error_code == -32007
        assert result.error_message == "Role validation failed"
        assert result.effective_permissions == ["read"]
        assert result.matched_roles == ["user"]
    
    def test_validation_result_defaults(self):
        """Test validation result with default values."""
        result = ValidationResult(is_valid=True)
        
        assert result.is_valid is True
        assert result.error_code is None
        assert result.error_message is None
        assert result.details == {}
        assert result.effective_permissions == []
        assert result.matched_roles == []
