"""
Command for managing proxy registration.

This command allows manual registration, unregistration, and status checking
for the proxy registration functionality.
"""

import asyncio
from typing import Dict, Any, Optional

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.core.proxy_registration import (
    register_with_proxy, 
    unregister_from_proxy, 
    get_proxy_registration_status,
    proxy_registration_manager
)
from mcp_proxy_adapter.core.logging import logger


class ProxyRegistrationResult(CommandResult):
    """Result class for proxy registration commands."""
    
    def __init__(self, success: bool, message: str, data: Optional[Dict[str, Any]] = None):
        """
        Initialize proxy registration result.
        
        Args:
            success: Whether the operation was successful.
            message: Result message.
            data: Additional data.
        """
        self.success = success
        self.message = message
        self.data = data
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for this result.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether the operation was successful"
                },
                "message": {
                    "type": "string",
                    "description": "Result message"
                },
                "data": {
                    "type": "object",
                    "description": "Additional data",
                    "additionalProperties": True
                }
            },
            "required": ["success", "message"]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation of the result.
        """
        result = {
            "success": self.success,
            "message": self.message
        }
        if self.data is not None:
            result["data"] = self.data
        return result


class ProxyRegistrationCommand(Command):
    """
    Command for managing proxy registration.
    
    Supports registration, unregistration, and status checking.
    """
    
    name = "proxy_registration"
    
    def __init__(self):
        """Initialize the proxy registration command."""
        super().__init__()
    
    async def execute(self, **kwargs) -> ProxyRegistrationResult:
        """
        Execute proxy registration command.
        
        Args:
            **kwargs: Command parameters containing:
                - action: "register", "unregister", or "status"
                - server_url: (optional) Server URL for registration
                
        Returns:
            ProxyRegistrationResult with operation result.
        """
        action = kwargs.get("action", "status")
        
        try:
            if action == "register":
                return await self._handle_register(kwargs)
            elif action == "unregister":
                return await self._handle_unregister(kwargs)
            elif action == "status":
                return await self._handle_status(kwargs)
            else:
                return ProxyRegistrationResult(
                    success=False,
                    message=f"Unknown action: {action}. Supported actions: register, unregister, status"
                )
                
        except Exception as e:
            logger.error(f"Proxy registration command failed: {e}")
            return ProxyRegistrationResult(
                success=False,
                message=f"Command execution failed: {str(e)}"
            )
    
    async def _handle_register(self, params: Dict[str, Any]) -> ProxyRegistrationResult:
        """
        Handle registration action.
        
        Args:
            params: Command parameters.
            
        Returns:
            ProxyRegistrationResult.
        """
        server_url = params.get("server_url")
        
        if not server_url:
            # Use current server configuration
            from mcp_proxy_adapter.config import config
            
            server_config = config.get("server", {})
            server_host = server_config.get("host", "0.0.0.0")
            server_port = server_config.get("port", 8000)
            
            # Determine server URL based on SSL configuration
            ssl_config = config.get("ssl", {})
            if ssl_config.get("enabled", False):
                protocol = "https"
            else:
                protocol = "http"
            
            # Use localhost for external access if host is 0.0.0.0
            if server_host == "0.0.0.0":
                server_host = "localhost"
            
            server_url = f"{protocol}://{server_host}:{server_port}"
        
        logger.info(f"Attempting to register with proxy using URL: {server_url}")
        
        success = await register_with_proxy(server_url)
        
        if success:
            status = get_proxy_registration_status()
            return ProxyRegistrationResult(
                success=True,
                message="✅ Successfully registered with proxy",
                data={
                    "server_url": server_url,
                    "server_key": status.get("server_key"),
                    "registration_status": status
                }
            )
        else:
            return ProxyRegistrationResult(
                success=False,
                message="❌ Failed to register with proxy"
            )
    
    async def _handle_unregister(self, params: Dict[str, Any]) -> ProxyRegistrationResult:
        """
        Handle unregistration action.
        
        Args:
            params: Command parameters.
            
        Returns:
            ProxyRegistrationResult.
        """
        logger.info("Attempting to unregister from proxy")
        
        success = await unregister_from_proxy()
        
        if success:
            return ProxyRegistrationResult(
                success=True,
                message="✅ Successfully unregistered from proxy"
            )
        else:
            return ProxyRegistrationResult(
                success=False,
                message="❌ Failed to unregister from proxy"
            )
    
    async def _handle_status(self, params: Dict[str, Any]) -> ProxyRegistrationResult:
        """
        Handle status action.
        
        Args:
            params: Command parameters.
            
        Returns:
            ProxyRegistrationResult.
        """
        status = get_proxy_registration_status()
        
        return ProxyRegistrationResult(
            success=True,
            message="Proxy registration status retrieved successfully",
            data={
                "registration_status": status,
                "enabled": status.get("enabled", False),
                "registered": status.get("registered", False),
                "server_key": status.get("server_key"),
                "server_url": status.get("server_url"),
                "proxy_url": status.get("proxy_url")
            }
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get command schema.
        
        Returns:
            Command schema.
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["register", "unregister", "status"],
                    "description": "Action to perform: register, unregister, or status"
                },
                "server_url": {
                    "type": "string",
                    "description": "Server URL for registration (optional, uses current config if not provided)"
                }
            },
            "required": ["action"]
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to dictionary.
        
        Returns:
            Command dictionary representation.
        """
        return {
            "name": self.name,
            "description": "Manage proxy registration (register, unregister, status)",
            "schema": self.__class__.get_schema()
        } 