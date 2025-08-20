"""
Middleware for rate limiting.
"""

import time
from typing import Dict, List, Callable, Awaitable
from collections import defaultdict

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware

class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware for limiting request rate.
    """
    
    def __init__(self, app, rate_limit: int = 100, time_window: int = 60, 
                 by_ip: bool = True, by_user: bool = True,
                 public_paths: List[str] = None):
        """
        Initializes middleware for rate limiting.
        
        Args:
            app: FastAPI application
            rate_limit: Maximum number of requests in the specified time period
            time_window: Time period in seconds
            by_ip: Limit requests by IP address
            by_user: Limit requests by user
            public_paths: List of paths for which rate limiting is not applied
        """
        super().__init__(app)
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.by_ip = by_ip
        self.by_user = by_user
        self.public_paths = public_paths or [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health"
        ]
        
        # Storage for requests by IP
        self.ip_requests = defaultdict(list)
        
        # Storage for requests by user
        self.user_requests = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Processes request and checks rate limit.
        
        Args:
            request: Request.
            call_next: Next handler.
            
        Returns:
            Response.
        """
        # Check if path is public
        path = request.url.path
        if self._is_public_path(path):
            # If path is public, skip rate limiting
            return await call_next(request)
        
        # Current time
        current_time = time.time()
        
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user from request state (if any)
        username = getattr(request.state, "username", None)
        
        # Check limit by IP
        if self.by_ip and client_ip != "unknown":
            # Clean old requests
            self._clean_old_requests(self.ip_requests[client_ip], current_time)
            
            # Check number of requests
            if len(self.ip_requests[client_ip]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip} | Path: {path}")
                return self._create_error_response("Rate limit exceeded", 429)
            
            # Add current request
            self.ip_requests[client_ip].append(current_time)
        
        # Check limit by user
        if self.by_user and username:
            # Clean old requests
            self._clean_old_requests(self.user_requests[username], current_time)
            
            # Check number of requests
            if len(self.user_requests[username]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for user: {username} | Path: {path}")
                return self._create_error_response("Rate limit exceeded", 429)
            
            # Add current request
            self.user_requests[username].append(current_time)
        
        # Call the next middleware or main handler
        return await call_next(request)
    
    def _clean_old_requests(self, requests: List[float], current_time: float) -> None:
        """
        Cleans old requests that are outside the time window.
        
        Args:
            requests: List of request timestamps.
            current_time: Current time.
        """
        min_time = current_time - self.time_window
        while requests and requests[0] < min_time:
            requests.pop(0)
    
    def _is_public_path(self, path: str) -> bool:
        """
        Checks if the path is public.
        
        Args:
            path: Path to check.
            
        Returns:
            True if path is public, False otherwise.
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
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