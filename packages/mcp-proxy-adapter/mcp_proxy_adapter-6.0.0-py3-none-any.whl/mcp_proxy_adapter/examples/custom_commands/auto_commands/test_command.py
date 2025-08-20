"""
Test command for demonstrating dynamic command loading.

This command is designed to be dynamically loaded and unloaded
to test the command discovery mechanism.
"""

from typing import Optional, Dict, Any
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult


class TestCommandResult(SuccessResult):
    """Result class for test command."""
    
    def __init__(self, message: str, test_data: Dict[str, Any]):
        """
        Initialize test command result.
        
        Args:
            message: Response message
            test_data: Additional test data
        """
        super().__init__()
        self.message = message
        self.test_data = test_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "message": self.message,
            "test_data": self.test_data,
            "command_type": "test_command",
            "dynamically_loaded": True
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get result schema."""
        return {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "test_data": {"type": "object"},
                "command_type": {"type": "string"},
                "dynamically_loaded": {"type": "boolean"}
            }
        }


class TestCommand(Command):
    """
    Test command for dynamic loading demonstration.
    
    This command can be used to test the dynamic command discovery
    and loading mechanism.
    """
    
    name = "test"
    result_class = TestCommandResult
    
    def __init__(self):
        """Initialize test command."""
        super().__init__()
    
    async def execute(self, message: Optional[str] = None, **kwargs) -> TestCommandResult:
        """
        Execute test command.
        
        Args:
            message: Optional test message
            **kwargs: Additional parameters
            
        Returns:
            TestCommandResult with test data
        """
        test_message = message or "Test command executed successfully!"
        
        test_data = {
            "timestamp": self._get_timestamp(),
            "command_name": "test_command",
            "parameters": kwargs,
            "status": "success"
        }
        
        return TestCommandResult(test_message, test_data)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Get command schema."""
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Test message to display",
                    "default": "Test command executed successfully!"
                }
            }
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat() 