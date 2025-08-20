"""
Module for proxy registration functionality.

This module handles automatic registration and unregistration of the server
with the MCP proxy server during startup and shutdown.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urljoin

import aiohttp
import requests
from requests.exceptions import RequestException

from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.core.logging import logger


class ProxyRegistrationError(Exception):
    """Exception raised when proxy registration fails."""
    pass


class ProxyRegistrationManager:
    """
    Manager for proxy registration functionality.
    
    Handles automatic registration and unregistration of the server
    with the MCP proxy server.
    """
    
    def __init__(self):
        """Initialize the proxy registration manager."""
        self.registration_config = config.get("proxy_registration", {})
        self.proxy_url = self.registration_config.get("proxy_url", "http://localhost:3004")
        self.server_id = self.registration_config.get("server_id", "mcp_proxy_adapter")
        self.server_name = self.registration_config.get("server_name", "MCP Proxy Adapter")
        self.description = self.registration_config.get("description", "JSON-RPC API for interacting with MCP Proxy")
        self.timeout = self.registration_config.get("registration_timeout", 30)
        self.retry_attempts = self.registration_config.get("retry_attempts", 3)
        self.retry_delay = self.registration_config.get("retry_delay", 5)
        self.auto_register = self.registration_config.get("auto_register_on_startup", True)
        self.auto_unregister = self.registration_config.get("auto_unregister_on_shutdown", True)
        
        self.registered = False
        self.server_key: Optional[str] = None
        self.server_url: Optional[str] = None
        
    def is_enabled(self) -> bool:
        """
        Check if proxy registration is enabled.
        
        Returns:
            True if registration is enabled, False otherwise.
        """
        return self.registration_config.get("enabled", False)
    
    def set_server_url(self, server_url: str) -> None:
        """
        Set the server URL for registration.
        
        Args:
            server_url: The URL where this server is accessible.
        """
        self.server_url = server_url
        logger.info(f"Proxy registration server URL set to: {server_url}")
    
    async def register_server(self) -> bool:
        """
        Register the server with the proxy.
        
        Returns:
            True if registration was successful, False otherwise.
        """
        if not self.is_enabled():
            logger.info("Proxy registration is disabled in configuration")
            return False
            
        if not self.server_url:
            logger.error("Server URL not set, cannot register with proxy")
            return False
        
        registration_data = {
            "server_id": self.server_id,
            "server_url": self.server_url,
            "server_name": self.server_name,
            "description": self.description
        }
        
        logger.info(f"Attempting to register server with proxy at {self.proxy_url}")
        logger.debug(f"Registration data: {registration_data}")
        
        for attempt in range(self.retry_attempts):
            try:
                success, result = await self._make_registration_request(registration_data)
                
                if success:
                    self.registered = True
                    self.server_key = result.get("server_key")
                    logger.info(f"✅ Successfully registered with proxy. Server key: {self.server_key}")
                    return True
                else:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    logger.warning(f"❌ Registration attempt {attempt + 1} failed: {error_msg}")
                    
                    if attempt < self.retry_attempts - 1:
                        logger.info(f"Retrying in {self.retry_delay} seconds...")
                        await asyncio.sleep(self.retry_delay)
                    
            except Exception as e:
                logger.error(f"❌ Registration attempt {attempt + 1} failed with exception: {e}")
                
                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
        
        logger.error(f"❌ Failed to register with proxy after {self.retry_attempts} attempts")
        return False
    
    async def unregister_server(self) -> bool:
        """
        Unregister the server from the proxy.
        
        Returns:
            True if unregistration was successful, False otherwise.
        """
        if not self.is_enabled():
            logger.info("Proxy registration is disabled, skipping unregistration")
            return True
            
        if not self.registered or not self.server_key:
            logger.info("Server not registered with proxy, skipping unregistration")
            return True
        
        # Extract copy_number from server_key (format: server_id_copy_number)
        try:
            copy_number = int(self.server_key.split("_")[-1])
        except (ValueError, IndexError):
            copy_number = 1
        
        unregistration_data = {
            "server_id": self.server_id,
            "copy_number": copy_number
        }
        
        logger.info(f"Attempting to unregister server from proxy at {self.proxy_url}")
        logger.debug(f"Unregistration data: {unregistration_data}")
        
        try:
            success, result = await self._make_unregistration_request(unregistration_data)
            
            if success:
                unregistered = result.get("unregistered", False)
                if unregistered:
                    logger.info("✅ Successfully unregistered from proxy")
                else:
                    logger.warning("⚠️ Server was not found in proxy registry")
                
                self.registered = False
                self.server_key = None
                return True
            else:
                error_msg = result.get("error", {}).get("message", "Unknown error")
                logger.error(f"❌ Failed to unregister from proxy: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Unregistration failed with exception: {e}")
            return False
    
    async def _make_registration_request(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Make registration request to proxy.
        
        Args:
            data: Registration data.
            
        Returns:
            Tuple of (success, result).
        """
        url = urljoin(self.proxy_url, "/register")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                result = await response.json()
                return response.status == 200, result
    
    async def _make_unregistration_request(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Make unregistration request to proxy.
        
        Args:
            data: Unregistration data.
            
        Returns:
            Tuple of (success, result).
        """
        url = urljoin(self.proxy_url, "/unregister")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                result = await response.json()
                return response.status == 200, result
    
    def get_registration_status(self) -> Dict[str, Any]:
        """
        Get current registration status.
        
        Returns:
            Dictionary with registration status information.
        """
        return {
            "enabled": self.is_enabled(),
            "registered": self.registered,
            "server_key": self.server_key,
            "server_url": self.server_url,
            "proxy_url": self.proxy_url,
            "server_id": self.server_id
        }


# Global proxy registration manager instance
proxy_registration_manager = ProxyRegistrationManager()


async def register_with_proxy(server_url: str) -> bool:
    """
    Register the server with the proxy.
    
    Args:
        server_url: The URL where this server is accessible.
        
    Returns:
        True if registration was successful, False otherwise.
    """
    proxy_registration_manager.set_server_url(server_url)
    return await proxy_registration_manager.register_server()


async def unregister_from_proxy() -> bool:
    """
    Unregister the server from the proxy.
    
    Returns:
        True if unregistration was successful, False otherwise.
    """
    return await proxy_registration_manager.unregister_server()


def get_proxy_registration_status() -> Dict[str, Any]:
    """
    Get current proxy registration status.
    
    Returns:
        Dictionary with registration status information.
    """
    return proxy_registration_manager.get_registration_status() 