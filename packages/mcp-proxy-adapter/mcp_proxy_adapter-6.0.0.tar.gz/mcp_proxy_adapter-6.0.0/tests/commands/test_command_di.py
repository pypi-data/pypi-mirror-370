"""
Tests for Dependency Injection in commands.
"""

import pytest
from unittest.mock import MagicMock, patch

from mcp_proxy_adapter.commands import Command, SuccessResult
from mcp_proxy_adapter.commands.result import ErrorResult
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.dependency_container import DependencyContainer
from mcp_proxy_adapter.commands.result import CommandResult


# Тестовые классы и сервисы для проверки DI
class MockService:
    """Test service to be injected."""
    
    def get_value(self):
        """Return a test value."""
        return "service_value"


class MockCommandResult(SuccessResult):
    """Test command result."""
    
    def __init__(self, value):
        """Initialize with a value."""
        super().__init__(data={"value": value})


class MockCommand(Command):
    """Test command that requires a dependency."""
    
    name = "test_di_command"
    result_class = MockCommandResult
    
    def __init__(self, service: MockService):
        """Initialize with a service dependency."""
        self.service = service
        
    async def execute(self) -> CommandResult:
        """Execute command using the service."""
        value = self.service.get_value()
        return MockCommandResult(value)


@pytest.fixture
def registry():
    """Create a fresh command registry for each test."""
    return CommandRegistry()


@pytest.fixture
def container():
    """Create a fresh dependency container for each test."""
    return DependencyContainer()


class TestCommandDependencyInjection:
    """Tests for Command Dependency Injection."""
    
    async def test_register_command_instance(self, registry):
        """Test registering a command instance with dependencies."""
        # Create test service
        service = MockService()
        
        # Create command with dependency
        command = MockCommand(service)
        
        # Register command instance
        registry.register_custom(command)
        
        # Verify command is registered
        assert registry.command_exists("test_di_command")
        assert registry.has_instance("test_di_command")
        
        # Get instance should return the same instance
        instance = registry.get_command_instance("test_di_command")
        assert instance is command
        
        # Execute the command
        result = await instance.execute()
        assert result.to_dict()["data"]["value"] == "service_value"
    
    async def test_run_command_with_di(self, registry):
        """Test running a command with DI via Command.run class method."""
        # Create test service
        service = MockService()
        
        # Create command with dependency
        command = MockCommand(service)
        
        # Register command instance
        registry.register_custom(command)
        
        # Patch registry in Command.run method
        with patch("mcp_proxy_adapter.commands.command_registry.registry", registry):
            # Run command via class method
            result = await MockCommand.run()
            
            # Should return error because MockCommand requires service parameter
            assert isinstance(result, ErrorResult)
            assert "missing 1 required positional argument: 'service'" in result.message
    
    async def test_require_instance_for_commands_with_dependencies(self, registry, caplog):
        """Test that commands with dependencies require instances."""
        # Try to register command class with dependencies
        # This should work now as the registry handles class registration
        registry.register_custom(MockCommand)
        
        # Verify command is registered
        assert registry.command_exists("test_di_command")
        
        # But trying to get instance should fail
        with pytest.raises(ValueError):
            registry.get_command_instance("test_di_command")
    
    async def test_container_integration(self, registry, container):
        """Test integration with dependency container."""
        # Create and register service in container
        service = MockService()
        container.register("test_service", service)
        
        # Create command with injected dependency from container
        command = MockCommand(container.get("test_service"))
        
        # Register command instance
        registry.register_custom(command)
        
        # Patch registry in Command.run method
        with patch("mcp_proxy_adapter.commands.command_registry.registry", registry):
            # Run command
            result = await MockCommand.run()
            
            # Should return error because MockCommand requires service parameter
            assert isinstance(result, ErrorResult)
            assert "missing 1 required positional argument: 'service'" in result.message
    
    async def test_command_executes_with_container(self, registry, container):
        """Test command execution using container during registration."""
        # Set up mock service to verify injection
        mock_service = MagicMock(spec=MockService)
        mock_service.get_value.return_value = "mock_value"
        
        # Register in container
        container.register("test_service", mock_service)
        
        # Create and register command
        command = MockCommand(container.get("test_service"))
        registry.register_custom(command)
        
        # Execute
        result = await command.execute()
        
        # Check service was called
        mock_service.get_value.assert_called_once()
        assert result.to_dict()["data"]["value"] == "mock_value" 