"""
Tests for Roles Management Command.

Tests role management functionality including listing, creating, updating,
deleting, and validating roles.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from mcp_proxy_adapter.commands.roles_management_command import (
    RolesManagementCommand,
    RolesListResult,
    RolesCreateResult,
    RolesUpdateResult,
    RolesDeleteResult,
    RolesValidateResult
)
from mcp_proxy_adapter.commands.result import ErrorResult
from mcp_proxy_adapter.core.errors import ValidationError, NotFoundError, InternalError


class TestRolesManagementCommand:
    """Test cases for RolesManagementCommand."""
    
    @pytest.fixture
    def mock_roles_config(self):
        """Mock roles configuration."""
        return {
            "roles": {
                "admin": {
                    "description": "Administrator with full access",
                    "allowed_servers": ["*"],
                    "allowed_clients": ["*"],
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                },
                "operator": {
                    "description": "Operator with limited access",
                    "allowed_servers": ["kubernetes_manager", "docker_manager"],
                    "allowed_clients": ["admin", "operator"],
                    "permissions": ["read", "write"],
                    "priority": 50
                },
                "user": {
                    "description": "Regular user",
                    "allowed_servers": ["basic_commands"],
                    "allowed_clients": ["admin", "operator", "user"],
                    "permissions": ["read"],
                    "priority": 10
                }
            },
            "server_roles": {
                "kubernetes_manager": {
                    "description": "Kubernetes management server",
                    "required_roles": ["admin", "operator"],
                    "allowed_commands": ["k8s_*"]
                }
            },
            "role_hierarchy": {
                "admin": ["operator", "user"],
                "operator": ["user"]
            }
        }
    
    @pytest.fixture
    def roles_command(self, mock_roles_config, tmp_path):
        """Create RolesManagementCommand instance with mock configuration."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        with patch('mcp_proxy_adapter.commands.roles_management_command.RolesManagementCommand._load_roles_config') as mock_load:
            mock_load.return_value = mock_roles_config
            command = RolesManagementCommand(str(config_file))
            return command
    
    def test_init(self, mock_roles_config, tmp_path):
        """Test command initialization."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        with patch('mcp_proxy_adapter.commands.roles_management_command.RolesManagementCommand._load_roles_config') as mock_load:
            mock_load.return_value = mock_roles_config
            command = RolesManagementCommand(str(config_file))
            
            assert command.roles_config == mock_roles_config
            assert command.roles_config_path == str(config_file)
    
    def test_load_roles_config_file_exists(self, mock_roles_config, tmp_path):
        """Test loading roles configuration from existing file."""
        config_file = tmp_path / "roles_schema.json"
        with open(config_file, 'w') as f:
            json.dump(mock_roles_config, f)
        
        command = RolesManagementCommand(str(config_file))
        assert command.roles_config == mock_roles_config
    
    def test_load_roles_config_file_not_exists(self, tmp_path):
        """Test loading roles configuration when file doesn't exist."""
        config_file = tmp_path / "nonexistent.json"
        command = RolesManagementCommand(str(config_file))
        
        assert "roles" in command.roles_config
        assert "server_roles" in command.roles_config
        assert "role_hierarchy" in command.roles_config
    
    def test_save_roles_config(self, roles_command, tmp_path):
        """Test saving roles configuration to file."""
        config_file = tmp_path / "test_roles.json"
        roles_command.roles_config_path = str(config_file)
        
        roles_command._save_roles_config()
        
        assert config_file.exists()
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        assert saved_config == roles_command.roles_config
    
    def test_save_roles_config_error(self, roles_command):
        """Test saving roles configuration with error."""
        roles_command.roles_config_path = "/invalid/path/test.json"
        
        with pytest.raises(InternalError):
            roles_command._save_roles_config()
    
    @pytest.mark.asyncio
    async def test_execute_list_action(self, roles_command):
        """Test execute method with list action."""
        params = {"action": "list"}
        result = await roles_command.execute(**params)
        
        assert isinstance(result, RolesListResult)
        assert result.to_dict()["success"] is True
        assert len(result.roles) == 3
        assert result.total_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_create_action(self, roles_command):
        """Test execute method with create action."""
        params = {
            "action": "create",
            "role_name": "test_role",
            "description": "Test role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.execute(**params)
            
            assert isinstance(result, RolesCreateResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "test_role"
            assert "test_role" in roles_command.roles_config["roles"]
    
    @pytest.mark.asyncio
    async def test_execute_update_action(self, roles_command):
        """Test execute method with update action."""
        params = {
            "action": "update",
            "role_name": "admin",
            "description": "Updated admin role",
            "priority": 150
        }
        
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.execute(**params)
            
            assert isinstance(result, RolesUpdateResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "admin"
            assert roles_command.roles_config["roles"]["admin"]["description"] == "Updated admin role"
    
    @pytest.mark.asyncio
    async def test_execute_delete_action(self, roles_command):
        """Test execute method with delete action."""
        params = {"action": "delete", "role_name": "user"}
        
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.execute(**params)
            
            assert isinstance(result, RolesDeleteResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "user"
            assert "user" not in roles_command.roles_config["roles"]
    
    @pytest.mark.asyncio
    async def test_execute_validate_action(self, roles_command):
        """Test execute method with validate action."""
        params = {"action": "validate", "role_name": "admin"}
        result = await roles_command.execute(**params)
        
        assert isinstance(result, RolesValidateResult)
        assert result.to_dict()["success"] is True
        assert result.role_name == "admin"
        assert result.is_valid is True
    
    @pytest.mark.asyncio
    async def test_execute_invalid_action(self, roles_command):
        """Test execute method with invalid action."""
        params = {"action": "invalid_action"}
        
        result = await roles_command.execute(**params)
        assert isinstance(result, ErrorResult)
        assert "Invalid action" in result.message
    
    @pytest.mark.asyncio
    async def test_roles_list_basic(self, roles_command):
        """Test basic roles list functionality."""
        result = await roles_command.roles_list()
        
        assert isinstance(result, RolesListResult)
        assert result.to_dict()["success"] is True
        assert len(result.roles) == 3
        assert result.total_count == 3
        
        # Check role structure
        admin_role = next(role for role in result.roles if role["name"] == "admin")
        assert admin_role["description"] == "Administrator with full access"
        assert admin_role["permissions"] == ["read", "write", "delete", "admin"]
        assert admin_role["priority"] == 100
    
    @pytest.mark.asyncio
    async def test_roles_list_with_filter(self, roles_command):
        """Test roles list with filter."""
        result = await roles_command.roles_list(filter="admin")
        
        assert isinstance(result, RolesListResult)
        assert len(result.roles) == 1
        assert result.roles[0]["name"] == "admin"
    
    @pytest.mark.asyncio
    async def test_roles_list_with_pagination(self, roles_command):
        """Test roles list with pagination."""
        result = await roles_command.roles_list(limit=2, offset=1)
        
        assert isinstance(result, RolesListResult)
        assert len(result.roles) == 2
        assert result.total_count == 3
    
    @pytest.mark.asyncio
    async def test_roles_create_success(self, roles_command):
        """Test successful role creation."""
        role_config = {
            "description": "Test role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.roles_create(role_name="test_role", **role_config)
            
            assert isinstance(result, RolesCreateResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "test_role"
            assert result.role_config == role_config
            assert "test_role" in roles_command.roles_config["roles"]
    
    @pytest.mark.asyncio
    async def test_roles_create_missing_name(self, roles_command):
        """Test role creation with missing name."""
        with pytest.raises(ValidationError, match="role_name is required"):
            await roles_command.roles_create(description="Test role")
    
    @pytest.mark.asyncio
    async def test_roles_create_invalid_name(self, roles_command):
        """Test role creation with invalid name."""
        with patch('mcp_proxy_adapter.core.role_utils.RoleUtils.validate_single_role') as mock_validate:
            mock_validate.return_value = False
            
            with pytest.raises(ValidationError, match="Invalid role name"):
                await roles_command.roles_create(role_name="invalid@role")
    
    @pytest.mark.asyncio
    async def test_roles_create_duplicate_name(self, roles_command):
        """Test role creation with duplicate name."""
        with pytest.raises(ValidationError, match="already exists"):
            await roles_command.roles_create(role_name="admin", description="Duplicate admin")
    
    @pytest.mark.asyncio
    async def test_roles_create_invalid_config(self, roles_command):
        """Test role creation with invalid configuration."""
        with pytest.raises(ValidationError, match="Invalid role configuration"):
            await roles_command.roles_create(
                role_name="test_role",
                allowed_servers="not_a_list",  # Should be list
                permissions=123  # Should be list
            )
    
    @pytest.mark.asyncio
    async def test_roles_update_success(self, roles_command):
        """Test successful role update."""
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.roles_update(
                role_name="admin",
                description="Updated admin role",
                priority=150
            )
            
            assert isinstance(result, RolesUpdateResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "admin"
            assert roles_command.roles_config["roles"]["admin"]["description"] == "Updated admin role"
            assert roles_command.roles_config["roles"]["admin"]["priority"] == 150
    
    @pytest.mark.asyncio
    async def test_roles_update_missing_name(self, roles_command):
        """Test role update with missing name."""
        with pytest.raises(ValidationError, match="role_name is required"):
            await roles_command.roles_update(description="Updated role")
    
    @pytest.mark.asyncio
    async def test_roles_update_nonexistent_role(self, roles_command):
        """Test role update with nonexistent role."""
        with pytest.raises(NotFoundError, match="not found"):
            await roles_command.roles_update(role_name="nonexistent", description="Test")
    
    @pytest.mark.asyncio
    async def test_roles_update_invalid_config(self, roles_command):
        """Test role update with invalid configuration."""
        with pytest.raises(ValidationError, match="Invalid role configuration"):
            await roles_command.roles_update(
                role_name="admin",
                priority="not_an_integer"  # Should be integer
            )
    
    @pytest.mark.asyncio
    async def test_roles_delete_success(self, roles_command):
        """Test successful role deletion."""
        with patch.object(roles_command, '_save_roles_config'):
            result = await roles_command.roles_delete(role_name="user")
            
            assert isinstance(result, RolesDeleteResult)
            assert result.to_dict()["success"] is True
            assert result.role_name == "user"
            assert "user" not in roles_command.roles_config["roles"]
    
    @pytest.mark.asyncio
    async def test_roles_delete_missing_name(self, roles_command):
        """Test role deletion with missing name."""
        with pytest.raises(ValidationError, match="role_name is required"):
            await roles_command.roles_delete()
    
    @pytest.mark.asyncio
    async def test_roles_delete_nonexistent_role(self, roles_command):
        """Test role deletion with nonexistent role."""
        with pytest.raises(NotFoundError, match="not found"):
            await roles_command.roles_delete(role_name="nonexistent")
    
    @pytest.mark.asyncio
    async def test_roles_delete_system_role(self, roles_command):
        """Test role deletion of system role."""
        # Add a system role to the configuration
        roles_command.roles_config["roles"]["system"] = {
            "description": "System role",
            "allowed_servers": ["*"],
            "allowed_clients": ["*"],
            "permissions": ["system"],
            "priority": 200
        }
        
        with patch('mcp_proxy_adapter.core.role_utils.RoleUtils.is_system_role') as mock_is_system:
            mock_is_system.return_value = True
            
            with pytest.raises(ValidationError, match="Cannot delete system role"):
                await roles_command.roles_delete(role_name="system")
    
    @pytest.mark.asyncio
    async def test_roles_validate_existing_role(self, roles_command):
        """Test validation of existing role."""
        result = await roles_command.roles_validate(role_name="admin")
        
        assert isinstance(result, RolesValidateResult)
        assert result.to_dict()["success"] is True
        assert result.role_name == "admin"
        assert result.is_valid is True
        assert len(result.validation_errors) == 0
    
    @pytest.mark.asyncio
    async def test_roles_validate_nonexistent_role(self, roles_command):
        """Test validation of nonexistent role."""
        result = await roles_command.roles_validate(role_name="nonexistent")
        
        assert isinstance(result, RolesValidateResult)
        assert result.to_dict()["success"] is True
        assert result.role_name == "nonexistent"
        assert result.is_valid is False
        assert len(result.validation_errors) > 0
    
    @pytest.mark.asyncio
    async def test_roles_validate_role_config(self, roles_command):
        """Test validation of role configuration."""
        role_config = {
            "description": "Test role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        result = await roles_command.roles_validate(role_config=role_config)
        
        assert isinstance(result, RolesValidateResult)
        assert result.to_dict()["success"] is True
        assert result.role_name == "unknown"
        assert result.is_valid is True
        assert len(result.validation_errors) == 0
    
    @pytest.mark.asyncio
    async def test_roles_validate_invalid_config(self, roles_command):
        """Test validation of invalid role configuration."""
        role_config = {
            "description": 123,  # Should be string
            "allowed_servers": "not_a_list",  # Should be list
            "permissions": ["invalid_permission"],
            "priority": "not_an_integer"  # Should be integer
        }
        
        result = await roles_command.roles_validate(role_config=role_config)
        
        assert isinstance(result, RolesValidateResult)
        assert result.to_dict()["success"] is True
        assert result.is_valid is False
        assert len(result.validation_errors) > 0
    
    @pytest.mark.asyncio
    async def test_roles_validate_missing_params(self, roles_command):
        """Test validation with missing parameters."""
        with pytest.raises(ValidationError, match="Either role_name or role_config is required"):
            await roles_command.roles_validate()
    
    def test_validate_role_config_valid(self, roles_command):
        """Test validation of valid role configuration."""
        role_config = {
            "description": "Test role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        errors = roles_command._validate_role_config(role_config)
        assert len(errors) == 0
    
    def test_validate_role_config_invalid(self, roles_command):
        """Test validation of invalid role configuration."""
        role_config = {
            "description": 123,  # Should be string
            "allowed_servers": "not_a_list",  # Should be list
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": "not_an_integer"  # Should be integer
        }
        
        errors = roles_command._validate_role_config(role_config)
        assert len(errors) > 0
        assert any("description must be a string" in error for error in errors)
        assert any("allowed_servers must be a list" in error for error in errors)
        assert any("priority must be an integer" in error for error in errors)
    
    def test_get_schema(self):
        """Test getting command schema."""
        schema = RolesManagementCommand.get_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "action" in schema["properties"]
        assert "role_name" in schema["properties"]
        assert "required" in schema
        assert "action" in schema["required"]


class TestRolesManagementCommandResults:
    """Test cases for role management command results."""
    
    def test_roles_list_result(self):
        """Test RolesListResult."""
        roles = [
            {
                "name": "admin",
                "description": "Administrator",
                "allowed_servers": ["*"],
                "allowed_clients": ["*"],
                "permissions": ["read", "write", "delete", "admin"],
                "priority": 100
            }
        ]
        
        result = RolesListResult(roles, 1)
        
        assert result.to_dict()["success"] is True
        assert result.roles == roles
        assert result.total_count == 1
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["roles"] == roles
        assert result_dict["total_count"] == 1
    
    def test_roles_create_result(self):
        """Test RolesCreateResult."""
        role_config = {
            "description": "Test role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        result = RolesCreateResult("test_role", role_config)
        
        assert result.to_dict()["success"] is True
        assert result.role_name == "test_role"
        assert result.role_config == role_config
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["role_name"] == "test_role"
        assert result_dict["role_config"] == role_config
    
    def test_roles_update_result(self):
        """Test RolesUpdateResult."""
        role_config = {
            "description": "Updated role",
            "allowed_servers": ["test_server"],
            "allowed_clients": ["admin"],
            "permissions": ["read"],
            "priority": 25
        }
        
        result = RolesUpdateResult("test_role", role_config)
        
        assert result.to_dict()["success"] is True
        assert result.role_name == "test_role"
        assert result.role_config == role_config
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["role_name"] == "test_role"
        assert result_dict["role_config"] == role_config
    
    def test_roles_delete_result(self):
        """Test RolesDeleteResult."""
        result = RolesDeleteResult("test_role")
        
        assert result.to_dict()["success"] is True
        assert result.role_name == "test_role"
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["role_name"] == "test_role"
    
    def test_roles_validate_result_valid(self):
        """Test RolesValidateResult with valid role."""
        result = RolesValidateResult("test_role", True, [])
        
        assert result.to_dict()["success"] is True
        assert result.role_name == "test_role"
        assert result.is_valid is True
        assert result.validation_errors == []
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["role_name"] == "test_role"
        assert result_dict["is_valid"] is True
        assert result_dict["validation_errors"] == []
    
    def test_roles_validate_result_invalid(self):
        """Test RolesValidateResult with invalid role."""
        errors = ["Invalid description", "Invalid permissions"]
        result = RolesValidateResult("test_role", False, errors)
        
        assert result.to_dict()["success"] is True
        assert result.role_name == "test_role"
        assert result.is_valid is False
        assert result.validation_errors == errors
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["role_name"] == "test_role"
        assert result_dict["is_valid"] is False
        assert result_dict["validation_errors"] == errors
    
    def test_result_schemas(self):
        """Test result schemas."""
        # Test RolesListResult schema
        schema = RolesListResult.get_schema()
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "roles" in schema["properties"]
        
        # Test RolesCreateResult schema
        schema = RolesCreateResult.get_schema()
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "role_name" in schema["properties"]
        
        # Test RolesUpdateResult schema
        schema = RolesUpdateResult.get_schema()
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "role_name" in schema["properties"]
        
        # Test RolesDeleteResult schema
        schema = RolesDeleteResult.get_schema()
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "role_name" in schema["properties"]
        
        # Test RolesValidateResult schema
        schema = RolesValidateResult.get_schema()
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "role_name" in schema["properties"]
        assert "is_valid" in schema["properties"]
        assert "validation_errors" in schema["properties"] 