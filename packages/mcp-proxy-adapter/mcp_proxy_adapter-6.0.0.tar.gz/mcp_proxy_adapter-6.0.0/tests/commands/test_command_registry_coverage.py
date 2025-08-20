"""
Additional tests for command_registry.py to achieve higher coverage.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Type

from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.core.errors import NotFoundError


class TestCommandRegistryCoverage:
    """Additional tests to cover missing lines in CommandRegistry."""
    
    @pytest.fixture
    def registry(self):
        """Create CommandRegistry instance."""
        return CommandRegistry()
    
    @pytest.fixture
    def mock_command_class(self):
        """Create a mock command class."""
        class MockCommand(Command):
            name = "test_command"
            description = "Test command"
            
            async def execute(self, **params):
                return {"result": "success"}
        
        return MockCommand
    
    def test_register_builtin_already_registered(self, registry, mock_command_class):
        """Test register_builtin with already registered command."""
        # Register first time
        registry.register_builtin(mock_command_class)
        
        # Try to register again
        with pytest.raises(ValueError, match="Built-in command 'test_command' is already registered"):
            registry.register_builtin(mock_command_class)
    
    def test_register_builtin_overrides_loaded(self, registry, mock_command_class):
        """Test register_builtin overrides loaded command."""
        # First register as loaded
        registry._loaded_commands["test_command"] = mock_command_class
        
        # Then register as built-in
        registry.register_builtin(mock_command_class)
        
        assert "test_command" in registry._builtin_commands
        assert "test_command" not in registry._loaded_commands
    
    def test_register_custom_already_registered(self, registry, mock_command_class):
        """Test register_custom with already registered command."""
        # Register first time
        registry.register_custom(mock_command_class)
        
        # Try to register again
        with pytest.raises(ValueError, match="Custom command 'test_command' is already registered"):
            registry.register_custom(mock_command_class)
    
    def test_register_custom_overrides_builtin(self, registry, mock_command_class):
        """Test register_custom overrides built-in command."""
        # First register as built-in
        registry._builtin_commands["test_command"] = mock_command_class
        
        # Then register as custom
        registry.register_custom(mock_command_class)
        
        assert "test_command" in registry._custom_commands
        assert "test_command" not in registry._builtin_commands
    
    def test_register_custom_overrides_loaded(self, registry, mock_command_class):
        """Test register_custom overrides loaded command."""
        # First register as loaded
        registry._loaded_commands["test_command"] = mock_command_class
        
        # Then register as custom
        registry.register_custom(mock_command_class)
        
        assert "test_command" in registry._custom_commands
        assert "test_command" not in registry._loaded_commands
    
    def test_register_loaded_conflicts_with_custom(self, registry, mock_command_class):
        """Test register_loaded conflicts with custom command."""
        # First register as custom
        registry._custom_commands["test_command"] = mock_command_class
        
        # Try to register as loaded
        result = registry.register_loaded(mock_command_class)
        assert result is False
    
    def test_register_loaded_conflicts_with_builtin(self, registry, mock_command_class):
        """Test register_loaded conflicts with built-in command."""
        # First register as built-in
        registry._builtin_commands["test_command"] = mock_command_class
        
        # Try to register as loaded
        result = registry.register_loaded(mock_command_class)
        assert result is False
    
    def test_register_loaded_duplicate(self, registry, mock_command_class):
        """Test register_loaded with duplicate command."""
        # Register first time
        result = registry.register_loaded(mock_command_class)
        assert result is True
        
        # Try to register again
        result = registry.register_loaded(mock_command_class)
        assert result is False
    
    def test_register_loaded_value_error(self, registry, mock_command_class):
        """Test register_loaded with ValueError from _register_command."""
        # Mock _register_command to raise ValueError
        with patch.object(registry, '_register_command', side_effect=ValueError("Test error")):
            result = registry.register_loaded(mock_command_class)
            assert result is False
    
    def test_register_command_with_instance(self, registry, mock_command_class):
        """Test _register_command with command instance."""
        command_instance = mock_command_class()
        
        registry._register_command(command_instance, registry._custom_commands, "custom")
        
        assert "test_command" in registry._custom_commands
        assert "test_command" in registry._instances
        assert registry._instances["test_command"] == command_instance
    
    def test_register_command_invalid_type(self, registry):
        """Test _register_command with invalid command type."""
        invalid_command = "not_a_command"
        
        with pytest.raises(ValueError, match="Invalid command type"):
            registry._register_command(invalid_command, registry._custom_commands, "custom")
    
    def test_register_command_already_in_target(self, registry, mock_command_class):
        """Test _register_command with command already in target dict."""
        # Add to target dict first
        registry._custom_commands["test_command"] = mock_command_class
        
        # Try to register again
        with pytest.raises(ValueError, match="Custom command 'test_command' is already registered"):
            registry._register_command(mock_command_class, registry._custom_commands, "custom")
    
    def test_get_command_name_without_name_attr(self):
        """Test _get_command_name with command without name attribute."""
        class CommandWithoutName(Command):
            async def execute(self, **params):
                return {"result": "success"}
        
        registry = CommandRegistry()
        command_name = registry._get_command_name(CommandWithoutName)
        assert command_name == "commandwithoutname"
    
    def test_get_command_name_without_name_attr_ends_with_command(self):
        """Test _get_command_name with command without name attr ending with Command."""
        class TestCommand(Command):
            async def execute(self, **params):
                return {"result": "success"}
        
        registry = CommandRegistry()
        command_name = registry._get_command_name(TestCommand)
        assert command_name == "test"
    
    def test_get_command_name_with_empty_name(self):
        """Test _get_command_name with empty name attribute."""
        class CommandWithEmptyName(Command):
            name = ""
            async def execute(self, **params):
                return {"result": "success"}
        
        registry = CommandRegistry()
        command_name = registry._get_command_name(CommandWithEmptyName)
        assert command_name == "commandwithemptyname"
    
    def test_load_command_from_source_local_file(self, registry):
        """Test load_command_from_source with local file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='_command.py', delete=False) as f:
            f.write("""
from mcp_proxy_adapter.commands.base import Command

class TestCommand(Command):
    name = "test_command"
    description = "Test command"
    
    async def execute(self, **params):
        return {"result": "success"}
""")
            temp_file = f.name
        
        try:
            result = registry.load_command_from_source(temp_file)
            assert result["success"] is True
            assert "test_command" in result["loaded_commands"]
        finally:
            Path(temp_file).unlink()
    
    def test_load_command_from_source_invalid_filename(self, registry):
        """Test load_command_from_source with invalid filename."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("# test file")
            temp_file = f.name
        
        try:
            result = registry.load_command_from_source(temp_file)
            assert result["success"] is False
            assert "Command file must end with '_command.py'" in result["error"]
        finally:
            Path(temp_file).unlink()
    
    def test_load_command_from_source_file_not_found(self, registry):
        """Test load_command_from_source with non-existent file."""
        result = registry.load_command_from_source("/nonexistent/path/test_command.py")
        assert result["success"] is False
        assert "Command file does not exist" in result["error"]
    
    @patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', True)
    def test_load_command_from_source_url_success(self, registry):
        """Test load_command_from_source with URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
from mcp_proxy_adapter.commands.base import Command

class TestCommand(Command):
    name = "test_command"
    description = "Test command"
    
    async def execute(self, **params):
        return {"result": "success"}
"""
        
        with patch('mcp_proxy_adapter.commands.command_registry.requests.get', return_value=mock_response):
            result = registry.load_command_from_source("https://example.com/test_command.py")
            assert result["success"] is True
            assert "test_command" in result["loaded_commands"]
    
    @patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', False)
    def test_load_command_from_source_url_requests_not_available(self, registry):
        """Test load_command_from_source with URL when requests not available."""
        result = registry.load_command_from_source("https://example.com/test_command.py")
        assert result["success"] is False
        assert "requests library not available" in result["error"]
    
    @patch('mcp_proxy_adapter.commands.command_registry.REQUESTS_AVAILABLE', True)
    def test_load_command_from_source_url_network_error(self, registry):
        """Test load_command_from_source with URL network error."""
        with patch('mcp_proxy_adapter.commands.command_registry.requests.get', side_effect=Exception("Network error")):
            result = registry.load_command_from_source("https://example.com/test_command.py")
            assert result["success"] is False
            assert "Network error" in result["error"]
    
    def test_unload_command_success(self, registry, mock_command_class):
        """Test unload_command with success."""
        # Register command first
        registry._loaded_commands["test_command"] = mock_command_class
        
        result = registry.unload_command("test_command")
        assert result["success"] is True
        assert "test_command" not in registry._loaded_commands
    
    def test_unload_command_not_found(self, registry):
        """Test unload_command with command not found."""
        result = registry.unload_command("nonexistent_command")
        assert result["success"] is False
        assert "Command 'nonexistent_command' is not a loaded command" in result["error"]
    
    def test_unload_command_with_instance(self, registry, mock_command_class):
        """Test unload_command with command instance."""
        # Register command with instance
        registry._loaded_commands["test_command"] = mock_command_class
        registry._instances["test_command"] = mock_command_class()
        
        result = registry.unload_command("test_command")
        assert result["success"] is True
        assert "test_command" not in registry._instances 