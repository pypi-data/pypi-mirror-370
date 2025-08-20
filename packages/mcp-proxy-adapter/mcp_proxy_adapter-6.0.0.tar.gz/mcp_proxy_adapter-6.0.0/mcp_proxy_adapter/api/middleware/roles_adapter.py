"""
Roles Middleware Adapter for backward compatibility.

This module provides an adapter that maintains the same interface as RolesMiddleware
while using the new SecurityMiddleware internally.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from pathlib import Path
from cryptography import x509

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from mcp_proxy_adapter.core.auth_validator import AuthValidator
from mcp_proxy_adapter.core.role_utils import RoleUtils
from mcp_proxy_adapter.core.certificate_utils import CertificateUtils
from .base import BaseMiddleware
from .security import SecurityMiddleware


class RolesMiddlewareAdapter(BaseMiddleware):
    """
    Adapter for RolesMiddleware that uses SecurityMiddleware internally.
    
    Maintains the same interface as the original RolesMiddleware for backward compatibility.
    """
    
    def __init__(self, app, roles_config_path: str):
        """
        Initialize roles middleware adapter.
        
        Args:
            app: FastAPI application
            roles_config_path: Path to roles configuration file
        """
        super().__init__(app)
        
        # Store original parameters for backward compatibility
        self.roles_config_path = roles_config_path
        self.auth_validator = AuthValidator()
        self.role_utils = RoleUtils()
        self.certificate_utils = CertificateUtils()
        
        # Load roles configuration
        self.roles_config = self._load_roles_config()
        
        # Check if roles are enabled and config file exists
        if not self.roles_config.get("enabled", True):
            logger.info("Roles middleware disabled by configuration")
            self.enabled = False
            return
        
        # Extract configuration
        self.enabled = self.roles_config.get("enabled", True)
        self.default_policy = self.roles_config.get("default_policy", {})
        self.roles = self.roles_config.get("roles", {})
        self.server_roles = self.roles_config.get("server_roles", {})
        self.role_hierarchy = self.roles_config.get("role_hierarchy", {})
        
        # Create internal security middleware
        self.security_middleware = self._create_security_middleware()
        
        logger.info(f"RolesMiddlewareAdapter initialized: enabled={self.enabled}, "
                   f"roles_count={len(self.roles)}, "
                   f"server_roles_count={len(self.server_roles)}")
    
    def _load_roles_config(self) -> Dict[str, Any]:
        """
        Load roles configuration from file.
        
        Returns:
            Roles configuration dictionary
        """
        try:
            config_path = Path(self.roles_config_path)
            if not config_path.exists():
                logger.error(f"Roles config file not found: {self.roles_config_path}")
                logger.error("Roles middleware will be disabled. Please create the roles schema file.")
                return {"enabled": False}
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            logger.info(f"Roles configuration loaded from {self.roles_config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load roles configuration: {e}")
            logger.error("Roles middleware will be disabled due to configuration error.")
            return {"enabled": False}
    
    def _create_security_middleware(self) -> SecurityMiddleware:
        """
        Create internal SecurityMiddleware with RolesMiddleware configuration.
        
        Returns:
            SecurityMiddleware instance
        """
        # Convert RolesMiddleware config to SecurityMiddleware config
        security_config = {
            "security": {
                "enabled": self.enabled,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": self.enabled,
                    "roles_file": self.roles_config_path,
                    "default_role": self.default_policy.get("default_role", "user"),
                    "deny_by_default": self.default_policy.get("deny_by_default", True)
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
            
            # Additional roles-specific processing
            client_roles = self._get_client_roles(request)
            if client_roles:
                # Validate roles against server roles
                if not self._validate_roles(client_roles):
                    raise ValueError("Access denied: insufficient roles")
                
                # Store roles in request state for backward compatibility
                request.state.client_roles = client_roles
                request.state.role_validation_passed = True
                
                logger.debug(f"Role validation successful for roles: {client_roles}")
            
        except Exception as e:
            logger.error(f"Role validation failed: {e}")
            raise
    
    def _get_client_roles(self, request: Request) -> List[str]:
        """
        Get client roles from various sources.
        
        Args:
            request: FastAPI request object
            
        Returns:
            List of client roles
        """
        roles = []
        
        # Get roles from request state (from other middleware)
        if hasattr(request.state, 'client_roles'):
            roles.extend(request.state.client_roles)
        
        # Get roles from certificate if available
        if hasattr(request.state, 'client_certificate'):
            cert_roles = self._extract_roles_from_certificate(request.state.client_certificate)
            roles.extend(cert_roles)
        
        # Get roles from headers
        header_roles = request.headers.get("X-Client-Roles")
        if header_roles:
            try:
                header_roles_list = json.loads(header_roles)
                if isinstance(header_roles_list, list):
                    roles.extend(header_roles_list)
            except json.JSONDecodeError:
                # Treat as comma-separated string
                roles.extend([role.strip() for role in header_roles.split(",")])
        
        # Remove duplicates and return
        return list(set(roles))
    
    def _extract_roles_from_certificate(self, cert: x509.Certificate) -> List[str]:
        """
        Extract roles from client certificate.
        
        Args:
            cert: Client certificate
            
        Returns:
            List of roles
        """
        try:
            roles = []
            
            # Extract from subject alternative names
            san = cert.extensions.get_extension_for_oid(x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
            if san:
                for name in san.value:
                    if isinstance(name, x509.DNSName):
                        if name.value.startswith("role="):
                            role = name.value.split("=", 1)[1]
                            roles.append(role)
            
            # Extract from subject
            subject = cert.subject
            for attr in subject:
                if attr.oid.dotted_string == "2.5.4.3":  # Common Name
                    if attr.value.startswith("role="):
                        role = attr.value.split("=", 1)[1]
                        roles.append(role)
            
            return roles
            
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def _validate_roles(self, client_roles: List[str]) -> bool:
        """
        Validate client roles against server roles.
        
        Args:
            client_roles: List of client roles
            
        Returns:
            True if roles are valid, False otherwise
        """
        if not client_roles:
            return self.default_policy.get("allow_empty_roles", False)
        
        # Check if any client role matches server roles
        for client_role in client_roles:
            if client_role in self.server_roles:
                return True
            
            # Check role hierarchy
            if client_role in self.role_hierarchy:
                inherited_roles = self.role_hierarchy[client_role]
                for inherited_role in inherited_roles:
                    if inherited_role in self.server_roles:
                        return True
        
        return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default roles configuration.
        
        Returns:
            Default roles configuration
        """
        return {
            "enabled": True,
            "default_policy": {
                "deny_by_default": True,
                "require_role_match": True,
                "case_sensitive": False,
                "allow_wildcard": True,
                "allow_empty_roles": False,
                "default_role": "user"
            },
            "roles": {
                "admin": {
                    "description": "Administrator",
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                },
                "user": {
                    "description": "Regular user",
                    "permissions": ["read", "write"],
                    "priority": 10
                },
                "guest": {
                    "description": "Guest user",
                    "permissions": ["read"],
                    "priority": 1
                }
            },
            "server_roles": ["admin", "user"],
            "role_hierarchy": {
                "admin": ["user", "guest"],
                "user": ["guest"]
            }
        }
    
    def get_client_roles(self, request: Request) -> List[str]:
        """
        Get client roles from request state (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            List of client roles
        """
        return getattr(request.state, 'client_roles', [])
    
    def is_role_validation_passed(self, request: Request) -> bool:
        """
        Check if role validation passed (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            True if role validation passed, False otherwise
        """
        return getattr(request.state, 'role_validation_passed', False)
    
    def has_role(self, request: Request, required_role: str) -> bool:
        """
        Check if client has required role (backward compatibility).
        
        Args:
            request: Request object
            required_role: Required role
            
        Returns:
            True if client has required role, False otherwise
        """
        client_roles = self.get_client_roles(request)
        return required_role in client_roles
    
    def has_any_role(self, request: Request, required_roles: List[str]) -> bool:
        """
        Check if client has any of the required roles (backward compatibility).
        
        Args:
            request: Request object
            required_roles: List of required roles
            
        Returns:
            True if client has any of the required roles, False otherwise
        """
        client_roles = self.get_client_roles(request)
        return any(role in client_roles for role in required_roles)
    
    def get_server_roles(self) -> List[str]:
        """
        Get server roles (backward compatibility).
        
        Returns:
            List of server roles
        """
        return self.server_roles
    
    def get_role_hierarchy(self) -> Dict[str, List[str]]:
        """
        Get role hierarchy (backward compatibility).
        
        Returns:
            Role hierarchy dictionary
        """
        return self.role_hierarchy
