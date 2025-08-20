"""
Tests for command registry.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.core.errors import NotFoundError


class MockResult(CommandResult):
    """Test result class for testing."""
    
    def __init__(self):
        pass
    
    def to_dict(self):
        return {}
    
    @classmethod
    def get_schema(cls):
        return {}


class TestCommand1(Command):
    """First test command."""
    
    name = "test_command1"
    result_class = MockResult
    
    async def execute(self, **kwargs):
        return MockResult()


class TestCommand2(Command):
    """Second test command."""
    
    name = "test_command2"
    result_class = MockResult
    
    async def execute(self, **kwargs):
        return MockResult()


def test_registry_initialization():
    """Test registry initialization."""
    registry = CommandRegistry()
    assert len(registry._commands) == 0


def test_register_command():
    """Test registering command."""
    registry = CommandRegistry()
    
    # Register first command
    registry.register(TestCommand1)
    assert len(registry._commands) == 1
    assert "test_command1" in registry._commands
    
    # Register second command
    registry.register(TestCommand2)
    assert len(registry._commands) == 2
    assert "test_command2" in registry._commands


def test_register_duplicated_command():
    """Test registering duplicated command."""
    registry = CommandRegistry()
    
    # Register command
    registry.register(TestCommand1)
    
    # Try to register again
    with pytest.raises(ValueError):
        registry.register(TestCommand1)


def test_register_command_without_name():
    """Test registering command without name attribute."""
    registry = CommandRegistry()
    
    # Create command without name
    class CommandWithoutName(Command):
        result_class = MockResult
        
        async def execute(self, **kwargs):
            return MockResult()
    
    # Register command
    registry.register(CommandWithoutName)
    
    # Check if registered with class name
    assert "commandwithoutname" in registry._commands


def test_unregister_command():
    """Test unregistering command."""
    registry = CommandRegistry()
    
    # Register command
    registry.register(TestCommand1)
    assert "test_command1" in registry._commands
    
    # Unregister command
    registry.unregister("test_command1")
    assert "test_command1" not in registry._commands


def test_unregister_nonexistent_command():
    """Test unregistering nonexistent command."""
    registry = CommandRegistry()
    
    # Try to unregister nonexistent command
    with pytest.raises(NotFoundError):
        registry.unregister("nonexistent")


def test_get_command():
    """Test getting command."""
    registry = CommandRegistry()
    
    # Register command
    registry.register(TestCommand1)
    
    # Get command
    command = registry.get_command("test_command1")
    assert command == TestCommand1


def test_get_nonexistent_command():
    """Test getting nonexistent command."""
    registry = CommandRegistry()
    
    # Try to get nonexistent command
    with pytest.raises(NotFoundError):
        registry.get_command("nonexistent")


def test_get_all_commands():
    """Test getting all commands."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register(TestCommand1)
    registry.register(TestCommand2)
    
    # Get all commands
    commands = registry.get_all_commands()
    assert len(commands) == 2
    assert "test_command1" in commands
    assert "test_command2" in commands
    assert commands["test_command1"] == TestCommand1
    assert commands["test_command2"] == TestCommand2


def test_get_command_info():
    """Test getting command info."""
    registry = CommandRegistry()
    
    # Register command
    registry.register(TestCommand1)
    
    # Get command info
    info = registry.get_command_info("test_command1")
    
    # Check info structure
    assert info["name"] == "test_command1"
    assert "description" in info
    assert "params" in info
    assert "schema" in info
    assert "result_schema" in info


def test_get_all_commands_info():
    """Test getting all commands info."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register(TestCommand1)
    registry.register(TestCommand2)
    
    # Get all commands info
    info = registry.get_all_commands_info()
    
    # Check info structure
    assert len(info) == 2
    assert "test_command1" in info
    assert "test_command2" in info
    assert info["test_command1"]["name"] == "test_command1"
    assert info["test_command2"]["name"] == "test_command2"


@patch("importlib.import_module")
@patch("pkgutil.iter_modules")
@patch("inspect.getmembers")
def test_discover_commands(mock_getmembers, mock_iter_modules, mock_import_module):
    """Test discovering commands."""
    registry = CommandRegistry()
    
    # Mock package
    mock_package = MagicMock()
    mock_package.__file__ = "/path/to/package"
    mock_import_module.return_value = mock_package
    
    # Mock modules
    mock_iter_modules.return_value = [
        (None, "test_command", False),
        (None, "other_module", False)
    ]
    
    # Mock command classes
    class DiscoveredCommand(Command):
        name = "discovered"
        result_class = MockResult
        
        async def execute(self, **kwargs):
            return MockResult()
    
    # Mock getmembers to return command class
    mock_getmembers.return_value = [
        ("DiscoveredCommand", DiscoveredCommand)
    ]
    
    # Discover commands
    registry.discover_commands()
    
    # Check if command was registered
    assert len(mock_import_module.mock_calls) > 0


def test_clear_registry():
    """Test clearing registry."""
    registry = CommandRegistry()
    
    # Register commands
    registry.register(TestCommand1)
    registry.register(TestCommand2)
    assert len(registry._commands) == 2
    
    # Clear registry
    registry.clear()
    assert len(registry._commands) == 0


def test_register_command_instance():
    """Test registering a command instance (with dependencies)."""
    registry = CommandRegistry()

    class Service:
        def __init__(self, value):
            self.value = value

    class CommandWithDependency(Command):
        name = "command_with_dep"
        result_class = MockResult
        def __init__(self, service: Service):
            self.service = service
        async def execute(self, **kwargs):
            # Return the value from the injected service
            result = MockResult()
            result.service_value = self.service.value
            return result

    service = Service(value=42)
    command_instance = CommandWithDependency(service=service)
    registry.register(command_instance)

    # Проверяем, что экземпляр зарегистрирован
    assert registry.has_instance("command_with_dep")
    # Проверяем, что get_command_instance возвращает именно этот экземпляр
    assert registry.get_command_instance("command_with_dep") is command_instance
    # Проверяем, что execute использует внедрённый сервис
    import asyncio
    result = asyncio.run(
        registry.get_command_instance("command_with_dep").execute()
    )
    assert hasattr(result, "service_value")
    assert result.service_value == 42 