"""
Tests for MTLSMiddleware module.

Tests mTLS authentication middleware functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from mcp_proxy_adapter.api.middleware.mtls_middleware import MTLSMiddleware
from mcp_proxy_adapter.core.auth_validator import AuthValidator
from mcp_proxy_adapter.core.role_utils import RoleUtils
from mcp_proxy_adapter.core.certificate_utils import CertificateUtils


class TestMTLSMiddleware:
    """Test cases for MTLSMiddleware class."""
    
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
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate
        cert_path = os.path.join(temp_dir, "ca.crt")
        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        return cert_path
    
    @pytest.fixture
    def sample_client_cert(self, temp_dir, sample_ca_cert):
        """Create sample client certificate for testing."""
        # Load CA certificate and key
        with open(sample_ca_cert, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        # Generate CA private key (for signing)
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Generate client private key
        client_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Create client certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "test-client"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            ca_cert.subject
        ).public_key(
            client_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc)
        ).not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=365)
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        ).sign(ca_key, hashes.SHA256())
        
        return cert
    
    @pytest.fixture
    def mtls_config(self, sample_ca_cert):
        """Create mTLS configuration for testing."""
        return {
            "enabled": True,
            "ca_cert": sample_ca_cert,
            "verify_client": True,
            "client_cert_required": True,
            "allowed_roles": ["admin", "user"],
            "require_roles": True
        }
    
    @pytest.fixture
    def mock_app(self):
        """Create mock FastAPI application."""
        return Mock()
    
    @pytest.fixture
    def middleware(self, mock_app, mtls_config):
        """Create MTLSMiddleware instance for testing."""
        return MTLSMiddleware(mock_app, mtls_config)
    
    def test_middleware_initialization(self, mock_app, mtls_config):
        """Test middleware initialization."""
        middleware = MTLSMiddleware(mock_app, mtls_config)
        
        assert middleware.enabled is True
        assert middleware.ca_cert_path == mtls_config["ca_cert"]
        assert middleware.verify_client is True
        assert middleware.client_cert_required is True
        assert middleware.allowed_roles == ["admin", "user"]
        assert middleware.require_roles is True
    
    def test_middleware_initialization_disabled(self, mock_app):
        """Test middleware initialization when disabled."""
        config = {"enabled": False}
        middleware = MTLSMiddleware(mock_app, config)
        
        assert middleware.enabled is False
        assert middleware.verify_client is True  # Default value
        assert middleware.client_cert_required is True  # Default value
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._validate_client_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_roles_from_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._validate_access')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._get_common_name')
    async def test_before_request_success(self, mock_get_cn, mock_validate_access, 
                                        mock_extract_roles, mock_validate_cert, 
                                        mock_extract_cert, middleware, sample_client_cert):
        """Test successful request processing."""
        # Setup mocks
        mock_extract_cert.return_value = sample_client_cert
        mock_validate_cert.return_value = True
        mock_extract_roles.return_value = ["admin"]
        mock_validate_access.return_value = True
        mock_get_cn.return_value = "test-client"
        
        # Create mock request
        request = Mock()
        request.state = Mock()
        
        # Call before_request
        await middleware.before_request(request)
        
        # Verify certificate and roles were stored
        assert request.state.client_certificate == sample_client_cert
        assert request.state.client_roles == ["admin"]
        assert request.state.client_common_name == "test-client"
        
        # Verify all methods were called
        mock_extract_cert.assert_called_once_with(request)
        mock_validate_cert.assert_called_once_with(sample_client_cert)
        mock_extract_roles.assert_called_once_with(sample_client_cert)
        mock_validate_access.assert_called_once_with(["admin"])
        mock_get_cn.assert_called_once_with(sample_client_cert)
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    async def test_before_request_disabled(self, mock_extract_cert, middleware):
        """Test request processing when middleware is disabled."""
        middleware.enabled = False
        
        request = Mock()
        
        await middleware.before_request(request)
        
        # Verify no certificate extraction was attempted
        mock_extract_cert.assert_not_called()
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    async def test_before_request_no_certificate_required(self, mock_extract_cert, middleware):
        """Test request processing when certificate is not required."""
        middleware.client_cert_required = False
        mock_extract_cert.return_value = None
        
        request = Mock()
        
        await middleware.before_request(request)
        
        # Should not raise an exception
        mock_extract_cert.assert_called_once_with(request)
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    async def test_before_request_certificate_required_but_not_provided(self, mock_extract_cert, middleware):
        """Test request processing when certificate is required but not provided."""
        mock_extract_cert.return_value = None
        
        request = Mock()
        
        with pytest.raises(ValueError, match="Client certificate is required but not provided"):
            await middleware.before_request(request)
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._validate_client_certificate')
    async def test_before_request_certificate_validation_failed(self, mock_validate_cert, 
                                                              mock_extract_cert, middleware, sample_client_cert):
        """Test request processing when certificate validation fails."""
        mock_extract_cert.return_value = sample_client_cert
        mock_validate_cert.return_value = False
        
        request = Mock()
        
        with pytest.raises(ValueError, match="Client certificate validation failed"):
            await middleware.before_request(request)
    
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_client_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._validate_client_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._extract_roles_from_certificate')
    @patch('mcp_proxy_adapter.api.middleware.mtls_middleware.MTLSMiddleware._validate_access')
    async def test_before_request_access_denied(self, mock_validate_access, mock_extract_roles,
                                              mock_validate_cert, mock_extract_cert, 
                                              middleware, sample_client_cert):
        """Test request processing when access is denied."""
        mock_extract_cert.return_value = sample_client_cert
        mock_validate_cert.return_value = True
        mock_extract_roles.return_value = ["user"]
        mock_validate_access.return_value = False
        
        request = Mock()
        
        with pytest.raises(ValueError, match="Access denied: insufficient roles"):
            await middleware.before_request(request)
    
    def test_extract_client_certificate_from_ssl_context(self, middleware, sample_client_cert):
        """Test extracting client certificate from SSL context."""
        # Create mock SSL context
        mock_ssl_context = Mock()
        mock_ssl_context.getpeercert.return_value = sample_client_cert.public_bytes(
            serialization.Encoding.DER
        )
        
        # Create mock request with SSL context
        request = Mock()
        request.scope = {"ssl": mock_ssl_context}
        
        result = middleware._extract_client_certificate(request)
        
        assert result is not None
        assert isinstance(result, x509.Certificate)
    
    def test_extract_client_certificate_from_header(self, middleware, sample_client_cert):
        """Test extracting client certificate from header."""
        # Create mock request with certificate in header
        request = Mock()
        request.headers = {
            "ssl-client-cert": sample_client_cert.public_bytes(
                serialization.Encoding.PEM
            ).decode('utf-8')
        }
        request.scope = {}
        
        result = middleware._extract_client_certificate(request)
        
        assert result is not None
        assert isinstance(result, x509.Certificate)
    
    def test_extract_client_certificate_from_header_base64(self, middleware, sample_client_cert):
        """Test extracting client certificate from base64 encoded header."""
        import base64
        
        # Create mock request with base64 encoded certificate in header
        request = Mock()
        request.headers = {
            "ssl-client-cert": base64.b64encode(
                sample_client_cert.public_bytes(serialization.Encoding.PEM)
            ).decode('utf-8')
        }
        request.scope = {}
        
        result = middleware._extract_client_certificate(request)
        
        assert result is not None
        assert isinstance(result, x509.Certificate)
    
    def test_extract_client_certificate_not_found(self, middleware):
        """Test extracting client certificate when not found."""
        request = Mock()
        request.scope = {}
        request.headers = {}
        
        result = middleware._extract_client_certificate(request)
        
        assert result is None
    
    def test_validate_client_certificate_success(self, middleware, sample_client_cert):
        """Test successful client certificate validation."""
        # Setup mock
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        
        # Set the mock on the middleware instance
        middleware.auth_validator = mock_auth_validator
        
        # Disable chain validation for this test
        middleware.ca_cert_path = None
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is True
        mock_auth_validator.validate_certificate_data.assert_called_once()
    
    def test_validate_client_certificate_failure(self, middleware, sample_client_cert):
        """Test failed client certificate validation."""
        # Setup mock
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = False
        mock_result.error_message = "Certificate expired"
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        
        # Set the mock on the middleware instance
        middleware.auth_validator = mock_auth_validator
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is False
    
    def test_validate_client_certificate_verify_disabled(self, middleware, sample_client_cert):
        """Test client certificate validation when verification is disabled."""
        middleware.verify_client = False
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is True
    
    def test_validate_client_certificate_with_chain_validation(self, middleware, sample_client_cert):
        """Test client certificate validation with chain validation."""
        # Setup mocks
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        middleware.auth_validator = mock_auth_validator
        
        # Set the mock on the middleware instance
        mock_cert_utils = Mock()
        middleware.certificate_utils = mock_cert_utils
        mock_cert_utils.validate_certificate_chain.return_value = True
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is True
        mock_cert_utils.validate_certificate_chain.assert_called_once()
    
    def test_extract_roles_from_certificate(self, middleware, sample_client_cert):
        """Test role extraction from certificate."""
        # Set the mock on the middleware instance
        mock_cert_utils = Mock()
        middleware.certificate_utils = mock_cert_utils
        mock_cert_utils.extract_roles_from_certificate_object.return_value = ["admin", "user"]
        
        result = middleware._extract_roles_from_certificate(sample_client_cert)
        
        assert result == ["admin", "user"]
        mock_cert_utils.extract_roles_from_certificate_object.assert_called_once_with(sample_client_cert)
    
    def test_validate_access_success(self, middleware):
        """Test successful access validation."""
        # Set the mock on the middleware instance
        mock_role_utils = Mock()
        middleware.role_utils = mock_role_utils
        mock_role_utils.compare_roles.return_value = True
        
        result = middleware._validate_access(["admin"])
        
        assert result is True
        mock_role_utils.compare_roles.assert_called()
    
    def test_validate_access_failure(self, middleware):
        """Test failed access validation."""
        # Set the mock on the middleware instance
        mock_role_utils = Mock()
        middleware.role_utils = mock_role_utils
        mock_role_utils.compare_roles.return_value = False
        
        result = middleware._validate_access(["user"])
        
        assert result is False
    
    def test_validate_access_no_allowed_roles(self, middleware):
        """Test access validation when no roles are allowed."""
        middleware.allowed_roles = []
        
        result = middleware._validate_access(["admin"])
        
        assert result is True  # No restrictions
    
    def test_validate_access_no_client_roles(self, middleware):
        """Test access validation when client has no roles."""
        result = middleware._validate_access([])
        
        assert result is False
    
    def test_get_common_name_success(self, middleware, sample_client_cert):
        """Test getting common name from certificate."""
        result = middleware._get_common_name(sample_client_cert)
        
        assert result == "test-client"
    
    def test_get_common_name_not_found(self, middleware):
        """Test getting common name when not found in certificate."""
        # Create certificate without common name
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        subject = x509.Name([
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test Organization"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.now(timezone.utc)
        ).not_valid_after(
            datetime.now(timezone.utc) + timedelta(days=365)
        ).sign(private_key, hashes.SHA256())
        
        result = middleware._get_common_name(cert)
        
        assert result == ""
    
    async def test_handle_error_certificate_required(self, middleware):
        """Test error handling for missing certificate."""
        request = Mock()
        request.state = Mock()
        request.state.request_id = "test-123"
        
        exception = ValueError("Client certificate is required but not provided")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 401
        assert response.body.decode() == '{"jsonrpc":"2.0","error":{"code":-32009,"message":"Client certificate is required but not provided","data":{"validation_type":"mtls","request_id":"test-123"}},"id":null}'
    
    async def test_handle_error_validation_failed(self, middleware):
        """Test error handling for validation failure."""
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        
        exception = ValueError("Client certificate validation failed")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 401
        assert response.body.decode() == '{"jsonrpc":"2.0","error":{"code":-32003,"message":"Client certificate validation failed","data":{"validation_type":"mtls","request_id":null}},"id":null}'
    
    async def test_handle_error_access_denied(self, middleware):
        """Test error handling for access denied."""
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        
        exception = ValueError("Access denied: insufficient roles")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 403
        assert response.body.decode() == '{"jsonrpc":"2.0","error":{"code":-32007,"message":"Access denied: insufficient roles","data":{"validation_type":"mtls","request_id":null}},"id":null}'
    
    async def test_handle_error_generic(self, middleware):
        """Test error handling for generic error."""
        request = Mock()
        request.state = Mock()
        request.state.request_id = None
        
        exception = Exception("Generic error")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 500
        assert response.body.decode() == '{"jsonrpc":"2.0","error":{"code":-32603,"message":"Generic error","data":{"validation_type":"mtls","request_id":null}},"id":null}' 

    def test_extract_client_certificate_exception(self, middleware):
        """Test client certificate extraction with exception."""
        # Create a request that will cause an exception
        request = Mock()
        request.scope = {"ssl": {"client_cert": "invalid_cert"}}
        
        # Mock certificate_utils to raise exception
        middleware.certificate_utils = Mock()
        middleware.certificate_utils.extract_certificate_from_pem.side_effect = Exception("Test exception")
        
        result = middleware._extract_client_certificate(request)
        
        assert result is None

    def test_validate_client_certificate_exception(self, middleware, sample_client_cert):
        """Test client certificate validation with exception."""
        # Mock auth_validator to raise exception
        middleware.auth_validator = Mock()
        middleware.auth_validator.validate_certificate_data.side_effect = Exception("Test exception")
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is False

    def test_extract_roles_from_certificate_exception(self, middleware, sample_client_cert):
        """Test role extraction with exception."""
        # Mock certificate_utils to raise exception
        middleware.certificate_utils = Mock()
        middleware.certificate_utils.extract_roles_from_certificate_object.side_effect = Exception("Test exception")
        
        result = middleware._extract_roles_from_certificate(sample_client_cert)
        
        assert result == []

    def test_validate_access_exception(self, middleware):
        """Test access validation with exception."""
        # Mock role_utils to raise exception
        middleware.role_utils = Mock()
        middleware.role_utils.compare_roles.side_effect = Exception("Test exception")
        
        result = middleware._validate_access(["admin"])
        
        assert result is False

    def test_get_common_name_exception(self, middleware):
        """Test getting common name with exception."""
        # Create a certificate that will cause an exception
        cert = Mock()
        cert.subject = Mock()
        cert.subject.__iter__ = Mock(side_effect=Exception("Test exception"))
        
        result = middleware._get_common_name(cert)
        
        assert result == ""

    async def test_handle_error_exception(self, middleware):
        """Test error handling with exception."""
        request = Mock()
        request.state = Mock()
        request.state.request_id = "test-123"
        
        # Test with a generic exception
        exception = Exception("Generic error")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 500
        content = response.body.decode()
        assert '"code":-32603' in content
        assert '"message":"Generic error"' in content

    def test_validate_client_certificate_chain_validation_exception(self, middleware, sample_client_cert):
        """Test client certificate validation with chain validation exception."""
        # Setup mocks
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        middleware.auth_validator = mock_auth_validator
        
        # Set CA cert path to trigger chain validation
        middleware.ca_cert_path = "/path/to/ca.crt"
        
        # Mock certificate_utils to raise exception during chain validation
        middleware.certificate_utils = Mock()
        middleware.certificate_utils.validate_certificate_chain.side_effect = Exception("Chain validation failed")
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is False

    def test_validate_client_certificate_chain_validation_file_cleanup(self, middleware, sample_client_cert):
        """Test that temporary files are cleaned up during chain validation."""
        # Setup mocks
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        middleware.auth_validator = mock_auth_validator
        
        # Set CA cert path to trigger chain validation
        middleware.ca_cert_path = "/path/to/ca.crt"
        
        # Mock certificate_utils to return True for chain validation
        middleware.certificate_utils = Mock()
        middleware.certificate_utils.validate_certificate_chain.return_value = True
        
        # Mock os.unlink to track if it's called
        with patch('os.unlink') as mock_unlink:
            result = middleware._validate_client_certificate(sample_client_cert)
            
            assert result is True
            # Verify that os.unlink was called to clean up temporary file
            mock_unlink.assert_called_once()

    def test_validate_access_with_empty_roles_list(self, middleware):
        """Test access validation when client has empty roles list."""
        middleware.allowed_roles = ["admin", "user"]
        
        result = middleware._validate_access([])
        
        assert result is False

    def test_validate_access_with_none_roles(self, middleware):
        """Test access validation when client has None roles."""
        middleware.allowed_roles = ["admin", "user"]
        
        result = middleware._validate_access(None)
        
        assert result is False

    def test_get_common_name_with_certificate_without_subject(self, middleware):
        """Test getting common name from certificate without subject."""
        cert = Mock()
        cert.subject = []
        
        result = middleware._get_common_name(cert)
        
        assert result == ""

    def test_get_common_name_with_certificate_without_common_name(self, middleware):
        """Test getting common name from certificate without common name attribute."""
        cert = Mock()
        cert.subject = [
            Mock(oid=x509.NameOID.ORGANIZATION_NAME, value="Test Org"),
            Mock(oid=x509.NameOID.COUNTRY_NAME, value="US")
        ]
        
        result = middleware._get_common_name(cert)
        
        assert result == ""

    async def test_handle_error_with_request_without_state(self, middleware):
        """Test error handling with request that has no state."""
        request = Mock()
        request.state = None
        
        exception = Exception("Test error")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 500
        content = response.body.decode()
        assert '"code":-32603' in content

    async def test_handle_error_with_request_without_request_id(self, middleware):
        """Test error handling with request that has no request_id in state."""
        request = Mock()
        request.state = Mock()
        # Mock getattr to return None for request_id
        request.state.request_id = None
        
        exception = Exception("Test error")
        
        response = await middleware.handle_error(request, exception)
        
        assert response.status_code == 500
        content = response.body.decode()
        assert '"code":-32603' in content 

    def test_validate_client_certificate_chain_validation_failure(self, middleware, sample_client_cert):
        """Test client certificate validation with chain validation failure."""
        # Setup mocks
        mock_auth_validator = Mock()
        mock_result = Mock()
        mock_result.is_valid = True
        mock_auth_validator.validate_certificate_data.return_value = mock_result
        middleware.auth_validator = mock_auth_validator
        
        # Set CA cert path to trigger chain validation
        middleware.ca_cert_path = "/path/to/ca.crt"
        
        # Mock certificate_utils to return False for chain validation
        middleware.certificate_utils = Mock()
        middleware.certificate_utils.validate_certificate_chain.return_value = False
        
        result = middleware._validate_client_certificate(sample_client_cert)
        
        assert result is False 