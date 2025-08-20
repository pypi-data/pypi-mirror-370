"""
Additional tests for hooks.py to achieve higher coverage.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_proxy_adapter.commands.hooks import CommandHooks, hooks


def create_mock_hook(name="test_hook"):
    """Create a mock hook function with __name__ attribute."""
    hook_func = Mock()
    hook_func.__name__ = name
    return hook_func


class TestCommandHooksCoverage:
    """Additional tests to cover missing lines in CommandHooks."""
    
    @pytest.fixture
    def command_hooks(self):
        """Create CommandHooks instance."""
        return CommandHooks()
    
    def test_register_custom_commands_hook(self, command_hooks):
        """Test register_custom_commands_hook."""
        hook_func = create_mock_hook()
        command_hooks.register_custom_commands_hook(hook_func)
        
        assert hook_func in command_hooks._custom_commands_hooks
    
    def test_register_before_init_hook(self, command_hooks):
        """Test register_before_init_hook."""
        hook_func = create_mock_hook()
        command_hooks.register_before_init_hook(hook_func)
        
        assert hook_func in command_hooks._before_init_hooks
    
    def test_register_after_init_hook(self, command_hooks):
        """Test register_after_init_hook."""
        hook_func = create_mock_hook()
        command_hooks.register_after_init_hook(hook_func)
        
        assert hook_func in command_hooks._after_init_hooks
    
    def test_register_before_command_hook(self, command_hooks):
        """Test register_before_command_hook."""
        hook_func = create_mock_hook()
        command_hooks.register_before_command_hook(hook_func)
        
        assert hook_func in command_hooks._before_command_hooks
    
    def test_register_after_command_hook(self, command_hooks):
        """Test register_after_command_hook."""
        hook_func = create_mock_hook()
        command_hooks.register_after_command_hook(hook_func)
        
        assert hook_func in command_hooks._after_command_hooks
    
    def test_execute_custom_commands_hooks_success(self, command_hooks):
        """Test execute_custom_commands_hooks with success."""
        hook_func = create_mock_hook()
        command_hooks._custom_commands_hooks.append(hook_func)
        
        registry = Mock()
        result = command_hooks.execute_custom_commands_hooks(registry)
        
        assert result == 1
        hook_func.assert_called_once_with(registry)
    
    def test_execute_custom_commands_hooks_exception(self, command_hooks):
        """Test execute_custom_commands_hooks with exception."""
        hook_func = create_mock_hook()
        hook_func.side_effect = Exception("Hook failed")
        command_hooks._custom_commands_hooks.append(hook_func)
        
        registry = Mock()
        result = command_hooks.execute_custom_commands_hooks(registry)
        
        assert result == 0
        hook_func.assert_called_once_with(registry)
    
    def test_execute_before_init_hooks_success(self, command_hooks):
        """Test execute_before_init_hooks with success."""
        hook_func = create_mock_hook()
        command_hooks._before_init_hooks.append(hook_func)
        
        result = command_hooks.execute_before_init_hooks()
        
        assert result == 1
        hook_func.assert_called_once()
    
    def test_execute_before_init_hooks_exception(self, command_hooks):
        """Test execute_before_init_hooks with exception."""
        hook_func = create_mock_hook()
        hook_func.side_effect = Exception("Hook failed")
        command_hooks._before_init_hooks.append(hook_func)
        
        result = command_hooks.execute_before_init_hooks()
        
        assert result == 0
        hook_func.assert_called_once()
    
    def test_execute_after_init_hooks_success(self, command_hooks):
        """Test execute_after_init_hooks with success."""
        hook_func = create_mock_hook()
        command_hooks._after_init_hooks.append(hook_func)
        
        result = command_hooks.execute_after_init_hooks()
        
        assert result == 1
        hook_func.assert_called_once()
    
    def test_execute_after_init_hooks_exception(self, command_hooks):
        """Test execute_after_init_hooks with exception."""
        hook_func = create_mock_hook()
        hook_func.side_effect = Exception("Hook failed")
        command_hooks._after_init_hooks.append(hook_func)
        
        result = command_hooks.execute_after_init_hooks()
        
        assert result == 0
        hook_func.assert_called_once()
    
    def test_execute_before_command_hooks_success(self, command_hooks):
        """Test execute_before_command_hooks with success."""
        hook_func = create_mock_hook()
        command_hooks._before_command_hooks.append(hook_func)
        
        command_name = "test_command"
        params = {"param1": "value1"}
        
        result = command_hooks.execute_before_command_hooks(command_name, params)
        
        assert result == 1
        hook_func.assert_called_once_with(command_name, params)
    
    def test_execute_before_command_hooks_exception(self, command_hooks):
        """Test execute_before_command_hooks with exception."""
        hook_func = create_mock_hook()
        hook_func.side_effect = Exception("Hook failed")
        command_hooks._before_command_hooks.append(hook_func)
        
        command_name = "test_command"
        params = {"param1": "value1"}
        
        result = command_hooks.execute_before_command_hooks(command_name, params)
        
        assert result == 0
        hook_func.assert_called_once_with(command_name, params)
    
    def test_execute_after_command_hooks_success(self, command_hooks):
        """Test execute_after_command_hooks with success."""
        hook_func = create_mock_hook()
        command_hooks._after_command_hooks.append(hook_func)
        
        command_name = "test_command"
        params = {"param1": "value1"}
        result_data = {"success": True}
        
        result = command_hooks.execute_after_command_hooks(command_name, params, result_data)
        
        assert result == 1
        hook_func.assert_called_once_with(command_name, params, result_data)
    
    def test_execute_after_command_hooks_exception(self, command_hooks):
        """Test execute_after_command_hooks with exception."""
        hook_func = create_mock_hook()
        hook_func.side_effect = Exception("Hook failed")
        command_hooks._after_command_hooks.append(hook_func)
        
        command_name = "test_command"
        params = {"param1": "value1"}
        result_data = {"success": True}
        
        result = command_hooks.execute_after_command_hooks(command_name, params, result_data)
        
        assert result == 0
        hook_func.assert_called_once_with(command_name, params, result_data)
    
    def test_clear_hooks(self, command_hooks):
        """Test clear_hooks."""
        # Add some hooks
        hook_func1 = create_mock_hook("hook1")
        hook_func2 = create_mock_hook("hook2")
        command_hooks._custom_commands_hooks.append(hook_func1)
        command_hooks._before_init_hooks.append(hook_func2)
        
        # Clear hooks
        command_hooks.clear_hooks()
        
        assert len(command_hooks._custom_commands_hooks) == 0
        assert len(command_hooks._before_init_hooks) == 0
        assert len(command_hooks._after_init_hooks) == 0
        assert len(command_hooks._before_command_hooks) == 0
        assert len(command_hooks._after_command_hooks) == 0


class TestGlobalHooksCoverage:
    """Additional tests to cover missing lines in global hooks functions."""
    
    def test_register_custom_commands_hook_global(self):
        """Test global register_custom_commands_hook function."""
        from mcp_proxy_adapter.commands.hooks import register_custom_commands_hook
        
        hook_func = create_mock_hook()
        register_custom_commands_hook(hook_func)
        
        assert hook_func in hooks._custom_commands_hooks
    
    def test_register_before_init_hook_global(self):
        """Test global register_before_init_hook function."""
        from mcp_proxy_adapter.commands.hooks import register_before_init_hook
        
        hook_func = create_mock_hook()
        register_before_init_hook(hook_func)
        
        assert hook_func in hooks._before_init_hooks
    
    def test_register_after_init_hook_global(self):
        """Test global register_after_init_hook function."""
        from mcp_proxy_adapter.commands.hooks import register_after_init_hook
        
        hook_func = create_mock_hook()
        register_after_init_hook(hook_func)
        
        assert hook_func in hooks._after_init_hooks
    
    def test_register_before_command_hook_global(self):
        """Test global register_before_command_hook function."""
        from mcp_proxy_adapter.commands.hooks import register_before_command_hook
        
        hook_func = create_mock_hook()
        register_before_command_hook(hook_func)
        
        assert hook_func in hooks._before_command_hooks
    
    def test_register_after_command_hook_global(self):
        """Test global register_after_command_hook function."""
        from mcp_proxy_adapter.commands.hooks import register_after_command_hook
        
        hook_func = create_mock_hook()
        register_after_command_hook(hook_func)
        
        assert hook_func in hooks._after_command_hooks 