"""
Auto-registered Info Command

This command will be automatically discovered and registered by the framework.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class AutoInfoResult(CommandResult):
    """
    Result of the auto-registered info command execution.
    """
    
    def __init__(self, info: Dict[str, Any], auto_registered: bool = True):
        """
        Initialize auto info command result.
        
        Args:
            info: Information data
            auto_registered: Flag indicating this was auto-registered
        """
        self.info = info
        self.auto_registered = auto_registered
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {
            "info": self.info,
            "auto_registered": self.auto_registered,
            "command_type": "auto_info"
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for the result.
        
        Returns:
            Dict[str, Any]: JSON schema
        """
        return {
            "type": "object",
            "properties": {
                "info": {"type": "object"},
                "auto_registered": {"type": "boolean"},
                "command_type": {"type": "string"}
            }
        }


class AutoInfoCommand(Command):
    """
    Auto-registered info command.
    """
    
    name = "auto_info"
    result_class = AutoInfoResult
    
    async def execute(self, topic: Optional[str] = None, **kwargs) -> AutoInfoResult:
        """
        Execute auto-registered info command.
        
        Args:
            topic: Information topic
            **kwargs: Additional parameters
            
        Returns:
            AutoInfoResult: Auto info command result
        """
        if topic is None:
            topic = "general"
        
        info_data = {
            "topic": topic,
            "auto_registered": True,
            "discovery_method": "automatic",
            "registration_time": "startup",
            "command_type": "auto_info"
        }
        
        return AutoInfoResult(
            info=info_data,
            auto_registered=True
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
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Information topic",
                    "default": "general"
                }
            }
        } 