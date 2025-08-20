"""
Echo Command Example

A simple echo command that returns the input message.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult


class EchoResult(SuccessResult):
    """
    Result of the echo command execution.
    """
    
    def __init__(self, message: str, timestamp: str):
        """
        Initialize echo command result.
        
        Args:
            message: The echoed message
            timestamp: Timestamp of execution
        """
        super().__init__(
            data={
                "message": message,
                "timestamp": timestamp,
                "echoed": True
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
                        "message": {"type": "string"},
                        "timestamp": {"type": "string"},
                        "echoed": {"type": "boolean"}
                    },
                    "required": ["message", "timestamp", "echoed"]
                }
            },
            "required": ["data"]
        }


class EchoCommand(Command):
    """
    Echo command that returns the input message.
    """
    
    name = "echo"
    result_class = EchoResult
    
    async def execute(self, message: Optional[str] = None, **kwargs) -> EchoResult:
        """
        Execute echo command.
        
        Args:
            message: Message to echo (optional)
            **kwargs: Additional parameters
            
        Returns:
            EchoResult: Echo command result
        """
        # Use provided message or default
        if message is None:
            message = kwargs.get("text", "Hello, World!")
        
        # Check if hook added timestamp
        hook_timestamp = kwargs.get("hook_timestamp")
        if hook_timestamp:
            # Use hook timestamp if available
            timestamp = hook_timestamp
        else:
            # Get current timestamp
            timestamp = datetime.now().isoformat()
        
        # Add hook metadata to result
        result = EchoResult(message=message, timestamp=timestamp)
        
        # Add hook information if available
        if kwargs.get("hook_processed"):
            result.data["hook_processed"] = True
            result.data["hook_timestamp"] = hook_timestamp
        
        return result
    
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
                    "default": "Hello, World!"
                },
                "text": {
                    "type": "string", 
                    "description": "Alternative parameter name for message"
                }
            }
        } 