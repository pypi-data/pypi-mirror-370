"""
Rate Limit Middleware Adapter for backward compatibility.

This module provides an adapter that maintains the same interface as RateLimitMiddleware
while using the new SecurityMiddleware internally.
"""

import time
from typing import Dict, List, Callable, Awaitable, Any
from collections import defaultdict

from fastapi import Request, Response
from starlette.responses import JSONResponse

from mcp_proxy_adapter.core.logging import logger
from .base import BaseMiddleware
from .security import SecurityMiddleware


class RateLimitMiddlewareAdapter(BaseMiddleware):
    """
    Adapter for RateLimitMiddleware that uses SecurityMiddleware internally.
    
    Maintains the same interface as the original RateLimitMiddleware for backward compatibility.
    """
    
    def __init__(self, app, rate_limit: int = 100, time_window: int = 60, 
                 by_ip: bool = True, by_user: bool = True,
                 public_paths: List[str] = None):
        """
        Initialize rate limit middleware adapter.
        
        Args:
            app: FastAPI application
            rate_limit: Maximum number of requests in the specified time period
            time_window: Time period in seconds
            by_ip: Limit requests by IP address
            by_user: Limit requests by user
            public_paths: List of paths for which rate limiting is not applied
        """
        super().__init__(app)
        
        # Store original parameters for backward compatibility
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
        
        # Legacy storage for backward compatibility
        self.ip_requests = defaultdict(list)
        self.user_requests = defaultdict(list)
        
        # Create internal security middleware
        self.security_middleware = self._create_security_middleware()
        
        logger.info(f"RateLimitMiddlewareAdapter initialized: rate_limit={rate_limit}, "
                   f"time_window={time_window}, by_ip={by_ip}, by_user={by_user}")
    
    def _create_security_middleware(self) -> SecurityMiddleware:
        """
        Create internal SecurityMiddleware with RateLimitMiddleware configuration.
        
        Returns:
            SecurityMiddleware instance
        """
        # Convert RateLimitMiddleware config to SecurityMiddleware config
        security_config = {
            "security": {
                "enabled": True,
                "auth": {
                    "enabled": False
                },
                "ssl": {
                    "enabled": False
                },
                "permissions": {
                    "enabled": False
                },
                "rate_limit": {
                    "enabled": True,
                    "requests_per_minute": self.rate_limit,
                    "requests_per_hour": self.rate_limit * 60,
                    "burst_limit": self.rate_limit // 10,
                    "by_ip": self.by_ip,
                    "by_user": self.by_user
                },
                "public_paths": self.public_paths
            }
        }
        
        return SecurityMiddleware(self.app, security_config)
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process request using internal SecurityMiddleware with legacy fallback.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        # Check if path is public
        path = request.url.path
        if self._is_public_path(path):
            return await call_next(request)
        
        # Try to use SecurityMiddleware first
        try:
            await self.security_middleware.before_request(request)
            return await call_next(request)
            
        except Exception as e:
            # Fallback to legacy rate limiting if SecurityMiddleware fails
            logger.warning(f"SecurityMiddleware rate limiting failed, using legacy fallback: {e}")
            return await self._legacy_rate_limit_check(request, call_next)
    
    async def _legacy_rate_limit_check(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Legacy rate limiting implementation as fallback.
        
        Args:
            request: Request object
            call_next: Next handler
            
        Returns:
            Response object
        """
        current_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        username = getattr(request.state, "username", None)
        
        # Check limit by IP
        if self.by_ip and client_ip != "unknown":
            self._clean_old_requests(self.ip_requests[client_ip], current_time)
            
            if len(self.ip_requests[client_ip]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return self._create_error_response("Rate limit exceeded", 429)
            
            self.ip_requests[client_ip].append(current_time)
        
        # Check limit by user
        if self.by_user and username:
            self._clean_old_requests(self.user_requests[username], current_time)
            
            if len(self.user_requests[username]) >= self.rate_limit:
                logger.warning(f"Rate limit exceeded for user: {username}")
                return self._create_error_response("Rate limit exceeded", 429)
            
            self.user_requests[username].append(current_time)
        
        return await call_next(request)
    
    def _clean_old_requests(self, requests_list: List[float], current_time: float) -> None:
        """
        Remove old requests from the list.
        
        Args:
            requests_list: List of request timestamps
            current_time: Current time
        """
        cutoff_time = current_time - self.time_window
        requests_list[:] = [req_time for req_time in requests_list if req_time > cutoff_time]
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if the path is public (doesn't require rate limiting).
        
        Args:
            path: Request path
            
        Returns:
            True if path is public, False otherwise
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
    
    def _create_error_response(self, message: str, status_code: int) -> JSONResponse:
        """
        Create error response in RateLimitMiddleware format.
        
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
                    "code": -32008 if status_code == 429 else -32603,
                    "message": message,
                    "data": {
                        "rate_limit": self.rate_limit,
                        "time_window": self.time_window,
                        "status_code": status_code
                    }
                },
                "id": None
            }
        )
    
    def get_rate_limit_info(self, request: Request) -> Dict[str, Any]:
        """
        Get rate limit information for the request (backward compatibility).
        
        Args:
            request: Request object
            
        Returns:
            Dictionary with rate limit information
        """
        client_ip = request.client.host if request.client else "unknown"
        username = getattr(request.state, "username", None)
        
        info = {
            "rate_limit": self.rate_limit,
            "time_window": self.time_window,
            "by_ip": self.by_ip,
            "by_user": self.by_user
        }
        
        if self.by_ip and client_ip != "unknown":
            info["ip_requests"] = len(self.ip_requests[client_ip])
            info["ip_remaining"] = max(0, self.rate_limit - len(self.ip_requests[client_ip]))
        
        if self.by_user and username:
            info["user_requests"] = len(self.user_requests[username])
            info["user_remaining"] = max(0, self.rate_limit - len(self.user_requests[username]))
        
        return info
