"""
Token Authentication Middleware

This module provides middleware for token-based authentication using JWT and API tokens.
Supports extraction of tokens from headers and validation using AuthValidator.

Author: MCP Proxy Adapter Team
Version: 1.0.0
"""

import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ...core.auth_validator import AuthValidator, AuthValidationResult
from ...core.logging import logger


class TokenAuthMiddleware(BaseHTTPMiddleware):
    """
    Token authentication middleware.
    
    Validates JWT and API tokens from request headers.
    Integrates with AuthValidator for token validation.
    """
    
    def __init__(self, app, token_config: Dict[str, Any]):
        """
        Initialize token authentication middleware.
        
        Args:
            app: FastAPI application
            token_config: Token configuration dictionary
        """
        super().__init__(app)
        self.token_config = token_config
        self.auth_validator = AuthValidator()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.enabled = token_config.get("enabled", False)
        self.header_name = token_config.get("header_name", "Authorization")
        self.token_prefix = token_config.get("token_prefix", "Bearer")
        self.tokens_file = token_config.get("tokens_file", "tokens.json")
        self.token_expiry = token_config.get("token_expiry", 3600)
        self.jwt_secret = token_config.get("jwt_secret", "")
        self.jwt_algorithm = token_config.get("jwt_algorithm", "HS256")
        
        # Load tokens if file exists
        self.tokens = self._load_tokens()
        
        self.logger.info(f"TokenAuthMiddleware initialized. Enabled: {self.enabled}")
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request through token authentication middleware.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware or endpoint
            
        Returns:
            Response from next middleware or endpoint
        """
        if not self.enabled:
            return await call_next(request)
        
        try:
            # Extract token from header
            auth_header = request.headers.get(self.header_name)
            if not auth_header:
                return self._create_auth_error("Authorization header required", 401)
            
            # Validate token
            is_valid = self._validate_token(auth_header)
            if not is_valid:
                return self._create_auth_error("Invalid or expired token", 401)
            
            # Continue to next middleware/endpoint
            return await call_next(request)
            
        except Exception as e:
            self.logger.error(f"Token authentication error: {e}")
            return self._create_auth_error("Token authentication failed", 500)
    
    def _validate_token(self, auth_header: str) -> bool:
        """
        Validate token from authorization header.
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            # Extract token from header
            if not auth_header.startswith(f"{self.token_prefix} "):
                return False
            
            token = auth_header[len(f"{self.token_prefix} "):].strip()
            if not token:
                return False
            
            # Determine token type and validate
            if self._is_jwt_token(token):
                return self._validate_jwt_token(token)
            else:
                return self._validate_api_token(token)
                
        except Exception as e:
            self.logger.error(f"Token validation error: {e}")
            return False
    
    def _is_jwt_token(self, token: str) -> bool:
        """
        Check if token is JWT format.
        
        Args:
            token: Token string
            
        Returns:
            True if token appears to be JWT, False otherwise
        """
        # Basic JWT format check (header.payload.signature)
        parts = token.split('.')
        return len(parts) == 3
    
    def _validate_jwt_token(self, token: str) -> bool:
        """
        Validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            True if JWT token is valid, False otherwise
        """
        try:
            # Use AuthValidator for JWT validation
            result = self.auth_validator.validate_token(token, "jwt")
            return result.is_valid
            
        except Exception as e:
            self.logger.error(f"JWT validation error: {e}")
            return False
    
    def _validate_api_token(self, token: str) -> bool:
        """
        Validate API token.
        
        Args:
            token: API token string
            
        Returns:
            True if API token is valid, False otherwise
        """
        try:
            # Check if token exists in loaded tokens
            if token in self.tokens:
                token_data = self.tokens[token]
                
                # Check if token is active
                if not token_data.get("active", True):
                    return False
                
                # Check if token has expired
                if "expires_at" in token_data:
                    import time
                    if time.time() > token_data["expires_at"]:
                        return False
                
                return True
            
            # Use AuthValidator for API token validation
            result = self.auth_validator.validate_token(token, "api")
            return result.is_valid
            
        except Exception as e:
            self.logger.error(f"API token validation error: {e}")
            return False
    
    def _load_tokens(self) -> Dict[str, Any]:
        """
        Load tokens from configuration file.
        
        Returns:
            Dictionary of tokens and their metadata
        """
        try:
            if not self.tokens_file or not Path(self.tokens_file).exists():
                return {}
            
            with open(self.tokens_file, 'r', encoding='utf-8') as f:
                tokens_data = json.load(f)
            
            self.logger.info(f"Loaded {len(tokens_data)} tokens from {self.tokens_file}")
            return tokens_data
            
        except Exception as e:
            self.logger.error(f"Failed to load tokens from {self.tokens_file}: {e}")
            return {}
    
    def _create_auth_error(self, message: str, status_code: int) -> JSONResponse:
        """
        Create authentication error response.
        
        Args:
            message: Error message
            status_code: HTTP status code
            
        Returns:
            JSONResponse with error details
        """
        error_data = {
            "error": {
                "code": -32004,  # Token validation failed
                "message": message,
                "type": "token_authentication_error"
            }
        }
        
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )
    
    def get_roles_from_token(self, auth_header: str) -> List[str]:
        """
        Extract roles from token.
        
        Args:
            auth_header: Authorization header value
            
        Returns:
            List of roles extracted from token
        """
        try:
            if not auth_header.startswith(f"{self.token_prefix} "):
                return []
            
            token = auth_header[len(f"{self.token_prefix} "):].strip()
            if not token:
                return []
            
            # Use AuthValidator to extract roles
            if self._is_jwt_token(token):
                result = self.auth_validator.validate_token(token, "jwt")
            else:
                result = self.auth_validator.validate_token(token, "api")
            
            return result.roles if result.is_valid else []
            
        except Exception as e:
            self.logger.error(f"Failed to extract roles from token: {e}")
            return [] 