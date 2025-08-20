"""
Tests for AuthValidator

Tests for the universal authentication validator.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, mock_open

from mcp_proxy_adapter.core.auth_validator import AuthValidator, AuthValidationResult, JSON_RPC_ERRORS


class TestAuthValidationResult:
    """Test AuthValidationResult class."""
    
    def test_init_valid_result(self):
        """Test initialization of valid result."""
        result = AuthValidationResult(is_valid=True, roles=["admin", "user"])
        
        assert result.is_valid is True
        assert result.error_code is None
        assert result.error_message is None
        assert result.roles == ["admin", "user"]
    
    def test_init_invalid_result(self):
        """Test initialization of invalid result."""
        result = AuthValidationResult(
            is_valid=False,
            error_code=-32003,
            error_message="Certificate validation failed",
            roles=[]
        )
        
        assert result.is_valid is False
        assert result.error_code == -32003
        assert result.error_message == "Certificate validation failed"
        assert result.roles == []
    
    def test_to_json_rpc_error_valid(self):
        """Test to_json_rpc_error for valid result."""
        result = AuthValidationResult(is_valid=True, roles=["admin"])
        
        error_dict = result.to_json_rpc_error()
        
        assert error_dict == {}
    
    def test_to_json_rpc_error_invalid(self):
        """Test to_json_rpc_error for invalid result."""
        result = AuthValidationResult(
            is_valid=False,
            error_code=-32003,
            error_message="Certificate validation failed",
            roles=["admin"]
        )
        
        error_dict = result.to_json_rpc_error()
        
        assert error_dict["code"] == -32003
        assert error_dict["message"] == "Certificate validation failed"
        assert error_dict["data"]["validation_type"] == "authentication"
        assert error_dict["data"]["roles"] == ["admin"]
    
    def test_to_dict(self):
        """Test to_dict method."""
        result = AuthValidationResult(
            is_valid=False,
            error_code=-32003,
            error_message="Certificate validation failed",
            roles=["admin"]
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["is_valid"] is False
        assert result_dict["error_code"] == -32003
        assert result_dict["error_message"] == "Certificate validation failed"
        assert result_dict["roles"] == ["admin"]


class TestAuthValidator:
    """Test AuthValidator class."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = AuthValidator()
    
    def test_init_default(self):
        """Test initialization with default config."""
        validator = AuthValidator()
        
        assert validator.config == {}
        assert validator.role_oid == "1.3.6.1.4.1.99999.1"
    
    def test_init_with_config(self):
        """Test initialization with config."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        assert validator.config == config
    
    def test_check_config_disabled(self):
        """Test _check_config when SSL is disabled."""
        result = self.validator._check_config("ssl")
        
        assert result is False
    
    def test_check_config_enabled(self):
        """Test _check_config when SSL is enabled."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        result = validator._check_config("ssl")
        
        assert result is True
    
    def test_check_config_token_enabled(self):
        """Test _check_config for token auth when enabled."""
        config = {
            "ssl": {
                "enabled": True,
                "token_auth": {"enabled": True}
            }
        }
        validator = AuthValidator(config)
        
        result = validator._check_config("token")
        
        assert result is True
    
    def test_check_config_token_disabled(self):
        """Test _check_config for token auth when disabled."""
        config = {
            "ssl": {
                "enabled": True,
                "token_auth": {"enabled": False}
            }
        }
        validator = AuthValidator(config)
        
        result = validator._check_config("token")
        
        assert result is False
    
    def test_get_validation_mode_none(self):
        """Test _get_validation_mode when no SSL."""
        mode = self.validator._get_validation_mode()
        
        assert mode == "none"
    
    def test_get_validation_mode_ssl(self):
        """Test _get_validation_mode for SSL."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        mode = validator._get_validation_mode()
        
        assert mode == "ssl"
    
    def test_get_validation_mode_token(self):
        """Test _get_validation_mode for token auth."""
        config = {
            "ssl": {
                "enabled": True,
                "token_auth": {"enabled": True}
            }
        }
        validator = AuthValidator(config)
        
        mode = validator._get_validation_mode()
        
        assert mode == "token"
    
    def test_get_validation_mode_mtls(self):
        """Test _get_validation_mode for mTLS."""
        config = {
            "ssl": {
                "enabled": True,
                "mtls": {"enabled": True}
            }
        }
        validator = AuthValidator(config)
        
        mode = validator._get_validation_mode()
        
        assert mode == "mtls"
    
    def test_validate_auth_disabled(self):
        """Test validate_auth when authentication is disabled."""
        result = self.validator.validate_auth({}, "ssl")
        
        assert result.is_valid is True
        assert result.roles == []
    
    def test_validate_auth_unsupported_type(self):
        """Test validate_auth with unsupported type."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        result = validator.validate_auth({}, "unsupported")
        
        assert result.is_valid is False
        assert result.error_code == -32602
        assert "Unsupported authentication type" in result.error_message
    
    def test_validate_auth_certificate_missing_path(self):
        """Test validate_auth for certificate with missing path."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        result = validator.validate_auth({}, "certificate")
        
        assert result.is_valid is False
        assert result.error_code == -32009
        assert "Certificate path not provided" in result.error_message
    
    def test_validate_auth_token_missing_token(self):
        """Test validate_auth for token with missing token."""
        config = {
            "ssl": {
                "enabled": True,
                "token_auth": {"enabled": True}
            }
        }
        validator = AuthValidator(config)
        
        result = validator.validate_auth({}, "token")
        
        assert result.is_valid is False
        assert result.error_code == -32011
        assert "Token not provided" in result.error_message
    
    def test_validate_auth_mtls_missing_certs(self):
        """Test validate_auth for mTLS with missing certificates."""
        config = {
            "ssl": {
                "enabled": True,
                "mtls": {"enabled": True}
            }
        }
        validator = AuthValidator(config)
        
        result = validator.validate_auth({}, "mtls")
        
        assert result.is_valid is False
        assert result.error_code == -32005
        assert "Client certificate and CA certificate required" in result.error_message
    
    def test_validate_auth_ssl_missing_cert(self):
        """Test validate_auth for SSL with missing certificate."""
        config = {"ssl": {"enabled": True}}
        validator = AuthValidator(config)
        
        result = validator.validate_auth({}, "ssl")
        
        assert result.is_valid is False
        assert result.error_code == -32006
        assert "Server certificate required" in result.error_message
    
    def test_validate_certificate_missing_path(self):
        """Test validate_certificate with missing path."""
        result = self.validator.validate_certificate(None)
        
        assert result.is_valid is False
        assert result.error_code == -32009
        assert "Certificate path not provided" in result.error_message
    
    def test_validate_certificate_file_not_found(self):
        """Test validate_certificate with non-existent file."""
        result = self.validator.validate_certificate("/nonexistent/cert.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32009
        assert "Certificate file not found" in result.error_message
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('os.path.exists')
    def test_validate_certificate_expired(self, mock_exists, mock_load_cert, mock_open):
        """Test validate_certificate with expired certificate."""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock certificate
        mock_cert = Mock()
        mock_cert.not_valid_before = datetime.utcnow() + timedelta(days=1)
        mock_cert.not_valid_after = datetime.utcnow() - timedelta(days=1)
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.validator.validate_certificate("/test/cert.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32008
        assert "Certificate has expired" in result.error_message
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('os.path.exists')
    def test_validate_certificate_valid(self, mock_exists, mock_load_cert, mock_open):
        """Test validate_certificate with valid certificate."""
        # Mock file exists
        mock_exists.return_value = True
        
        # Mock certificate
        mock_cert = Mock()
        mock_cert.not_valid_before = datetime.utcnow() - timedelta(days=1)
        mock_cert.not_valid_after = datetime.utcnow() + timedelta(days=1)
        mock_cert.extensions = []
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = self.validator.validate_certificate("/test/cert.crt")
        
        assert result.is_valid is True
        assert result.roles == []
    
    def test_validate_token_missing_token(self):
        """Test validate_token with missing token."""
        result = self.validator.validate_token(None)
        
        assert result.is_valid is False
        assert result.error_code == -32011
        assert "Token not provided" in result.error_message
    
    def test_validate_token_unsupported_type(self):
        """Test validate_token with unsupported type."""
        result = self.validator.validate_token("test_token", "unsupported")
        
        assert result.is_valid is False
        assert result.error_code == -32602
        assert "Unsupported token type" in result.error_message
    
    def test_validate_token_jwt_invalid_format(self):
        """Test validate_token with invalid JWT format."""
        result = self.validator.validate_token("invalid.jwt")
        
        assert result.is_valid is False
        assert result.error_code == -32004
        assert "Invalid JWT token format" in result.error_message
    
    def test_validate_token_jwt_valid_format(self):
        """Test validate_token with valid JWT format."""
        result = self.validator.validate_token("header.payload.signature")
        
        assert result.is_valid is True
        assert result.roles == []
    
    def test_validate_token_api_valid(self):
        """Test validate_token with valid API token."""
        result = self.validator.validate_token("api_token", "api")
        
        assert result.is_valid is True
        assert result.roles == []
    
    def test_validate_mtls_missing_client_cert(self):
        """Test validate_mtls with missing client certificate."""
        result = self.validator.validate_mtls(None, "/test/ca.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32005
        assert "Client certificate and CA certificate required" in result.error_message
    
    def test_validate_mtls_missing_ca_cert(self):
        """Test validate_mtls with missing CA certificate."""
        result = self.validator.validate_mtls("/test/client.crt", None)
        
        assert result.is_valid is False
        assert result.error_code == -32005
        assert "Client certificate and CA certificate required" in result.error_message
    
    def test_validate_ssl_missing_cert(self):
        """Test validate_ssl with missing certificate."""
        result = self.validator.validate_ssl(None)
        
        assert result.is_valid is False
        assert result.error_code == -32006
        assert "Server certificate required" in result.error_message
    
    def test_extract_roles_from_certificate_no_roles(self):
        """Test _extract_roles_from_certificate with no roles."""
        mock_cert = Mock()
        mock_cert.extensions = []
        
        roles = self.validator._extract_roles_from_certificate(mock_cert)
        
        assert roles == []
    
    def test_extract_roles_from_certificate_with_roles(self):
        """Test _extract_roles_from_certificate with roles."""
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid.dotted_string = "1.3.6.1.4.1.99999.1"
        mock_extension.value.value = b"admin,user,moderator"
        mock_cert.extensions = [mock_extension]
        
        roles = self.validator._extract_roles_from_certificate(mock_cert)
        
        assert roles == ["admin", "user", "moderator"]
    
    def test_validate_server_certificate_valid(self):
        """Test _validate_server_certificate with valid certificate."""
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid = "key_usage"
        mock_extension.value.digital_signature = True
        mock_extension.value.key_encipherment = True
        mock_cert.extensions = [mock_extension]
        
        result = self.validator._validate_server_certificate(mock_cert)
        
        assert result is True
    
    def test_validate_client_certificate_valid(self):
        """Test _validate_client_certificate with valid certificate."""
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid = "extended_key_usage"
        mock_extension.value = ["client_auth"]
        mock_cert.extensions = [mock_extension]
        
        result = self.validator._validate_client_certificate(mock_cert)
        
        assert result is True
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('cryptography.hazmat.primitives.serialization.load_pem_private_key')
    def test_verify_certificate_chain(self, mock_load_key, mock_load_cert, mock_open):
        """Test _verify_certificate_chain."""
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock certificates
        mock_client_cert = Mock()
        mock_ca_cert = Mock()
        mock_ca_cert.public_key.return_value = Mock()
        mock_load_cert.side_effect = [mock_client_cert, mock_ca_cert]
        
        # Mock CA key
        mock_ca_key = Mock()
        mock_load_key.return_value = mock_ca_key
        
        result = self.validator._verify_certificate_chain("/test/client.crt", "/test/ca.crt")
        
        assert result is True


class TestJSONRPCErrors:
    """Test JSON-RPC error codes."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = AuthValidator()
    
    def test_error_codes_exist(self):
        """Test that all required error codes exist."""
        required_codes = [
            -32600, -32601, -32602, -32603, -32700,  # General errors
            -32001, -32002, -32003, -32004, -32005,  # Authentication errors
            -32006, -32007, -32008, -32009, -32010, -32011
        ]
        
        for code in required_codes:
            assert code in JSON_RPC_ERRORS
            assert isinstance(JSON_RPC_ERRORS[code], str)
            assert len(JSON_RPC_ERRORS[code]) > 0

    def test_validate_token_unsupported_type(self):
        """Test validate_token with unsupported token type."""
        result = self.validator.validate_token("test_token", "unsupported")
        
        assert result.is_valid is False
        assert result.error_code == -32602
        assert "Unsupported token type" in result.error_message

    def test_validate_ssl_missing_cert(self):
        """Test validate_ssl with missing certificate."""
        result = self.validator.validate_ssl(None)
        
        assert result.is_valid is False
        assert result.error_code == -32006
        assert "Server certificate required for SSL validation" in result.error_message

    def test_validate_ssl_exception(self):
        """Test validate_ssl with exception."""
        with patch('os.path.exists', side_effect=Exception("Test error")):
            result = self.validator.validate_ssl("/test/server.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32003  # Certificate validation error code
        assert "Certificate validation failed" in result.error_message

    def test_validate_auth_exception(self):
        """Test validate_auth with exception."""
        # Mock _get_validation_mode to raise exception
        with patch.object(self.validator, '_get_validation_mode', side_effect=Exception("Test error")):
            result = self.validator.validate_auth({})
        
        assert result.is_valid is False
        assert result.error_code == -32603
        assert "Internal validation error" in result.error_message

    def test_validate_certificate_exception(self):
        """Test validate_certificate with exception."""
        with patch('os.path.exists', side_effect=Exception("Test error")):
            result = self.validator.validate_certificate("/test/cert.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32003
        assert "Certificate validation failed" in result.error_message

    def test_validate_token_exception(self):
        """Test validate_token with exception."""
        with patch.object(self.validator, '_validate_jwt_token', side_effect=Exception("Test error")):
            result = self.validator.validate_token("test_token", "jwt")
        
        assert result.is_valid is False
        assert result.error_code == -32004
        assert "Token validation failed" in result.error_message

    def test_validate_mtls_exception(self):
        """Test validate_mtls with exception."""
        with patch.object(self.validator, 'validate_certificate', side_effect=Exception("Test error")):
            result = self.validator.validate_mtls("/test/client.crt", "/test/ca.crt")
        
        assert result.is_valid is False
        assert result.error_code == -32005
        assert "mTLS validation failed" in result.error_message 