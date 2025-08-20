"""
Tests for echo_command_di example.
"""

import pytest
from datetime import datetime

# Skip this test as examples are not available in PyPI version
# from mcp_proxy_adapter.examples.commands.echo_command_di import (
#     EchoCommand, 
#     EchoCommandResult, 
#     TimeService,
#     register_echo_command
# )
from mcp_proxy_adapter.commands import registry, container


@pytest.fixture
def setup_command():
    """Setup command with dependencies for testing."""
    # Skip this test as examples are not available in PyPI version
    pytest.skip("Examples not available in PyPI version")
    
    # Clear existing registrations
    registry.clear()
    container.clear()
    
    # Create time service with fixed timestamp for testing
    class FixedTimeService(TimeService):
        def get_current_time(self):
            return "2023-01-01T12:00:00"
    
    # Create and register fixed time service
    time_service = FixedTimeService()
    container.register("time_service", time_service)
    
    # Create and register command
    command = EchoCommand(time_service)
    registry.register(command)
    
    return command


class TestEchoCommandDI:
    """Tests for EchoCommand with dependency injection."""
    
    async def test_echo_command_result(self):
        """Test that EchoCommandResult correctly formats data."""
        pytest.skip("Examples not available in PyPI version")
        result = EchoCommandResult(
            message="Test message",
            timestamp="2023-01-01T12:00:00"
        )
        
        # Check result properties
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["data"]["message"] == "Test message"
        assert result_dict["data"]["timestamp"] == "2023-01-01T12:00:00"
        assert result_dict["message"] == "Echo response: Test message"
        
        # Check schema
        schema = EchoCommandResult.get_schema()
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "success" in schema["properties"]
        assert "data" in schema["properties"]
        assert "message" in schema["properties"]["data"]["properties"]
        assert "timestamp" in schema["properties"]["data"]["properties"]
    
    async def test_time_service(self):
        """Test TimeService returns ISO formatted timestamp."""
        pytest.skip("Examples not available in PyPI version")
        service = TimeService()
        timestamp = service.get_current_time()
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")
    
    async def test_echo_command_execute(self, setup_command):
        """Test EchoCommand.execute with injected dependencies."""
        pytest.skip("Examples not available in PyPI version")
        command = setup_command
        
        # Execute with default parameter
        default_result = await command.execute()
        assert default_result.to_dict()["data"]["message"] == "Hello, World!"
        assert default_result.to_dict()["data"]["timestamp"] == "2023-01-01T12:00:00"
        
        # Execute with custom parameter
        custom_result = await command.execute(message="Custom message")
        assert custom_result.to_dict()["data"]["message"] == "Custom message"
        assert custom_result.to_dict()["data"]["timestamp"] == "2023-01-01T12:00:00"
    
    async def test_echo_command_run(self, setup_command):
        """Test EchoCommand.run class method with registered instance."""
        pytest.skip("Examples not available in PyPI version")
        # Run command through class method
        result = await EchoCommand.run(message="Run method test")
        
        # Verify result
        assert result.to_dict()["data"]["message"] == "Run method test"
        assert result.to_dict()["data"]["timestamp"] == "2023-01-01T12:00:00"
    
    def test_register_echo_command(self):
        """Test register_echo_command function."""
        pytest.skip("Examples not available in PyPI version")
        # Clear existing registrations
        registry.clear()
        container.clear()
        
        # Register command using function
        command = register_echo_command()
        
        # Verify command is registered
        assert registry.command_exists("echo_di")
        assert registry.has_instance("echo_di")
        
        # Verify service is registered
        assert container.has("time_service")
        assert isinstance(container.get("time_service"), TimeService)
        
        # Verify command uses the registered service
        assert command.time_service is container.get("time_service") 