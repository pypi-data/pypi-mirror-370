"""
Roles Middleware

This module provides middleware for role-based access control (RBAC).
Validates client roles against server roles and permissions.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from cryptography import x509

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ...core.auth_validator import AuthValidator
from ...core.role_utils import RoleUtils
from ...core.certificate_utils import CertificateUtils
from .base import BaseMiddleware

logger = logging.getLogger(__name__)


class RolesMiddleware(BaseMiddleware):
    """
    Middleware for role-based access control.
    
    Validates client roles against server roles and permissions,
    integrates with mTLS middleware for certificate-based authentication.
    """
    
    def __init__(self, app, roles_config_path: str):
        """
        Initialize roles middleware.
        
        Args:
            app: FastAPI application
            roles_config_path: Path to roles configuration file
        """
        super().__init__(app)
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
        
        logger.info(f"Roles middleware initialized: enabled={self.enabled}, "
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
                "allow_wildcard": True
            },
            "roles": {
                "admin": {
                    "description": "Administrator with full access",
                    "allowed_servers": ["*"],
                    "allowed_clients": ["*"],
                    "permissions": ["read", "write", "delete", "admin"],
                    "priority": 100
                }
            },
            "server_roles": {},
            "role_hierarchy": {}
        }
    
    async def before_request(self, request: Request) -> None:
        """
        Process request before calling the main handler.
        
        Args:
            request: FastAPI request object
        """
        if not self.enabled:
            return
        
        # Skip role validation for OpenAPI schema endpoint
        if request.url.path == "/openapi.json":
            return
        
        try:
            # Extract client roles from request state (set by mTLS middleware)
            client_roles = getattr(request.state, 'client_roles', [])
            client_cert = getattr(request.state, 'client_certificate', None)
            
            # If no roles from mTLS, try to extract from certificate
            if not client_roles and client_cert:
                client_roles = self._extract_roles_from_certificate(client_cert)
            
            # Extract server role from request
            server_role = self._extract_server_role(request)
            
            # Validate access based on roles
            if not self._validate_access(client_roles, server_role, request):
                raise ValueError("Access denied: insufficient roles or permissions")
            
            # Store roles in request state for downstream middleware
            request.state.client_roles = client_roles
            request.state.server_role = server_role
            request.state.role_validation_passed = True
            
            logger.debug(f"Role validation successful for client roles: {client_roles}, "
                        f"server role: {server_role}")
            
        except Exception as e:
            logger.error(f"Role validation failed: {e}")
            request.state.role_validation_passed = False
            request.state.role_validation_error = str(e)
    
    def _extract_roles_from_certificate(self, cert: x509.Certificate) -> List[str]:
        """
        Extract roles from certificate using RoleUtils.
        
        Args:
            cert: Certificate object
            
        Returns:
            List of roles extracted from certificate
        """
        try:
            return self.role_utils.extract_roles_from_certificate_object(cert)
        except Exception as e:
            logger.error(f"Failed to extract roles from certificate: {e}")
            return []
    
    def _extract_server_role(self, request: Request) -> str:
        """
        Extract server role from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Server role string
        """
        # Try to extract from path
        path = request.url.path
        
        # Check if path contains server role information
        if path.startswith('/api/'):
            parts = path.split('/')
            if len(parts) > 2:
                potential_role = parts[2]
                if potential_role in self.server_roles:
                    return potential_role
        
        # Check from headers
        server_role_header = request.headers.get('X-Server-Role')
        if server_role_header and server_role_header in self.server_roles:
            return server_role_header
        
        # Default to 'basic_commands' if no specific role found
        return 'basic_commands'
    
    def _validate_access(self, client_roles: List[str], server_role: str, 
                        request: Request) -> bool:
        """
        Validate access based on client roles and server role.
        
        Args:
            client_roles: List of client roles
            server_role: Server role
            request: FastAPI request object
            
        Returns:
            True if access is allowed, False otherwise
        """
        # Check default policy
        deny_by_default = self.default_policy.get("deny_by_default", True)
        require_role_match = self.default_policy.get("require_role_match", True)
        
        # If no client roles and deny by default, deny access
        if not client_roles and deny_by_default:
            logger.warning("Access denied: no client roles provided and deny_by_default is True")
            return False
        
        # If no server role found, allow if not requiring role match
        if not server_role and not require_role_match:
            return True
        
        # Get server role configuration
        server_config = self.server_roles.get(server_role, {})
        required_roles = server_config.get("required_roles", [])
        
        # If no required roles specified, allow access
        if not required_roles:
            return True
        
        # Check if client has any of the required roles
        for client_role in client_roles:
            if self._has_required_role(client_role, required_roles):
                return True
        
        # Check role hierarchy
        for client_role in client_roles:
            if self._has_role_in_hierarchy(client_role, required_roles):
                return True
        
        logger.warning(f"Access denied: client roles {client_roles} do not match "
                      f"required roles {required_roles} for server role {server_role}")
        return False
    
    def _has_required_role(self, client_role: str, required_roles: List[str]) -> bool:
        """
        Check if client role matches any required role.
        
        Args:
            client_role: Client role to check
            required_roles: List of required roles
            
        Returns:
            True if client role matches any required role
        """
        # Use RoleUtils for case-insensitive comparison
        for required_role in required_roles:
            if self.role_utils.compare_roles(client_role, required_role):
                return True
        
        # Check for wildcard
        if "*" in required_roles:
            return True
        
        return False
    
    def _has_role_in_hierarchy(self, client_role: str, required_roles: List[str]) -> bool:
        """
        Check if client role has any required role in its hierarchy.
        
        Args:
            client_role: Client role to check
            required_roles: List of required roles
            
        Returns:
            True if client role has any required role in hierarchy
        """
        # Get client role hierarchy
        client_hierarchy = self._get_role_hierarchy(client_role)
        
        # Check if any role in hierarchy matches required roles
        for hierarchy_role in client_hierarchy:
            if self._has_required_role(hierarchy_role, required_roles):
                return True
        
        return False
    
    def _get_role_hierarchy(self, role: str) -> List[str]:
        """
        Get role hierarchy for a given role.
        
        Args:
            role: Role to get hierarchy for
            
        Returns:
            List of roles in hierarchy
        """
        return self.role_hierarchy.get(role, [])
    
    def _validate_permissions(self, client_roles: List[str], required_permissions: List[str]) -> bool:
        """
        Validate if client roles have required permissions.
        
        Args:
            client_roles: List of client roles
            required_permissions: List of required permissions
            
        Returns:
            True if client has required permissions
        """
        for client_role in client_roles:
            role_config = self.roles.get(client_role, {})
            role_permissions = role_config.get("permissions", [])
            
            # Check if role has all required permissions
            if all(perm in role_permissions for perm in required_permissions):
                return True
        
        return False
    
    def get_client_roles(self, request: Request) -> List[str]:
        """
        Get client roles from request state.
        
        Args:
            request: FastAPI request object
            
        Returns:
            List of client roles
        """
        return getattr(request.state, 'client_roles', [])
    
    def get_server_role(self, request: Request) -> str:
        """
        Get server role from request state.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Server role string
        """
        return getattr(request.state, 'server_role', '')
    
    def is_role_validation_passed(self, request: Request) -> bool:
        """
        Check if role validation passed.
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if role validation passed
        """
        return getattr(request.state, 'role_validation_passed', False)
    
    def get_role_validation_error(self, request: Request) -> Optional[str]:
        """
        Get role validation error message.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Error message if validation failed, None otherwise
        """
        return getattr(request.state, 'role_validation_error', None) 