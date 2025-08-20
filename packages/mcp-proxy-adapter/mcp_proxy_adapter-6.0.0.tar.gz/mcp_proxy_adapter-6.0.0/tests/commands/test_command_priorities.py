"""
Tests for command priority system.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command


def create_mock_command_class(command_name: str):
    """Create a mock command class with the given name."""
    class DynamicMockCommand(Command):
        """Dynamic mock command for testing."""
        
        # Set name as class attribute
        name = command_name
        
        def __init__(self, command_type: str = "mock"):
            self.command_type = command_type
        
        async def execute(self, **params):
            return {"result": f"executed {self.name} ({self.command_type})"}
    
    return DynamicMockCommand


class TestCommandPriorities:
    """Test command priority system."""
    
    def setup_method(self):
        """Setup test method."""
        self.registry = CommandRegistry()
    
    def test_priority_order(self):
        """Test that commands are returned in correct priority order."""
        # Create command classes with different names
        LoadedCommand = create_mock_command_class("test")
        BuiltinCommand = create_mock_command_class("test")
        CustomCommand = create_mock_command_class("test")
        
        # Register commands in priority order (custom overrides built-in overrides loaded)
        result1 = self.registry.register_loaded(LoadedCommand())
        print(f"After loaded: {list(self.registry._loaded_commands.keys())}")
        
        self.registry.register_builtin(BuiltinCommand())
        print(f"After builtin: {list(self.registry._builtin_commands.keys())}")
        print(f"Loaded after builtin: {list(self.registry._loaded_commands.keys())}")
        
        self.registry.register_custom(CustomCommand())
        print(f"After custom: {list(self.registry._custom_commands.keys())}")
        print(f"Builtin after custom: {list(self.registry._builtin_commands.keys())}")
        print(f"Loaded after custom: {list(self.registry._loaded_commands.keys())}")
        
        # Should return custom command (highest priority)
        command = self.registry.get_command("test")
        assert command.name == "test"
        assert command in self.registry._custom_commands.values()
        
        # Verify that built-in and loaded commands were removed
        assert "test" not in self.registry._builtin_commands
        assert "test" not in self.registry._loaded_commands
    
    def test_custom_overrides_builtin(self):
        """Test that custom commands override built-in commands."""
        # Create command classes
        BuiltinCommand = create_mock_command_class("test")
        CustomCommand = create_mock_command_class("test")
        
        # Register built-in first
        self.registry.register_builtin(BuiltinCommand())
        
        # Then register custom
        self.registry.register_custom(CustomCommand())
        
        # Should return custom command
        command = self.registry.get_command("test")
        assert command in self.registry._custom_commands.values()
        
        # Verify that built-in command was removed
        assert "test" not in self.registry._builtin_commands
    
    def test_builtin_overrides_loaded(self):
        """Test that built-in commands override loaded commands."""
        # Create command classes
        LoadedCommand = create_mock_command_class("test")
        BuiltinCommand = create_mock_command_class("test")
        
        # Register loaded first
        self.registry.register_loaded(LoadedCommand())
        
        # Then register built-in
        self.registry.register_builtin(BuiltinCommand())
        
        # Should return built-in command
        command = self.registry.get_command("test")
        assert command in self.registry._builtin_commands.values()
        
        # Verify that loaded command was removed
        assert "test" not in self.registry._loaded_commands
    
    def test_custom_conflicts_with_builtin(self):
        """Test that custom commands override built-in commands."""
        # Create command classes
        BuiltinCommand = create_mock_command_class("test")
        CustomCommand = create_mock_command_class("test")
        
        # Register built-in first
        self.registry.register_builtin(BuiltinCommand())
        
        # Register custom with same name - should override built-in
        self.registry.register_custom(CustomCommand())
        
        # Should return custom command
        command = self.registry.get_command("test")
        assert command in self.registry._custom_commands.values()
        assert "test" not in self.registry._builtin_commands
    
    def test_loaded_conflicts_with_custom(self):
        """Test that loaded commands are skipped when conflicting with custom."""
        # Create command classes
        CustomCommand = create_mock_command_class("test")
        LoadedCommand = create_mock_command_class("test")
        
        # Register custom first
        self.registry.register_custom(CustomCommand())
        
        # Try to register loaded with same name - should return False
        result = self.registry.register_loaded(LoadedCommand())
        assert result is False
        
        # Custom command should still be there
        command = self.registry.get_command("test")
        assert command in self.registry._custom_commands.values()
    
    def test_loaded_conflicts_with_builtin(self):
        """Test that loaded commands are skipped when conflicting with built-in."""
        # Create command classes
        BuiltinCommand = create_mock_command_class("test")
        LoadedCommand = create_mock_command_class("test")
        
        # Register built-in first
        self.registry.register_builtin(BuiltinCommand())
        
        # Try to register loaded with same name - should return False
        result = self.registry.register_loaded(LoadedCommand())
        assert result is False
        
        # Built-in command should still be there
        command = self.registry.get_command("test")
        assert command in self.registry._builtin_commands.values()
    
    def test_loaded_duplicate_skipped(self):
        """Test that duplicate loaded commands are skipped."""
        # Create command classes
        LoadedCommand1 = create_mock_command_class("test")
        LoadedCommand2 = create_mock_command_class("test")
        
        # Register loaded command
        result1 = self.registry.register_loaded(LoadedCommand1())
        assert result1 is True
        
        # Try to register another loaded command with same name - should return False
        result2 = self.registry.register_loaded(LoadedCommand2())
        assert result2 is False
    
    def test_get_all_commands_priority_order(self):
        """Test that get_all_commands returns commands in priority order."""
        # Create command classes with different names
        LoadedCommand = create_mock_command_class("test1")
        BuiltinCommand = create_mock_command_class("test2")
        CustomCommand = create_mock_command_class("test3")
        OverrideBuiltinCommand = create_mock_command_class("override")
        OverrideCustomCommand = create_mock_command_class("override")
        
        # Register commands in reverse priority order
        self.registry.register_loaded(LoadedCommand())
        self.registry.register_builtin(BuiltinCommand())
        self.registry.register_custom(CustomCommand())
        
        # Register a custom command that overrides built-in
        self.registry.register_builtin(OverrideBuiltinCommand())
        self.registry.register_custom(OverrideCustomCommand())
        
        all_commands = self.registry.get_all_commands()
        
        # Should have 4 unique commands (test1, test2, test3, override)
        assert len(all_commands) == 4
        
        # Custom commands should be present
        assert "test3" in all_commands
        assert "override" in all_commands
        
        # Built-in command should be present (not overridden)
        assert "test2" in all_commands
        
        # Loaded command should be present (not overridden)
        assert "test1" in all_commands
        
        # Override should be custom version
        assert all_commands["override"] in self.registry._custom_commands.values()
    
    def test_get_commands_by_type(self):
        """Test that get_commands_by_type returns correct grouping."""
        # Create command classes with different names
        LoadedCommand1 = create_mock_command_class("loaded1")
        LoadedCommand2 = create_mock_command_class("loaded2")
        BuiltinCommand1 = create_mock_command_class("builtin1")
        BuiltinCommand2 = create_mock_command_class("builtin2")
        CustomCommand1 = create_mock_command_class("custom1")
        CustomCommand2 = create_mock_command_class("custom2")
        
        # Register commands of different types
        self.registry.register_loaded(LoadedCommand1())
        self.registry.register_loaded(LoadedCommand2())
        self.registry.register_builtin(BuiltinCommand1())
        self.registry.register_builtin(BuiltinCommand2())
        self.registry.register_custom(CustomCommand1())
        self.registry.register_custom(CustomCommand2())
        
        by_type = self.registry.get_commands_by_type()
        
        assert len(by_type["loaded"]) == 2
        assert len(by_type["builtin"]) == 2
        assert len(by_type["custom"]) == 2
        
        assert "loaded1" in by_type["loaded"]
        assert "loaded2" in by_type["loaded"]
        assert "builtin1" in by_type["builtin"]
        assert "builtin2" in by_type["builtin"]
        assert "custom1" in by_type["custom"]
        assert "custom2" in by_type["custom"] 