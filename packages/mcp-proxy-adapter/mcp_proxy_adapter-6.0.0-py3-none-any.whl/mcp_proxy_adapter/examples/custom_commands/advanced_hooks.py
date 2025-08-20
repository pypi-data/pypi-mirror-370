"""
Advanced Hooks Example

This module demonstrates advanced hook capabilities:
1. Data transformation hooks - modify input data before command execution and format output after
2. Interception hooks - completely bypass command execution based on conditions
"""

import time
import logging
from typing import Dict, Any
from datetime import datetime

from mcp_proxy_adapter.commands.hooks import hooks
from mcp_proxy_adapter.commands.result import CommandResult
from mcp_proxy_adapter.commands.hooks import HookContext
from mcp_proxy_adapter.commands.hooks import HookType
# Import will be done locally when needed to avoid circular imports


# Setup logging for advanced hooks
logger = logging.getLogger("mcp_proxy_adapter.examples.advanced_hooks")


def data_transform_before_hook(context: HookContext) -> None:
    """
    Before hook for data_transform command - modifies input data.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔄 Data transform before hook: {context}")
    
    # Get original data
    original_data = context.params.get("data", {})
    
    # Transform data before command execution
    transformed_data = {}
    for key, value in original_data.items():
        if isinstance(value, str):
            # Add prefix and suffix to string values
            transformed_data[f"pre_{key}_post"] = f"ENHANCED_{value}_PROCESSED"
        elif isinstance(value, (int, float)):
            # Multiply numeric values by 2
            transformed_data[f"doubled_{key}"] = value * 2
        else:
            # Keep other types as is
            transformed_data[key] = value
    
    # Add metadata
    transformed_data["_hook_modified"] = True
    transformed_data["_modification_time"] = datetime.now().isoformat()
    
    # Replace original data with transformed data
    context.params["data"] = transformed_data
    context.params["data_modified"] = True
    
    logger.info(f"📊 Original data: {original_data}")
    logger.info(f"🔄 Transformed data: {transformed_data}")
    

def data_transform_after_hook(context: HookContext) -> None:
    """
    After hook for data_transform command - formats output data.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🔄 Data transform after hook: {context}")
    
    if context.result and hasattr(context.result, 'transformed_data'):
        # Get the transformed data from command result
        transformed_data = context.result.transformed_data
        
        # Apply additional formatting
        formatted_data = {}
        for key, value in transformed_data.items():
            if isinstance(value, str):
                # Add formatting to string values
                formatted_data[f"formatted_{key}"] = f"✨ {value} ✨"
            else:
                formatted_data[key] = value
        
        # Add formatting metadata
        formatted_data["_formatted_by_hook"] = True
        formatted_data["_formatting_time"] = datetime.now().isoformat()
        
        # Update the result with formatted data
        context.result.transformed_data = formatted_data
        
        logger.info(f"✨ Formatted data: {formatted_data}")
    

def intercept_before_hook(context: HookContext) -> None:
    """
    Before hook for intercept command - can completely bypass execution.
    
    Args:
        context: Hook context with command information
    """
    logger.info(f"🚫 Intercept before hook: {context}")
    
    # Check bypass flag
    bypass_flag = context.params.get("bypass_flag", 1)
    
    if bypass_flag == 0:
        # Completely bypass command execution
        logger.info(f"🚫 Intercepting command execution - bypass_flag = 0")
        
        # Create a mock result without calling the actual command
        from .intercept_command import InterceptResult
        
        mock_result = InterceptResult(
            message="Command intercepted by hook - not executed",
            executed=False,
            intercept_reason="bypass_flag = 0",
            hook_data={
                "intercepted_by": "intercept_before_hook",
                "interception_time": datetime.now().isoformat(),
                "bypass_flag": bypass_flag
            }
        )
        
        # Set the result and disable standard processing
        context.result = mock_result
        context.standard_processing = False
        
        logger.info(f"🚫 Command execution bypassed, result: {mock_result}")
    else:
        logger.info(f"✅ Command execution allowed - bypass_flag = {bypass_flag}")
        context.params["hook_processed"] = True
    

def intercept_after_hook(context: HookContext) -> None:
    """
    After hook for intercept command.
    
    Args:
        context: Hook context with command information
    """
    if context.standard_processing:
        logger.info(f"✅ Intercept command executed normally")
    else:
        logger.info(f"🚫 Intercept command was intercepted by hook")
    
    # Add execution metadata
    if context.result and hasattr(context.result, 'hook_data'):
        context.result.hook_data["after_hook_processed"] = True
        context.result.hook_data["after_hook_time"] = datetime.now().isoformat()


def conditional_transform_hook(context: HookContext) -> None:
    """
    Conditional transformation hook - applies different transformations based on data.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        logger.info(f"🎯 Conditional transform before hook: {context.command_name}")
        
        # Check if this is a data_transform command
        if context.command_name == "data_transform":
            data = context.params.get("data", {})
            transform_type = context.params.get("transform_type", "default")
            
            # Apply conditional transformation based on data content
            if "special" in str(data).lower():
                logger.info(f"🎯 Special data detected - applying enhanced transformation")
                context.params["transform_type"] = "uppercase"
                context.params["_special_enhancement"] = True
            elif "test" in str(data).lower():
                logger.info(f"🎯 Test data detected - applying test transformation")
                context.params["transform_type"] = "reverse"
                context.params["_test_mode"] = True
    
    elif context.hook_type == HookType.AFTER_EXECUTION:
        logger.info(f"🎯 Conditional transform after hook: {context.command_name}")
        
        # Add conditional metadata to result
        if context.result and hasattr(context.result, 'processing_info'):
            context.result.processing_info["conditional_processed"] = True
            context.result.processing_info["conditional_time"] = datetime.now().isoformat()


def smart_intercept_hook(context: HookContext) -> None:
    """
    Smart interception hook - intercepts based on multiple conditions.
    
    Args:
        context: Hook context with command information
    """
    if context.hook_type == HookType.BEFORE_EXECUTION:
        logger.info(f"🧠 Smart intercept before hook: {context.command_name}")
        
        # Check multiple conditions for interception
        action = context.params.get("action", "")
        bypass_flag = context.params.get("bypass_flag", 1)
        
        # Intercept if action is "blocked" or bypass_flag is 0
        if action == "blocked" or bypass_flag == 0:
            logger.info(f"🧠 Smart intercept: action='{action}', bypass_flag={bypass_flag}")
            
            # Create intercepted result
            from .intercept_command import InterceptResult
            
            intercept_reason = "blocked_action" if action == "blocked" else "bypass_flag_zero"
            
            mock_result = InterceptResult(
                message=f"Command intercepted by smart hook - reason: {intercept_reason}",
                executed=False,
                intercept_reason=intercept_reason,
                hook_data={
                    "intercepted_by": "smart_intercept_hook",
                    "interception_time": datetime.now().isoformat(),
                    "smart_analysis": True
                }
            )
            
            # Set the result and disable standard processing
            context.result = mock_result
            context.standard_processing = False
            
            logger.info(f"✅ Smart interception completed")
    

def register_advanced_hooks(hooks_manager) -> None:
    """
    Register advanced hooks with the hooks system.
    
    Args:
        hooks_manager: Hooks manager instance to register hooks with
    """
    logger.info("🔧 Registering advanced hooks...")
    
    # Register data transform hooks
    hooks_manager.register_before_hook("data_transform", data_transform_before_hook)
    hooks_manager.register_after_hook("data_transform", data_transform_after_hook)
    
    # Register intercept hooks
    hooks_manager.register_before_hook("intercept", intercept_before_hook)
    hooks_manager.register_after_hook("intercept", intercept_after_hook)
    
    # Register global hooks
    hooks_manager.register_global_before_hook(conditional_transform_hook)
    hooks_manager.register_global_before_hook(smart_intercept_hook)
    hooks_manager.register_global_after_hook(conditional_transform_hook)
    
    # Register system lifecycle hooks
    hooks_manager.register_before_init_hook(system_before_init_hook)
    hooks_manager.register_after_init_hook(system_after_init_hook)
    
    # Register command-specific hooks for all commands
    hooks_manager.register_before_hook("echo", echo_before_hook)
    hooks_manager.register_after_hook("echo", echo_after_hook)
    
    hooks_manager.register_before_hook("help", help_before_hook)
    hooks_manager.register_after_hook("help", help_after_hook)
    
    hooks_manager.register_before_hook("health", health_before_hook)
    hooks_manager.register_after_hook("health", health_after_hook)
    
    hooks_manager.register_before_hook("config", config_before_hook)
    hooks_manager.register_after_hook("config", config_after_hook)
    
    hooks_manager.register_before_hook("load", load_before_hook)
    hooks_manager.register_after_hook("load", load_after_hook)
    
    hooks_manager.register_before_hook("unload", unload_before_hook)
    hooks_manager.register_after_hook("unload", unload_after_hook)
    
    hooks_manager.register_before_hook("reload", reload_before_hook)
    hooks_manager.register_after_hook("reload", reload_after_hook)
    
    hooks_manager.register_before_hook("plugins", plugins_before_hook)
    hooks_manager.register_after_hook("plugins", plugins_after_hook)
    
    hooks_manager.register_before_hook("settings", settings_before_hook)
    hooks_manager.register_after_hook("settings", settings_after_hook)
    
    # Register custom commands hooks
    hooks_manager.register_before_hook("manual_echo", manual_echo_before_hook)
    hooks_manager.register_after_hook("manual_echo", manual_echo_after_hook)
    
    hooks_manager.register_before_hook("auto_echo", auto_echo_before_hook)
    hooks_manager.register_after_hook("auto_echo", auto_echo_after_hook)
    
    hooks_manager.register_before_hook("auto_info", auto_info_before_hook)
    hooks_manager.register_after_hook("auto_info", auto_info_after_hook)
    
    logger.info("✅ Advanced hooks registered successfully")


# ============================================================================
# SYSTEM LIFECYCLE HOOKS
# ============================================================================

def system_before_init_hook(registry) -> None:
    """
    Before system initialization hook.
    
    Args:
        registry: Command registry instance
    """
    logger.info("🚀 System before init hook: Preparing system initialization")
    
    # Add initialization metadata
    registry.metadata["init_start_time"] = datetime.now().isoformat()
    registry.metadata["init_hooks_processed"] = True
    
    logger.info("✅ System initialization preparation completed")


def system_after_init_hook(registry) -> None:
    """
    After system initialization hook.
    
    Args:
        registry: Command registry instance
    """
    logger.info("🎉 System after init hook: System initialization completed")
    
    # Add completion metadata
    registry.metadata["init_end_time"] = datetime.now().isoformat()
    registry.metadata["total_commands"] = len(registry.get_all_commands())
    
    logger.info(f"✅ System initialization completed with {registry.metadata['total_commands']} commands")


# ============================================================================
# BUILT-IN COMMAND HOOKS
# ============================================================================

def echo_before_hook(context: HookContext) -> None:
    """Before hook for echo command."""
    logger.info(f"📢 Echo before hook: {context.command_name}")
    
    # Add timestamp to message
    if context.params and "message" in context.params:
        original_message = context.params["message"]
        context.params["message"] = f"[{datetime.now().strftime('%H:%M:%S')}] {original_message}"
        context.params["_timestamp_added"] = True
    
    context.metadata["echo_processed"] = True


def echo_after_hook(context: HookContext) -> None:
    """After hook for echo command."""
    logger.info(f"📢 Echo after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'message'):
        context.result.message = f"ECHO: {context.result.message}"
        context.metadata["echo_formatted"] = True


def help_before_hook(context: HookContext) -> None:
    """Before hook for help command."""
    logger.info(f"❓ Help before hook: {context.command_name}")
    
    # Add help metadata
    context.metadata["help_requested"] = True
    context.metadata["help_time"] = datetime.now().isoformat()


def help_after_hook(context: HookContext) -> None:
    """After hook for help command."""
    logger.info(f"❓ Help after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'commands_info'):
        # Add hook information to help
        context.result.commands_info["hooks_available"] = True
        context.result.commands_info["hook_count"] = 15  # Total number of hooks


def health_before_hook(context: HookContext) -> None:
    """Before hook for health command."""
    logger.info(f"🏥 Health before hook: {context.command_name}")
    
    # Add health check metadata
    context.metadata["health_check_start"] = datetime.now().isoformat()


def health_after_hook(context: HookContext) -> None:
    """After hook for health command."""
    logger.info(f"🏥 Health after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'status'):
        # Add hook health status
        context.result.status["hooks_healthy"] = True
        context.result.status["hook_count"] = 15


def config_before_hook(context: HookContext) -> None:
    """Before hook for config command."""
    logger.info(f"⚙️ Config before hook: {context.command_name}")
    
    # Add config operation metadata
    context.metadata["config_operation"] = context.params.get("operation", "unknown")
    context.metadata["config_time"] = datetime.now().isoformat()


def config_after_hook(context: HookContext) -> None:
    """After hook for config command."""
    logger.info(f"⚙️ Config after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'config'):
        # Add hook configuration
        context.result.config["hooks_enabled"] = True
        context.result.config["hook_system_version"] = "1.0.0"


def load_before_hook(context: HookContext) -> None:
    """Before hook for load command."""
    logger.info(f"📦 Load before hook: {context.command_name}")
    
    # Add load metadata
    context.metadata["load_source"] = context.params.get("source", "unknown")
    context.metadata["load_time"] = datetime.now().isoformat()


def load_after_hook(context: HookContext) -> None:
    """After hook for load command."""
    logger.info(f"📦 Load after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'loaded_commands'):
        # Add hook information to loaded commands
        context.result.loaded_commands["_hooks_loaded"] = True


def unload_before_hook(context: HookContext) -> None:
    """Before hook for unload command."""
    logger.info(f"🗑️ Unload before hook: {context.command_name}")
    
    # Add unload metadata
    context.metadata["unload_command"] = context.params.get("command_name", "unknown")
    context.metadata["unload_time"] = datetime.now().isoformat()


def unload_after_hook(context: HookContext) -> None:
    """After hook for unload command."""
    logger.info(f"🗑️ Unload after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'unloaded_commands'):
        # Add hook information to unloaded commands
        context.result.unloaded_commands["_hooks_cleaned"] = True


def reload_before_hook(context: HookContext) -> None:
    """Before hook for reload command."""
    logger.info(f"🔄 Reload before hook: {context.command_name}")
    
    # Add reload metadata
    context.metadata["reload_components"] = context.params.get("components", [])
    context.metadata["reload_time"] = datetime.now().isoformat()


def reload_after_hook(context: HookContext) -> None:
    """After hook for reload command."""
    logger.info(f"🔄 Reload after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'reloaded_components'):
        # Add hook information to reloaded components
        context.result.reloaded_components["_hooks_reloaded"] = True


def plugins_before_hook(context: HookContext) -> None:
    """Before hook for plugins command."""
    logger.info(f"🔌 Plugins before hook: {context.command_name}")
    
    # Add plugins metadata
    context.metadata["plugins_check_time"] = datetime.now().isoformat()


def plugins_after_hook(context: HookContext) -> None:
    """After hook for plugins command."""
    logger.info(f"🔌 Plugins after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'plugins'):
        # Add hook information to plugins
        context.result.plugins["_hooks_plugin"] = {
            "name": "Advanced Hooks System",
            "version": "1.0.0",
            "enabled": True
        }


def settings_before_hook(context: HookContext) -> None:
    """Before hook for settings command."""
    logger.info(f"🔧 Settings before hook: {context.command_name}")
    
    # Add settings metadata
    context.metadata["settings_operation"] = context.params.get("operation", "unknown")
    context.metadata["settings_time"] = datetime.now().isoformat()


def settings_after_hook(context: HookContext) -> None:
    """After hook for settings command."""
    logger.info(f"🔧 Settings after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'settings'):
        # Add hook settings
        context.result.settings["hooks"] = {
            "enabled": True,
            "before_hooks": 15,
            "after_hooks": 15,
            "global_hooks": 3
        }


# ============================================================================
# CUSTOM COMMAND HOOKS
# ============================================================================

def manual_echo_before_hook(context: HookContext) -> None:
    """Before hook for manual echo command."""
    logger.info(f"📝 Manual echo before hook: {context.command_name}")
    
    # Add manual registration flag
    if context.params and "message" in context.params:
        context.params["_manually_registered"] = True
        context.params["_hook_processed"] = True


def manual_echo_after_hook(context: HookContext) -> None:
    """After hook for manual echo command."""
    logger.info(f"📝 Manual echo after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'message'):
        context.result.message = f"[MANUAL] {context.result.message}"


def auto_echo_before_hook(context: HookContext) -> None:
    """Before hook for auto echo command."""
    logger.info(f"🤖 Auto echo before hook: {context.command_name}")
    
    # Add auto registration flag
    if context.params and "message" in context.params:
        context.params["_auto_registered"] = True
        context.params["_hook_processed"] = True


def auto_echo_after_hook(context: HookContext) -> None:
    """After hook for auto echo command."""
    logger.info(f"🤖 Auto echo after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'message'):
        context.result.message = f"[AUTO] {context.result.message}"


def auto_info_before_hook(context: HookContext) -> None:
    """Before hook for auto info command."""
    logger.info(f"🤖 Auto info before hook: {context.command_name}")
    
    # Add auto registration flag
    if context.params and "topic" in context.params:
        context.params["_auto_registered"] = True
        context.params["_hook_processed"] = True


def auto_info_after_hook(context: HookContext) -> None:
    """After hook for auto info command."""
    logger.info(f"🤖 Auto info after hook: {context.command_name}")
    
    if context.result and hasattr(context.result, 'info'):
        context.result.info["_auto_generated"] = True
        context.result.info["_hook_enhanced"] = True 