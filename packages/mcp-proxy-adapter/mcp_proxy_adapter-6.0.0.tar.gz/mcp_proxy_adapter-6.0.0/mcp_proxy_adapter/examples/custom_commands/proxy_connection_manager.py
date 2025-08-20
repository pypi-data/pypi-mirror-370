#!/usr/bin/env python3
"""
Proxy Connection Manager

Manages connection to the proxy server with regular health checks
and automatic re-registration when needed.
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from mcp_proxy_adapter.core.proxy_registration import register_with_proxy, unregister_from_proxy
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.core.logging import get_logger


class ProxyConnectionManager:
    """
    Manages connection to proxy server with health monitoring and auto-reconnection.
    """
    
    def __init__(self, check_interval: int = 30, max_retries: int = 3):
        """
        Initialize proxy connection manager.
        
        Args:
            check_interval: Interval between health checks in seconds
            max_retries: Maximum number of retry attempts
        """
        self.logger = get_logger("proxy_connection_manager")
        self.check_interval = check_interval
        self.max_retries = max_retries
        self.is_running = False
        self.last_registration = None
        self.registration_count = 0
        self.failed_attempts = 0
        self.server_url = None
        self.server_id = None
        
        # Get configuration
        proxy_config = config.get("proxy_registration", {})
        self.proxy_url = proxy_config.get("proxy_url", "http://localhost:3004")
        self.server_id = proxy_config.get("server_id", "mcp_proxy_adapter_custom")
        
        # Get server configuration
        server_config = config.get("server", {})
        server_host = server_config.get("host", "0.0.0.0")
        server_port = server_config.get("port", 8000)
        
        # Use localhost for external access if host is 0.0.0.0
        if server_host == "0.0.0.0":
            server_host = "localhost"
        
        self.server_url = f"http://{server_host}:{server_port}"
        
        self.logger.info(f"Proxy Connection Manager initialized:")
        self.logger.info(f"  • Server URL: {self.server_url}")
        self.logger.info(f"  • Proxy URL: {self.proxy_url}")
        self.logger.info(f"  • Server ID: {self.server_id}")
        self.logger.info(f"  • Check interval: {check_interval}s")
        self.logger.info(f"  • Max retries: {max_retries}")
    
    async def start(self) -> None:
        """
        Start the proxy connection manager.
        """
        if self.is_running:
            self.logger.warning("Proxy Connection Manager is already running")
            return
        
        self.is_running = True
        self.logger.info("🚀 Starting Proxy Connection Manager")
        
        # Initial registration
        await self.register_with_proxy()
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self) -> None:
        """
        Stop the proxy connection manager.
        """
        if not self.is_running:
            return
        
        self.is_running = False
        self.logger.info("🛑 Stopping Proxy Connection Manager")
        
        # Unregister from proxy
        await self.unregister_from_proxy()
    
    async def register_with_proxy(self) -> bool:
        """
        Register server with proxy.
        
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            self.logger.info(f"📡 Attempting to register server with proxy at {self.proxy_url}")
            
            success = await register_with_proxy(self.server_url)
            
            if success:
                self.last_registration = datetime.now()
                self.registration_count += 1
                self.failed_attempts = 0
                self.logger.info(f"✅ Successfully registered with proxy (attempt #{self.registration_count})")
                return True
            else:
                self.failed_attempts += 1
                self.logger.warning(f"⚠️ Failed to register with proxy (attempt #{self.failed_attempts})")
                return False
                
        except Exception as e:
            self.failed_attempts += 1
            self.logger.error(f"❌ Error registering with proxy: {e}")
            return False
    
    async def unregister_from_proxy(self) -> bool:
        """
        Unregister server from proxy.
        
        Returns:
            True if unregistration was successful, False otherwise
        """
        try:
            self.logger.info("📡 Unregistering from proxy")
            
            success = await unregister_from_proxy()
            
            if success:
                self.logger.info("✅ Successfully unregistered from proxy")
            else:
                self.logger.warning("⚠️ Failed to unregister from proxy")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Error unregistering from proxy: {e}")
            return False
    
    async def check_proxy_health(self) -> bool:
        """
        Check if proxy is accessible and server is registered.
        
        Returns:
            True if proxy is healthy, False otherwise
        """
        try:
            import httpx
            
            # Check if proxy is accessible
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.proxy_url}/health")
                
                if response.status_code == 200:
                    self.logger.debug("✅ Proxy health check passed")
                    return True
                else:
                    self.logger.warning(f"⚠️ Proxy health check failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            self.logger.warning(f"⚠️ Proxy health check error: {e}")
            return False
    
    async def _monitoring_loop(self) -> None:
        """
        Main monitoring loop that checks proxy health and re-registers if needed.
        """
        self.logger.info("🔄 Starting proxy monitoring loop")
        
        while self.is_running:
            try:
                # Check if we need to re-register
                should_reregister = False
                
                # Check if last registration was too long ago (more than 5 minutes)
                if self.last_registration:
                    time_since_registration = datetime.now() - self.last_registration
                    if time_since_registration > timedelta(minutes=5):
                        self.logger.info("⏰ Last registration was more than 5 minutes ago, re-registering")
                        should_reregister = True
                
                # Check proxy health
                proxy_healthy = await self.check_proxy_health()
                
                if not proxy_healthy:
                    self.logger.warning("⚠️ Proxy health check failed, attempting re-registration")
                    should_reregister = True
                
                # Re-register if needed
                if should_reregister:
                    if self.failed_attempts >= self.max_retries:
                        self.logger.error(f"❌ Max retries ({self.max_retries}) reached, stopping re-registration attempts")
                        break
                    
                    await self.register_with_proxy()
                
                # Log status
                if self.last_registration:
                    time_since = datetime.now() - self.last_registration
                    self.logger.info(f"📊 Status: Registered {time_since.total_seconds():.0f}s ago, "
                                   f"attempts: {self.registration_count}, "
                                   f"failed: {self.failed_attempts}")
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                self.logger.info("🛑 Monitoring loop cancelled")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)
        
        self.logger.info("🔄 Proxy monitoring loop stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the connection manager.
        
        Returns:
            Dictionary with status information
        """
        status = {
            "is_running": self.is_running,
            "server_url": self.server_url,
            "proxy_url": self.proxy_url,
            "server_id": self.server_id,
            "registration_count": self.registration_count,
            "failed_attempts": self.failed_attempts,
            "check_interval": self.check_interval,
            "max_retries": self.max_retries
        }
        
        if self.last_registration:
            time_since = datetime.now() - self.last_registration
            status["last_registration"] = self.last_registration.isoformat()
            status["time_since_registration"] = time_since.total_seconds()
        else:
            status["last_registration"] = None
            status["time_since_registration"] = None
        
        return status


# Global instance
proxy_manager = ProxyConnectionManager()


async def start_proxy_manager() -> None:
    """
    Start the global proxy connection manager.
    """
    await proxy_manager.start()


async def stop_proxy_manager() -> None:
    """
    Stop the global proxy connection manager.
    """
    await proxy_manager.stop()


def get_proxy_manager_status() -> Dict[str, Any]:
    """
    Get status of the global proxy connection manager.
    
    Returns:
        Dictionary with status information
    """
    return proxy_manager.get_status()
