"""
Intercept Command Example

A command that can be completely intercepted by hooks based on conditions.
"""

from typing import Dict, Any, Optional
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult


class InterceptResult(CommandResult):
    """
    Result of the intercept command execution.
    """
    
    def __init__(self, message: str, executed: bool, intercept_reason: Optional[str] = None,
                 hook_data: Optional[Dict[str, Any]] = None):
        """
        Initialize intercept command result.
        
        Args:
            message: Result message
            executed: Whether the command was actually executed
            intercept_reason: Reason for interception (if any)
            hook_data: Data from hooks
        """
        self.message = message
        self.executed = executed
        self.intercept_reason = intercept_reason
        self.hook_data = hook_data or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        return {
            "message": self.message,
            "executed": self.executed,
            "intercept_reason": self.intercept_reason,
            "hook_data": self.hook_data,
            "command_type": "intercept"
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
                "executed": {"type": "boolean"},
                "intercept_reason": {"type": "string"},
                "hook_data": {"type": "object"},
                "command_type": {"type": "string"}
            }
        }


class InterceptCommand(Command):
    """
    Intercept command for demonstrating hook interception.
    """
    
    name = "intercept"
    result_class = InterceptResult
    
    async def execute(self, action: Optional[str] = None, 
                     bypass_flag: Optional[int] = None, **kwargs) -> InterceptResult:
        """
        Execute intercept command.
        
        Args:
            action: Action to perform
            bypass_flag: Flag to determine if command should be bypassed (0 = bypass, 1 = execute)
            **kwargs: Additional parameters
            
        Returns:
            InterceptResult: Intercept command result
        """
        action = action or "default"
        bypass_flag = bypass_flag if bypass_flag is not None else 1
        
        # This should only execute if bypass_flag == 1
        # If bypass_flag == 0, hooks should intercept and return result
        
        return InterceptResult(
            message=f"Command executed with action: {action}",
            executed=True,
            intercept_reason=None,
            hook_data=kwargs
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
                "action": {
                    "type": "string",
                    "description": "Action to perform"
                },
                "bypass_flag": {
                    "type": "integer",
                    "enum": [0, 1],
                    "description": "Flag to determine execution (0 = bypass, 1 = execute)"
                }
            }
        } 