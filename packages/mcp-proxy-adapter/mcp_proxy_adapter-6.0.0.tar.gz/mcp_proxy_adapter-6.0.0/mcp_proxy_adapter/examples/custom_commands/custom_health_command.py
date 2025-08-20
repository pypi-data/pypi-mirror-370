"""
Custom Health Command Example

A custom health command with enhanced system information.
"""

import os
import platform
import sys
import psutil
from datetime import datetime
from typing import Dict, Any

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.commands.command_registry import registry


class CustomHealthResult(SuccessResult):
    """
    Result of the custom health command execution.
    """
    
    def __init__(self, status: str, version: str, uptime: float, 
                 components: Dict[str, Any], custom_metrics: Dict[str, Any]):
        """
        Initialize custom health command result.
        
        Args:
            status: Server status ("ok" or "error")
            version: Server version
            uptime: Server uptime in seconds
            components: Dictionary with components status
            custom_metrics: Additional custom metrics
        """
        super().__init__(
            data={
                "status": status,
                "version": version,
                "uptime": uptime,
                "components": components,
                "custom_metrics": custom_metrics,
                "custom_health": True
            }
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for result validation.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "version": {"type": "string"},
                        "uptime": {"type": "number"},
                        "components": {"type": "object"},
                        "custom_metrics": {"type": "object"},
                        "custom_health": {"type": "boolean"}
                    },
                    "required": ["status", "version", "uptime", "components", "custom_metrics", "custom_health"]
                }
            },
            "required": ["data"]
        }


class CustomHealthCommand(Command):
    """
    Custom health command with enhanced system information.
    """
    
    name = "health"
    result_class = CustomHealthResult
    
    async def execute(self, **kwargs) -> CustomHealthResult:
        """
        Execute custom health command.
        
        Returns:
            CustomHealthResult: Custom health command result
        """
        # Get version from package
        try:
            from mcp_proxy_adapter.version import __version__ as version
        except ImportError:
            version = "unknown"
        
        # Get process start time
        process = psutil.Process(os.getpid())
        start_time = datetime.fromtimestamp(process.create_time())
        uptime_seconds = (datetime.now() - start_time).total_seconds()
        
        # Get system information
        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available
        }
        
        # Get process information
        process_info = {
            "pid": os.getpid(),
            "memory_usage": process.memory_info().rss,
            "cpu_percent": process.cpu_percent(),
            "create_time": process.create_time()
        }
        
        # Get commands information
        from mcp_proxy_adapter.commands.command_registry import registry
        commands_info = {
            "total_commands": len(registry.get_all_commands()),
            "custom_commands": ["echo", "help", "health"],
            "registry_status": "active"
        }
        
        # Custom metrics
        custom_metrics = {
            "custom_health_check": True,
            "enhanced_monitoring": True,
            "system_load": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "free": psutil.disk_usage('/').free,
                "used": psutil.disk_usage('/').used
            },
            "network_interfaces": len(psutil.net_if_addrs()),
            "custom_features": ["enhanced_metrics", "system_monitoring", "custom_health"],
            "hook_enhanced": kwargs.get("hook_enhanced", False),
            "health_check_id": kwargs.get("health_check_id"),
            "global_hook_processed": kwargs.get("global_hook_processed", False)
        }
        
        components = {
            "system": system_info,
            "process": process_info,
            "commands": commands_info
        }
        
        return CustomHealthResult(
            status="ok",
            version=version,
            uptime=uptime_seconds,
            components=components,
            custom_metrics=custom_metrics
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {},
            "description": "Get enhanced system health information"
        } 