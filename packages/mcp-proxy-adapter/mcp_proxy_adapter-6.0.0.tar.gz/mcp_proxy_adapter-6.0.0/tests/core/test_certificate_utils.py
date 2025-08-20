"""
Tests for CertificateUtils module.

Tests certificate creation, validation, and role extraction functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from mcp_proxy_adapter.core.certificate_utils import CertificateUtils
from mcp_proxy_adapter.core.auth_validator import AuthValidator
from mcp_proxy_adapter.core.role_utils import RoleUtils


class TestCertificateUtils:
    """Test cases for CertificateUtils class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def sample_ca_cert(self, temp_dir):
        """Create sample CA certificate for testing."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "Test CA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc)
        ).not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=True,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                encipher_only=False,
                decipher_only=False,
                content_commitment=False
            ),
            critical=True
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_path = os.path.join(temp_dir, "ca.crt")
        key_path = os.path.join(temp_dir, "ca.key")
        
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        return {
            "cert_path": cert_path,
            "key_path": key_path,
            "cert": cert,
            "key": private_key
        }
    
    def test_create_ca_certificate_success(self, temp_dir):
        """Test successful CA certificate creation."""
        result = CertificateUtils.create_ca_certificate(
            common_name="Test CA",
            output_dir=temp_dir,
            validity_days=365,
            key_size=2048
        )
        
        assert result["common_name"] == "Test CA"
        assert result["validity_days"] == 365
        assert os.path.exists(result["cert_path"])
        assert os.path.exists(result["key_path"])
        
        # Verify certificate can be loaded
        with open(result["cert_path"], "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
        
        assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "Test CA"
    
    def test_create_ca_certificate_invalid_parameters(self, temp_dir):
        """Test CA certificate creation with invalid parameters."""
        # Empty common name
        with pytest.raises(ValueError, match="Common name cannot be empty"):
            CertificateUtils.create_ca_certificate("", temp_dir)
        
        # Invalid validity days
        with pytest.raises(ValueError, match="Validity days must be positive"):
            CertificateUtils.create_ca_certificate("Test CA", temp_dir, validity_days=0)
        
        # Invalid key size
        with pytest.raises(ValueError, match="Key size must be at least 1024 bits"):
            CertificateUtils.create_ca_certificate("Test CA", temp_dir, key_size=512)
    
    def test_create_server_certificate_success(self, temp_dir, sample_ca_cert):
        """Test successful server certificate creation."""
        result = CertificateUtils.create_server_certificate(
            common_name="test-server.example.com",
            roles=["server", "admin"],
            ca_cert_path=sample_ca_cert["cert_path"],
            ca_key_path=sample_ca_cert["key_path"],
            output_dir=temp_dir
        )
        
        assert result["common_name"] == "test-server.example.com"
        assert result["roles"] == ["server", "admin"]
        assert os.path.exists(result["cert_path"])
        assert os.path.exists(result["key_path"])
        
        # Verify certificate can be loaded
        with open(result["cert_path"], "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
        
        assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "test-server.example.com"
    
    def test_create_server_certificate_ca_not_found(self, temp_dir):
        """Test server certificate creation with non-existent CA."""
        with pytest.raises(FileNotFoundError):
            CertificateUtils.create_server_certificate(
                common_name="test-server.example.com",
                roles=["server"],
                ca_cert_path="/nonexistent/ca.crt",
                ca_key_path="/nonexistent/ca.key",
                output_dir=temp_dir
            )
    
    def test_create_client_certificate_success(self, temp_dir, sample_ca_cert):
        """Test successful client certificate creation."""
        result = CertificateUtils.create_client_certificate(
            common_name="test-client",
            roles=["client", "user"],
            ca_cert_path=sample_ca_cert["cert_path"],
            ca_key_path=sample_ca_cert["key_path"],
            output_dir=temp_dir
        )
        
        assert result["common_name"] == "test-client"
        assert result["roles"] == ["client", "user"]
        assert os.path.exists(result["cert_path"])
        assert os.path.exists(result["key_path"])
        
        # Verify certificate can be loaded
        with open(result["cert_path"], "rb") as f:
            cert = x509.load_pem_x509_certificate(f.read())
        
        assert cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == "test-client"
    
    def test_create_client_certificate_ca_not_found(self, temp_dir):
        """Test client certificate creation with non-existent CA."""
        with pytest.raises(FileNotFoundError):
            CertificateUtils.create_client_certificate(
                common_name="test-client",
                roles=["client"],
                ca_cert_path="/nonexistent/ca.crt",
                ca_key_path="/nonexistent/ca.key",
                output_dir=temp_dir
            )
    
    @patch('mcp_proxy_adapter.core.certificate_utils.RoleUtils')
    def test_extract_roles_from_certificate(self, mock_role_utils, temp_dir, sample_ca_cert):
        """Test role extraction from certificate file."""
        mock_role_utils.extract_roles_from_certificate.return_value = ["admin", "user"]
        
        result = CertificateUtils.extract_roles_from_certificate(sample_ca_cert["cert_path"])
        
        assert result == ["admin", "user"]
        mock_role_utils.extract_roles_from_certificate.assert_called_once_with(sample_ca_cert["cert_path"])
    
    @patch('mcp_proxy_adapter.core.certificate_utils.RoleUtils')
    def test_extract_roles_from_certificate_object(self, mock_role_utils):
        """Test role extraction from certificate object."""
        mock_cert = Mock()
        mock_role_utils.extract_roles_from_certificate_object.return_value = ["admin", "user"]
        
        result = CertificateUtils.extract_roles_from_certificate_object(mock_cert)
        
        assert result == ["admin", "user"]
        mock_role_utils.extract_roles_from_certificate_object.assert_called_once_with(mock_cert)
    
    @patch('mcp_proxy_adapter.core.certificate_utils.CertificateUtils.validate_certificate_chain')
    def test_validate_certificate_chain_success(self, mock_validate, temp_dir, sample_ca_cert):
        """Test certificate chain validation success."""
        mock_validate.return_value = True
        
        result = CertificateUtils.validate_certificate_chain(
            sample_ca_cert["cert_path"], sample_ca_cert["cert_path"]
        )
        
        assert result is True
        mock_validate.assert_called_once()
    
    @patch('mcp_proxy_adapter.core.certificate_utils.CertificateUtils.validate_certificate_chain')
    def test_validate_certificate_chain_failure(self, mock_validate, temp_dir, sample_ca_cert):
        """Test certificate chain validation failure."""
        mock_validate.return_value = False
        
        result = CertificateUtils.validate_certificate_chain(
            sample_ca_cert["cert_path"], sample_ca_cert["cert_path"]
        )
        
        assert result is False
    
    @patch('mcp_proxy_adapter.core.certificate_utils.AuthValidator')
    def test_validate_certificate_success(self, mock_auth_validator, temp_dir, sample_ca_cert):
        """Test certificate validation success."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_validator.validate_certificate.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        result = CertificateUtils.validate_certificate(sample_ca_cert["cert_path"])
        
        assert result is True
        mock_validator.validate_certificate.assert_called_once_with(sample_ca_cert["cert_path"])
    
    @patch('mcp_proxy_adapter.core.certificate_utils.AuthValidator')
    def test_validate_certificate_failure(self, mock_auth_validator, temp_dir, sample_ca_cert):
        """Test certificate validation failure."""
        mock_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = False
        mock_validator.validate_certificate.return_value = mock_result
        mock_auth_validator.return_value = mock_validator
        
        result = CertificateUtils.validate_certificate(sample_ca_cert["cert_path"])
        
        assert result is False
    
    def test_get_certificate_info_success(self, temp_dir, sample_ca_cert):
        """Test getting certificate information."""
        result = CertificateUtils.get_certificate_info(sample_ca_cert["cert_path"])
        
        assert "subject" in result
        assert "issuer" in result
        assert "serial_number" in result
        assert "not_valid_before" in result
        assert "not_valid_after" in result
        assert "roles" in result
        assert "is_ca" in result
        assert result["is_ca"] is True
    
    def test_get_certificate_info_file_not_found(self, temp_dir):
        """Test getting certificate information for non-existent file."""
        result = CertificateUtils.get_certificate_info("/nonexistent/cert.crt")
        
        assert result == {}
    
    def test_create_certificates_with_roles(self, temp_dir):
        """Test creating certificates with role extensions."""
        # Create CA
        ca_result = CertificateUtils.create_ca_certificate("Test CA", temp_dir)
        
        # Create server certificate with roles
        server_result = CertificateUtils.create_server_certificate(
            common_name="test-server",
            roles=["server", "admin"],
            ca_cert_path=ca_result["cert_path"],
            ca_key_path=ca_result["key_path"],
            output_dir=temp_dir
        )
        
        # Create client certificate with roles
        client_result = CertificateUtils.create_client_certificate(
            common_name="test-client",
            roles=["client", "user"],
            ca_cert_path=ca_result["cert_path"],
            ca_key_path=ca_result["key_path"],
            output_dir=temp_dir
        )
        
        # Verify all certificates were created
        assert os.path.exists(server_result["cert_path"])
        assert os.path.exists(client_result["cert_path"])
        
        # Verify roles were set
        assert server_result["roles"] == ["server", "admin"]
        assert client_result["roles"] == ["client", "user"]
    
    def test_create_certificates_default_roles(self, temp_dir):
        """Test creating certificates with default roles."""
        # Create CA
        ca_result = CertificateUtils.create_ca_certificate("Test CA", temp_dir)
        
        # Create server certificate without specifying roles
        server_result = CertificateUtils.create_server_certificate(
            common_name="test-server",
            roles=[],  # Empty roles list
            ca_cert_path=ca_result["cert_path"],
            ca_key_path=ca_result["key_path"],
            output_dir=temp_dir
        )
        
        # Create client certificate without specifying roles
        client_result = CertificateUtils.create_client_certificate(
            common_name="test-client",
            roles=[],  # Empty roles list
            ca_cert_path=ca_result["cert_path"],
            ca_key_path=ca_result["key_path"],
            output_dir=temp_dir
        )
        
        # Verify default roles were set
        assert server_result["roles"] == ["server"]
        assert client_result["roles"] == ["client"] 