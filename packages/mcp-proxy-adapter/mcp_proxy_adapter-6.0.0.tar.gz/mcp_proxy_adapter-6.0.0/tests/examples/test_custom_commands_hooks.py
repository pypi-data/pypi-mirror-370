"""
Tests for custom commands hooks example.

This module tests the custom hooks functionality including:
- Echo command hooks
- Help command hooks
- Health command hooks
- Global hooks
- Performance monitoring hooks
- Security monitoring hooks
- Hook registration
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from datetime import datetime

from mcp_proxy_adapter.commands.hooks import HookContext, HookType
from mcp_proxy_adapter.examples.custom_commands import hooks


class TestEchoHooks:
    """Test echo command hooks."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_echo_before_hook_with_message(self, mock_logger):
        """Test echo_before_hook with message parameter."""
        context = HookContext(
            command_name="echo",
            params={"message": "Hello, World!"},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.echo_before_hook(context)

        assert "hook_timestamp" in context.params
        assert context.params["message"] == "Hello, World!"
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_echo_before_hook_with_text(self, mock_logger):
        """Test echo_before_hook with text parameter."""
        context = HookContext(
            command_name="echo",
            params={"text": "Test message"},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.echo_before_hook(context)

        assert "hook_timestamp" in context.params
        assert context.params["text"] == "Test message"
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_echo_before_hook_without_message(self, mock_logger):
        """Test echo_before_hook without message or text parameter."""
        context = HookContext(
            command_name="echo",
            params={},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.echo_before_hook(context)

        assert "hook_timestamp" in context.params
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_echo_after_hook_with_result(self, mock_logger):
        """Test echo_after_hook with result containing data."""
        mock_result = MagicMock()
        mock_result.data = {
            "message": "Echoed message",
            "timestamp": "2023-01-01T12:00:00"
        }

        context = HookContext(
            command_name="echo",
            params={},
            result=mock_result,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.echo_after_hook(context)

        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_echo_after_hook_without_result(self, mock_logger):
        """Test echo_after_hook without result."""
        context = HookContext(
            command_name="echo",
            params={},
            result=None,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.echo_after_hook(context)

        mock_logger.info.assert_called()


class TestHelpHooks:
    """Test help command hooks."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_help_before_hook_with_cmdname(self, mock_time, mock_logger):
        """Test help_before_hook with cmdname parameter."""
        mock_time.time.return_value = 1234567890
        context = HookContext(
            command_name="help",
            params={"cmdname": "echo"},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.help_before_hook(context)

        assert "request_id" in context.params
        assert context.params["request_id"] == "help_1234567890"
        assert context.params["hook_processed"] is True
        assert context.params["cmdname"] == "echo"
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_help_before_hook_without_cmdname(self, mock_time, mock_logger):
        """Test help_before_hook without cmdname parameter."""
        mock_time.time.return_value = 1234567890
        context = HookContext(
            command_name="help",
            params={},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.help_before_hook(context)

        assert "request_id" in context.params
        assert context.params["request_id"] == "help_1234567890"
        assert context.params["hook_processed"] is True
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_help_after_hook_with_result(self, mock_logger):
        """Test help_after_hook with result containing total."""
        mock_result = MagicMock()
        mock_result.to_dict.return_value = {"total": 5}

        context = HookContext(
            command_name="help",
            params={},
            result=mock_result,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.help_after_hook(context)

        mock_result.to_dict.assert_called_once()
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_help_after_hook_without_result(self, mock_logger):
        """Test help_after_hook without result."""
        context = HookContext(
            command_name="help",
            params={},
            result=None,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.help_after_hook(context)

        mock_logger.info.assert_called()


class TestHealthHooks:
    """Test health command hooks."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_health_before_hook(self, mock_time, mock_logger):
        """Test health_before_hook."""
        mock_time.time.return_value = 1234567890
        context = HookContext(
            command_name="health",
            params={},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.health_before_hook(context)

        assert "health_check_id" in context.params
        assert context.params["health_check_id"] == "health_1234567890"
        assert context.params["hook_enhanced"] is True
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_health_after_hook_with_result(self, mock_logger):
        """Test health_after_hook with result containing data."""
        mock_result = MagicMock()
        mock_result.data = {
            "status": "healthy",
            "uptime": 123.45
        }

        context = HookContext(
            command_name="health",
            params={},
            result=mock_result,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.health_after_hook(context)

        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_health_after_hook_without_result(self, mock_logger):
        """Test health_after_hook without result."""
        context = HookContext(
            command_name="health",
            params={},
            result=None,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.health_after_hook(context)

        mock_logger.info.assert_called()


class TestGlobalHooks:
    """Test global hooks."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_global_before_hook(self, mock_time, mock_logger):
        """Test global_before_hook."""
        mock_time.time.return_value = 1234567890
        context = HookContext(
            command_name="test_command",
            params={},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.global_before_hook(context)

        assert "global_hook_processed" in context.params
        assert context.params["global_hook_processed"] is True
        assert "execution_start_time" in context.params
        assert context.params["execution_start_time"] == 1234567890
        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_global_after_hook_with_result(self, mock_time, mock_logger):
        """Test global_after_hook with result."""
        mock_time.time.return_value = 1234567891
        context = HookContext(
            command_name="test_command",
            params={"execution_start_time": 1234567890},
            result=MagicMock(),
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.global_after_hook(context)

        mock_logger.info.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_global_after_hook_without_result(self, mock_time, mock_logger):
        """Test global_after_hook without result."""
        mock_time.time.return_value = 1234567891
        context = HookContext(
            command_name="test_command",
            params={"execution_start_time": 1234567890},
            result=None,
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.global_after_hook(context)

        mock_logger.info.assert_called()
        mock_logger.warning.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_global_after_hook_without_start_time(self, mock_time, mock_logger):
        """Test global_after_hook without execution_start_time."""
        mock_time.time.return_value = 1234567891
        context = HookContext(
            command_name="test_command",
            params={},
            result=MagicMock(),
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.global_after_hook(context)

        mock_logger.info.assert_called()


class TestPerformanceHook:
    """Test performance monitoring hook."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_performance_hook_before_execution(self, mock_time, mock_logger):
        """Test performance_hook with BEFORE_EXECUTION."""
        mock_time.time.return_value = 1234567890
        context = HookContext(
            command_name="test_command",
            params={},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.performance_hook(context)

        assert "_performance_start" in context.params
        assert context.params["_performance_start"] == 1234567890
        mock_logger.debug.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_performance_hook_after_execution_fast(self, mock_time, mock_logger):
        """Test performance_hook with AFTER_EXECUTION for fast command."""
        mock_time.time.side_effect = [1234567890, 1234567890.5]  # 0.5s execution
        context = HookContext(
            command_name="test_command",
            params={"_performance_start": 1234567890},
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.performance_hook(context)

        mock_logger.info.assert_called()
        mock_logger.warning.assert_not_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_performance_hook_after_execution_slow(self, mock_time, mock_logger):
        """Test performance_hook with AFTER_EXECUTION for slow command."""
        mock_time.time.side_effect = [1234567890, 1234567891.5]  # 1.5s execution
        context = HookContext(
            command_name="test_command",
            params={"_performance_start": 1234567890},
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.performance_hook(context)

        mock_logger.info.assert_called()
        mock_logger.warning.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.time')
    def test_performance_hook_after_execution_without_start_time(self, mock_time, mock_logger):
        """Test performance_hook with AFTER_EXECUTION without start time."""
        mock_time.time.return_value = 1234567891
        context = HookContext(
            command_name="test_command",
            params={},
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.performance_hook(context)

        mock_logger.info.assert_called()


class TestSecurityHook:
    """Test security monitoring hook."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_security_hook_before_execution_with_sensitive_data(self, mock_logger):
        """Test security_hook with sensitive data in params."""
        context = HookContext(
            command_name="test_command",
            params={"password": "secret", "token": "abc123", "normal_param": "value"},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.security_hook(context)

        assert "_security_checked" in context.params
        assert context.params["_security_checked"] is True
        mock_logger.warning.assert_called()
        mock_logger.debug.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_security_hook_before_execution_without_sensitive_data(self, mock_logger):
        """Test security_hook without sensitive data in params."""
        context = HookContext(
            command_name="test_command",
            params={"normal_param": "value", "another_param": "data"},
            hook_type=HookType.BEFORE_EXECUTION
        )

        hooks.security_hook(context)

        assert "_security_checked" in context.params
        assert context.params["_security_checked"] is True
        mock_logger.warning.assert_not_called()
        mock_logger.debug.assert_called()

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_security_hook_after_execution(self, mock_logger):
        """Test security_hook with AFTER_EXECUTION (should do nothing)."""
        context = HookContext(
            command_name="test_command",
            params={},
            hook_type=HookType.AFTER_EXECUTION
        )

        hooks.security_hook(context)

        mock_logger.warning.assert_not_called()
        mock_logger.debug.assert_not_called()


class TestRegisterAllHooks:
    """Test hook registration."""

    @patch('mcp_proxy_adapter.examples.custom_commands.hooks.logger')
    def test_register_all_hooks(self, mock_logger):
        """Test register_all_hooks function."""
        mock_hooks_manager = MagicMock()

        hooks.register_all_hooks(mock_hooks_manager)

        # Verify command-specific hooks
        mock_hooks_manager.register_before_hook.assert_any_call("echo", hooks.echo_before_hook)
        mock_hooks_manager.register_after_hook.assert_any_call("echo", hooks.echo_after_hook)
        mock_hooks_manager.register_before_hook.assert_any_call("help", hooks.help_before_hook)
        mock_hooks_manager.register_after_hook.assert_any_call("help", hooks.help_after_hook)
        mock_hooks_manager.register_before_hook.assert_any_call("health", hooks.health_before_hook)
        mock_hooks_manager.register_after_hook.assert_any_call("health", hooks.health_after_hook)

        # Verify global hooks
        mock_hooks_manager.register_global_before_hook.assert_any_call(hooks.global_before_hook)
        mock_hooks_manager.register_global_after_hook.assert_any_call(hooks.global_after_hook)
        mock_hooks_manager.register_global_before_hook.assert_any_call(hooks.performance_hook)
        mock_hooks_manager.register_global_after_hook.assert_any_call(hooks.performance_hook)
        mock_hooks_manager.register_global_before_hook.assert_any_call(hooks.security_hook)

        mock_logger.info.assert_called() 