"""
Unit tests for CertificateManager.

Tests for certificate creation, validation, and revocation functionality.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from mcp_security.certificate_manager import CertificateManager
from mcp_security.schemas.models import RolesSchema


class TestCertificateManager:
    """Test cases for CertificateManager."""
    
    def test_init(self, temp_dir):
        """Test CertificateManager initialization."""
        cert_manager = CertificateManager(str(temp_dir))
        
        assert cert_manager.ca_dir == temp_dir
        assert cert_manager.ca_cert_path == temp_dir / "ca.crt"
        assert cert_manager.ca_key_path == temp_dir / "ca.key"
        assert cert_manager.crl_path == temp_dir / "crl.pem"
        assert cert_manager.cert_db_path == temp_dir / "certificates.json"
        assert cert_manager.cert_db == {"certificates": [], "revoked": []}
    
    @patch('mcp_security.certificate_manager.rsa.generate_private_key')
    @patch('mcp_security.certificate_manager.x509.CertificateBuilder')
    def test_create_root_ca(self, mock_cert_builder, mock_generate_key, temp_dir):
        """Test creating root CA certificate."""
        # Mock the certificate building process
        mock_key = Mock()
        mock_generate_key.return_value = mock_key
        mock_key.public_key.return_value = Mock()
        
        mock_builder = Mock()
        mock_cert_builder.return_value = mock_builder
        mock_builder.subject_name.return_value = mock_builder
        mock_builder.issuer_name.return_value = mock_builder
        mock_builder.public_key.return_value = mock_builder
        mock_builder.serial_number.return_value = mock_builder
        mock_builder.not_valid_before.return_value = mock_builder
        mock_builder.not_valid_after.return_value = mock_builder
        mock_builder.add_extension.return_value = mock_builder
        mock_builder.sign.return_value = Mock()
        
        cert_manager = CertificateManager(str(temp_dir))
        
        with patch('builtins.open', mock_open()) as mock_file:
            cert_pem, key_pem = cert_manager.create_root_ca(
                common_name="Test CA",
                organization="Test Org"
            )
        
        assert isinstance(cert_pem, str)
        assert isinstance(key_pem, str)
        mock_generate_key.assert_called_once()
        mock_cert_builder.assert_called_once()
    
    def test_create_client_certificate_no_ca(self, temp_dir):
        """Test creating client certificate without CA."""
        cert_manager = CertificateManager(str(temp_dir))
        
        with pytest.raises(RuntimeError, match="CA certificate and key not found"):
            cert_manager.create_client_certificate(
                common_name="test_user",
                roles=["user"],
                permissions=["read"]
            )
    
    @patch('mcp_security.certificate_manager.rsa.generate_private_key')
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    @patch('mcp_security.certificate_manager.load_pem_private_key')
    @patch('mcp_security.certificate_manager.x509.CertificateBuilder')
    def test_create_client_certificate(
        self, mock_cert_builder, mock_load_key, mock_load_cert, mock_generate_key, temp_dir
    ):
        """Test creating client certificate."""
        # Create CA files first
        ca_cert_file = temp_dir / "ca.crt"
        ca_key_file = temp_dir / "ca.key"
        ca_cert_file.write_text("fake ca cert")
        ca_key_file.write_text("fake ca key")
        
        # Mock certificate building
        mock_key = Mock()
        mock_generate_key.return_value = mock_key
        mock_key.public_key.return_value = Mock()
        
        mock_ca_cert = Mock()
        mock_load_cert.return_value = mock_ca_cert
        mock_ca_cert.subject = Mock()
        
        mock_ca_key = Mock()
        mock_load_key.return_value = mock_ca_key
        mock_ca_key.public_key.return_value = Mock()
        
        mock_builder = Mock()
        mock_cert_builder.return_value = mock_builder
        mock_builder.subject_name.return_value = mock_builder
        mock_builder.issuer_name.return_value = mock_builder
        mock_builder.public_key.return_value = mock_builder
        mock_builder.serial_number.return_value = mock_builder
        mock_builder.not_valid_before.return_value = mock_builder
        mock_builder.not_valid_after.return_value = mock_builder
        mock_builder.add_extension.return_value = mock_builder
        mock_builder.sign.return_value = Mock()
        
        cert_manager = CertificateManager(str(temp_dir))
        
        with patch('builtins.open', mock_open()) as mock_file:
            cert_pem, key_pem = cert_manager.create_client_certificate(
                common_name="test_user",
                roles=["user"],
                permissions=["read"]
            )
        
        assert isinstance(cert_pem, str)
        assert isinstance(key_pem, str)
    
    def test_revoke_certificate_not_found(self, temp_dir):
        """Test revoking non-existent certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        success = cert_manager.revoke_certificate("123456789")
        assert success is False
    
    def test_revoke_certificate_success(self, temp_dir):
        """Test successful certificate revocation."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Add a certificate to the database
        cert_info = {
            "serial_number": "123456789",
            "common_name": "test_user",
            "roles": ["user"],
            "permissions": ["read"],
            "created": "2023-01-01T00:00:00",
            "valid_until": "2024-01-01T00:00:00",
            "revoked": False
        }
        cert_manager.cert_db["certificates"].append(cert_info)
        
        with patch.object(cert_manager, '_update_crl'):
            success = cert_manager.revoke_certificate("123456789", "test reason")
        
        assert success is True
        assert len(cert_manager.cert_db["certificates"]) == 0
        assert len(cert_manager.cert_db["revoked"]) == 1
        assert cert_manager.cert_db["revoked"][0]["revoked"] is True
        assert cert_manager.cert_db["revoked"][0]["revocation_reason"] == "test reason"
    
    def test_get_certificate_info_not_found(self, temp_dir):
        """Test getting info for non-existent certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        info = cert_manager.get_certificate_info("123456789")
        assert info is None
    
    def test_get_certificate_info_found(self, temp_dir):
        """Test getting info for existing certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        cert_info = {
            "serial_number": "123456789",
            "common_name": "test_user",
            "roles": ["user"],
            "permissions": ["read"]
        }
        cert_manager.cert_db["certificates"].append(cert_info)
        
        info = cert_manager.get_certificate_info("123456789")
        assert info == cert_info
    
    def test_list_certificates(self, temp_dir):
        """Test listing certificates."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Add some certificates
        cert_manager.cert_db["certificates"].append({
            "serial_number": "123",
            "common_name": "user1"
        })
        cert_manager.cert_db["revoked"].append({
            "serial_number": "456",
            "common_name": "user2",
            "revoked": True
        })
        
        # Test without revoked
        certs = cert_manager.list_certificates(include_revoked=False)
        assert len(certs) == 1
        assert certs[0]["serial_number"] == "123"
        
        # Test with revoked
        certs = cert_manager.list_certificates(include_revoked=True)
        assert len(certs) == 2
    
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate(self, mock_load_cert, temp_dir):
        """Test extracting roles from certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Mock certificate with custom extension
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid = cert_manager.MCP_ROLE_OID
        mock_extension.value = b"admin,user"
        mock_cert.extensions = [mock_extension]
        
        mock_load_cert.return_value = mock_cert
        
        roles = cert_manager.extract_roles_from_certificate("fake cert pem")
        assert roles == ["admin", "user"]
    
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    def test_extract_permissions_from_certificate(self, mock_load_cert, temp_dir):
        """Test extracting permissions from certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Mock certificate with custom extension
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid = cert_manager.MCP_PERMISSIONS_OID
        mock_extension.value = b"read,write"
        mock_cert.extensions = [mock_extension]
        
        mock_load_cert.return_value = mock_cert
        
        permissions = cert_manager.extract_permissions_from_certificate("fake cert pem")
        assert permissions == ["read", "write"]
    
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    def test_extract_server_role_from_certificate(self, mock_load_cert, temp_dir):
        """Test extracting server role from certificate."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Mock certificate with custom extension
        mock_cert = Mock()
        mock_extension = Mock()
        mock_extension.oid = cert_manager.MCP_SERVER_ROLE_OID
        mock_extension.value = b"kubernetes_manager"
        mock_cert.extensions = [mock_extension]
        
        mock_load_cert.return_value = mock_cert
        
        server_role = cert_manager.extract_server_role_from_certificate("fake cert pem")
        assert server_role == "kubernetes_manager"
    
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    def test_verify_certificate_no_ca(self, mock_load_cert, temp_dir):
        """Test verifying certificate without CA."""
        cert_manager = CertificateManager(str(temp_dir))
        
        is_valid = cert_manager.verify_certificate("fake cert pem")
        assert is_valid is False
    
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate')
    @patch('mcp_security.certificate_manager.x509.load_pem_x509_crl')
    def test_verify_certificate_with_crl(self, mock_load_crl, mock_load_cert, temp_dir):
        """Test verifying certificate with CRL."""
        # Create CA file
        ca_cert_file = temp_dir / "ca.crt"
        ca_cert_file.write_text("fake ca cert")
        
        cert_manager = CertificateManager(str(temp_dir))
        
        # Mock certificate
        mock_cert = Mock()
        mock_cert.serial_number = 123456789
        mock_cert.signature = b"fake signature"
        mock_cert.tbs_certificate_bytes = b"fake tbs"
        mock_cert.signature_hash_algorithm = Mock()
        mock_cert.not_valid_before = Mock()
        mock_cert.not_valid_after = Mock()
        
        mock_load_cert.return_value = mock_cert
        
        # Mock CA certificate
        mock_ca_cert = Mock()
        mock_ca_cert.public_key.return_value = Mock()
        mock_ca_cert.public_key.return_value.verify = Mock()
        
        with patch('builtins.open', mock_open(read_data="fake ca cert")):
            with patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate') as mock_load_ca:
                mock_load_ca.return_value = mock_ca_cert
                
                # Mock CRL
                mock_crl = Mock()
                mock_revoked_cert = Mock()
                mock_revoked_cert.serial_number = 123456789
                mock_crl.__iter__.return_value = [mock_revoked_cert]
                mock_load_crl.return_value = mock_crl
                
                # Create CRL file
                crl_file = temp_dir / "crl.pem"
                crl_file.write_text("fake crl")
                
                with patch('builtins.open', mock_open(read_data="fake crl")):
                    is_valid = cert_manager.verify_certificate("fake cert pem")
                    assert is_valid is False  # Certificate is revoked
    
    def test_load_cert_db_file_not_found(self, temp_dir):
        """Test loading certificate database when file doesn't exist."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Database should be initialized with empty structure
        assert cert_manager.cert_db == {"certificates": [], "revoked": []}
    
    def test_load_cert_db_invalid_json(self, temp_dir):
        """Test loading certificate database with invalid JSON."""
        cert_db_file = temp_dir / "certificates.json"
        cert_db_file.write_text("{ invalid json }")
        
        cert_manager = CertificateManager(str(temp_dir))
        
        # Should fall back to empty database
        assert cert_manager.cert_db == {"certificates": [], "revoked": []}
    
    def test_save_cert_db(self, temp_dir):
        """Test saving certificate database."""
        cert_manager = CertificateManager(str(temp_dir))
        
        # Add some data
        cert_manager.cert_db["certificates"].append({"test": "data"})
        
        with patch('builtins.open', mock_open()) as mock_file:
            cert_manager._save_cert_db()
        
        # Check that file was opened for writing
        mock_file.assert_called_with(cert_manager.cert_db_path, 'w')
    
    def test_update_crl_no_ca(self, temp_dir):
        """Test updating CRL without CA."""
        cert_manager = CertificateManager(str(temp_dir))
        
        cert_manager._update_crl()
        # Should not raise exception, just log error
    
    @patch('mcp_security.certificate_manager.x509.CertificateRevocationListBuilder')
    def test_update_crl_success(self, mock_crl_builder, temp_dir):
        """Test successful CRL update."""
        # Create CA files
        ca_cert_file = temp_dir / "ca.crt"
        ca_key_file = temp_dir / "ca.key"
        ca_cert_file.write_text("fake ca cert")
        ca_key_file.write_text("fake ca key")
        
        cert_manager = CertificateManager(str(temp_dir))
        
        # Add revoked certificate
        cert_manager.cert_db["revoked"].append({
            "serial_number": "123456789",
            "revoked_at": "2023-01-01T00:00:00"
        })
        
        # Mock CRL building
        mock_builder = Mock()
        mock_crl_builder.return_value = mock_builder
        mock_builder.issuer_name.return_value = mock_builder
        mock_builder.last_update.return_value = mock_builder
        mock_builder.next_update.return_value = mock_builder
        mock_builder.add_revoked_certificate.return_value = mock_builder
        mock_builder.build.return_value = Mock()
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('mcp_security.certificate_manager.x509.load_pem_x509_certificate') as mock_load_cert:
                with patch('mcp_security.certificate_manager.load_pem_private_key') as mock_load_key:
                    mock_load_cert.return_value = Mock()
                    mock_load_key.return_value = Mock()
                    
                    cert_manager._update_crl()
        
        # Check that CRL file was written
        mock_file.assert_called_with(cert_manager.crl_path, 'wb')
