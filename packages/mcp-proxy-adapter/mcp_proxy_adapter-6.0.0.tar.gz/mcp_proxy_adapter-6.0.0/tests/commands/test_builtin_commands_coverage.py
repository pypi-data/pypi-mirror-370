"""
Additional tests for builtin_commands.py to achieve higher coverage.
"""

import pytest
from unittest.mock import Mock, patch
from mcp_proxy_adapter.commands.builtin_commands import register_builtin_commands, get_builtin_commands_list


class TestBuiltinCommandsCoverage:
    """Additional tests to cover missing lines in builtin_commands."""
    
    def test_register_builtin_commands_success(self):
        """Test register_builtin_commands with success."""
        with patch('mcp_proxy_adapter.commands.builtin_commands.registry') as mock_registry:
            mock_registry.command_exists.return_value = False
            mock_registry.register_builtin.return_value = None
            
            result = register_builtin_commands()
            
            assert result == 8  # All 8 built-in commands should be registered
            assert mock_registry.register_builtin.call_count == 8
    
    def test_register_builtin_commands_already_exists(self):
        """Test register_builtin_commands when command already exists."""
        with patch('mcp_proxy_adapter.commands.builtin_commands.registry') as mock_registry:
            # First command already exists
            mock_registry.command_exists.side_effect = [True, False, False, False, False, False, False, False]
            mock_registry.register_builtin.return_value = None
            
            result = register_builtin_commands()
            
            assert result == 7  # 7 commands should be registered (1 skipped)
            assert mock_registry.register_builtin.call_count == 7
    
    def test_register_builtin_commands_registration_error(self):
        """Test register_builtin_commands with registration error."""
        with patch('mcp_proxy_adapter.commands.builtin_commands.registry') as mock_registry:
            mock_registry.command_exists.return_value = False
            mock_registry.register_builtin.side_effect = Exception("Registration failed")
            
            result = register_builtin_commands()
            
            assert result == 0  # No commands should be registered due to error
            assert mock_registry.register_builtin.call_count == 8  # All calls fail
    
    def test_register_builtin_commands_command_name_extraction(self):
        """Test register_builtin_commands with command name extraction."""
        with patch('mcp_proxy_adapter.commands.builtin_commands.registry') as mock_registry:
            mock_registry.command_exists.return_value = False
            mock_registry.register_builtin.return_value = None
            
            # Test that command name extraction works for commands without 'name' attribute
            # This is already covered by the existing commands in the list
            result = register_builtin_commands()
            
            assert result == 8
            assert mock_registry.register_builtin.call_count == 8
    
    def test_get_builtin_commands_list(self):
        """Test get_builtin_commands_list."""
        result = get_builtin_commands_list()
        
        assert len(result) == 8
        assert all(hasattr(cmd, '__name__') for cmd in result)
        
        # Check that all expected commands are in the list
        command_names = [cmd.__name__ for cmd in result]
        expected_names = [
            'HelpCommand', 'HealthCommand', 'ConfigCommand', 'ReloadCommand',
            'SettingsCommand', 'LoadCommand', 'UnloadCommand', 'PluginsCommand'
        ]
        
        for expected_name in expected_names:
            assert expected_name in command_names 