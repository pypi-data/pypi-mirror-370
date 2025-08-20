"""
Auto-registered Echo Command

This command will be automatically discovered and registered by the framework.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class AutoEchoResult(CommandResult):
    """
    Result of the auto-registered echo command execution.
    """
    
    def __init__(self, message: str, auto_registered: bool = True):
        """
        Initialize auto echo command result.
        
        Args:
            message: Echoed message
            auto_registered: Flag indicating this was auto-registered
        """
        self.message = message
        self.auto_registered = auto_registered
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {
            "message": self.message,
            "auto_registered": self.auto_registered,
            "command_type": "auto_echo"
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
                "message": {"type": "string"},
                "auto_registered": {"type": "boolean"},
                "command_type": {"type": "string"}
            }
        }


class AutoEchoCommand(Command):
    """
    Auto-registered echo command.
    """
    
    name = "auto_echo"
    result_class = AutoEchoResult
    
    async def execute(self, message: Optional[str] = None, **kwargs) -> AutoEchoResult:
        """
        Execute auto-registered echo command.
        
        Args:
            message: Message to echo
            **kwargs: Additional parameters
            
        Returns:
            AutoEchoResult: Auto echo command result
        """
        if message is None:
            message = "Hello from auto-registered command!"
        
        return AutoEchoResult(
            message=message,
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
                "message": {
                    "type": "string",
                    "description": "Message to echo",
                    "default": "Hello from auto-registered command!"
                }
            }
        } 