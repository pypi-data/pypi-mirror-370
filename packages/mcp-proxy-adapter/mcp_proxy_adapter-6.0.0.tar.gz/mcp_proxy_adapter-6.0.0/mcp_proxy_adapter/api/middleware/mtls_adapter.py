"""
MTLS Middleware Adapter for backward compatibility.

This module provides an adapter that maintains the same interface as MTLSMiddleware
while using the new SecurityMiddleware internally.
"""

import logging
from typing import Dict, List, Optional, Any, Callable, Awaitable
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.auth_validator import AuthValidator
from mcp_proxy_adapter.core.role_utils import RoleUtils
from mcp_proxy_adapter.core.certificate_utils import CertificateUtils
from .base import BaseMiddleware
from .security import SecurityMiddleware


class MTLSMiddlewareAdapter(BaseMiddleware):
    """
    Adapter for MTLSMiddleware that uses SecurityMiddleware internally.
    
    Maintains the same interface as the original MTLSMiddleware for backward compatibility.
    """
    
    def __init__(self, app, mtls_config: Dict[str, Any]):
        """
        Initialize mTLS middleware adapter.
        
        Args:
            app: FastAPI application
            mtls_config: mTLS configuration dictionary
        """
        super().__init__(app)
        
        # Store original configuration for backward compatibility
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
        
        # Create internal security middleware
        self.security_middleware = self._create_security_middleware()
        
        logger.info(f"MTLSMiddlewareAdapter initialized: enabled={self.enabled}, "
                   f"verify_client={self.verify_client}, "
                   f"client_cert_required={self.client_cert_required}")
    
    def _create_security_middleware(self) -> SecurityMiddleware:
        """
        Create internal SecurityMiddleware with MTLSMiddleware configuration.
        
        Returns:
            SecurityMiddleware instance
        """
        # Convert MTLSMiddleware config to SecurityMiddleware config
        security_config = {
            "security": {
                "enabled": self.enabled,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": self.enabled,
                    "cert_file": None,
                    "key_file": None,
                    "ca_cert": self.ca_cert_path,
                    "min_tls_version": "TLSv1.2",
                    "verify_client": self.verify_client,
                    "client_cert_required": self.client_cert_required
                },
                "permissions": {
                    "enabled": self.require_roles,
                    "roles_file": None,
                    "default_role": "user",
                    "deny_by_default": True
                },
                "rate_limit": {
                    "enabled": False
                }
            }
        }
        
        return SecurityMiddleware(self.app, security_config)
    
    async def before_request(self, request: Request) -> None:
        """
        Process request before calling the main handler.
        
        Args:
            request: FastAPI request object
        """
        if not self.enabled:
            return
        
        try:
            # Use SecurityMiddleware for validation
            await self.security_middleware.before_request(request)
            
            # Additional MTLS-specific processing
            client_cert = self._extract_client_certificate(request)
            if client_cert:
                # Store certificate and roles in request state for backward compatibility
                request.state.client_certificate = client_cert
                request.state.client_roles = self._extract_roles_from_certificate(client_cert)
                request.state.client_common_name = self._get_common_name(client_cert)
                
                logger.debug(f"mTLS authentication successful for {request.state.client_common_name} "
                            f"with roles: {request.state.client_roles}")
            
        except Exception as e:
            logger.error(f"mTLS authentication failed: {e}")
            raise
    
    def _extract_client_certificate(self, request: Request) -> Optional[x509.Certificate]:
        """
        Extract client certificate from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client certificate or None
        """
        # Check for certificate in request headers
        cert_header = request.headers.get("X-Client-Cert")
        if cert_header:
            try:
                cert_data = cert_header.encode('utf-8')
                return x509.load_pem_x509_certificate(cert_data)
            except Exception as e:
                logger.warning(f"Failed to parse certificate from header: {e}")
        
        # Check for certificate in request state (from SSL context)
        if hasattr(request, 'client') and hasattr(request.client, 'get_extra_info'):
            cert = request.client.get_extra_info('ssl_object')
            if cert:
                return cert
        
        return None
    
    def _validate_client_certificate(self, cert: x509.Certificate) -> bool:
        """
        Validate client certificate.
        
        Args:
            cert: Client certificate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic validation
            if not self.certificate_utils.is_certificate_valid(cert):
                return False
            
            # CA validation if CA cert is provided
            if self.ca_cert_path:
                return self.certificate_utils.validate_certificate_chain(cert, self.ca_cert_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False
    
    def _extract_roles_from_certificate(self, cert: x509.Certificate) -> List[str]:
        """
        Extract roles from client certificate.
        
        Args:
            cert: Client certificate
            
        Returns:
            List of roles
        """
        try:
            # Extract from subject alternative names
            roles = []
            
            # Check for roles in SAN
            san = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            if san:
                for name in san.value:
                    if isinstance(name, x509.DNSName):
                        if name.value.startswith("role="):
                            role = name.value.split("=", 1)[1]
                            roles.append(role)
            
            # Check for roles in subject
            subject = cert.subject
            for attr in subject:
                if attr.oid.dotted_string == "2.5.4.3":  # Common Name
                    if attr.value.startswith("role="):
                        role = attr.value.split("=", 1)[1]
                        roles.append(role)
            
            # Check allowed roles if specified
            if self.allowed_roles:
                roles = [role for role in roles if role in self.allowed_roles]
            
            return roles
            
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def _get_common_name(self, cert: x509.Certificate) -> str:
        """
        Get common name from certificate.
        
        Args:
            cert: Client certificate
            
        Returns:
            Common name
        """
        try:
            subject = cert.subject
            for attr in subject:
                if attr.oid.dotted_string == "2.5.4.3":  # Common Name
                    return attr.value
            return "unknown"
        except Exception:
            return "unknown"
    
    def _validate_access(self, roles: List[str]) -> bool:
        """
        Validate access based on roles.
        
        Args:
            roles: List of client roles
            
        Returns:
            True if access is allowed, False otherwise
        """
        if not self.require_roles:
            return True
        
        if not roles:
            return False
        
        # Check if any role is allowed
        return any(role in self.allowed_roles for role in roles)
    
    def get_client_certificate(self, request: Request) -> Optional[x509.Certificate]:
        """
        Get client certificate from request state (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            Client certificate or None
        """
        return getattr(request.state, 'client_certificate', None)
    
    def get_client_roles(self, request: Request) -> List[str]:
        """
        Get client roles from request state (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            List of client roles
        """
        return getattr(request.state, 'client_roles', [])
    
    def get_client_common_name(self, request: Request) -> str:
        """
        Get client common name from request state (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            Client common name
        """
        return getattr(request.state, 'client_common_name', 'unknown')
    
    def is_mtls_authenticated(self, request: Request) -> bool:
        """
        Check if request is mTLS authenticated (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            True if mTLS authenticated, False otherwise
        """
        return hasattr(request.state, 'client_certificate') and request.state.client_certificate is not None
