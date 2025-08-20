"""
Tests for Token Management Commands

This module contains tests for the TokenManagementCommand class.
Tests cover token creation, validation, revocation, listing, and refresh operations.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from mcp_proxy_adapter.commands.token_management_command import TokenManagementCommand
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult


class TestTokenManagementCommand:
    """Test cases for TokenManagementCommand."""
    
    @pytest.fixture
    def command(self):
        """Create TokenManagementCommand instance."""
        return TokenManagementCommand()
    
    @pytest.fixture
    def temp_tokens_file(self):
        """Create temporary tokens file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            tokens_data = {
                "test-api-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": True,
                    "created_at": time.time(),
                    "expires_at": time.time() + 3600,
                    "description": "Test API token",
                    "user_id": "test-user"
                },
                "expired-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": True,
                    "created_at": time.time() - 7200,
                    "expires_at": time.time() - 3600,
                    "description": "Expired token",
                    "user_id": "test-user"
                },
                "revoked-token": {
                    "type": "api",
                    "roles": ["user"],
                    "active": False,
                    "created_at": time.time(),
                    "expires_at": time.time() + 3600,
                    "description": "Revoked token",
                    "user_id": "test-user"
                }
            }
            json.dump(tokens_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        Path(temp_file).unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_token_create_jwt_success(self, command):
        """Test JWT token creation success."""
        token_data = {
            "roles": ["admin", "user"],
            "expires_in": 7200,
            "description": "Test JWT token",
            "user_id": "test-user"
        }
        
        result = await command.token_create("jwt", token_data)
        
        assert isinstance(result, SuccessResult)
        assert result.data["token_type"] == "jwt"
        assert result.data["roles"] == ["admin", "user"]
        assert result.data["user_id"] == "test-user"
        assert "token" in result.data
    
    @pytest.mark.asyncio
    async def test_token_create_api_success(self, command, temp_tokens_file):
        """Test API token creation success."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            token_data = {
                "roles": ["user"],
                "expires_in": 3600,
                "description": "Test API token",
                "user_id": "test-user"
            }
            
            result = await command.token_create("api", token_data)
            
            assert isinstance(result, SuccessResult)
            assert result.data["token_type"] == "api"
            assert result.data["roles"] == ["user"]
            assert result.data["user_id"] == "test-user"
            assert "token" in result.data
    
    @pytest.mark.asyncio
    async def test_token_create_unsupported_type(self, command):
        """Test token creation with unsupported type."""
        token_data = {"roles": ["user"]}
        
        result = await command.token_create("unsupported", token_data)
        
        assert isinstance(result, ErrorResult)
        assert result.code == -32602
        assert "Unsupported token type" in result.message
    
    @pytest.mark.asyncio
    async def test_token_create_exception(self, command):
        """Test token creation with exception."""
        with patch.object(command, '_create_api_token', side_effect=Exception("Test error")):
            token_data = {"roles": ["user"]}
            
            result = await command.token_create("api", token_data)
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32603
            assert "Token creation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_token_validate_success(self, command):
        """Test token validation success."""
        with patch.object(command.auth_validator, 'validate_token') as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = True
            mock_result.roles = ["admin", "user"]
            mock_validate.return_value = mock_result
            
            result = await command.token_validate("valid-token", "jwt")
            
            assert isinstance(result, SuccessResult)
            assert result.data["valid"] is True
            assert result.data["token_type"] == "jwt"
            assert result.data["roles"] == ["admin", "user"]
            mock_validate.assert_called_once_with("valid-token", "jwt")
    
    @pytest.mark.asyncio
    async def test_token_validate_failure(self, command):
        """Test token validation failure."""
        with patch.object(command.auth_validator, 'validate_token') as mock_validate:
            mock_result = Mock()
            mock_result.is_valid = False
            mock_result.to_json_rpc_error.return_value = {
                "code": -32004,
                "message": "Token validation failed"
            }
            mock_validate.return_value = mock_result
            
            result = await command.token_validate("invalid-token", "jwt")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32004
            assert "Token validation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_token_validate_no_token(self, command):
        """Test token validation without token."""
        result = await command.token_validate("", "jwt")
        
        assert isinstance(result, ErrorResult)
        assert result.code == -32602
        assert "Token not provided" in result.message
    
    @pytest.mark.asyncio
    async def test_token_validate_auto_detect_jwt(self, command):
        """Test token validation with auto-detection of JWT."""
        with patch.object(command, '_is_jwt_token', return_value=True):
            with patch.object(command.auth_validator, 'validate_token') as mock_validate:
                mock_result = Mock()
                mock_result.is_valid = True
                mock_result.roles = ["user"]
                mock_validate.return_value = mock_result
                
                result = await command.token_validate("header.payload.signature", "auto")
                
                assert isinstance(result, SuccessResult)
                assert result.data["token_type"] == "jwt"
                mock_validate.assert_called_once_with("header.payload.signature", "jwt")
    
    @pytest.mark.asyncio
    async def test_token_validate_auto_detect_api(self, command):
        """Test token validation with auto-detection of API token."""
        with patch.object(command, '_is_jwt_token', return_value=False):
            with patch.object(command.auth_validator, 'validate_token') as mock_validate:
                mock_result = Mock()
                mock_result.is_valid = True
                mock_result.roles = ["user"]
                mock_validate.return_value = mock_result
                
                result = await command.token_validate("api-token", "auto")
                
                assert isinstance(result, SuccessResult)
                assert result.data["token_type"] == "api"
                mock_validate.assert_called_once_with("api-token", "api")
    
    @pytest.mark.asyncio
    async def test_token_validate_exception(self, command):
        """Test token validation with exception."""
        with patch.object(command.auth_validator, 'validate_token', side_effect=Exception("Test error")):
            result = await command.token_validate("test-token", "jwt")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32603
            assert "Token validation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_token_revoke_success(self, command, temp_tokens_file):
        """Test token revocation success."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_revoke("test-api-token")
            
            assert isinstance(result, SuccessResult)
            assert result.data["revoked"] is True
            assert result.data["token"] == "test-api-token"
            assert "revoked_at" in result.data
    
    @pytest.mark.asyncio
    async def test_token_revoke_not_found(self, command, temp_tokens_file):
        """Test token revocation with non-existent token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_revoke("non-existent-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32011
            assert "Token not found" in result.message
    
    @pytest.mark.asyncio
    async def test_token_revoke_no_token(self, command):
        """Test token revocation without token."""
        result = await command.token_revoke("")
        
        assert isinstance(result, ErrorResult)
        assert result.code == -32602
        assert "Token not provided" in result.message
    
    @pytest.mark.asyncio
    async def test_token_revoke_exception(self, command):
        """Test token revocation with exception."""
        with patch.object(command, '_load_tokens', side_effect=Exception("Test error")):
            result = await command.token_revoke("test-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32603
            assert "Token revocation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_token_list_all(self, command, temp_tokens_file):
        """Test token listing with all tokens."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_list(active_only=False)
            
            assert isinstance(result, SuccessResult)
            assert result.data["count"] == 3
            assert len(result.data["tokens"]) == 3
            assert result.data["active_only"] is False
    
    @pytest.mark.asyncio
    async def test_token_list_active_only(self, command, temp_tokens_file):
        """Test token listing with active tokens only."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_list(active_only=True)
            
            assert isinstance(result, SuccessResult)
            # Should return only active tokens (test-api-token and expired-token are both active=True)
            assert result.data["count"] == 2
            assert len(result.data["tokens"]) == 2
            assert result.data["active_only"] is True
            
            # Check that only active tokens are returned
            token_ids = [token["id"] for token in result.data["tokens"]]
            assert "test-api-token" in token_ids
            assert "expired-token" in token_ids
            assert "revoked-token" not in token_ids
    
    @pytest.mark.asyncio
    async def test_token_list_empty(self, command):
        """Test token listing with empty tokens file."""
        with patch.object(command, '_load_tokens', return_value={}):
            result = await command.token_list()
            
            assert isinstance(result, SuccessResult)
            assert result.data["count"] == 0
            assert len(result.data["tokens"]) == 0
    
    @pytest.mark.asyncio
    async def test_token_list_exception(self, command):
        """Test token listing with exception."""
        with patch.object(command, '_load_tokens', side_effect=Exception("Test error")):
            result = await command.token_list()
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32603
            assert "Token listing failed" in result.message
    
    @pytest.mark.asyncio
    async def test_token_refresh_success(self, command, temp_tokens_file):
        """Test token refresh success."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_refresh("test-api-token")
            
            assert isinstance(result, SuccessResult)
            assert result.data["refreshed"] is True
            assert result.data["old_token"] == "test-api-token"
            assert "new_token" in result.data
            assert "expires_at" in result.data
    
    @pytest.mark.asyncio
    async def test_token_refresh_not_found(self, command, temp_tokens_file):
        """Test token refresh with non-existent token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_refresh("non-existent-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32011
            assert "Token not found" in result.message
    
    @pytest.mark.asyncio
    async def test_token_refresh_revoked(self, command, temp_tokens_file):
        """Test token refresh with revoked token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_refresh("revoked-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32011
            assert "Token is revoked" in result.message
    
    @pytest.mark.asyncio
    async def test_token_refresh_expired(self, command, temp_tokens_file):
        """Test token refresh with expired token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            result = await command.token_refresh("expired-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32010
            assert "Token has expired" in result.message
    
    @pytest.mark.asyncio
    async def test_token_refresh_no_token(self, command):
        """Test token refresh without token."""
        result = await command.token_refresh("")
        
        assert isinstance(result, ErrorResult)
        assert result.code == -32602
        assert "Token not provided" in result.message
    
    @pytest.mark.asyncio
    async def test_token_refresh_exception(self, command):
        """Test token refresh with exception."""
        with patch.object(command, '_load_tokens', side_effect=Exception("Test error")):
            result = await command.token_refresh("test-token")
            
            assert isinstance(result, ErrorResult)
            assert result.code == -32603
            assert "Token refresh failed" in result.message
    
    def test_is_jwt_token_valid(self, command):
        """Test JWT token format detection with valid token."""
        token = "header.payload.signature"
        assert command._is_jwt_token(token) is True
    
    def test_is_jwt_token_invalid(self, command):
        """Test JWT token format detection with invalid token."""
        token = "invalid.token"
        assert command._is_jwt_token(token) is False
    
    def test_get_token_expiry_api(self, command, temp_tokens_file):
        """Test getting token expiry for API token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            expiry = command._get_token_expiry("test-api-token", "api")
            assert expiry is not None
            assert isinstance(expiry, (int, float))
    
    def test_get_token_expiry_not_found(self, command, temp_tokens_file):
        """Test getting token expiry for non-existent token."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            expiry = command._get_token_expiry("non-existent-token", "api")
            assert expiry is None
    
    def test_get_token_expiry_jwt(self, command):
        """Test getting token expiry for JWT token."""
        expiry = command._get_token_expiry("jwt.token", "jwt")
        assert expiry is None  # JWT expiry would require decoding
    
    def test_load_tokens_success(self, command, temp_tokens_file):
        """Test loading tokens successfully."""
        with patch.object(command, 'tokens_file', temp_tokens_file):
            tokens = command._load_tokens()
            
            assert isinstance(tokens, dict)
            assert len(tokens) == 3
            assert "test-api-token" in tokens
            assert "expired-token" in tokens
            assert "revoked-token" in tokens
    
    def test_load_tokens_file_not_exists(self, command):
        """Test loading tokens when file doesn't exist."""
        with patch.object(command, 'tokens_file', 'nonexistent.json'):
            tokens = command._load_tokens()
            assert tokens == {}
    
    def test_load_tokens_exception(self, command):
        """Test loading tokens with exception."""
        with patch.object(command, 'tokens_file', 'nonexistent.json'):
            with patch('builtins.open', side_effect=Exception("Test error")):
                tokens = command._load_tokens()
                assert tokens == {}
    
    def test_save_tokens_success(self, command):
        """Test saving tokens successfully."""
        temp_file = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_file.close()
        
        try:
            with patch.object(command, 'tokens_file', temp_file.name):
                tokens_data = {"test-token": {"type": "api", "active": True}}
                command._save_tokens(tokens_data)
                
                # Verify tokens were saved
                with open(temp_file.name, 'r') as f:
                    saved_data = json.load(f)
                
                assert saved_data == tokens_data
        finally:
            Path(temp_file.name).unlink(missing_ok=True)
    
    def test_save_tokens_exception(self, command):
        """Test saving tokens with exception."""
        with patch.object(command, 'tokens_file', '/invalid/path/tokens.json'):
            with pytest.raises(Exception):
                command._save_tokens({"test": "data"}) 