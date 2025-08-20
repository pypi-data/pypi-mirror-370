"""
mTLS Middleware

This module provides middleware for mutual TLS (mTLS) authentication.
Extracts and validates client certificates, extracts roles, and validates access.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...core.auth_validator import AuthValidator
from ...core.role_utils import RoleUtils
from ...core.certificate_utils import CertificateUtils
from .base import BaseMiddleware

logger = logging.getLogger(__name__)


class MTLSMiddleware(BaseMiddleware):
    """
    Middleware for mTLS authentication.
    
    Extracts client certificates from requests, validates them against CA,
    extracts roles, and validates access based on configuration.
    """
    
    def __init__(self, app, mtls_config: Dict[str, Any]):
        """
        Initialize mTLS middleware.
        
        Args:
            app: FastAPI application
            mtls_config: mTLS configuration dictionary
        """
        super().__init__(app)
        self.mtls_config = mtls_config
        self.auth_validator = AuthValidator()
        self.role_utils = RoleUtils()
        self.certificate_utils = CertificateUtils()
        
        # Extract configuration
        self.enabled = mtls_config.get("enabled", False)
        self.ca_cert_path = mtls_config.get("ca_cert")
        self.verify_client = mtls_config.get("verify_client", True)
        self.client_cert_required = mtls_config.get("client_cert_required", True)
        self.allowed_roles = mtls_config.get("allowed_roles", [])
        self.require_roles = mtls_config.get("require_roles", False)
        
        logger.info(f"mTLS middleware initialized: enabled={self.enabled}, "
                   f"verify_client={self.verify_client}, "
                   f"client_cert_required={self.client_cert_required}")
    
    async def before_request(self, request: Request) -> None:
        """
        Process request before calling the main handler.
        
        Args:
            request: FastAPI request object
        """
        if not self.enabled:
            return
        
        try:
            # Extract client certificate
            client_cert = self._extract_client_certificate(request)
            
            if client_cert is None:
                if self.client_cert_required:
                    raise ValueError("Client certificate is required but not provided")
                return
            
            # Validate client certificate
            if not self._validate_client_certificate(client_cert):
                raise ValueError("Client certificate validation failed")
            
            # Extract roles from certificate
            roles = self._extract_roles_from_certificate(client_cert)
            
            # Validate access based on roles
            if self.require_roles and not self._validate_access(roles):
                raise ValueError("Access denied: insufficient roles")
            
            # Store certificate and roles in request state
            request.state.client_certificate = client_cert
            request.state.client_roles = roles
            request.state.client_common_name = self._get_common_name(client_cert)
            
            logger.debug(f"mTLS authentication successful for {request.state.client_common_name} "
                        f"with roles: {roles}")
            
        except Exception as e:
            logger.error(f"mTLS authentication failed: {e}")
            raise
    
    def _extract_client_certificate(self, request: Request) -> Optional[x509.Certificate]:
        """
        Extract client certificate from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client certificate object or None if not found
        """
        try:
            # Check if client certificate is available in SSL context
            if hasattr(request, 'scope') and 'ssl' in request.scope:
                ssl_context = request.scope['ssl']
                if hasattr(ssl_context, 'getpeercert'):
                    cert_data = ssl_context.getpeercert(binary_form=True)
                    if cert_data:
                        return x509.load_der_x509_certificate(cert_data)
            
            # Check for certificate in headers (for proxy scenarios)
            cert_header = request.headers.get('ssl-client-cert')
            if cert_header:
                # Remove header prefix if present
                if cert_header.startswith('-----BEGIN CERTIFICATE-----'):
                    cert_data = cert_header.encode('utf-8')
                else:
                    # Assume it's base64 encoded
                    import base64
                    cert_data = base64.b64decode(cert_header)
                
                return x509.load_pem_x509_certificate(cert_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract client certificate: {e}")
            return None
    
    def _validate_client_certificate(self, cert: x509.Certificate) -> bool:
        """
        Validate client certificate.
        
        Args:
            cert: Client certificate object
            
        Returns:
            True if certificate is valid, False otherwise
        """
        try:
            if not self.verify_client:
                return True
            
            # Convert certificate to PEM format for validation
            cert_pem = cert.public_bytes(serialization.Encoding.PEM)
            
            # Use AuthValidator to validate certificate
            result = self.auth_validator.validate_certificate_data(cert_pem)
            if not result.is_valid:
                logger.warning(f"Certificate validation failed: {result.error_message}")
                return False
            
            # Validate certificate chain if CA is provided
            if self.ca_cert_path and self.ca_cert_path != "None":
                # Create temporary file for certificate
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='wb', suffix='.crt', delete=False) as f:
                    f.write(cert_pem)
                    temp_cert_path = f.name
                
                try:
                    chain_valid = self.certificate_utils.validate_certificate_chain(
                        temp_cert_path, self.ca_cert_path
                    )
                    if not chain_valid:
                        logger.warning("Certificate chain validation failed")
                        return False
                finally:
                    os.unlink(temp_cert_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate client certificate: {e}")
            return False
    
    def _extract_roles_from_certificate(self, cert: x509.Certificate) -> List[str]:
        """
        Extract roles from client certificate.
        
        Args:
            cert: Client certificate object
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            return self.certificate_utils.extract_roles_from_certificate_object(cert)
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def _validate_access(self, roles: List[str]) -> bool:
        """
        Validate access based on roles.
        
        Args:
            roles: List of roles from client certificate
            
        Returns:
            True if access is allowed, False otherwise
        """
        try:
            if not self.allowed_roles:
                return True
            
            if not roles:
                return False
            
            # Check if any of the client roles match allowed roles
            for client_role in roles:
                for allowed_role in self.allowed_roles:
                    if self.role_utils.compare_roles(client_role, allowed_role):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to validate access: {e}")
            return False
    
    def _get_common_name(self, cert: x509.Certificate) -> str:
        """
        Get common name from certificate.
        
        Args:
            cert: Certificate object
            
        Returns:
            Common name or empty string if not found
        """
        try:
            for name_attribute in cert.subject:
                if name_attribute.oid == x509.NameOID.COMMON_NAME:
                    return str(name_attribute.value)
            return ""
        except Exception as e:
            logger.error(f"Failed to get common name: {e}")
            return ""
    
    async def handle_error(self, request: Request, exception: Exception) -> Response:
        """
        Handle mTLS authentication errors.
        
        Args:
            request: FastAPI request object
            exception: Exception that occurred
            
        Returns:
            Error response
        """
        from fastapi.responses import JSONResponse
        
        error_message = str(exception)
        
        if "certificate is required" in error_message.lower():
            status_code = 401
            error_code = -32009  # Certificate not found
        elif "validation failed" in error_message.lower():
            status_code = 401
            error_code = -32003  # Certificate validation failed
        elif "access denied" in error_message.lower():
            status_code = 403
            error_code = -32007  # Role validation failed
        else:
            status_code = 500
            error_code = -32603  # Internal error
        
        return JSONResponse(
            status_code=status_code,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": error_code,
                    "message": error_message,
                    "data": {
                        "validation_type": "mtls",
                        "request_id": getattr(request.state, 'request_id', None)
                    }
                },
                "id": None
            }
        ) 