"""
Tests for RoleUtils

Tests for role utilities.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock

from mcp_proxy_adapter.core.role_utils import RoleUtils


class TestRoleUtils:
    """Test RoleUtils class."""
    
    def setup_method(self):
        """Set up test method."""
        pass
    
    def test_role_extension_oid(self):
        """Test ROLE_EXTENSION_OID constant."""
        assert RoleUtils.ROLE_EXTENSION_OID == "1.3.6.1.4.1.99999.1"
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_with_roles(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.1"
        mock_extension.value.value = b"admin,user,moderator"
        mock_cert.extensions = [mock_extension]
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = RoleUtils.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == ["admin", "user", "moderator"]
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_no_roles(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with no roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_cert.extensions = []
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = RoleUtils.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_wrong_oid(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with wrong OID."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.2"  # Wrong OID
        mock_cert.extensions = [mock_extension]
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = RoleUtils.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_empty_roles(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with empty roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.1"
        mock_extension.value.value = b""
        mock_cert.extensions = [mock_extension]
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = RoleUtils.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_with_spaces(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with roles containing spaces."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.1"
        mock_extension.value.value = b" admin , user , moderator "
        mock_cert.extensions = [mock_extension]
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = RoleUtils.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == ["admin", "user", "moderator"]
    
    def test_extract_roles_from_certificate_object_with_roles(self):
        """Test extract_roles_from_certificate_object with roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.1"
        mock_extension.value.value = b"admin,user"
        mock_cert.extensions = [mock_extension]
        
        roles = RoleUtils.extract_roles_from_certificate_object(mock_cert)
        
        assert roles == ["admin", "user"]
    
    def test_extract_roles_from_certificate_object_no_roles(self):
        """Test extract_roles_from_certificate_object with no roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_cert.extensions = []
        
        roles = RoleUtils.extract_roles_from_certificate_object(mock_cert)
        
        assert roles == []
    
    def test_compare_roles_equal(self):
        """Test compare_roles with equal roles."""
        assert RoleUtils.compare_roles("admin", "admin") is True
        assert RoleUtils.compare_roles("Admin", "admin") is True
        assert RoleUtils.compare_roles("ADMIN", "admin") is True
        assert RoleUtils.compare_roles(" admin ", "admin") is True
    
    def test_compare_roles_not_equal(self):
        """Test compare_roles with different roles."""
        assert RoleUtils.compare_roles("admin", "user") is False
        assert RoleUtils.compare_roles("admin", "AdminUser") is False
    
    def test_compare_roles_empty(self):
        """Test compare_roles with empty roles."""
        assert RoleUtils.compare_roles("", "admin") is False
        assert RoleUtils.compare_roles("admin", "") is False
        assert RoleUtils.compare_roles("", "") is False
        assert RoleUtils.compare_roles(None, "admin") is False
        assert RoleUtils.compare_roles("admin", None) is False
    
    def test_compare_role_lists_equal(self):
        """Test compare_role_lists with equal lists."""
        roles1 = ["admin", "user"]
        roles2 = ["admin", "user"]
        
        assert RoleUtils.compare_role_lists(roles1, roles2) is True
    
    def test_compare_role_lists_case_insensitive(self):
        """Test compare_role_lists with case insensitive comparison."""
        roles1 = ["Admin", "User"]
        roles2 = ["admin", "user"]
        
        assert RoleUtils.compare_role_lists(roles1, roles2) is True
    
    def test_compare_role_lists_different_order(self):
        """Test compare_role_lists with different order."""
        roles1 = ["admin", "user"]
        roles2 = ["user", "admin"]
        
        assert RoleUtils.compare_role_lists(roles1, roles2) is True
    
    def test_compare_role_lists_not_equal(self):
        """Test compare_role_lists with different lists."""
        roles1 = ["admin", "user"]
        roles2 = ["admin", "moderator"]
        
        assert RoleUtils.compare_role_lists(roles1, roles2) is False
    
    def test_compare_role_lists_empty(self):
        """Test compare_role_lists with empty lists."""
        assert RoleUtils.compare_role_lists([], []) is True
        assert RoleUtils.compare_role_lists(["admin"], []) is False
        assert RoleUtils.compare_role_lists([], ["admin"]) is False
    
    def test_validate_roles_valid(self):
        """Test validate_roles with valid roles."""
        roles = ["admin", "user", "moderator"]
        
        assert RoleUtils.validate_roles(roles) is True
    
    def test_validate_roles_invalid_type(self):
        """Test validate_roles with invalid type."""
        assert RoleUtils.validate_roles("admin") is False
        assert RoleUtils.validate_roles(None) is False
    
    def test_validate_roles_invalid_role(self):
        """Test validate_roles with invalid role."""
        roles = ["admin", "", "user"]
        
        assert RoleUtils.validate_roles(roles) is False
    
    def test_validate_single_role_valid(self):
        """Test validate_single_role with valid role."""
        assert RoleUtils.validate_single_role("admin") is True
        assert RoleUtils.validate_single_role("user-role") is True
        assert RoleUtils.validate_single_role("user_role") is True
        assert RoleUtils.validate_single_role("user123") is True
    
    def test_validate_single_role_invalid_type(self):
        """Test validate_single_role with invalid type."""
        assert RoleUtils.validate_single_role(None) is False
        assert RoleUtils.validate_single_role(123) is False
        assert RoleUtils.validate_single_role([]) is False
    
    def test_validate_single_role_empty(self):
        """Test validate_single_role with empty role."""
        assert RoleUtils.validate_single_role("") is False
        assert RoleUtils.validate_single_role("   ") is False
    
    def test_validate_single_role_invalid_chars(self):
        """Test validate_single_role with invalid characters."""
        assert RoleUtils.validate_single_role("admin@user") is False
        assert RoleUtils.validate_single_role("admin.user") is False
        assert RoleUtils.validate_single_role("admin user") is False
    
    def test_validate_single_role_too_long(self):
        """Test validate_single_role with too long role."""
        long_role = "a" * 51
        assert RoleUtils.validate_single_role(long_role) is False
    
    def test_normalize_role(self):
        """Test normalize_role."""
        assert RoleUtils.normalize_role("Admin") == "admin"
        assert RoleUtils.normalize_role(" ADMIN ") == "admin"
        assert RoleUtils.normalize_role("Admin User") == "admin-user"
        assert RoleUtils.normalize_role("Admin  User") == "admin-user"
        assert RoleUtils.normalize_role("") == ""
        assert RoleUtils.normalize_role(None) == ""
    
    def test_normalize_roles(self):
        """Test normalize_roles."""
        roles = ["Admin", "User Role", "Moderator"]
        normalized = RoleUtils.normalize_roles(roles)
        
        assert normalized == ["admin", "user-role", "moderator"]
    
    def test_normalize_roles_duplicates(self):
        """Test normalize_roles with duplicates."""
        roles = ["Admin", "admin", "ADMIN"]
        normalized = RoleUtils.normalize_roles(roles)
        
        assert normalized == ["admin"]
    
    def test_normalize_roles_empty(self):
        """Test normalize_roles with empty list."""
        assert RoleUtils.normalize_roles([]) == []
        assert RoleUtils.normalize_roles(None) == []
    
    def test_has_role_true(self):
        """Test has_role with matching role."""
        user_roles = ["admin", "user"]
        
        assert RoleUtils.has_role(user_roles, "admin") is True
        assert RoleUtils.has_role(user_roles, "Admin") is True
        assert RoleUtils.has_role(user_roles, "user") is True
    
    def test_has_role_false(self):
        """Test has_role with non-matching role."""
        user_roles = ["admin", "user"]
        
        assert RoleUtils.has_role(user_roles, "moderator") is False
        assert RoleUtils.has_role(user_roles, "guest") is False
    
    def test_has_role_empty(self):
        """Test has_role with empty roles."""
        assert RoleUtils.has_role([], "admin") is False
        assert RoleUtils.has_role(None, "admin") is False
        assert RoleUtils.has_role(["admin"], "") is False
        assert RoleUtils.has_role(["admin"], None) is False
    
    def test_has_any_role_true(self):
        """Test has_any_role with matching role."""
        user_roles = ["admin", "user"]
        required_roles = ["moderator", "admin"]
        
        assert RoleUtils.has_any_role(user_roles, required_roles) is True
    
    def test_has_any_role_false(self):
        """Test has_any_role with no matching roles."""
        user_roles = ["admin", "user"]
        required_roles = ["moderator", "guest"]
        
        assert RoleUtils.has_any_role(user_roles, required_roles) is False
    
    def test_has_any_role_empty(self):
        """Test has_any_role with empty roles."""
        assert RoleUtils.has_any_role([], ["admin"]) is False
        assert RoleUtils.has_any_role(["admin"], []) is False
        assert RoleUtils.has_any_role(None, ["admin"]) is False
        assert RoleUtils.has_any_role(["admin"], None) is False
    
    def test_has_all_roles_true(self):
        """Test has_all_roles with all matching roles."""
        user_roles = ["admin", "user", "moderator"]
        required_roles = ["admin", "user"]
        
        assert RoleUtils.has_all_roles(user_roles, required_roles) is True
    
    def test_has_all_roles_false(self):
        """Test has_all_roles with missing roles."""
        user_roles = ["admin", "user"]
        required_roles = ["admin", "user", "moderator"]
        
        assert RoleUtils.has_all_roles(user_roles, required_roles) is False
    
    def test_has_all_roles_empty(self):
        """Test has_all_roles with empty roles."""
        assert RoleUtils.has_all_roles([], ["admin"]) is False
        assert RoleUtils.has_all_roles(["admin"], []) is False
        assert RoleUtils.has_all_roles(None, ["admin"]) is False
        assert RoleUtils.has_all_roles(["admin"], None) is False
    
    def test_get_common_roles(self):
        """Test get_common_roles."""
        roles1 = ["admin", "user", "moderator"]
        roles2 = ["user", "guest", "admin"]
        
        common = RoleUtils.get_common_roles(roles1, roles2)
        
        assert set(common) == {"admin", "user"}
    
    def test_get_common_roles_no_common(self):
        """Test get_common_roles with no common roles."""
        roles1 = ["admin", "user"]
        roles2 = ["moderator", "guest"]
        
        common = RoleUtils.get_common_roles(roles1, roles2)
        
        assert common == []
    
    def test_get_common_roles_empty(self):
        """Test get_common_roles with empty lists."""
        assert RoleUtils.get_common_roles([], ["admin"]) == []
        assert RoleUtils.get_common_roles(["admin"], []) == []
        assert RoleUtils.get_common_roles([], []) == []
    
    def test_merge_roles(self):
        """Test merge_roles."""
        roles1 = ["admin", "user"]
        roles2 = ["user", "moderator"]
        
        merged = RoleUtils.merge_roles(roles1, roles2)
        
        assert set(merged) == {"admin", "user", "moderator"}
    
    def test_merge_roles_empty(self):
        """Test merge_roles with empty lists."""
        assert RoleUtils.merge_roles([], ["admin"]) == ["admin"]
        assert RoleUtils.merge_roles(["admin"], []) == ["admin"]
        assert RoleUtils.merge_roles([], []) == []
    
    def test_remove_roles(self):
        """Test remove_roles."""
        roles = ["admin", "user", "moderator"]
        to_remove = ["user", "guest"]
        
        result = RoleUtils.remove_roles(roles, to_remove)
        
        assert result == ["admin", "moderator"]
    
    def test_remove_roles_empty(self):
        """Test remove_roles with empty lists."""
        assert RoleUtils.remove_roles([], ["admin"]) == []
        assert RoleUtils.remove_roles(["admin"], []) == ["admin"]
        assert RoleUtils.remove_roles([], []) == []
    
    def test_is_admin_role_true(self):
        """Test is_admin_role with admin roles."""
        assert RoleUtils.is_admin_role("admin") is True
        assert RoleUtils.is_admin_role("Admin") is True
        assert RoleUtils.is_admin_role("ADMIN") is True
        assert RoleUtils.is_admin_role("administrator") is True
        assert RoleUtils.is_admin_role("root") is True
        assert RoleUtils.is_admin_role("superuser") is True
        assert RoleUtils.is_admin_role("super-admin") is True
    
    def test_is_admin_role_false(self):
        """Test is_admin_role with non-admin roles."""
        assert RoleUtils.is_admin_role("user") is False
        assert RoleUtils.is_admin_role("moderator") is False
        assert RoleUtils.is_admin_role("guest") is False
        assert RoleUtils.is_admin_role("") is False
        assert RoleUtils.is_admin_role(None) is False
    
    def test_is_system_role_true(self):
        """Test is_system_role with system roles."""
        assert RoleUtils.is_system_role("system") is True
        assert RoleUtils.is_system_role("System") is True
        assert RoleUtils.is_system_role("service") is True
        assert RoleUtils.is_system_role("daemon") is True
        assert RoleUtils.is_system_role("internal") is True
        assert RoleUtils.is_system_role("system-user") is True
    
    def test_is_system_role_false(self):
        """Test is_system_role with non-system roles."""
        assert RoleUtils.is_system_role("user") is False
        assert RoleUtils.is_system_role("admin") is False
        assert RoleUtils.is_system_role("guest") is False
        assert RoleUtils.is_system_role("") is False
        assert RoleUtils.is_system_role(None) is False
    
    def test_get_role_hierarchy(self):
        """Test get_role_hierarchy."""
        hierarchy = RoleUtils.get_role_hierarchy("super-admin")
        assert hierarchy == ["admin", "user"]
        
        hierarchy = RoleUtils.get_role_hierarchy("admin")
        assert hierarchy == ["user"]
        
        hierarchy = RoleUtils.get_role_hierarchy("user")
        assert hierarchy == []
        
        hierarchy = RoleUtils.get_role_hierarchy("unknown")
        assert hierarchy == []
    
    def test_get_role_permissions(self):
        """Test get_role_permissions."""
        permissions = RoleUtils.get_role_permissions("super-admin")
        assert set(permissions) == {"read", "write", "delete", "admin", "system"}
        
        permissions = RoleUtils.get_role_permissions("admin")
        assert set(permissions) == {"read", "write", "delete", "admin"}
        
        permissions = RoleUtils.get_role_permissions("user")
        assert set(permissions) == {"read", "write"}
        
        permissions = RoleUtils.get_role_permissions("guest")
        assert set(permissions) == {"read"}
        
        permissions = RoleUtils.get_role_permissions("unknown")
        assert permissions == [] 