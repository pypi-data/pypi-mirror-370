"""
Middleware for authentication.
"""

import json
from typing import Dict, List, Optional, Callable, Awaitable

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware

class AuthMiddleware(BaseMiddleware):
    """
    Middleware for authenticating requests.
    """
    
    def __init__(self, app, api_keys: Dict[str, str] = None, public_paths: List[str] = None, auth_enabled: bool = True):
        """
        Initializes middleware for authentication.
        
        Args:
            app: FastAPI application
            api_keys: Dictionary with API keys (key: username)
            public_paths: List of paths accessible without authentication
            auth_enabled: Flag to enable/disable authentication
        """
        super().__init__(app)
        self.api_keys = api_keys or {}
        self.public_paths = public_paths or [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health"
        ]
        self.auth_enabled = auth_enabled
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Processes request and checks authentication.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        # Check if authentication is disabled
        if not self.auth_enabled:
            logger.debug("Authentication is disabled, skipping authentication check")
            return await call_next(request)
            
        # Check if path is public
        path = request.url.path
        if self._is_public_path(path):
            # If path is public, skip authentication
            return await call_next(request)
        
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            # Check for API key in query parameters
            api_key = request.query_params.get("api_key")
        
        if not api_key and request.method in ["POST", "PUT", "PATCH"]:
            # Check for API key in JSON-RPC request body
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
        
        # If API key not found, return error
        if not api_key:
            logger.warning(f"Authentication failed: API key not provided | Path: {path}")
            return self._create_error_response("API key not provided", 401)
        
        # Check if API key is valid
        username = self._validate_api_key(api_key)
        if not username:
            logger.warning(f"Authentication failed: Invalid API key | Path: {path}")
            return self._create_error_response("Invalid API key", 401)
        
        # If API key is valid, save user information in request state
        request.state.username = username
        logger.info(f"Authentication successful: {username} | Path: {path}")
        
        # Call the next middleware or main handler
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """
        Checks if the path is public.
        
        Args:
            path: Path to check.
            
        Returns:
            True if path is public, False otherwise.
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    def _validate_api_key(self, api_key: str) -> Optional[str]:
        """
        Validates API key.
        
        Args:
            api_key: API key to validate.
            
        Returns:
            Username if API key is valid, otherwise None.
        """
        return self.api_keys.get(api_key)
    
    def _create_error_response(self, message: str, status_code: int) -> Response:
        """
        Creates error response in JSON-RPC format.
        
        Args:
            message: Error message.
            status_code: HTTP status code.
            
        Returns:
            JSON response with error.
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": message
                },
                "id": None
            }
        ) 