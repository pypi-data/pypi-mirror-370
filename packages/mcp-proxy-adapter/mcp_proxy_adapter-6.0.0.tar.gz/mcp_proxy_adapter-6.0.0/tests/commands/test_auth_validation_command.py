"""
Tests for AuthValidationCommand

Tests for authentication validation commands.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mcp_proxy_adapter.commands.auth_validation_command import AuthValidationCommand
from mcp_proxy_adapter.core.auth_validator import AuthValidationResult


class TestAuthValidationCommand:
    """Test AuthValidationCommand class."""
    
    def setup_method(self):
        """Set up test method."""
        self.command = AuthValidationCommand()
    
    def test_init(self):
        """Test initialization."""
        command = AuthValidationCommand()
        
        assert command.validator is not None
        assert command.logger is not None
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_success(self, mock_validator_class):
        """Test auth_validate with successful validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(is_valid=True, roles=["admin", "user"])
        mock_validator.validate_auth.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        auth_data = {
            "auth_type": "certificate",
            "cert_path": "/test/cert.crt",
            "cert_type": "server"
        }
        
        result = await command.auth_validate(auth_data)
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["valid"] is True
        assert result_dict["data"]["roles"] == ["admin", "user"]
        assert result_dict["data"]["auth_type"] == "certificate"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_failure(self, mock_validator_class):
        """Test auth_validate with failed validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(
            is_valid=False,
            error_code=-32003,
            error_message="Certificate validation failed"
        )
        mock_validator.validate_auth.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        auth_data = {
            "auth_type": "certificate",
            "cert_path": "/test/cert.crt"
        }
        
        result = await command.auth_validate(auth_data)
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32003
        assert result_dict["error"]["message"] == "Certificate validation failed"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_exception(self, mock_validator_class):
        """Test auth_validate with exception."""
        # Mock validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_auth.side_effect = Exception("Test error")
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        auth_data = {"auth_type": "certificate"}
        
        result = await command.auth_validate(auth_data)
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32603
        assert "Internal authentication validation error" in result_dict["error"]["message"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_cert_success(self, mock_validator_class):
        """Test auth_validate_cert with successful validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(is_valid=True, roles=["admin"])
        mock_validator.validate_certificate.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_cert("/test/cert.crt", "server")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["valid"] is True
        assert result_dict["data"]["cert_path"] == "/test/cert.crt"
        assert result_dict["data"]["cert_type"] == "server"
        assert result_dict["data"]["roles"] == ["admin"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_cert_failure(self, mock_validator_class):
        """Test auth_validate_cert with failed validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(
            is_valid=False,
            error_code=-32009,
            error_message="Certificate not found"
        )
        mock_validator.validate_certificate.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_cert("/nonexistent/cert.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32009
        assert result_dict["error"]["message"] == "Certificate not found"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_cert_exception(self, mock_validator_class):
        """Test auth_validate_cert with exception."""
        # Mock validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_certificate.side_effect = Exception("Test error")
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_cert("/test/cert.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32603
        assert "Internal certificate validation error" in result_dict["error"]["message"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_token_success(self, mock_validator_class):
        """Test auth_validate_token with successful validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(is_valid=True, roles=["user"])
        mock_validator.validate_token.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_token("test_token", "jwt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["valid"] is True
        assert result_dict["data"]["token_type"] == "jwt"
        assert result_dict["data"]["roles"] == ["user"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_token_failure(self, mock_validator_class):
        """Test auth_validate_token with failed validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(
            is_valid=False,
            error_code=-32004,
            error_message="Token validation failed"
        )
        mock_validator.validate_token.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_token("invalid_token")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32004
        assert result_dict["error"]["message"] == "Token validation failed"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_token_exception(self, mock_validator_class):
        """Test auth_validate_token with exception."""
        # Mock validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_token.side_effect = Exception("Test error")
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_token("test_token")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32603
        assert "Internal token validation error" in result_dict["error"]["message"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_mtls_success(self, mock_validator_class):
        """Test auth_validate_mtls with successful validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(is_valid=True, roles=["admin"])
        mock_validator.validate_mtls.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_mtls("/test/client.crt", "/test/ca.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["valid"] is True
        assert result_dict["data"]["client_cert"] == "/test/client.crt"
        assert result_dict["data"]["ca_cert"] == "/test/ca.crt"
        assert result_dict["data"]["roles"] == ["admin"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_mtls_failure(self, mock_validator_class):
        """Test auth_validate_mtls with failed validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(
            is_valid=False,
            error_code=-32005,
            error_message="mTLS validation failed"
        )
        mock_validator.validate_mtls.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_mtls("/test/client.crt", "/test/ca.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32005
        assert result_dict["error"]["message"] == "mTLS validation failed"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_mtls_exception(self, mock_validator_class):
        """Test auth_validate_mtls with exception."""
        # Mock validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_mtls.side_effect = Exception("Test error")
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_mtls("/test/client.crt", "/test/ca.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32603
        assert "Internal mTLS validation error" in result_dict["error"]["message"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_ssl_success(self, mock_validator_class):
        """Test auth_validate_ssl with successful validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(is_valid=True, roles=["server"])
        mock_validator.validate_ssl.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_ssl("/test/server.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["valid"] is True
        assert result_dict["data"]["server_cert"] == "/test/server.crt"
        assert result_dict["data"]["roles"] == ["server"]
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_ssl_failure(self, mock_validator_class):
        """Test auth_validate_ssl with failed validation."""
        # Mock validator
        mock_validator = Mock()
        mock_result = AuthValidationResult(
            is_valid=False,
            error_code=-32006,
            error_message="SSL validation failed"
        )
        mock_validator.validate_ssl.return_value = mock_result
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_ssl("/test/server.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32006
        assert result_dict["error"]["message"] == "SSL validation failed"
    
    @patch('mcp_proxy_adapter.commands.auth_validation_command.AuthValidator')
    async def test_auth_validate_ssl_exception(self, mock_validator_class):
        """Test auth_validate_ssl with exception."""
        # Mock validator to raise exception
        mock_validator = Mock()
        mock_validator.validate_ssl.side_effect = Exception("Test error")
        mock_validator_class.return_value = mock_validator
        
        command = AuthValidationCommand()
        
        result = await command.auth_validate_ssl("/test/server.crt")
        
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["error"]["code"] == -32603
        assert "Internal SSL validation error" in result_dict["error"]["message"]
    
    def test_get_schema(self):
        """Test get_schema method."""
        schema = self.command.get_schema()
        
        # Check that all expected commands are present
        expected_commands = [
            "auth_validate",
            "auth_validate_cert",
            "auth_validate_token",
            "auth_validate_mtls",
            "auth_validate_ssl"
        ]
        
        for command in expected_commands:
            assert command in schema
            assert "description" in schema[command]
            assert "parameters" in schema[command]
            assert "returns" in schema[command]
    
    def test_get_schema_auth_validate(self):
        """Test get_schema for auth_validate command."""
        schema = self.command.get_schema()
        auth_validate_schema = schema["auth_validate"]
        
        assert auth_validate_schema["description"] == "Universal authentication validation"
        assert "auth_data" in auth_validate_schema["parameters"]
        assert "valid" in auth_validate_schema["returns"]["properties"]
        assert "roles" in auth_validate_schema["returns"]["properties"]
    
    def test_get_schema_auth_validate_cert(self):
        """Test get_schema for auth_validate_cert command."""
        schema = self.command.get_schema()
        cert_schema = schema["auth_validate_cert"]
        
        assert cert_schema["description"] == "Validate certificate"
        assert "cert_path" in cert_schema["parameters"]
        assert "cert_type" in cert_schema["parameters"]
        assert "valid" in cert_schema["returns"]["properties"]
        assert "cert_path" in cert_schema["returns"]["properties"]
    
    def test_get_schema_auth_validate_token(self):
        """Test get_schema for auth_validate_token command."""
        schema = self.command.get_schema()
        token_schema = schema["auth_validate_token"]
        
        assert token_schema["description"] == "Validate token"
        assert "token" in token_schema["parameters"]
        assert "token_type" in token_schema["parameters"]
        assert "valid" in token_schema["returns"]["properties"]
        assert "token_type" in token_schema["returns"]["properties"]
    
    def test_get_schema_auth_validate_mtls(self):
        """Test get_schema for auth_validate_mtls command."""
        schema = self.command.get_schema()
        mtls_schema = schema["auth_validate_mtls"]
        
        assert mtls_schema["description"] == "Validate mTLS connection"
        assert "client_cert" in mtls_schema["parameters"]
        assert "ca_cert" in mtls_schema["parameters"]
        assert "valid" in mtls_schema["returns"]["properties"]
        assert "client_cert" in mtls_schema["returns"]["properties"]
    
    def test_get_schema_auth_validate_ssl(self):
        """Test get_schema for auth_validate_ssl command."""
        schema = self.command.get_schema()
        ssl_schema = schema["auth_validate_ssl"]
        
        assert ssl_schema["description"] == "Validate SSL connection"
        assert "server_cert" in ssl_schema["parameters"]
        assert "valid" in ssl_schema["returns"]["properties"]
        assert "server_cert" in ssl_schema["returns"]["properties"] 