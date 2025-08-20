"""
Tests for command hooks system.
"""

import pytest
from unittest.mock import Mock, patch

from mcp_proxy_adapter.commands.hooks import CommandHooks, register_custom_commands_hook, register_before_init_hook, register_after_init_hook
from mcp_proxy_adapter.commands.command_registry import CommandRegistry
from mcp_proxy_adapter.commands.base import Command


def create_mock_command_class(command_name: str):
    """Create a mock command class with the given name."""
    class DynamicMockCommand(Command):
        """Dynamic mock command for testing."""
        
        # Set name as class attribute
        name = command_name
        
        def __init__(self):
            pass
        
        async def execute(self, **params):
            return {"result": f"executed {self.name}"}
    
    return DynamicMockCommand


class TestCommandHooks:
    """Test command hooks system."""
    
    def setup_method(self):
        """Setup test method."""
        self.hooks = CommandHooks()
        self.registry = CommandRegistry()
    
    def test_register_custom_commands_hook(self):
        """Test registering custom commands hook."""
        hook_called = False
        
        def test_hook(registry):
            nonlocal hook_called
            hook_called = True
            assert registry is self.registry
        
        self.hooks.register_custom_commands_hook(test_hook)
        assert len(self.hooks._custom_commands_hooks) == 1
        assert test_hook in self.hooks._custom_commands_hooks
    
    def test_register_before_init_hook(self):
        """Test registering before init hook."""
        hook_called = False
        
        def test_hook():
            nonlocal hook_called
            hook_called = True
        
        self.hooks.register_before_init_hook(test_hook)
        assert len(self.hooks._before_init_hooks) == 1
        assert test_hook in self.hooks._before_init_hooks
    
    def test_register_after_init_hook(self):
        """Test registering after init hook."""
        hook_called = False
        
        def test_hook():
            nonlocal hook_called
            hook_called = True
        
        self.hooks.register_after_init_hook(test_hook)
        assert len(self.hooks._after_init_hooks) == 1
        assert test_hook in self.hooks._after_init_hooks
    
    def test_execute_custom_commands_hooks(self):
        """Test executing custom commands hooks."""
        hooks_executed = 0
        
        def test_hook1(registry):
            nonlocal hooks_executed
            hooks_executed += 1
            Hook1Command = create_mock_command_class("hook1")
            registry.register_custom(Hook1Command())
        
        def test_hook2(registry):
            nonlocal hooks_executed
            hooks_executed += 1
            Hook2Command = create_mock_command_class("hook2")
            registry.register_custom(Hook2Command())
        
        self.hooks.register_custom_commands_hook(test_hook1)
        self.hooks.register_custom_commands_hook(test_hook2)
        
        result = self.hooks.execute_custom_commands_hooks(self.registry)
        
        assert result == 2
        assert hooks_executed == 2
        assert self.registry.command_exists("hook1")
        assert self.registry.command_exists("hook2")
    
    def test_execute_before_init_hooks(self):
        """Test executing before init hooks."""
        hooks_executed = 0
        
        def test_hook1():
            nonlocal hooks_executed
            hooks_executed += 1
        
        def test_hook2():
            nonlocal hooks_executed
            hooks_executed += 1
        
        self.hooks.register_before_init_hook(test_hook1)
        self.hooks.register_before_init_hook(test_hook2)
        
        result = self.hooks.execute_before_init_hooks()
        
        assert result == 2
        assert hooks_executed == 2
    
    def test_execute_after_init_hooks(self):
        """Test executing after init hooks."""
        hooks_executed = 0
        
        def test_hook1():
            nonlocal hooks_executed
            hooks_executed += 1
        
        def test_hook2():
            nonlocal hooks_executed
            hooks_executed += 1
        
        self.hooks.register_after_init_hook(test_hook1)
        self.hooks.register_after_init_hook(test_hook2)
        
        result = self.hooks.execute_after_init_hooks()
        
        assert result == 2
        assert hooks_executed == 2
    
    def test_hook_execution_error_handling(self):
        """Test that hook execution errors are handled gracefully."""
        def failing_hook(registry):
            raise Exception("Hook failed")
        
        self.hooks.register_custom_commands_hook(failing_hook)
        
        # Should not raise exception, should return 0
        result = self.hooks.execute_custom_commands_hooks(self.registry)
        assert result == 0
    
    def test_clear_hooks(self):
        """Test clearing all hooks."""
        def test_hook1(registry):
            pass
        
        def test_hook2():
            pass
        
        self.hooks.register_custom_commands_hook(test_hook1)
        self.hooks.register_before_init_hook(test_hook2)
        self.hooks.register_after_init_hook(test_hook2)
        
        assert len(self.hooks._custom_commands_hooks) > 0
        assert len(self.hooks._before_init_hooks) > 0
        assert len(self.hooks._after_init_hooks) > 0
        
        self.hooks.clear_hooks()
        
        assert len(self.hooks._custom_commands_hooks) == 0
        assert len(self.hooks._before_init_hooks) == 0
        assert len(self.hooks._after_init_hooks) == 0


class TestHookFunctions:
    """Test hook registration functions."""
    
    def setup_method(self):
        """Setup test method."""
        self.hooks = CommandHooks()
    
    @patch('mcp_proxy_adapter.commands.hooks.hooks')
    def test_register_custom_commands_hook_function(self, mock_hooks):
        """Test register_custom_commands_hook function."""
        def test_hook(registry):
            pass
        
        register_custom_commands_hook(test_hook)
        mock_hooks.register_custom_commands_hook.assert_called_once_with(test_hook)
    
    @patch('mcp_proxy_adapter.commands.hooks.hooks')
    def test_register_before_init_hook_function(self, mock_hooks):
        """Test register_before_init_hook function."""
        def test_hook():
            pass
        
        register_before_init_hook(test_hook)
        mock_hooks.register_before_init_hook.assert_called_once_with(test_hook)
    
    @patch('mcp_proxy_adapter.commands.hooks.hooks')
    def test_register_after_init_hook_function(self, mock_hooks):
        """Test register_after_init_hook function."""
        def test_hook():
            pass
        
        register_after_init_hook(test_hook)
        mock_hooks.register_after_init_hook.assert_called_once_with(test_hook) 