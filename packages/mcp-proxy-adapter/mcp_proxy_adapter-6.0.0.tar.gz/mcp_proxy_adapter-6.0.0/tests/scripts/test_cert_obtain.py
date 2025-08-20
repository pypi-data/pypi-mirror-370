"""
Tests for Certificate Obtainer Script

Tests for the certificate obtainer script.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from scripts.cert_obtain import CertificateObtainer, main


class TestCertificateObtainer:
    """Test CertificateObtainer class."""
    
    def setup_method(self):
        """Set up test method."""
        self.config = {
            "cert_service": {
                "url": "https://cert-service.example.com",
                "auth": {
                    "type": "api_key",
                    "api_key": "test-api-key"
                },
                "templates": {
                    "ca_cert": {
                        "validity_days": 3650,
                        "key_size": 4096
                    },
                    "server_cert": {
                        "validity_days": 365,
                        "key_size": 2048
                    },
                    "client_cert": {
                        "validity_days": 90,
                        "key_size": 2048
                    }
                },
                "role_extension_oid": "1.3.6.1.4.1.99999.1"
            }
        }
    
    def test_init_valid_config(self):
        """Test initialization with valid config."""
        obtainer = CertificateObtainer(self.config)
        
        assert obtainer.service_config == self.config
        assert obtainer.logger is not None
    
    def test_init_missing_config_keys(self):
        """Test initialization with missing config keys."""
        invalid_config = {"cert_service": {"url": "https://example.com"}}
        
        with pytest.raises(ValueError, match="Missing required configuration key"):
            CertificateObtainer(invalid_config)
    
    def test_validate_config(self):
        """Test _validate_config method."""
        obtainer = CertificateObtainer(self.config)
        
        # Should not raise exception
        obtainer._validate_config()
    
    @patch('scripts.cert_obtain.CertificateObtainer._make_service_request')
    @patch('scripts.cert_obtain.CertificateObtainer._save_certificate_and_key')
    async def test_obtain_ca_certificate(self, mock_save, mock_request):
        """Test obtain_ca_certificate method."""
        # Mock service response
        mock_response = {
            "certificate": "-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----"
        }
        mock_request.return_value = mock_response
        
        obtainer = CertificateObtainer(self.config)
        
        result = await obtainer.obtain_ca_certificate("test-ca")
        
        assert result["certificate_path"] == "certs/ca_test-ca.crt"
        assert result["key_path"] == "certs/ca_test-ca.key"
        assert result["common_name"] == "test-ca"
        
        # Verify service request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "obtain_ca"
        assert call_args[0][1]["cert_type"] == "ca"
        assert call_args[0][1]["common_name"] == "test-ca"
        assert call_args[0][1]["validity_days"] == 3650
        assert call_args[0][1]["key_size"] == 4096
    
    @patch('scripts.cert_obtain.CertificateObtainer._make_service_request')
    @patch('scripts.cert_obtain.CertificateObtainer._save_certificate_and_key')
    async def test_obtain_server_certificate(self, mock_save, mock_request):
        """Test obtain_server_certificate method."""
        # Mock service response
        mock_response = {
            "certificate": "-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----"
        }
        mock_request.return_value = mock_response
        
        obtainer = CertificateObtainer(self.config)
        roles = ["admin", "user"]
        
        result = await obtainer.obtain_server_certificate("test-server", roles)
        
        assert result["certificate_path"] == "certs/server_test-server.crt"
        assert result["key_path"] == "certs/server_test-server.key"
        assert result["common_name"] == "test-server"
        assert result["roles"] == roles
        
        # Verify service request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "obtain_server"
        assert call_args[0][1]["cert_type"] == "server"
        assert call_args[0][1]["common_name"] == "test-server"
        assert call_args[0][1]["roles"] == roles
        assert call_args[0][1]["validity_days"] == 365
        assert call_args[0][1]["key_size"] == 2048
    
    @patch('scripts.cert_obtain.CertificateObtainer._make_service_request')
    @patch('scripts.cert_obtain.CertificateObtainer._save_certificate_and_key')
    async def test_obtain_client_certificate(self, mock_save, mock_request):
        """Test obtain_client_certificate method."""
        # Mock service response
        mock_response = {
            "certificate": "-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----"
        }
        mock_request.return_value = mock_response
        
        obtainer = CertificateObtainer(self.config)
        roles = ["user"]
        
        result = await obtainer.obtain_client_certificate("test-client", roles)
        
        assert result["certificate_path"] == "certs/client_test-client.crt"
        assert result["key_path"] == "certs/client_test-client.key"
        assert result["common_name"] == "test-client"
        assert result["roles"] == roles
        
        # Verify service request
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[0][0] == "obtain_client"
        assert call_args[0][1]["cert_type"] == "client"
        assert call_args[0][1]["common_name"] == "test-client"
        assert call_args[0][1]["roles"] == roles
        assert call_args[0][1]["validity_days"] == 90
        assert call_args[0][1]["key_size"] == 2048
    
    @patch('scripts.cert_obtain.CertificateObtainer._make_service_request')
    async def test_make_service_request_success(self, mock_request):
        """Test _make_service_request with successful response."""
        # Mock the request method directly
        mock_request.return_value = {"status": "success"}
        
        obtainer = CertificateObtainer(self.config)
        
        result = await obtainer._make_service_request("test_endpoint", {"data": "test"})
        
        assert result == {"status": "success"}
        
        # Verify request was called
        mock_request.assert_called_once_with("test_endpoint", {"data": "test"})
    
    @patch('scripts.cert_obtain.CertificateObtainer._make_service_request')
    async def test_make_service_request_failure(self, mock_request):
        """Test _make_service_request with failed response."""
        # Mock the request method to raise exception
        mock_request.side_effect = Exception("Service request failed: 500")
        
        obtainer = CertificateObtainer(self.config)
        
        with pytest.raises(Exception, match="Service request failed: 500"):
            await obtainer._make_service_request("test_endpoint", {"data": "test"})
    
    def test_get_auth_headers_api_key(self):
        """Test _get_auth_headers with API key auth."""
        obtainer = CertificateObtainer(self.config)
        
        headers = obtainer._get_auth_headers()
        
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"
    
    def test_get_auth_headers_unsupported_type(self):
        """Test _get_auth_headers with unsupported auth type."""
        config = self.config.copy()
        config["cert_service"]["auth"]["type"] = "unsupported"
        obtainer = CertificateObtainer(config)
        
        with pytest.raises(ValueError, match="Unsupported auth type"):
            obtainer._get_auth_headers()
    
    @patch('builtins.open')
    @patch('os.makedirs')
    async def test_save_certificate_and_key(self, mock_makedirs, mock_open):
        """Test _save_certificate_and_key method."""
        response = {
            "certificate": "-----BEGIN CERTIFICATE-----\nMOCK_CERT\n-----END CERTIFICATE-----",
            "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----"
        }
        
        obtainer = CertificateObtainer(self.config)
        
        await obtainer._save_certificate_and_key(response, "test.crt", "test.key")
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with("", exist_ok=True)
        
        # Verify file writes
        assert mock_open.call_count == 2
        
        # Check certificate file write
        cert_call = mock_open.call_args_list[0]
        assert cert_call[0][0] == "test.crt"
        
        # Check key file write
        key_call = mock_open.call_args_list[1]
        assert key_call[0][0] == "test.key"
    
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
        
        obtainer = CertificateObtainer(self.config)
        
        roles = obtainer.extract_roles_from_certificate("/test/cert.crt")
        
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
        
        obtainer = CertificateObtainer(self.config)
        
        roles = obtainer.extract_roles_from_certificate("/test/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_extract_roles_from_certificate_exception(self, mock_load_cert, mock_open):
        """Test extract_roles_from_certificate with exception."""
        # Mock file open to raise exception
        mock_open.side_effect = Exception("File not found")
        
        obtainer = CertificateObtainer(self.config)
        
        roles = obtainer.extract_roles_from_certificate("/nonexistent/cert.crt")
        
        assert roles == []
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_validate_certificate_valid(self, mock_load_cert, mock_open):
        """Test validate_certificate with valid certificate."""
        # Mock certificate
        mock_cert = Mock()
        mock_cert.not_valid_before = "2023-01-01"
        mock_cert.not_valid_after = "2024-01-01"
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock datetime
        with patch('scripts.cert_obtain.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = "2023-06-01"
            
            obtainer = CertificateObtainer(self.config)
            
            result = obtainer.validate_certificate("/test/cert.crt")
            
            assert result is True
    
    @patch('builtins.open')
    @patch('cryptography.x509.load_pem_x509_certificate')
    def test_validate_certificate_expired(self, mock_load_cert, mock_open):
        """Test validate_certificate with expired certificate."""
        # Mock certificate
        mock_cert = Mock()
        mock_cert.not_valid_before = "2023-01-01"
        mock_cert.not_valid_after = "2023-02-01"
        mock_load_cert.return_value = mock_cert
        
        # Mock file open
        mock_file = Mock()
        mock_file.read.return_value = b"cert_data"
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Mock datetime
        with patch('scripts.cert_obtain.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = "2023-06-01"
            
            obtainer = CertificateObtainer(self.config)
            
            result = obtainer.validate_certificate("/test/cert.crt")
            
            assert result is False
    
    @patch('builtins.open')
    def test_validate_certificate_file_not_found(self, mock_open):
        """Test validate_certificate with file not found."""
        mock_open.side_effect = FileNotFoundError("File not found")
        
        obtainer = CertificateObtainer(self.config)
        
        result = obtainer.validate_certificate("/nonexistent/cert.crt")
        
        assert result is False


class TestMainFunction:
    """Test main function."""
    
    @patch('scripts.cert_obtain.CertificateObtainer')
    @patch('builtins.open')
    @patch('json.load')
    async def test_main_ca_certificate(self, mock_json_load, mock_open, mock_obtainer_class):
        """Test main function with CA certificate."""
        # Mock command line arguments
        with patch('sys.argv', ['cert_obtain.py', '--config', 'config.json', '--type', 'ca', '--common-name', 'test-ca']):
            # Mock config loading
            mock_config = {"cert_service": {"url": "https://example.com", "auth": {"type": "api_key", "api_key": "test"}}}
            mock_json_load.return_value = mock_config
            
            # Mock obtainer
            mock_obtainer = AsyncMock()
            mock_obtainer.obtain_ca_certificate.return_value = {
                "certificate_path": "certs/ca_test-ca.crt",
                "key_path": "certs/ca_test-ca.key",
                "common_name": "test-ca"
            }
            mock_obtainer_class.return_value = mock_obtainer
            
            # Mock print
            with patch('builtins.print') as mock_print:
                await main()
                
                # Verify obtainer was called
                mock_obtainer.obtain_ca_certificate.assert_called_once_with("test-ca")
                
                # Verify output was printed
                mock_print.assert_called_once()
    
    @patch('scripts.cert_obtain.CertificateObtainer')
    @patch('builtins.open')
    @patch('json.load')
    async def test_main_server_certificate(self, mock_json_load, mock_open, mock_obtainer_class):
        """Test main function with server certificate."""
        # Mock command line arguments
        with patch('sys.argv', ['cert_obtain.py', '--config', 'config.json', '--type', 'server', '--common-name', 'test-server', '--roles', 'admin', 'user']):
            # Mock config loading
            mock_config = {"cert_service": {"url": "https://example.com", "auth": {"type": "api_key", "api_key": "test"}}}
            mock_json_load.return_value = mock_config
            
            # Mock obtainer
            mock_obtainer = AsyncMock()
            mock_obtainer.obtain_server_certificate.return_value = {
                "certificate_path": "certs/server_test-server.crt",
                "key_path": "certs/server_test-server.key",
                "common_name": "test-server",
                "roles": ["admin", "user"]
            }
            mock_obtainer_class.return_value = mock_obtainer
            
            # Mock print
            with patch('builtins.print') as mock_print:
                await main()
                
                # Verify obtainer was called
                mock_obtainer.obtain_server_certificate.assert_called_once_with("test-server", ["admin", "user"])
                
                # Verify output was printed
                mock_print.assert_called_once()
    
    @patch('scripts.cert_obtain.CertificateObtainer')
    @patch('builtins.open')
    @patch('json.load')
    async def test_main_client_certificate(self, mock_json_load, mock_open, mock_obtainer_class):
        """Test main function with client certificate."""
        # Mock command line arguments
        with patch('sys.argv', ['cert_obtain.py', '--config', 'config.json', '--type', 'client', '--common-name', 'test-client', '--roles', 'user']):
            # Mock config loading
            mock_config = {"cert_service": {"url": "https://example.com", "auth": {"type": "api_key", "api_key": "test"}}}
            mock_json_load.return_value = mock_config
            
            # Mock obtainer
            mock_obtainer = AsyncMock()
            mock_obtainer.obtain_client_certificate.return_value = {
                "certificate_path": "certs/client_test-client.crt",
                "key_path": "certs/client_test-client.key",
                "common_name": "test-client",
                "roles": ["user"]
            }
            mock_obtainer_class.return_value = mock_obtainer
            
            # Mock print
            with patch('builtins.print') as mock_print:
                await main()
                
                # Verify obtainer was called
                mock_obtainer.obtain_client_certificate.assert_called_once_with("test-client", ["user"])
                
                # Verify output was printed
                mock_print.assert_called_once() 