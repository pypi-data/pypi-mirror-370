"""
Auth Middleware Adapter for backward compatibility.

This module provides an adapter that maintains the same interface as AuthMiddleware
while using the new SecurityMiddleware internally.
"""

import json
from typing import Dict, List, Optional, Callable, Awaitable

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware
from .security import SecurityMiddleware


class AuthMiddlewareAdapter(BaseMiddleware):
    """
    Adapter for AuthMiddleware that uses SecurityMiddleware internally.
    
    Maintains the same interface as the original AuthMiddleware for backward compatibility.
    """
    
    def __init__(self, app, api_keys: Dict[str, str] = None, 
                 public_paths: List[str] = None, auth_enabled: bool = True):
        """
        Initialize auth middleware adapter.
        
        Args:
            app: FastAPI application
            api_keys: Dictionary with API keys (key: username)
            public_paths: List of paths accessible without authentication
            auth_enabled: Flag to enable/disable authentication
        """
        super().__init__(app)
        
        # Store original parameters for backward compatibility
        self.api_keys = api_keys or {}
        self.public_paths = public_paths or [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health"
        ]
        self.auth_enabled = auth_enabled
        
        # Create internal security middleware
        self.security_middleware = self._create_security_middleware()
        
        logger.info(f"AuthMiddlewareAdapter initialized: auth_enabled={auth_enabled}, "
                   f"api_keys_count={len(self.api_keys)}, public_paths_count={len(self.public_paths)}")
    
    def _create_security_middleware(self) -> SecurityMiddleware:
        """
        Create internal SecurityMiddleware with AuthMiddleware configuration.
        
        Returns:
            SecurityMiddleware instance
        """
        # Convert AuthMiddleware config to SecurityMiddleware config
        security_config = {
            "security": {
                "enabled": self.auth_enabled,
                "auth": {
                    "enabled": self.auth_enabled,
                    "methods": ["api_key"],
                    "api_keys": self.api_keys
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": False
                },
                "rate_limit": {
                    "enabled": False
                },
                "public_paths": self.public_paths
            }
        }
        
        return SecurityMiddleware(self.app, security_config)
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request using internal SecurityMiddleware with legacy API key handling.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        # Check if authentication is disabled
        if not self.auth_enabled:
            logger.debug("Authentication is disabled, skipping authentication check")
            return await call_next(request)
        
        # Check if path is public
        path = request.url.path
        if self._is_public_path(path):
            return await call_next(request)
        
        # Extract API key from various sources (legacy compatibility)
        api_key = self._extract_api_key(request)
        
        # Check for API key in JSON-RPC request body if not found in headers/query
        if not api_key and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    try:
                        body_json = json.loads(body.decode("utf-8"))
                        # Look for API key in params of JSON-RPC object
                        if isinstance(body_json, dict) and "params" in body_json:
                            api_key = body_json.get("params", {}).get("api_key")
                    except json.JSONDecodeError:
                        pass
            except Exception:
                pass
        
        if api_key:
            # Validate API key
            username = self._validate_api_key(api_key)
            if username:
                # Store username in request state for backward compatibility
                request.state.username = username
                logger.debug(f"API key authentication successful for {username}")
                return await call_next(request)
            else:
                logger.warning(f"Invalid API key provided | Path: {path}")
                return self._create_error_response("Invalid API key", 401)
        else:
            logger.warning(f"API key not provided | Path: {path}")
            return self._create_error_response("API key not provided", 401)
    
    def _extract_api_key(self, request: Request) -> Optional[str]:
        """
        Extract API key from request (legacy compatibility).
        
        Args:
            request: Request object
            
        Returns:
            API key or None
        """
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            # Check for API key in query parameters
            api_key = request.query_params.get("api_key")
        
        # Note: Body extraction is handled in dispatch method
        # This method only handles headers and query parameters
        
        return api_key
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if the path is public (doesn't require authentication).
        
        Args:
            path: Request path
            
        Returns:
            True if path is public, False otherwise
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    def _validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validate API key and return username.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Username if valid, None otherwise
        """
        return self.api_keys.get(api_key)
    
    def _create_error_response(self, message: str, status_code: int) -> JSONResponse:
        """
        Create error response in AuthMiddleware format.
        
        Args:
            message: Error message
            status_code: HTTP status code
            
        Returns:
            JSONResponse with error
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000 if status_code == 401 else -32603,
                    "message": message,
                    "data": {
                        "auth_type": "api_key",
                        "status_code": status_code
                    }
                },
                "id": None
            }
        )
    
    def get_username(self, request: Request) -> Optional[str]:
        """
        Get username from request state (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            Username or None
        """
        return getattr(request.state, 'username', None)
    
    def is_authenticated(self, request: Request) -> bool:
        """
        Check if request is authenticated (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            True if authenticated, False otherwise
        """
        return hasattr(request.state, 'username') and request.state.username is not None
