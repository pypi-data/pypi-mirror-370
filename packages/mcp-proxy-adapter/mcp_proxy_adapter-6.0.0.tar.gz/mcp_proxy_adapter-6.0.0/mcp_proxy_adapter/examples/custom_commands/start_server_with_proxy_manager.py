#!/usr/bin/env python3
"""
Server startup script with Proxy Connection Manager.

This script starts the server and manages proxy connection with regular
health checks and automatic re-registration.
"""

import asyncio
import time
import sys
import os
import uvicorn
import threading
import signal
from pathlib import Path

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.core.logging import get_logger, setup_logging
from mcp_proxy_adapter.core.settings import (
    Settings,
    get_server_host,
    get_server_port,
    get_server_debug,
    get_setting,
    get_custom_setting_value
)
from mcp_proxy_adapter.core.ssl_utils import SSLUtils
from mcp_proxy_adapter.core.transport_manager import transport_manager
from custom_settings_manager import CustomSettingsManager, get_app_name, is_feature_enabled

# Import custom commands and hooks
from custom_help_command import CustomHelpCommand
from custom_health_command import CustomHealthCommand
from data_transform_command import DataTransformCommand
from intercept_command import InterceptCommand
from advanced_hooks import register_advanced_hooks

# Import auto-registered commands
from auto_commands.auto_echo_command import AutoEchoCommand
from auto_commands.auto_info_command import AutoInfoCommand

# Import manual registration example
from manual_echo_command import ManualEchoCommand

# Import echo command
from echo_command import EchoCommand

# Import custom OpenAPI generator
from custom_openapi_generator import custom_openapi_generator

# Import command registry for manual registration
from mcp_proxy_adapter.commands.command_registry import registry
from mcp_proxy_adapter.config import config
from mcp_proxy_adapter.commands.hooks import register_custom_commands_hook

# Import proxy connection manager
from proxy_connection_manager import start_proxy_manager, stop_proxy_manager, get_proxy_manager_status


def custom_commands_hook(registry):
    """Hook function for registering custom commands."""
    logger = get_logger("custom_commands")
    logger.info("Registering custom commands via hook...")
    
    # Get custom commands configuration from custom settings
    custom_commands_config = get_custom_setting_value("custom_commands", {})
    
    # Register echo command (only if not already registered)
    if not registry.command_exists("echo"):
        registry.register_custom(EchoCommand)
        logger.info("Registered: echo command")
    else:
        logger.debug("Command 'echo' is already registered, skipping")
    
    # Register custom help command (will override built-in)
    if custom_commands_config.get("help", {}).get("enabled", True):
        registry.register_custom(CustomHelpCommand)
        logger.info("Registered: custom help command")
    
    # Register custom health command (will override built-in)
    if custom_commands_config.get("health", {}).get("enabled", True):
        registry.register_custom(CustomHealthCommand)
        logger.info("Registered: custom health command")
    
    # Register advanced demonstration commands
    if custom_commands_config.get("data_transform", {}).get("enabled", True):
        registry.register_custom(DataTransformCommand)
        logger.info("Registered: data_transform command")
    
    if custom_commands_config.get("intercept", {}).get("enabled", True):
        registry.register_custom(InterceptCommand)
        logger.info("Registered: intercept command")


def setup_hooks():
    """Setup hooks for command processing."""
    logger = get_logger("custom_commands")
    logger.info("Setting up hooks...")
    
    # Register custom commands hook
    register_custom_commands_hook(custom_commands_hook)
    
    # Note: Advanced hooks are not compatible with current API
    # They will be registered automatically by the command registry
    logger.info("Basic hooks setup completed")


async def initialize_commands():
    """
    Initialize commands using the unified system initialization logic.
    This function is used both at startup and during reload.
    
    Returns:
        Number of commands discovered.
    """
    # Use the unified reload method from registry
    result = await registry.reload_system()
    return result["total_commands"]


def start_server():
    """Start the server in a separate thread."""
    # Initialize settings
    settings = Settings()
    server_settings = settings.get_server_settings()
    logging_settings = settings.get_logging_settings()
    commands_settings = settings.get_commands_settings()
    
    # Setup logging - pass only the level, not the entire dict
    setup_logging(logging_settings.get('level', 'INFO'))
    logger = get_logger("server_startup")
    
    # Load transport configuration
    if not transport_manager.load_config(config.config_data):
        logger.error("Failed to load transport configuration")
        return
    
    # Validate transport configuration
    if not transport_manager.validate_config():
        logger.error("Transport configuration validation failed")
        return
    
    # Print server header and description
    print("=" * 80)
    print("🔧 ADVANCED MCP PROXY ADAPTER SERVER WITH PROXY MANAGER")
    print("=" * 80)
    print("📋 Description:")
    print(f"   {get_app_name()} - Advanced server with proxy connection management")
    print()
    
    # Get transport info
    transport_info = transport_manager.get_transport_info()
    
    print("⚙️  Configuration:")
    print(f"   • Server: {server_settings['host']}:{transport_manager.get_port()}")
    print(f"   • Transport: {transport_info['type']}")
    print(f"   • Debug: {server_settings['debug']}")
    print(f"   • Log Level: {logging_settings.get('level', 'INFO')}")
    print(f"   • Log Directory: {logging_settings.get('log_dir', './logs')}")
    print(f"   • Auto Discovery: {commands_settings['auto_discovery']}")
    print(f"   • SSL Enabled: {transport_info['ssl_enabled']}")
    if transport_info['ssl_enabled']:
        ssl_config = transport_info['ssl_config']
        print(f"   • SSL Cert: {ssl_config.get('cert_file', 'Not specified')}")
        print(f"   • Client Verification: {ssl_config.get('verify_client', False)}")
    print()
    print("🔧 Available Commands:")
    print("   • help - Custom help command (overrides built-in)")
    print("   • health - Custom health command (overrides built-in)")
    print("   • config - Built-in config command")
    print("   • reload - Built-in reload command")
    print("   • settings - Built-in settings command")
    print("   • load - Built-in load command")
    print("   • unload - Built-in unload command")
    print("   • plugins - Built-in plugins command")
    print("   • echo - Custom echo command")
    print("   • data_transform - Data transformation command")
    print("   • intercept - Command interception example")
    print("   • manual_echo - Manually registered echo command")
    print("   • test - Remote command (loaded from plugin server)")
    print()
    print("🎯 Features:")
    print("   • Advanced JSON-RPC API")
    print("   • Custom commands with hooks")
    print("   • Data transformation hooks")
    print("   • Command interception hooks")
    print("   • Auto-registration and manual registration")
    print("   • Custom OpenAPI schema generation")
    print("   • Configuration-driven settings")
    print("   • Custom settings management")
    print("   • 🔄 Proxy Connection Manager with health monitoring")
    print("   • 🔄 Automatic re-registration on proxy failure")
    print("=" * 80)
    print()
    
    logger.info("Starting Advanced Custom Commands MCP Proxy Adapter Server with Proxy Manager...")
    logger.info(f"Server configuration: {server_settings}")
    logger.info(f"Logging configuration: {logging_settings}")
    logger.info(f"Commands configuration: {commands_settings}")
    logger.info(f"Transport configuration: {transport_info}")
    
    # Setup hooks for command processing
    setup_hooks()
    
    # Initialize commands
    asyncio.run(initialize_commands())
    
    # Create application with settings from configuration
    app = create_app(
        title=get_app_name(),
        description="Advanced MCP Proxy Adapter server with proxy connection management, demonstrating hook capabilities including data transformation, command interception, conditional processing, and smart interception hooks. Features custom commands with enhanced functionality, comprehensive settings management, and robust proxy connection handling.",
        version="2.2.0"
    )
    
    # Get uvicorn configuration from transport manager
    uvicorn_config = transport_manager.get_uvicorn_config()
    uvicorn_config["host"] = server_settings['host']
    uvicorn_config["log_level"] = server_settings['log_level'].lower()
    
    logger.info(f"Starting server with uvicorn config: {uvicorn_config}")
    
    # Run the server with configuration settings
    uvicorn.run(
        app,
        **uvicorn_config
    )


async def start_proxy_manager_after_server():
    """
    Start proxy manager after server is fully started and listening.
    """
    logger = get_logger("proxy_manager_startup")
    
    # Wait a bit for server to fully start
    await asyncio.sleep(5)
    
    logger.info("🚀 Starting Proxy Connection Manager after server startup")
    
    # Start proxy manager
    await start_proxy_manager()
    
    logger.info("✅ Proxy Connection Manager started successfully")


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    
    # Stop proxy manager
    asyncio.run(stop_proxy_manager())
    
    print("✅ Graceful shutdown completed")
    sys.exit(0)


def main():
    """Main function to start server and proxy manager."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(8)
    
    # Start proxy manager after server is ready
    asyncio.run(start_proxy_manager_after_server())
    
    # Keep main thread alive and monitor status
    try:
        while True:
            # Get proxy manager status
            status = get_proxy_manager_status()
            
            if status["is_running"]:
                time_since = status.get("time_since_registration", 0)
                if time_since is not None:
                    print(f"📊 Proxy Status: Registered {time_since:.0f}s ago, "
                          f"attempts: {status['registration_count']}, "
                          f"failed: {status['failed_attempts']}")
            
            time.sleep(30)  # Print status every 30 seconds
            
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
        asyncio.run(stop_proxy_manager())
        sys.exit(0)


if __name__ == "__main__":
    main()
