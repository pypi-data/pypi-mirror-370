"""
Unified Security Middleware for mcp_security_framework integration.

This module provides a single middleware that replaces AuthMiddleware, RateLimitMiddleware,
MTLSMiddleware, and RolesMiddleware with a unified security solution.
"""

import json
import logging
from typing import Callable, Awaitable, Dict, Any, Optional

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.security_factory import SecurityFactory
from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware


class SecurityMiddleware(BaseMiddleware):
    """
    Unified security middleware based on mcp_security_framework.
    
    Replaces AuthMiddleware, RateLimitMiddleware, MTLSMiddleware, and RolesMiddleware
    with a single, comprehensive security solution.
    """
    
    def __init__(self, app, config: Dict[str, Any]):
        """
        Initialize unified security middleware.
        
        Args:
            app: FastAPI application
            config: mcp_proxy_adapter configuration dictionary
        """
        super().__init__(app)
        self.config = config
        self.security_config = config.get("security", {})
        
        # Create security adapter
        self.security_adapter = SecurityFactory.create_security_adapter(config)
        
        # Public paths that don't require security validation
        self.public_paths = [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health",
            "/favicon.ico"
        ]
        
        # Add custom public paths from config
        custom_public_paths = self.security_config.get("public_paths", [])
        self.public_paths.extend(custom_public_paths)
        
        logger.info(f"Security middleware initialized with {len(self.public_paths)} public paths")
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request and handle security validation.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        try:
            # Process request before calling the main handler
            await self.before_request(request)
            
            # Call the next middleware or main handler
            return await call_next(request)
            
        except SecurityValidationError as e:
            # Handle security validation errors
            return await self.handle_error(request, e)
        except Exception as e:
            # Handle other errors
            logger.error(f"Unexpected error in security middleware: {e}")
            return await self.handle_error(request, e)
    
    async def before_request(self, request: Request) -> None:
        """
        Process request before calling the main handler.
        
        Args:
            request: FastAPI request object
        """
        # Check if security is enabled
        if not self.security_config.get("enabled", True):
            logger.debug("Security middleware disabled, skipping validation")
            return
        
        # Check if path is public
        path = request.url.path
        if self._is_public_path(path):
            logger.debug(f"Public path accessed: {path}")
            return
        
        try:
            # Prepare request data for validation
            request_data = await self._prepare_request_data_async(request)
            
            # Validate request through security framework
            logger.debug(f"Validating request data: {request_data}")
            validation_result = self.security_adapter.validate_request(request_data)
            logger.debug(f"Validation result: {validation_result}")
            
            if not validation_result.get("is_valid", False):
                error_message = validation_result.get("error_message", "Security validation failed")
                error_code = validation_result.get("error_code", -32000)
                raise SecurityValidationError(error_message, error_code)
            
            # Store validation results in request state
            request.state.security_result = validation_result
            request.state.user_roles = validation_result.get("roles", [])
            request.state.user_id = validation_result.get("user_id")
            request.state.security_validated = True
            
            logger.debug(f"Security validation successful for {request.state.user_id} "
                        f"with roles: {request.state.user_roles}")
            
        except SecurityValidationError as e:
            # Re-raise security validation errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in security validation: {e}")
            raise SecurityValidationError(f"Internal security error: {str(e)}", -32603)
    
    async def _prepare_request_data_async(self, request: Request) -> Dict[str, Any]:
        """
        Prepare request data for security validation (async version).
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with request data for validation
        """
        # Extract basic request information
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "body": {}
        }
        
        # Extract request body for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        request_data["body"] = json.loads(body.decode("utf-8"))
                    except json.JSONDecodeError:
                        # If not JSON, store as string
                        request_data["body"] = body.decode("utf-8", errors="ignore")
            except Exception as e:
                logger.warning(f"Failed to extract request body: {e}")
        
        return request_data
    
    def _prepare_request_data(self, request: Request) -> Dict[str, Any]:
        """
        Prepare request data for security validation (sync version).
        
        Args:
            request: FastAPI request object
            
        Returns:
            Dictionary with request data for validation
        """
        # Extract basic request information
        request_data = {
            "method": request.method,
            "path": request.url.path,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "client_ip": self._get_client_ip(request),
            "body": {}
        }
        
        return request_data
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address string
        """
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to client host
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if the path is public (doesn't require security validation).
        
        Args:
            path: Request path
            
        Returns:
            True if path is public, False otherwise
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    async def handle_error(self, request: Request, exception: Exception) -> Response:
        """
        Handle security validation errors.
        
        Args:
            request: FastAPI request object
            exception: Exception that occurred
            
        Returns:
            Error response
        """
        if isinstance(exception, SecurityValidationError):
            status_code = self._get_status_code_for_error(exception.error_code)
            error_code = exception.error_code
            error_message = exception.message
        else:
            status_code = 500
            error_code = -32603
            error_message = "Internal server error"
        
        logger.warning(f"Security validation failed: {error_message} | "
                      f"Path: {request.url.path} | Code: {error_code}")
        
        return JSONResponse(
            status_code=status_code,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": error_code,
                    "message": error_message,
                    "data": {
                        "validation_type": "security",
                        "path": request.url.path,
                        "method": request.method,
                        "client_ip": self._get_client_ip(request)
                    }
                },
                "id": None
            }
        )
    
    def _get_status_code_for_error(self, error_code: int) -> int:
        """
        Map security error codes to HTTP status codes.
        
        Args:
            error_code: Security error code
            
        Returns:
            HTTP status code
        """
        error_code_mapping = {
            -32000: 401,  # Authentication failed
            -32001: 401,  # Authentication disabled
            -32002: 500,  # Invalid configuration
            -32003: 401,  # Certificate validation failed
            -32004: 401,  # Token validation failed
            -32005: 401,  # MTLS validation failed
            -32006: 401,  # SSL validation failed
            -32007: 403,  # Role validation failed
            -32008: 401,  # Certificate expired
            -32009: 401,  # Certificate not found
            -32010: 401,  # Token expired
            -32011: 401,  # Token not found
            -32603: 500,  # Internal error
        }
        
        return error_code_mapping.get(error_code, 500)
    
    def get_user_roles(self, request: Request) -> list:
        """
        Get user roles from request state.
        
        Args:
            request: FastAPI request object
            
        Returns:
            List of user roles
        """
        return getattr(request.state, 'user_roles', [])
    
    def get_user_id(self, request: Request) -> Optional[str]:
        """
        Get user ID from request state.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User ID or None
        """
        return getattr(request.state, 'user_id', None)
    
    def is_security_validated(self, request: Request) -> bool:
        """
        Check if security validation passed for the request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            True if security validation passed
        """
        return getattr(request.state, 'security_validated', False)
    
    def has_role(self, request: Request, required_role: str) -> bool:
        """
        Check if user has required role.
        
        Args:
            request: FastAPI request object
            required_role: Required role to check
            
        Returns:
            True if user has required role
        """
        user_roles = self.get_user_roles(request)
        return required_role in user_roles or "*" in user_roles
    
    def has_any_role(self, request: Request, required_roles: list) -> bool:
        """
        Check if user has any of the required roles.
        
        Args:
            request: FastAPI request object
            required_roles: List of required roles
            
        Returns:
            True if user has any of the required roles
        """
        user_roles = self.get_user_roles(request)
        return any(role in user_roles for role in required_roles) or "*" in user_roles


class SecurityValidationError(Exception):
    """
    Exception raised when security validation fails.
    """
    
    def __init__(self, message: str, error_code: int):
        """
        Initialize security validation error.
        
        Args:
            message: Error message
            error_code: JSON-RPC error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
