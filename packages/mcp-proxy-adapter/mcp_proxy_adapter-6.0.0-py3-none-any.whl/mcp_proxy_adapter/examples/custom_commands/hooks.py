"""
Custom Hooks Example

This module demonstrates how to use hooks in the MCP Proxy Adapter framework.
Hooks allow you to intercept command execution before and after processing.
"""

import time
import logging
from typing import Dict, Any
from datetime import datetime

from mcp_proxy_adapter.commands.hooks import HookContext, HookType


# Setup logging for hooks
logger = logging.getLogger("mcp_proxy_adapter.examples.hooks")


def echo_before_hook(context: HookContext) -> None:
    """
    Before hook for echo command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔔 Echo command will be executed with params: {context.params}")
    
    # Add timestamp to params
    context.params["hook_timestamp"] = datetime.now().isoformat()
    
    # Log the message that will be echoed
    message = context.params.get("message", context.params.get("text", "Hello, World!"))
    logger.info(f"📢 Will echo message: '{message}'")


def echo_after_hook(context: HookContext) -> None:
    """
    After hook for echo command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"✅ Echo command completed successfully")
    
    # Log the result
    if context.result and hasattr(context.result, 'data'):
        echoed_message = context.result.data.get("message", "Unknown")
        timestamp = context.result.data.get("timestamp", "Unknown")
        logger.info(f"📤 Echoed: '{echoed_message}' at {timestamp}")


def help_before_hook(context: HookContext) -> None:
    """
    Before hook for help command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔔 Help command will be executed")
    
    # Add request tracking
    context.params["request_id"] = f"help_{int(time.time())}"
    context.params["hook_processed"] = True
    
    cmdname = context.params.get("cmdname")
    if cmdname:
        logger.info(f"📖 Will get help for command: {cmdname}")
    else:
        logger.info(f"📖 Will get help for all commands")


def help_after_hook(context: HookContext) -> None:
    """
    After hook for help command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"✅ Help command completed successfully")
    
    # Log the result summary
    if context.result and hasattr(context.result, 'to_dict'):
        result_dict = context.result.to_dict()
        total_commands = result_dict.get("total", 0)
        logger.info(f"📚 Help returned {total_commands} commands")


def health_before_hook(context: HookContext) -> None:
    """
    Before hook for health command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔔 Health command will be executed")
    
    # Add health check metadata
    context.params["health_check_id"] = f"health_{int(time.time())}"
    context.params["hook_enhanced"] = True
    
    logger.info(f"🏥 Starting enhanced health check")


def health_after_hook(context: HookContext) -> None:
    """
    After hook for health command.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"✅ Health command completed successfully")
    
    # Log health status
    if context.result and hasattr(context.result, 'data'):
        status = context.result.data.get("status", "unknown")
        uptime = context.result.data.get("uptime", 0)
        logger.info(f"🏥 Health status: {status}, Uptime: {uptime:.2f}s")


def global_before_hook(context: HookContext) -> None:
    """
    Global before hook for all commands.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🌐 Global before hook: {context.command_name}")
    
    # Add global tracking
    context.params["global_hook_processed"] = True
    context.params["execution_start_time"] = time.time()
    
    logger.info(f"🚀 Starting execution of '{context.command_name}'")


def global_after_hook(context: HookContext) -> None:
    """
    Global after hook for all commands.
    
    Args:
        context: Hook context with command information
    """
    start_time = context.params.get("execution_start_time", time.time())
    execution_time = time.time() - start_time
    
    logger.info(f"🌐 Global after hook: {context.command_name}")
    logger.info(f"⏱️  Execution time: {execution_time:.3f}s")
    
    # Log success/failure
    if context.result:
        logger.info(f"✅ Command '{context.command_name}' completed successfully")
    else:
        logger.warning(f"⚠️  Command '{context.command_name}' completed with issues")


def performance_hook(context: HookContext) -> None:
    """
    Performance monitoring hook.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        # Store start time
        context.params["_performance_start"] = time.time()
        logger.debug(f"⏱️  Performance monitoring started for {context.command_name}")
    
    elif context.hook_type == HookType.AFTER_EXECUTION:
        # Calculate execution time
        start_time = context.params.get("_performance_start", time.time())
        execution_time = time.time() - start_time
        
        logger.info(f"📊 Performance: {context.command_name} took {execution_time:.3f}s")
        
        # Log slow commands
        if execution_time > 1.0:
            logger.warning(f"🐌 Slow command detected: {context.command_name} ({execution_time:.3f}s)")


def security_hook(context: HookContext) -> None:
    """
    Security monitoring hook.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        # Check for sensitive data in params
        sensitive_keys = ["password", "token", "secret", "key"]
        found_sensitive = [key for key in context.params.keys() if any(s in key.lower() for s in sensitive_keys)]
        
        if found_sensitive:
            logger.warning(f"🔒 Security: Sensitive parameters detected in {context.command_name}: {found_sensitive}")
        
        # Add security metadata
        context.params["_security_checked"] = True
        logger.debug(f"🔒 Security check completed for {context.command_name}")


def register_all_hooks(hooks_manager) -> None:
    """
    Register all hooks with the hooks manager.
    
    Args:
        hooks_manager: The hooks manager instance
    """
    logger.info("🔧 Registering custom hooks...")
    
    # Register command-specific hooks
    hooks_manager.register_before_hook("echo", echo_before_hook)
    hooks_manager.register_after_hook("echo", echo_after_hook)
    
    hooks_manager.register_before_hook("help", help_before_hook)
    hooks_manager.register_after_hook("help", help_after_hook)
    
    hooks_manager.register_before_hook("health", health_before_hook)
    hooks_manager.register_after_hook("health", health_after_hook)
    
    # Register global hooks
    hooks_manager.register_global_before_hook(global_before_hook)
    hooks_manager.register_global_after_hook(global_after_hook)
    
    # Register utility hooks
    hooks_manager.register_global_before_hook(performance_hook)
    hooks_manager.register_global_after_hook(performance_hook)
    
    hooks_manager.register_global_before_hook(security_hook)
    
    logger.info("✅ All hooks registered successfully") 