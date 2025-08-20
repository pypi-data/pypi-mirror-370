"""
Tests for Certificate Management Command

Tests certificate creation, validation, revocation, and information retrieval.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from mcp_proxy_adapter.commands.certificate_management_command import CertificateManagementCommand, CertificateResult
from mcp_proxy_adapter.commands.result import CommandResult


class TestCertificateResult:
    """Test CertificateResult class."""
    
    def test_certificate_result_initialization(self):
        """Test CertificateResult initialization."""
        result = CertificateResult(
            cert_path="/path/to/cert.pem",
            cert_type="server",
            common_name="test.example.com",
            roles=["admin", "user"],
            status="valid"
        )
        
        assert result.cert_path == "/path/to/cert.pem"
        assert result.cert_type == "server"
        assert result.common_name == "test.example.com"
        assert result.roles == ["admin", "user"]
        assert result.status == "valid"
        assert result.error is None
    
    def test_certificate_result_to_dict(self):
        """Test CertificateResult to_dict method."""
        result = CertificateResult(
            cert_path="/path/to/cert.pem",
            cert_type="client",
            common_name="client.example.com",
            roles=["user"],
            expiry_date="2024-12-31T23:59:59",
            serial_number="123456789",
            status="valid"
        )
        
        data = result.to_dict()
        
        assert data["cert_path"] == "/path/to/cert.pem"
        assert data["cert_type"] == "client"
        assert data["common_name"] == "client.example.com"
        assert data["roles"] == ["user"]
        assert data["expiry_date"] == "2024-12-31T23:59:59"
        assert data["serial_number"] == "123456789"
        assert data["status"] == "valid"
    
    def test_certificate_result_get_schema(self):
        """Test CertificateResult get_schema method."""
        result = CertificateResult(
            cert_path="/path/to/cert.pem",
            cert_type="CA",
            common_name="ca.example.com",
            status="valid"
        )
        schema = result.get_schema()
        
        assert schema["type"] == "object"
        assert "cert_path" in schema["properties"]
        assert "cert_type" in schema["properties"]
        assert "common_name" in schema["properties"]
        assert "status" in schema["properties"]


class TestCertificateManagementCommand:
    """Test CertificateManagementCommand class."""
    
    @pytest.fixture
    def cert_command(self):
        """Create CertificateManagementCommand instance."""
        return CertificateManagementCommand()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_cert_files(self, temp_dir):
        """Create mock certificate files."""
        ca_cert_file = os.path.join(temp_dir, "ca.crt")
        ca_key_file = os.path.join(temp_dir, "ca.key")
        
        # Create mock files
        with open(ca_cert_file, 'w') as f:
            f.write("MOCK CA CERTIFICATE")
        with open(ca_key_file, 'w') as f:
            f.write("MOCK CA PRIVATE KEY")
        
        return ca_cert_file, ca_key_file
    
    @pytest.mark.asyncio
    async def test_cert_create_ca_invalid_common_name(self, cert_command, temp_dir):
        """Test CA certificate creation with invalid common name."""
        result = await cert_command.cert_create_ca("", temp_dir)
        
        assert result.to_dict()["success"] is False
        assert "Common name cannot be empty" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_ca_invalid_validity_days(self, cert_command, temp_dir):
        """Test CA certificate creation with invalid validity days."""
        result = await cert_command.cert_create_ca("test-ca", temp_dir, validity_days=0)
        
        assert result.to_dict()["success"] is False
        assert "Validity days must be positive" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_ca_invalid_key_size(self, cert_command, temp_dir):
        """Test CA certificate creation with invalid key size."""
        result = await cert_command.cert_create_ca("test-ca", temp_dir, key_size=512)
        
        assert result.to_dict()["success"] is False
        assert "Key size must be at least 1024 bits" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_ca_success(self, cert_command, temp_dir):
        """Test successful CA certificate creation."""
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.create_ca_certificate.return_value = {
            "cert_path": os.path.join(temp_dir, "ca.crt"),
            "key_path": os.path.join(temp_dir, "ca.key")
        }
        cert_command.certificate_utils = mock_utils
        
        # Mock successful validation
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_certificate.return_value = mock_validation_result
        cert_command.auth_validator = mock_validator
        
        result = await cert_command.cert_create_ca("test-ca", temp_dir)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["cert_type"] == "CA"
        assert result.data["certificate"]["common_name"] == "test-ca"
        assert result.data["certificate"]["status"] == "valid"
    
    @pytest.mark.asyncio
    async def test_cert_create_server_invalid_common_name(self, cert_command, mock_cert_files):
        """Test server certificate creation with invalid common name."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_server("", ["admin"], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "Common name cannot be empty" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_no_roles(self, cert_command, mock_cert_files):
        """Test server certificate creation with no roles."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_server("test-server", [], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "At least one role must be specified" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_invalid_roles(self, cert_command, mock_cert_files):
        """Test server certificate creation with invalid roles."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        # Mock role validation failure
        mock_role_utils_instance = Mock()
        mock_role_utils_instance.validate_roles.return_value = False
        cert_command.role_utils = mock_role_utils_instance
        
        result = await cert_command.cert_create_server("test-server", ["invalid-role"], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "Invalid roles specified" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_missing_ca_cert(self, cert_command, mock_cert_files):
        """Test server certificate creation with missing CA certificate."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_server("test-server", ["admin"], "/nonexistent/ca.crt", ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "CA certificate not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_missing_ca_key(self, cert_command, mock_cert_files):
        """Test server certificate creation with missing CA key."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_server("test-server", ["admin"], ca_cert_file, "/nonexistent/ca.key", "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "CA private key not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_success(self, cert_command, mock_cert_files, temp_dir):
        """Test successful server certificate creation."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        # Mock role validation success
        mock_role_utils_instance = Mock()
        mock_role_utils_instance.validate_roles.return_value = True
        cert_command.role_utils = mock_role_utils_instance
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.create_server_certificate.return_value = {
            "cert_path": os.path.join(temp_dir, "server.crt"),
            "key_path": os.path.join(temp_dir, "server.key")
        }
        cert_command.certificate_utils = mock_utils
        
        # Mock successful validation
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_certificate.return_value = mock_validation_result
        cert_command.auth_validator = mock_validator
        
        result = await cert_command.cert_create_server("test-server", ["admin"], ca_cert_file, ca_key_file, temp_dir)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["cert_type"] == "server"
        assert result.data["certificate"]["common_name"] == "test-server"
        assert result.data["certificate"]["roles"] == ["admin"]
        assert result.data["certificate"]["status"] == "valid"
    
    @pytest.mark.asyncio
    async def test_cert_create_client_invalid_common_name(self, cert_command, mock_cert_files):
        """Test client certificate creation with invalid common name."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_client("", ["user"], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "Common name cannot be empty" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_client_no_roles(self, cert_command, mock_cert_files):
        """Test client certificate creation with no roles."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        result = await cert_command.cert_create_client("test-client", [], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "At least one role must be specified" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_client_success(self, cert_command, mock_cert_files, temp_dir):
        """Test successful client certificate creation."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        # Mock role validation success
        mock_role_utils_instance = Mock()
        mock_role_utils_instance.validate_roles.return_value = True
        cert_command.role_utils = mock_role_utils_instance
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.create_client_certificate.return_value = {
            "cert_path": os.path.join(temp_dir, "client.crt"),
            "key_path": os.path.join(temp_dir, "client.key")
        }
        cert_command.certificate_utils = mock_utils
        
        # Mock successful validation
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validator.validate_certificate.return_value = mock_validation_result
        cert_command.auth_validator = mock_validator
        
        result = await cert_command.cert_create_client("test-client", ["user"], ca_cert_file, ca_key_file, temp_dir)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["cert_type"] == "client"
        assert result.data["certificate"]["common_name"] == "test-client"
        assert result.data["certificate"]["roles"] == ["user"]
        assert result.data["certificate"]["status"] == "valid"
    
    @pytest.mark.asyncio
    async def test_cert_revoke_missing_file(self, cert_command):
        """Test certificate revocation with missing file."""
        result = await cert_command.cert_revoke("/nonexistent/cert.pem")
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.certificate_management_command.CertificateUtils')
    async def test_cert_revoke_cannot_read_info(self, mock_cert_utils, cert_command, mock_cert_files):
        """Test certificate revocation when cannot read certificate info."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils to return None
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = None
        mock_cert_utils.return_value = mock_utils
        
        result = await cert_command.cert_revoke(ca_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Could not read certificate information" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.certificate_management_command.CertificateUtils')
    async def test_cert_revoke_success(self, mock_cert_utils, cert_command, mock_cert_files):
        """Test successful certificate revocation."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test-server",
            "roles": ["admin"],
            "serial_number": "123456789"
        }
        mock_utils.revoke_certificate.return_value = {"revoked": True}
        mock_cert_utils.return_value = mock_utils
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_revoke(ca_cert_file)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["status"] == "revoked"
        assert result.data["certificate"]["cert_type"] == "server"
        assert result.data["certificate"]["common_name"] == "test-server"
    
    @pytest.mark.asyncio
    async def test_cert_list_missing_directory(self, cert_command):
        """Test certificate listing with missing directory."""
        result = await cert_command.cert_list("/nonexistent/dir")
        
        assert result.to_dict()["success"] is False
        assert "Directory not found" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_list_not_directory(self, cert_command, mock_cert_files):
        """Test certificate listing with path that is not a directory."""
        ca_cert_file, _ = mock_cert_files
        
        result = await cert_command.cert_list(ca_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Path is not a directory" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.certificate_management_command.CertificateUtils')
    async def test_cert_list_success(self, mock_cert_utils, cert_command, temp_dir):
        """Test successful certificate listing."""
        # Create some mock certificate files
        cert_files = [
            os.path.join(temp_dir, "cert1.crt"),
            os.path.join(temp_dir, "cert2.pem"),
            os.path.join(temp_dir, "cert3.cer")
        ]
        
        for cert_file in cert_files:
            with open(cert_file, 'w') as f:
                f.write("MOCK CERTIFICATE")
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = lambda path: {
            "type": "server",
            "common_name": f"test-{os.path.basename(path)}",
            "roles": ["admin"],
            "expiry_date": "2024-12-31T23:59:59",
            "serial_number": "123456789",
            "status": "valid"
        }
        mock_cert_utils.return_value = mock_utils
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_list(temp_dir)
        
        assert result.to_dict()["success"] is True
        assert "certificates" in result.data
        assert len(result.data["certificates"]) == 3
        assert result.data["total_count"] == 3
        assert result.data["directory"] == temp_dir
    
    @pytest.mark.asyncio
    async def test_cert_info_missing_file(self, cert_command):
        """Test certificate info with missing file."""
        result = await cert_command.cert_info("/nonexistent/cert.pem")
        
        assert result.to_dict()["success"] is False
        assert "Certificate file not found" in result.error
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.certificate_management_command.CertificateUtils')
    @patch('mcp_proxy_adapter.commands.certificate_management_command.AuthValidator')
    async def test_cert_info_success(self, mock_auth_validator, mock_cert_utils, cert_command, mock_cert_files):
        """Test successful certificate info retrieval."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test-server",
            "roles": ["admin"],
            "expiry_date": "2024-12-31T23:59:59",
            "serial_number": "123456789"
        }
        mock_cert_utils.return_value = mock_utils
        cert_command.certificate_utils = mock_utils
        
        # Mock successful validation
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = True
        mock_validation_result.error_code = None
        mock_validation_result.error_message = None
        mock_validation_result.roles = ["admin"]
        mock_validator.validate_certificate.return_value = mock_validation_result
        mock_auth_validator.return_value = mock_validator
        cert_command.auth_validator = mock_validator
        
        result = await cert_command.cert_info(ca_cert_file)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["cert_type"] == "server"
        assert result.data["certificate"]["common_name"] == "test-server"
        assert result.data["certificate"]["status"] == "valid"
        assert "validation" in result.data
        assert result.data["validation"]["is_valid"] is True
    
    @pytest.mark.asyncio
    @patch('mcp_proxy_adapter.commands.certificate_management_command.CertificateUtils')
    @patch('mcp_proxy_adapter.commands.certificate_management_command.AuthValidator')
    async def test_cert_info_validation_failed(self, mock_auth_validator, mock_cert_utils, cert_command, mock_cert_files):
        """Test certificate info with validation failure."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils
        mock_utils = Mock()
        mock_utils.get_certificate_info.return_value = {
            "type": "server",
            "common_name": "test-server",
            "roles": ["admin"]
        }
        mock_cert_utils.return_value = mock_utils
        cert_command.certificate_utils = mock_utils
        
        # Mock validation failure
        mock_validator = Mock()
        mock_validation_result = Mock()
        mock_validation_result.is_valid = False
        mock_validation_result.error_code = -32003
        mock_validation_result.error_message = "Certificate validation failed"
        mock_validation_result.roles = []
        mock_validator.validate_certificate.return_value = mock_validation_result
        mock_auth_validator.return_value = mock_validator
        cert_command.auth_validator = mock_validator
        
        result = await cert_command.cert_info(ca_cert_file)
        
        assert result.to_dict()["success"] is True
        assert "certificate" in result.data
        assert result.data["certificate"]["status"] == "error"
        assert result.data["certificate"]["error"] == "Certificate validation failed"
        assert result.data["validation"]["is_valid"] is False
    
    @pytest.mark.asyncio
    async def test_cert_create_ca_exception_handling(self, cert_command, temp_dir):
        """Test CA certificate creation exception handling."""
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.create_ca_certificate.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_create_ca("test-ca", temp_dir)
        
        assert result.to_dict()["success"] is False
        assert "CA certificate creation failed" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_server_exception_handling(self, cert_command, mock_cert_files):
        """Test server certificate creation exception handling."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        # Mock role validation success
        mock_role_utils_instance = Mock()
        mock_role_utils_instance.validate_roles.return_value = True
        cert_command.role_utils = mock_role_utils_instance
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.create_server_certificate.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_create_server("test-server", ["admin"], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "Server certificate creation failed" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_create_client_exception_handling(self, cert_command, mock_cert_files):
        """Test client certificate creation exception handling."""
        ca_cert_file, ca_key_file = mock_cert_files
        
        # Mock role validation success
        mock_role_utils_instance = Mock()
        mock_role_utils_instance.validate_roles.return_value = True
        cert_command.role_utils = mock_role_utils_instance
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.create_client_certificate.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_create_client("test-client", ["user"], ca_cert_file, ca_key_file, "/tmp")
        
        assert result.to_dict()["success"] is False
        assert "Client certificate creation failed" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_revoke_exception_handling(self, cert_command, mock_cert_files):
        """Test certificate revocation exception handling."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_revoke(ca_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Certificate revocation failed" in result.error
    
    @pytest.mark.asyncio
    async def test_cert_list_exception_handling(self, cert_command, temp_dir):
        """Test certificate listing exception handling."""
        # Create some mock certificate files
        cert_files = [
            os.path.join(temp_dir, "cert1.crt"),
            os.path.join(temp_dir, "cert2.pem")
        ]
        
        for cert_file in cert_files:
            with open(cert_file, 'w') as f:
                f.write("MOCK CERTIFICATE")
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_list(temp_dir)
        
        assert result.to_dict()["success"] is True
        assert "certificates" in result.data
        assert len(result.data["certificates"]) == 2
        # Check that both certificates have error status
        for cert in result.data["certificates"]:
            assert cert["status"] == "error"
            assert "Test exception" in cert["error"]
    
    @pytest.mark.asyncio
    async def test_cert_info_exception_handling(self, cert_command, mock_cert_files):
        """Test certificate info exception handling."""
        ca_cert_file, _ = mock_cert_files
        
        # Mock certificate utils to raise exception
        mock_utils = Mock()
        mock_utils.get_certificate_info.side_effect = Exception("Test exception")
        cert_command.certificate_utils = mock_utils
        
        result = await cert_command.cert_info(ca_cert_file)
        
        assert result.to_dict()["success"] is False
        assert "Certificate info retrieval failed" in result.error 