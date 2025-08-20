"""
Stub module for echo command tests.
"""

from typing import Any, Dict, Optional, ClassVar, Type

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.logging import logger


class EchoResult:
    """
    Result of the echo command execution (stub for tests).
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize echo result.
        
        Args:
            params: Parameters to echo back.
        """
        self.params = params or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {"params": self.params}
    
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
                "params": {
                    "type": "object",
                    "additionalProperties": True
                }
            },
            "required": ["params"]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EchoResult":
        """
        Creates result instance from dictionary.

        Args:
            data: Dictionary with result data.

        Returns:
            EchoResult instance.
        """
        return cls(
            params=data.get("params", {})
        )


class EchoCommand(Command):
    """
    Test stub for echo command.
    """
    
    name: ClassVar[str] = "echo"
    result_class: ClassVar[Type[EchoResult]] = EchoResult
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Returns JSON schema for command parameters validation.
        
        Returns:
            Dictionary with JSON schema.
        """
        return {
            "type": "object",
            "additionalProperties": True,
            "description": "Any parameters will be echoed back in the response"
        }
    
    async def execute(self, **kwargs) -> EchoResult:
        """
        Executes echo command and returns the parameters back.
        
        Args:
            **kwargs: Any parameters to echo back.
            
        Returns:
            EchoResult: Command execution result with the parameters.
        """
        logger.debug(f"Echo command received parameters: {kwargs}")
        
        # Simply return the parameters that were passed
        return EchoResult(params=kwargs)
