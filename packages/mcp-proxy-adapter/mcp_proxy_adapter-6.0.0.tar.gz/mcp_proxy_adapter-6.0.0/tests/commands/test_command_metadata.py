"""
Module for testing command metadata functionality.
"""

import pytest
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.result import CommandResult


# Test result class for metadata testing
class MockCommandResult(CommandResult):
    """Test result class."""
    
    def __init__(self, result: str):
        self.result = result
    
    def to_dict(self) -> dict:
        return {"result": self.result}
    
    @classmethod
    def get_schema(cls) -> dict:
        return {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            },
            "required": ["result"]
        }


# Test command for metadata checking
class MockCommand(Command):
    """
    Test command for metadata checking.
    
    Second line of description.
    """
    
    name = "test_command"
    result_class = MockCommandResult
    
    def __init__(self, param1: str, param2: int = 0, param3: bool = False):
        """
        Initialize test command.
        
        Args:
            param1: First parameter (string)
            param2: Second parameter (number), default 0
            param3: Third parameter (flag), default False
        """
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
    
    async def execute(self, param1: str, param2: int = 0, param3: bool = False) -> MockCommandResult:
        """
        Execute command.
        
        Args:
            param1: First parameter (string)
            param2: Second parameter (number), default 0
            param3: Third parameter (flag), default False
            
        Returns:
            MockCommandResult: Command result
        """
        return MockCommandResult(f"{param1}-{param2}-{param3}")


def test_command_metadata():
    """Test getting command metadata."""
    metadata = MockCommand.get_metadata()
    
    # Check basic fields
    assert metadata["name"] == "test_command"
    assert "Test command for metadata checking" in metadata["summary"]
    assert "Second line of description" in metadata["description"]
    
    # Check parameters information
    assert "param1" in metadata["params"]
    assert metadata["params"]["param1"]["required"] is True
    assert metadata["params"]["param2"]["required"] is False
    assert metadata["params"]["param2"]["default"] == 0
    
    # Check examples
    assert len(metadata["examples"]) > 0
    assert any(example.get("command") == "test_command" for example in metadata["examples"])
    
    # Check result class information
    assert metadata["result_class"] == "MockCommandResult"


def test_command_registry_metadata():
    """Test getting metadata from command registry."""
    registry = CommandRegistry()
    registry.register_custom(MockCommand)
    
    # Check getting metadata for a single command
    all_metadata = registry.get_all_metadata()
    metadata = all_metadata["test_command"]
    assert metadata["name"] == "test_command"
    
    # Check getting metadata for all commands
    all_metadata = registry.get_all_metadata()
    assert "test_command" in all_metadata
    assert all_metadata["test_command"]["name"] == "test_command"


@pytest.mark.asyncio
async def test_generated_examples():
    """Test generated examples in command metadata."""
    metadata = MockCommand.get_metadata()
    examples = metadata["examples"]
    
    # Should have at least two examples (required params and all params)
    assert len(examples) >= 2
    
    # Check required params example
    required_example = next((ex for ex in examples if "params" in ex and len(ex["params"]) == 1), None)
    assert required_example is not None
    assert "param1" in required_example["params"]
    
    # Check all params example
    all_params_example = next((ex for ex in examples if "params" in ex and len(ex["params"]) == 3), None)
    assert all_params_example is not None
    assert "param1" in all_params_example["params"]
    assert "param2" in all_params_example["params"]
    assert "param3" in all_params_example["params"] 