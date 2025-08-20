"""
Tests for Test Certificate Generator Script

Tests for the test certificate generator script.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from scripts.generate_test_certs import TestCertificateGenerator, main


class TestTestCertificateGenerator:
    """Test TestCertificateGenerator class."""
    
    def setup_method(self):
        """Set up test method."""
        self.output_dir = tempfile.mkdtemp()
        self.generator = TestCertificateGenerator(self.output_dir)
    
    def teardown_method(self):
        """Clean up after test method."""
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    def test_init(self):
        """Test initialization."""
        generator = TestCertificateGenerator("test_dir")
        
        assert generator.output_dir == "test_dir"
        assert generator.logger is not None
        assert generator.role_oid.dotted_string == "1.3.6.1.4.1.99999.1"
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator._save_certificate_and_key')
    @patch('scripts.generate_test_certs.rsa.generate_private_key')
    @patch('scripts.generate_test_certs.x509.CertificateBuilder')
    @patch('scripts.generate_test_certs.x509.random_serial_number')
    @patch('scripts.generate_test_certs.datetime')
    def test_generate_ca_certificate(self, mock_datetime, mock_serial, mock_builder, mock_key_gen, mock_save):
        """Test generate_ca_certificate method."""
        # Mock datetime
        mock_now = datetime(2023, 1, 1)
        mock_datetime.utcnow.return_value = mock_now
        
        # Mock private key
        mock_private_key = Mock()
        mock_public_key = Mock()
        mock_private_key.public_key.return_value = mock_public_key
        mock_key_gen.return_value = mock_private_key
        
        # Mock certificate builder
        mock_builder_instance = Mock()
        mock_builder.return_value = mock_builder_instance
        mock_builder_instance.subject_name.return_value = mock_builder_instance
        mock_builder_instance.issuer_name.return_value = mock_builder_instance
        mock_builder_instance.public_key.return_value = mock_builder_instance
        mock_builder_instance.serial_number.return_value = mock_builder_instance
        mock_builder_instance.not_valid_before.return_value = mock_builder_instance
        mock_builder_instance.not_valid_after.return_value = mock_builder_instance
        mock_builder_instance.add_extension.return_value = mock_builder_instance
        mock_builder_instance.sign.return_value = Mock()
        
        # Mock serial number
        mock_serial.return_value = 12345
        
        result = self.generator.generate_ca_certificate("test-ca")
        
        assert result["certificate_path"] == os.path.join(self.output_dir, "ca_test-ca.crt")
        assert result["key_path"] == os.path.join(self.output_dir, "ca_test-ca.key")
        assert result["common_name"] == "test-ca"
        
        # Verify certificate builder was called correctly
        mock_builder_instance.add_extension.assert_called()
        mock_builder_instance.sign.assert_called_once()
        # Check that sign was called with the private key and SHA256
        call_args = mock_builder_instance.sign.call_args
        assert call_args[0][0] == mock_private_key
        assert "SHA256" in str(call_args[0][1])
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator._save_certificate_and_key')
    @patch('scripts.generate_test_certs.rsa.generate_private_key')
    @patch('scripts.generate_test_certs.x509.CertificateBuilder')
    @patch('scripts.generate_test_certs.x509.random_serial_number')
    @patch('scripts.generate_test_certs.datetime')
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('scripts.generate_test_certs.serialization.load_pem_private_key')
    def test_generate_server_certificate(self, mock_load_key, mock_load_cert, mock_open, mock_datetime, mock_serial, mock_builder, mock_key_gen, mock_save):
        """Test generate_server_certificate method."""
        # Mock datetime
        mock_now = datetime(2023, 1, 1)
        mock_datetime.utcnow.return_value = mock_now
        
        # Mock private key
        mock_private_key = Mock()
        mock_public_key = Mock()
        mock_private_key.public_key.return_value = mock_public_key
        mock_key_gen.return_value = mock_private_key
        
        # Mock CA certificate
        mock_ca_cert = Mock()
        mock_ca_cert.subject = Mock()
        mock_load_cert.return_value = mock_ca_cert
        
        # Mock CA key
        mock_ca_key = Mock()
        mock_load_key.return_value = mock_ca_key
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"ca_cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock certificate builder
        mock_builder_instance = Mock()
        mock_builder.return_value = mock_builder_instance
        mock_builder_instance.subject_name.return_value = mock_builder_instance
        mock_builder_instance.issuer_name.return_value = mock_builder_instance
        mock_builder_instance.public_key.return_value = mock_builder_instance
        mock_builder_instance.serial_number.return_value = mock_builder_instance
        mock_builder_instance.not_valid_before.return_value = mock_builder_instance
        mock_builder_instance.not_valid_after.return_value = mock_builder_instance
        mock_builder_instance.add_extension.return_value = mock_builder_instance
        mock_builder_instance.sign.return_value = Mock()
        
        # Mock serial number
        mock_serial.return_value = 12345
        
        result = self.generator.generate_server_certificate("test-server", "ca.crt", "ca.key", ["admin", "user"])
        
        assert result["certificate_path"] == os.path.join(self.output_dir, "server_test-server.crt")
        assert result["key_path"] == os.path.join(self.output_dir, "server_test-server.key")
        assert result["common_name"] == "test-server"
        assert result["roles"] == ["admin", "user"]
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator._save_certificate_and_key')
    @patch('scripts.generate_test_certs.rsa.generate_private_key')
    @patch('scripts.generate_test_certs.x509.CertificateBuilder')
    @patch('scripts.generate_test_certs.x509.random_serial_number')
    @patch('scripts.generate_test_certs.datetime')
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    @patch('scripts.generate_test_certs.serialization.load_pem_private_key')
    def test_generate_client_certificate(self, mock_load_key, mock_load_cert, mock_open, mock_datetime, mock_serial, mock_builder, mock_key_gen, mock_save):
        """Test generate_client_certificate method."""
        # Mock datetime
        mock_now = datetime(2023, 1, 1)
        mock_datetime.utcnow.return_value = mock_now
        
        # Mock private key
        mock_private_key = Mock()
        mock_public_key = Mock()
        mock_private_key.public_key.return_value = mock_public_key
        mock_key_gen.return_value = mock_private_key
        
        # Mock CA certificate
        mock_ca_cert = Mock()
        mock_ca_cert.subject = Mock()
        mock_load_cert.return_value = mock_ca_cert
        
        # Mock CA key
        mock_ca_key = Mock()
        mock_load_key.return_value = mock_ca_key
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"ca_cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock certificate builder
        mock_builder_instance = Mock()
        mock_builder.return_value = mock_builder_instance
        mock_builder_instance.subject_name.return_value = mock_builder_instance
        mock_builder_instance.issuer_name.return_value = mock_builder_instance
        mock_builder_instance.public_key.return_value = mock_builder_instance
        mock_builder_instance.serial_number.return_value = mock_builder_instance
        mock_builder_instance.not_valid_before.return_value = mock_builder_instance
        mock_builder_instance.not_valid_after.return_value = mock_builder_instance
        mock_builder_instance.add_extension.return_value = mock_builder_instance
        mock_builder_instance.sign.return_value = Mock()
        
        # Mock serial number
        mock_serial.return_value = 12345
        
        result = self.generator.generate_client_certificate("test-client", "ca.crt", "ca.key", ["user"])
        
        assert result["certificate_path"] == os.path.join(self.output_dir, "client_test-client.crt")
        assert result["key_path"] == os.path.join(self.output_dir, "client_test-client.key")
        assert result["common_name"] == "test-client"
        assert result["roles"] == ["user"]
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_with_roles(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with roles."""
        # Mock certificate
        mock_cert = Mock()
        mock_extension = Mock()
        # Create a proper OID mock that matches the generator's role_oid
        mock_extension.oid = self.generator.role_oid
        mock_extension.value.value = b"admin,user,moderator"
        mock_cert.extensions = [mock_extension]
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        roles = self.generator.extract_roles_from_certificate("/test/cert.crt")
        
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
        
        roles = self.generator.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_exception(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with exception."""
        # Mock file open to raise exception
        mock_open.side_effect = Exception("File not found")
        
        roles = self.generator.extract_roles_from_certificate("/nonexistent/cert.crt")
        
        assert roles == []


class TestMainFunction:
    """Test main function."""
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator')
    def test_main_generate_all(self, mock_generator_class):
        """Test main function with --generate-all flag."""
        # Mock command line arguments
        with patch('sys.argv', ['generate_test_certs.py', '--generate-all']):
            # Mock generator
            mock_generator = Mock()
            mock_generator.generate_ca_certificate.return_value = {
                "certificate_path": "test_certs/ca_test-ca.crt",
                "key_path": "test_certs/ca_test-ca.key",
                "common_name": "test-ca"
            }
            mock_generator.generate_server_certificate.return_value = {
                "certificate_path": "test_certs/server_test-server.crt",
                "key_path": "test_certs/server_test-server.key",
                "common_name": "test-server",
                "roles": ["admin", "user"]
            }
            mock_generator.generate_client_certificate.return_value = {
                "certificate_path": "test_certs/client_test-client.crt",
                "key_path": "test_certs/client_test-client.key",
                "common_name": "test-client",
                "roles": ["user"]
            }
            mock_generator.extract_roles_from_certificate.return_value = ["admin", "user"]
            mock_generator_class.return_value = mock_generator
            
            # Mock print
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify generator methods were called
                mock_generator.generate_ca_certificate.assert_called_once_with("test-ca")
                mock_generator.generate_server_certificate.assert_called_once_with("test-server", "test_certs/ca_test-ca.crt", "test_certs/ca_test-ca.key", ["admin", "user"])
                mock_generator.generate_client_certificate.assert_called_once_with("test-client", "test_certs/ca_test-ca.crt", "test_certs/ca_test-ca.key", ["user"])
                
                # Verify output was printed
                assert mock_print.call_count > 0
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator')
    def test_main_with_custom_parameters(self, mock_generator_class):
        """Test main function with custom parameters."""
        # Mock command line arguments
        with patch('sys.argv', [
            'generate_test_certs.py',
            '--output-dir', 'custom_dir',
            '--ca-name', 'custom-ca',
            '--server-name', 'custom-server',
            '--client-name', 'custom-client',
            '--server-roles', 'admin', 'moderator',
            '--client-roles', 'user',
            '--generate-all'
        ]):
            # Mock generator
            mock_generator = Mock()
            mock_generator.generate_ca_certificate.return_value = {
                "certificate_path": "custom_dir/ca_custom-ca.crt",
                "key_path": "custom_dir/ca_custom-ca.key",
                "common_name": "custom-ca"
            }
            mock_generator.generate_server_certificate.return_value = {
                "certificate_path": "custom_dir/server_custom-server.crt",
                "key_path": "custom_dir/server_custom-server.key",
                "common_name": "custom-server",
                "roles": ["admin", "moderator"]
            }
            mock_generator.generate_client_certificate.return_value = {
                "certificate_path": "custom_dir/client_custom-client.crt",
                "key_path": "custom_dir/client_custom-client.key",
                "common_name": "custom-client",
                "roles": ["user"]
            }
            mock_generator.extract_roles_from_certificate.return_value = ["admin", "moderator"]
            mock_generator_class.return_value = mock_generator
            
            # Mock print
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify generator was created with custom output directory
                mock_generator_class.assert_called_once_with("custom_dir")
                
                # Verify generator methods were called with custom parameters
                mock_generator.generate_ca_certificate.assert_called_once_with("custom-ca")
                mock_generator.generate_server_certificate.assert_called_once_with("custom-server", "custom_dir/ca_custom-ca.crt", "custom_dir/ca_custom-ca.key", ["admin", "moderator"])
                mock_generator.generate_client_certificate.assert_called_once_with("custom-client", "custom_dir/ca_custom-ca.crt", "custom_dir/ca_custom-ca.key", ["user"])
                
                # Verify output was printed
                assert mock_print.call_count > 0
    
    @patch('scripts.generate_test_certs.TestCertificateGenerator')
    def test_main_without_generate_all(self, mock_generator_class):
        """Test main function without --generate-all flag."""
        # Mock command line arguments
        with patch('sys.argv', ['generate_test_certs.py']):
            # Mock generator
            mock_generator = Mock()
            mock_generator_class.return_value = mock_generator
            
            # Mock print
            with patch('builtins.print') as mock_print:
                main()
                
                # Verify no generator methods were called
                mock_generator.generate_ca_certificate.assert_not_called()
                mock_generator.generate_server_certificate.assert_not_called()
                mock_generator.generate_client_certificate.assert_not_called()
                
                # Verify no output was printed
                mock_print.assert_not_called() 