"""
Tests for SSL Setup Command.

Tests the SSLSetupResult and SSLSetupCommand classes.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from mcp_proxy_adapter.commands.ssl_setup_command import SSLSetupResult, SSLSetupCommand
from mcp_proxy_adapter.commands.result import SuccessResult, ErrorResult


class TestSSLSetupResult:
    """Test SSLSetupResult class."""
    
    def test_ssl_setup_result_initialization(self):
        """Test SSLSetupResult initialization."""
        result = SSLSetupResult(
            ssl_enabled=True,
            cert_path="/path/to/cert.pem",
            key_path="/path/to/key.pem",
            config={"enabled": True},
            status="enabled"
        )
        
        assert result.ssl_enabled is True
        assert result.cert_path == "/path/to/cert.pem"
        assert result.key_path == "/path/to/key.pem"
        assert result.config["enabled"] is True
        assert result.status == "enabled"
    
    def test_ssl_setup_result_to_dict(self):
        """Test SSLSetupResult to_dict method."""
        result = SSLSetupResult(
            ssl_enabled=True,
            cert_path="/path/to/cert.pem",
            key_path="/path/to/key.pem",
            config={"enabled": True, "mtls": True},
            status="enabled"
        )
        
        data = result.to_dict()
        
        assert data["ssl_enabled"] is True
        assert data["cert_path"] == "/path/to/cert.pem"
        assert data["key_path"] == "/path/to/key.pem"
        assert data["config"]["enabled"] is True
        assert data["config"]["mtls"] is True
        assert data["status"] == "enabled"
    
    def test_ssl_setup_result_get_schema(self):
        """Test SSLSetupResult get_schema method."""
        result = SSLSetupResult(ssl_enabled=True, status="enabled")
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "ssl_enabled" in schema["properties"]
        assert "cert_path" in schema["properties"]
        assert "key_path" in schema["properties"]
        assert "config" in schema["properties"]
        assert "status" in schema["properties"]
        assert "error" in schema["properties"]


class TestSSLSetupCommand:
    """Test SSLSetupCommand class."""
    
    @pytest.fixture
    def command(self):
        """Create SSLSetupCommand instance."""
        return SSLSetupCommand()
    
    @pytest.mark.asyncio
    async def test_ssl_setup_disabled(self, command):
        """Test SSL setup with disabled configuration."""
        ssl_config = {"enabled": False}
        
        result = await command.ssl_setup(ssl_config)
        
        assert isinstance(result, SuccessResult)
        assert result.data["ssl_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_ssl_setup_invalid_config(self, command):
        """Test SSL setup with invalid configuration."""
        ssl_config = "invalid_config"
        
        result = await command.ssl_setup(ssl_config)
        
        assert isinstance(result, ErrorResult)
        assert "SSL configuration must be a dictionary" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_setup_missing_files(self, command):
        """Test SSL setup with missing certificate files."""
        ssl_config = {
            "enabled": True,
            "cert_file": "/nonexistent/cert.pem",
            "key_file": "/nonexistent/key.pem"
        }
        
        result = await command.ssl_setup(ssl_config)
        
        assert isinstance(result, ErrorResult)
        assert "Certificate file not found" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_setup_missing_cert_file(self, command):
        """Test SSL setup with missing certificate file."""
        with tempfile.NamedTemporaryFile(suffix=".key", delete=False) as key_file:
            key_file.write(b"test key content")
            key_path = key_file.name
        
        try:
            ssl_config = {
                "enabled": True,
                "cert_file": "/nonexistent/cert.pem",
                "key_file": key_path
            }
            
            result = await command.ssl_setup(ssl_config)
            
            assert isinstance(result, ErrorResult)
            assert "Certificate file not found" in result.message
        finally:
            os.unlink(key_path)
    
    @pytest.mark.asyncio
    async def test_ssl_setup_missing_key_file(self, command):
        """Test SSL setup with missing key file."""
        with tempfile.NamedTemporaryFile(suffix=".crt", delete=False) as cert_file:
            cert_file.write(b"test cert content")
            cert_path = cert_file.name
        
        try:
            ssl_config = {
                "enabled": True,
                "cert_file": cert_path,
                "key_file": "/nonexistent/key.pem"
            }
            
            result = await command.ssl_setup(ssl_config)
            
            assert isinstance(result, ErrorResult)
            assert "Private key file not found" in result.message
        finally:
            os.unlink(cert_path)
    
    @pytest.mark.asyncio
    async def test_ssl_setup_cert_validation_failed(self, command):
        """Test SSL setup with certificate validation failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "test.crt")
            key_path = os.path.join(temp_dir, "test.key")
            
            # Create invalid certificate and key files
            with open(cert_path, 'w') as f:
                f.write("invalid cert content")
            with open(key_path, 'w') as f:
                f.write("invalid key content")
            
            ssl_config = {
                "enabled": True,
                "cert_file": cert_path,
                "key_file": key_path
            }
            
            result = await command.ssl_setup(ssl_config)
            
            assert isinstance(result, ErrorResult)
            assert "Certificate validation failed" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_setup_success(self, command):
        """Test successful SSL setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "test.crt")
            key_path = os.path.join(temp_dir, "test.key")
            
            # Create valid certificate and key files
            with open(cert_path, 'w') as f:
                f.write("valid cert content")
            with open(key_path, 'w') as f:
                f.write("valid key content")
            
            # Mock certificate validation to succeed
            with patch.object(command.auth_validator, 'validate_certificate') as mock_validate, \
                 patch.object(command, '_test_ssl_config') as mock_test:
                mock_validation = MagicMock()
                mock_validation.is_valid = True
                mock_validation.error_message = None
                mock_validate.return_value = mock_validation
                
                mock_test.return_value = {"success": True}
                
                ssl_config = {
                    "enabled": True,
                    "cert_file": cert_path,
                    "key_file": key_path
                }
                
                result = await command.ssl_setup(ssl_config)
                
                assert isinstance(result, SuccessResult)
                assert result.data["ssl_enabled"] is True
                assert result.data["cert_path"] == cert_path
                assert result.data["key_path"] == key_path
    
    @pytest.mark.asyncio
    async def test_ssl_status_disabled(self, command):
        """Test SSL status when SSL is disabled."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config.get.return_value = {"enabled": False}
            mock_config_class.return_value = mock_config
            
            result = await command.ssl_status()
            
            assert isinstance(result, SuccessResult)
            assert result.data["ssl_enabled"] is False
    
    @pytest.mark.asyncio
    async def test_ssl_status_enabled(self, command):
        """Test SSL status when SSL is enabled."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class, \
             patch('os.path.exists') as mock_exists, \
             patch.object(command.auth_validator, 'validate_certificate') as mock_validate:
            mock_config = MagicMock()
            mock_config.get.return_value = {
                "enabled": True,
                "cert_file": "/path/to/cert.pem",
                "key_file": "/path/to/key.pem"
            }
            mock_config_class.return_value = mock_config
            
            # Mock file existence
            mock_exists.return_value = True
            
            # Mock certificate validation
            mock_validation = MagicMock()
            mock_validation.is_valid = True
            mock_validation.error_message = None
            mock_validate.return_value = mock_validation
            
            result = await command.ssl_status()
            
            assert isinstance(result, SuccessResult)
            assert result.data["ssl_enabled"] is True
            assert result.data["cert_path"] == "/path/to/cert.pem"
            assert result.data["key_path"] == "/path/to/key.pem"
    
    @pytest.mark.asyncio
    async def test_ssl_test_missing_files(self, command):
        """Test SSL test with missing files."""
        result = await command.ssl_test("/nonexistent/cert.pem", "/nonexistent/key.pem")
        
        assert isinstance(result, ErrorResult)
        assert "Certificate file not found" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_test_missing_cert_file(self, command):
        """Test SSL test with missing certificate file."""
        with tempfile.NamedTemporaryFile(suffix=".key", delete=False) as key_file:
            key_file.write(b"test key content")
            key_path = key_file.name
        
        try:
            result = await command.ssl_test("/nonexistent/cert.pem", key_path)
            
            assert isinstance(result, ErrorResult)
            assert "Certificate file not found" in result.message
        finally:
            os.unlink(key_path)
    
    @pytest.mark.asyncio
    async def test_ssl_test_missing_key_file(self, command):
        """Test SSL test with missing key file."""
        with tempfile.NamedTemporaryFile(suffix=".crt", delete=False) as cert_file:
            cert_file.write(b"test cert content")
            cert_path = cert_file.name
        
        try:
            result = await command.ssl_test(cert_path, "/nonexistent/key.pem")
            
            assert isinstance(result, ErrorResult)
            assert "Private key file not found" in result.message
        finally:
            os.unlink(cert_path)
    
    @pytest.mark.asyncio
    async def test_ssl_test_success(self, command):
        """Test successful SSL test."""
        with tempfile.TemporaryDirectory() as temp_dir:
            cert_path = os.path.join(temp_dir, "test.crt")
            key_path = os.path.join(temp_dir, "test.key")
            
            # Create valid certificate and key files
            with open(cert_path, 'w') as f:
                f.write("valid cert content")
            with open(key_path, 'w') as f:
                f.write("valid key content")
            
            # Mock SSL test to succeed
            with patch('ssl.create_default_context') as mock_ssl_context:
                mock_context = MagicMock()
                mock_ssl_context.return_value = mock_context
                
                result = await command.ssl_test(cert_path, key_path)
                
                assert isinstance(result, SuccessResult)
                assert result.data["test_passed"] is True
    
    @pytest.mark.asyncio
    async def test_ssl_config_get(self, command):
        """Test SSL config get action."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config.get.return_value = {"enabled": True}
            mock_config_class.return_value = mock_config
            
            result = await command.ssl_config("get", {})
            
            assert isinstance(result, SuccessResult)
            assert result.data["ssl_config"]["enabled"] is True
    
    @pytest.mark.asyncio
    async def test_ssl_config_set(self, command):
        """Test SSL config set action."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            config_data = {"enabled": True, "cert_file": "/path/to/cert.pem"}
            result = await command.ssl_config("set", config_data)
            
            assert isinstance(result, SuccessResult)
            mock_config.update_config.assert_called_once_with({"ssl": config_data})
    
    @pytest.mark.asyncio
    async def test_ssl_config_update(self, command):
        """Test SSL config update action."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config.get.return_value = {"enabled": False}
            mock_config_class.return_value = mock_config
            
            config_data = {"enabled": True}
            result = await command.ssl_config("update", config_data)
            
            assert isinstance(result, SuccessResult)
            mock_config.update_config.assert_called_once_with({"ssl": {"enabled": True}})
    
    @pytest.mark.asyncio
    async def test_ssl_config_reset(self, command):
        """Test SSL config reset action."""
        with patch('mcp_proxy_adapter.config.Config') as mock_config_class:
            mock_config = MagicMock()
            mock_config_class.return_value = mock_config
            
            result = await command.ssl_config("reset", {})
            
            assert isinstance(result, SuccessResult)
            mock_config.update_config.assert_called_once_with({"ssl": {"enabled": False, "cert_file": None, "key_file": None, "ca_file": None, "verify_mode": "CERT_REQUIRED", "cipher_suites": []}})
    
    @pytest.mark.asyncio
    async def test_ssl_config_unknown_action(self, command):
        """Test SSL config with unknown action."""
        result = await command.ssl_config("unknown_action", {})
        
        assert isinstance(result, ErrorResult)
        assert "Unknown action" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_config_invalid_data(self, command):
        """Test SSL config with invalid data."""
        result = await command.ssl_config("set", "invalid_data")
        
        assert isinstance(result, ErrorResult)
        assert "Configuration data must be a dictionary" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_setup_exception_handling(self, command):
        """Test SSL setup exception handling."""
        with patch.object(command.certificate_utils, 'create_ssl_context', side_effect=Exception("Test exception")):
            ssl_config = {"enabled": True}
            
            result = await command.ssl_setup(ssl_config)
            
            assert isinstance(result, ErrorResult)
            assert "Certificate and key files are required when SSL is enabled" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_status_exception_handling(self, command):
        """Test SSL status exception handling."""
        with patch('mcp_proxy_adapter.config.Config', side_effect=Exception("Test exception")):
            result = await command.ssl_status()
            
            assert isinstance(result, ErrorResult)
            assert "SSL status check failed" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_test_exception_handling(self, command):
        """Test SSL test exception handling."""
        with patch('ssl.create_default_context', side_effect=Exception("Test exception")):
            result = await command.ssl_test("/test/cert.pem", "/test/key.pem")
            
            assert isinstance(result, ErrorResult)
            assert "Certificate file not found" in result.message
    
    @pytest.mark.asyncio
    async def test_ssl_config_exception_handling(self, command):
        """Test SSL config exception handling."""
        with patch('mcp_proxy_adapter.config.Config', side_effect=Exception("Test exception")):
            result = await command.ssl_config("get", {})
            
            assert isinstance(result, ErrorResult)
            assert "SSL config action failed" in result.message 