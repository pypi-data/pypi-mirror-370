"""
Manually registered Echo Command

This command must be manually registered in the server code.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class ManualEchoResult(CommandResult):
    """
    Result of the manually registered echo command execution.
    """
    
    def __init__(self, message: str, manually_registered: bool = True):
        """
        Initialize manual echo command result.
        
        Args:
            message: Echoed message
            manually_registered: Flag indicating this was manually registered
        """
        self.message = message
        self.manually_registered = manually_registered
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {
            "message": self.message,
            "manually_registered": self.manually_registered,
            "command_type": "manual_echo"
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
                "manually_registered": {"type": "boolean"},
                "command_type": {"type": "string"}
            }
        }


class ManualEchoCommand(Command):
    """
    Manually registered echo command.
    """
    
    name = "manual_echo"
    result_class = ManualEchoResult
    
    async def execute(self, message: Optional[str] = None, **kwargs) -> ManualEchoResult:
        """
        Execute manually registered echo command.
        
        Args:
            message: Message to echo
            **kwargs: Additional parameters
            
        Returns:
            ManualEchoResult: Manual echo command result
        """
        if message is None:
            message = "Hello from manually registered command!"
        
        return ManualEchoResult(
            message=message,
            manually_registered=True
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
                    "default": "Hello from manually registered command!"
                }
            }
        } 