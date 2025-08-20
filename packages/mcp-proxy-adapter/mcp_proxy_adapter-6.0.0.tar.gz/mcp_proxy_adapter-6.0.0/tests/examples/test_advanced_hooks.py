"""
Tests for advanced hooks functionality.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))


class TestAdvancedHooks:
    """Test advanced hooks functionality."""
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_data_transform_before_hook(self, mock_logger):
        """Test data transform before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import data_transform_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.params = {
            "data": {
                "string_value": "test",
                "number_value": 5,
                "dict_value": {"key": "value"}
            }
        }
        
        data_transform_before_hook(context)
        
        # Verify data was transformed
        assert context.params["data"]["pre_string_value_post"] == "ENHANCED_test_PROCESSED"
        assert context.params["data"]["doubled_number_value"] == 10
        assert context.params["data"]["dict_value"] == {"key": "value"}
        assert context.params["data"]["_hook_modified"] is True
        assert context.params["data_modified"] is True
        assert "_modification_time" in context.params["data"]
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_data_transform_after_hook(self, mock_logger):
        """Test data transform after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import data_transform_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context with result
        context = Mock(spec=HookContext)
        context.result = Mock()
        context.result.transformed_data = {
            "string_value": "test",
            "number_value": 10
        }
        
        data_transform_after_hook(context)
        
        # Verify data was formatted
        assert context.result.transformed_data["formatted_string_value"] == "✨ test ✨"
        assert context.result.transformed_data["number_value"] == 10
        assert context.result.transformed_data["_formatted_by_hook"] is True
        assert "_formatting_time" in context.result.transformed_data
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_data_transform_after_hook_no_result(self, mock_logger):
        """Test data transform after hook with no result."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import data_transform_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context without result
        context = Mock(spec=HookContext)
        context.result = None
        
        # Should not raise exception
        data_transform_after_hook(context)
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_intercept_before_hook_bypass(self, mock_logger):
        """Test intercept before hook with bypass."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import intercept_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context with bypass flag
        context = Mock(spec=HookContext)
        context.params = {"bypass_flag": 0}
        
        # Mock InterceptResult
        intercept_before_hook(context)
        
        # Verify command was intercepted
        assert context.result is not None
        assert hasattr(context.result, 'message')
        assert context.result.message == "Command intercepted by hook - not executed"
        assert context.standard_processing is False
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_intercept_before_hook_no_bypass(self, mock_logger):
        """Test intercept before hook without bypass."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import intercept_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context without bypass flag
        context = Mock(spec=HookContext)
        context.params = {"bypass_flag": 1}
        
        intercept_before_hook(context)
        
        # Verify command was not intercepted
        assert context.params["hook_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_intercept_after_hook_standard_processing(self, mock_logger):
        """Test intercept after hook with standard processing."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import intercept_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context with standard processing
        context = Mock(spec=HookContext)
        context.standard_processing = True
        context.result = Mock()
        context.result.hook_data = {}
        
        intercept_after_hook(context)
        
        # Verify metadata was added
        assert context.result.hook_data["after_hook_processed"] is True
        assert "after_hook_time" in context.result.hook_data
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_intercept_after_hook_intercepted(self, mock_logger):
        """Test intercept after hook with intercepted processing."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import intercept_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context with intercepted processing
        context = Mock(spec=HookContext)
        context.standard_processing = False
        context.result = Mock()
        context.result.hook_data = {}
        
        intercept_after_hook(context)
        
        # Verify metadata was added
        assert context.result.hook_data["after_hook_processed"] is True
        assert "after_hook_time" in context.result.hook_data
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_conditional_transform_hook_before_special_data(self, mock_logger):
        """Test conditional transform hook before with special data."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import conditional_transform_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with special data
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "data_transform"
        context.params = {
            "data": {"key": "special_value"},
            "transform_type": "default"
        }
        
        conditional_transform_hook(context)
        
        # Verify transformation was applied
        assert context.params["transform_type"] == "uppercase"
        assert context.params["_special_enhancement"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_conditional_transform_hook_before_test_data(self, mock_logger):
        """Test conditional transform hook before with test data."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import conditional_transform_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with test data
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "data_transform"
        context.params = {
            "data": {"key": "test_value"},
            "transform_type": "default"
        }
        
        conditional_transform_hook(context)
        
        # Verify transformation was applied
        assert context.params["transform_type"] == "reverse"
        assert context.params["_test_mode"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_conditional_transform_hook_before_other_command(self, mock_logger):
        """Test conditional transform hook before with other command."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import conditional_transform_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with other command
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "other_command"
        context.params = {
            "data": {"key": "special_value"},
            "transform_type": "default"
        }
        
        conditional_transform_hook(context)
        
        # Verify no transformation was applied
        assert context.params["transform_type"] == "default"
        assert "_special_enhancement" not in context.params
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_conditional_transform_hook_after(self, mock_logger):
        """Test conditional transform hook after execution."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import conditional_transform_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context after execution
        context = Mock(spec=HookContext)
        context.hook_type = HookType.AFTER_EXECUTION
        context.command_name = "data_transform"
        context.result = Mock()
        context.result.processing_info = {}
        
        conditional_transform_hook(context)
        
        # Verify metadata was added
        assert context.result.processing_info["conditional_processed"] is True
        assert "conditional_time" in context.result.processing_info
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_smart_intercept_hook_blocked_action(self, mock_logger):
        """Test smart intercept hook with blocked action."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import smart_intercept_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with blocked action
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "intercept"
        context.params = {"action": "blocked", "bypass_flag": 1}
        
        smart_intercept_hook(context)
        
        # Verify command was intercepted
        assert context.result is not None
        assert hasattr(context.result, 'message')
        assert context.result.message == "Command intercepted by smart hook - reason: blocked_action"
        assert context.standard_processing is False
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_smart_intercept_hook_bypass_flag_zero(self, mock_logger):
        """Test smart intercept hook with bypass flag zero."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import smart_intercept_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with bypass flag zero
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "intercept"
        context.params = {"action": "allowed", "bypass_flag": 0}
        
        smart_intercept_hook(context)
        
        # Verify command was intercepted
        assert context.result is not None
        assert hasattr(context.result, 'message')
        assert context.result.message == "Command intercepted by smart hook - reason: bypass_flag_zero"
        assert context.standard_processing is False
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_smart_intercept_hook_allowed(self, mock_logger):
        """Test smart intercept hook with allowed action."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import smart_intercept_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context with allowed action
        context = Mock(spec=HookContext)
        context.hook_type = HookType.BEFORE_EXECUTION
        context.command_name = "intercept"
        context.params = {"action": "allowed", "bypass_flag": 1}
        context.standard_processing = True
        
        smart_intercept_hook(context)
        
        # Verify command was not intercepted
        assert context.standard_processing is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_smart_intercept_hook_after_execution(self, mock_logger):
        """Test smart intercept hook after execution."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import smart_intercept_hook
        from mcp_proxy_adapter.commands.hooks import HookContext, HookType
        
        # Create mock context after execution
        context = Mock(spec=HookContext)
        context.hook_type = HookType.AFTER_EXECUTION
        context.command_name = "intercept"
        
        # Should not raise exception
        smart_intercept_hook(context)
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_register_advanced_hooks(self, mock_logger):
        """Test register_advanced_hooks function."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import register_advanced_hooks
        
        # Mock hooks manager
        mock_hooks_manager = Mock()
        
        # Mock command classes for hooks
        with patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.InterceptResult'):
            register_advanced_hooks(mock_hooks_manager)
        
        # Verify hooks were registered
        assert mock_hooks_manager.register_before_hook.call_count >= 14
        assert mock_hooks_manager.register_after_hook.call_count >= 14
        assert mock_hooks_manager.register_global_before_hook.call_count >= 2
        assert mock_hooks_manager.register_global_after_hook.call_count >= 1
        assert mock_hooks_manager.register_before_init_hook.call_count == 1
        assert mock_hooks_manager.register_after_init_hook.call_count == 1
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_system_before_init_hook(self, mock_logger):
        """Test system before init hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import system_before_init_hook
        
        # Mock registry
        mock_registry = Mock()
        mock_registry.metadata = {}
        
        system_before_init_hook(mock_registry)
        
        # Verify metadata was added
        assert "init_start_time" in mock_registry.metadata
        assert mock_registry.metadata["init_hooks_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_system_after_init_hook(self, mock_logger):
        """Test system after init hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import system_after_init_hook
        
        # Mock registry
        mock_registry = Mock()
        mock_registry.metadata = {}
        mock_registry.get_all_commands.return_value = {"cmd1": Mock(), "cmd2": Mock()}
        
        system_after_init_hook(mock_registry)
        
        # Verify metadata was added
        assert "init_end_time" in mock_registry.metadata
        assert mock_registry.metadata["total_commands"] == 2
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_echo_before_hook(self, mock_logger):
        """Test echo before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import echo_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "echo"
        context.params = {"message": "test message"}
        context.metadata = {}
        
        echo_before_hook(context)
        
        # Verify timestamp was added
        assert "[" in context.params["message"] and "]" in context.params["message"]
        assert context.params["_timestamp_added"] is True
        assert context.metadata["echo_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_echo_after_hook(self, mock_logger):
        """Test echo after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import echo_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "echo"
        context.result = Mock()
        context.result.message = "test message"
        context.metadata = {}
        
        echo_after_hook(context)
        
        # Verify message was formatted
        assert context.result.message == "ECHO: test message"
        assert context.metadata["echo_formatted"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_help_before_hook(self, mock_logger):
        """Test help before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import help_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "help"
        context.params = {}
        context.metadata = {}
        
        help_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["help_requested"] is True
        assert "help_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_help_after_hook(self, mock_logger):
        """Test help after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import help_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "help"
        context.result = Mock()
        context.result.commands_info = {"hooks_available": False, "hook_count": 0}
        
        # Mock the hook to actually set the values
        with patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.hooks') as mock_hooks:
            mock_hooks.get_hooks_count.return_value = 14
            help_after_hook(context)
        
        # Verify metadata was added
        assert context.result.commands_info["hooks_available"] is True
        assert context.result.commands_info["hook_count"] == 15
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_health_before_hook(self, mock_logger):
        """Test health before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import health_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "health"
        context.params = {}
        context.metadata = {}
        
        health_before_hook(context)
        
        # Verify metadata was added
        assert "health_check_start" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_health_after_hook(self, mock_logger):
        """Test health after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import health_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "health"
        context.result = Mock()
        context.result.status = {}
        
        health_after_hook(context)
        
        # Verify metadata was added
        assert context.result.status["hooks_healthy"] is True
        assert context.result.status["hook_count"] == 15
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_config_before_hook(self, mock_logger):
        """Test config before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import config_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "config"
        context.params = {"operation": "get"}
        context.metadata = {}
        
        config_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["config_operation"] == "get"
        assert "config_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_config_after_hook(self, mock_logger):
        """Test config after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import config_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "config"
        context.result = Mock()
        context.result.config = {}
        
        # Mock the hook to actually set the values
        with patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.hooks') as mock_hooks:
            mock_hooks.get_hooks_count.return_value = 14
            config_after_hook(context)
        
        # Verify metadata was added
        assert context.result.config["hooks_enabled"] is True
        assert context.result.config["hook_system_version"] == "1.0.0"
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_load_before_hook(self, mock_logger):
        """Test load before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import load_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "load"
        context.params = {"source": "test_source"}
        context.metadata = {}
        
        load_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["load_source"] == "test_source"
        assert "load_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_load_after_hook(self, mock_logger):
        """Test load after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import load_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "load"
        context.result = Mock()
        context.result.loaded_commands = {}
        
        load_after_hook(context)
        
        # Verify metadata was added
        assert context.result.loaded_commands["_hooks_loaded"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_unload_before_hook(self, mock_logger):
        """Test unload before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import unload_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "unload"
        context.params = {"command_name": "test_command"}
        context.metadata = {}
        
        unload_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["unload_command"] == "test_command"
        assert "unload_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_unload_after_hook(self, mock_logger):
        """Test unload after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import unload_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "unload"
        context.result = Mock()
        context.result.unloaded_commands = {}
        
        unload_after_hook(context)
        
        # Verify metadata was added
        assert context.result.unloaded_commands["_hooks_cleaned"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_reload_before_hook(self, mock_logger):
        """Test reload before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import reload_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "reload"
        context.params = {"components": ["commands", "config"]}
        context.metadata = {}
        
        reload_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["reload_components"] == ["commands", "config"]
        assert "reload_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_reload_after_hook(self, mock_logger):
        """Test reload after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import reload_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "reload"
        context.result = Mock()
        context.result.reloaded_components = {}
        
        reload_after_hook(context)
        
        # Verify metadata was added
        assert context.result.reloaded_components["_hooks_reloaded"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_plugins_before_hook(self, mock_logger):
        """Test plugins before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import plugins_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "plugins"
        context.params = {}
        context.metadata = {}
        
        plugins_before_hook(context)
        
        # Verify metadata was added
        assert "plugins_check_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_plugins_after_hook(self, mock_logger):
        """Test plugins after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import plugins_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "plugins"
        context.result = Mock()
        context.result.plugins = {}
        
        plugins_after_hook(context)
        
        # Verify metadata was added
        assert context.result.plugins["_hooks_plugin"]["name"] == "Advanced Hooks System"
        assert context.result.plugins["_hooks_plugin"]["version"] == "1.0.0"
        assert context.result.plugins["_hooks_plugin"]["enabled"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_settings_before_hook(self, mock_logger):
        """Test settings before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import settings_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "settings"
        context.params = {"operation": "set"}
        context.metadata = {}
        
        settings_before_hook(context)
        
        # Verify metadata was added
        assert context.metadata["settings_operation"] == "set"
        assert "settings_time" in context.metadata
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_settings_after_hook(self, mock_logger):
        """Test settings after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import settings_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "settings"
        context.result = Mock()
        context.result.settings = {}
        
        settings_after_hook(context)
        
        # Verify metadata was added
        assert context.result.settings["hooks"]["enabled"] is True
        assert context.result.settings["hooks"]["before_hooks"] == 15
        assert context.result.settings["hooks"]["after_hooks"] == 15
        assert context.result.settings["hooks"]["global_hooks"] == 3
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_manual_echo_before_hook(self, mock_logger):
        """Test manual echo before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import manual_echo_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "manual_echo"
        context.params = {"message": "test message"}
        context.metadata = {}
        
        manual_echo_before_hook(context)
        
        # Verify metadata was added
        assert context.params["_manually_registered"] is True
        assert context.params["_hook_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_manual_echo_after_hook(self, mock_logger):
        """Test manual echo after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import manual_echo_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "manual_echo"
        context.result = Mock()
        context.result.message = "test message"
        context.metadata = {}
        
        manual_echo_after_hook(context)
        
        # Verify message was formatted
        assert context.result.message == "[MANUAL] test message"
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_auto_echo_before_hook(self, mock_logger):
        """Test auto echo before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import auto_echo_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "auto_echo"
        context.params = {"message": "test message"}
        context.metadata = {}
        
        auto_echo_before_hook(context)
        
        # Verify metadata was added
        assert context.params["_auto_registered"] is True
        assert context.params["_hook_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_auto_echo_after_hook(self, mock_logger):
        """Test auto echo after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import auto_echo_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "auto_echo"
        context.result = Mock()
        context.result.message = "test message"
        context.metadata = {}
        
        auto_echo_after_hook(context)
        
        # Verify message was formatted
        assert context.result.message == "[AUTO] test message"
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_auto_info_before_hook(self, mock_logger):
        """Test auto info before hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import auto_info_before_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "auto_info"
        context.params = {"topic": "test topic"}
        context.metadata = {}
        
        auto_info_before_hook(context)
        
        # Verify metadata was added
        assert context.params["_auto_registered"] is True
        assert context.params["_hook_processed"] is True
    
    @patch('mcp_proxy_adapter.examples.custom_commands.advanced_hooks.logger')
    def test_auto_info_after_hook(self, mock_logger):
        """Test auto info after hook."""
        from mcp_proxy_adapter.examples.custom_commands.advanced_hooks import auto_info_after_hook
        from mcp_proxy_adapter.commands.hooks import HookContext
        
        # Create mock context
        context = Mock(spec=HookContext)
        context.command_name = "auto_info"
        context.result = Mock()
        context.result.info = {}
        context.metadata = {}
        
        auto_info_after_hook(context)
        
        # Verify metadata was added
        assert context.result.info["_auto_generated"] is True
        assert context.result.info["_hook_enhanced"] is True 