"""
Test command for loadable commands testing.

This command demonstrates the loadable commands functionality.
"""

from typing import Any, Dict

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult


class TestCommandResult:
    """
    Result of test command execution.
    """
    
    def __init__(self, message: str, test_data: Dict[str, Any]):
        """
        Initialize test command result.
        
        Args:
            message: Result message
            test_data: Test data
        """
        self.message = message
        self.test_data = test_data
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dictionary representation of the result.
        """
        return {
            "success": True,
            "message": self.message,
            "test_data": self.test_data
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for the result.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "description": "Whether command was successful"
                },
                "message": {
                    "type": "string",
                    "description": "Result message"
                },
                "test_data": {
                    "type": "object",
                    "description": "Test data"
                }
            },
            "required": ["success", "message", "test_data"]
        }


class TestCommand(Command):
    """
    Test command for loadable commands testing.
    """
    
    name = "test"
    result_class = TestCommandResult
    
    async def execute(self, **kwargs) -> TestCommandResult:
        """
        Execute test command.
        
        Args:
            **kwargs: Command parameters
            
        Returns:
            TestCommandResult with test information
        """
        # Get parameters
        test_param = kwargs.get("test_param", "default_value")
        echo_text = kwargs.get("echo_text", "Hello from loadable command!")
        
        # Create test data
        test_data = {
            "command_type": "loadable",
            "test_param": test_param,
            "echo_text": echo_text,
            "timestamp": "2025-08-12T09:45:00Z",
            "status": "working"
        }
        
        return TestCommandResult(
            message=f"Test command executed successfully with param: {test_param}",
            test_data=test_data
        )
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for command parameters.
        
        Returns:
            JSON schema dictionary.
        """
        return {
            "type": "object",
            "properties": {
                "test_param": {
                    "type": "string",
                    "description": "Test parameter",
                    "default": "default_value"
                },
                "echo_text": {
                    "type": "string",
                    "description": "Text to echo",
                    "default": "Hello from loadable command!"
                }
            },
            "additionalProperties": False
        } 