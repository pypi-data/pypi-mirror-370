"""
Custom Settings Example for Basic Server

This example demonstrates how to use custom settings in a basic server.
"""

import json
import os
from mcp_proxy_adapter.core.settings import (
    add_custom_settings,
    get_custom_setting_value,
    set_custom_setting_value,
    get_custom_settings
)
from mcp_proxy_adapter.core.logging import get_logger


def setup_basic_custom_settings():
    """
    Setup basic custom settings for the basic server example.
    
    This demonstrates how to add custom settings to the framework
    and access them throughout the application.
    """
    logger = get_logger("basic_server_custom_settings")
    
    # Define basic custom settings
    basic_settings = {
        "application": {
            "name": "Basic MCP Proxy Server",
            "version": "1.0.0",
            "environment": "development"
        },
        "features": {
            "basic_logging": True,
            "simple_commands": True,
            "custom_settings_demo": True
        },
        "server_info": {
            "description": "Basic server with custom settings example",
            "author": "MCP Proxy Adapter Team",
            "contact": "support@example.com"
        },
        "demo_settings": {
            "welcome_message": "Welcome to Basic MCP Proxy Server!",
            "max_connections": 100,
            "timeout": 30,
            "debug_mode": True
        }
    }
    
    # Add settings to the framework
    add_custom_settings(basic_settings)
    
    logger.info("✅ Basic custom settings loaded")
    logger.info(f"📋 Application: {basic_settings['application']['name']} v{basic_settings['application']['version']}")
    logger.info(f"🔧 Features: {list(basic_settings['features'].keys())}")
    
    return basic_settings


def demonstrate_custom_settings_usage():
    """
    Demonstrate how to use custom settings in the application.
    """
    logger = get_logger("basic_server_custom_settings")
    
    # Get specific settings
    app_name = get_custom_setting_value("application.name", "Unknown")
    app_version = get_custom_setting_value("application.version", "0.0.0")
    welcome_msg = get_custom_setting_value("demo_settings.welcome_message", "Hello!")
    max_connections = get_custom_setting_value("demo_settings.max_connections", 50)
    
    logger.info(f"🏷️  Application: {app_name} v{app_version}")
    logger.info(f"💬 Welcome Message: {welcome_msg}")
    logger.info(f"🔗 Max Connections: {max_connections}")
    
    # Check if features are enabled
    features = get_custom_setting_value("features", {})
    enabled_features = [name for name, enabled in features.items() if enabled]
    
    logger.info(f"✅ Enabled Features: {', '.join(enabled_features)}")
    
    # Set a new custom setting
    set_custom_setting_value("demo_settings.last_updated", "2025-08-08")
    logger.info("🔧 Set new custom setting: demo_settings.last_updated")
    
    # Get all custom settings
    all_custom_settings = get_custom_settings()
    logger.info(f"📊 Total custom settings: {len(all_custom_settings)} sections")
    
    return {
        "app_name": app_name,
        "app_version": app_version,
        "welcome_message": welcome_msg,
        "max_connections": max_connections,
        "enabled_features": enabled_features,
        "total_settings_sections": len(all_custom_settings)
    }


def create_custom_settings_file():
    """
    Create a custom settings JSON file for the basic server.
    """
    custom_settings = {
        "application": {
            "name": "Basic MCP Proxy Server with Custom Settings",
            "version": "1.1.0",
            "environment": "development",
            "description": "Basic server demonstrating custom settings usage"
        },
        "features": {
            "basic_logging": True,
            "simple_commands": True,
            "custom_settings_demo": True,
            "file_based_config": True
        },
        "server_info": {
            "description": "Basic server with file-based custom settings",
            "author": "MCP Proxy Adapter Team",
            "contact": "support@example.com",
            "documentation": "https://example.com/docs"
        },
        "demo_settings": {
            "welcome_message": "Welcome to Basic MCP Proxy Server with Custom Settings!",
            "max_connections": 150,
            "timeout": 45,
            "debug_mode": True,
            "log_level": "INFO"
        },
        "performance": {
            "enable_caching": True,
            "cache_ttl": 300,
            "max_cache_size": 1000
        },
        "security": {
            "enable_rate_limiting": False,
            "max_request_size": "5MB",
            "allowed_origins": ["*"]
        }
    }
    
    # Write to file
    settings_file = "basic_custom_settings.json"
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(custom_settings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created custom settings file: {settings_file}")
    return settings_file


def load_custom_settings_from_file(file_path: str = "basic_custom_settings.json"):
    """
    Load custom settings from a JSON file.
    
    Args:
        file_path: Path to the custom settings JSON file
    """
    logger = get_logger("basic_server_custom_settings")
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                custom_settings = json.load(f)
            
            # Add to framework
            add_custom_settings(custom_settings)
            
            logger.info(f"📁 Loaded custom settings from: {file_path}")
            logger.info(f"📋 Application: {custom_settings.get('application', {}).get('name', 'Unknown')}")
            
            return custom_settings
        else:
            logger.warning(f"⚠️  Custom settings file not found: {file_path}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to load custom settings from {file_path}: {e}")
        return None


def print_custom_settings_summary():
    """
    Print a summary of current custom settings.
    """
    logger = get_logger("basic_server_custom_settings")
    
    all_settings = get_custom_settings()
    
    logger.info("📊 Custom Settings Summary:")
    
    # Application info
    app_name = get_custom_setting_value("application.name", "Unknown")
    app_version = get_custom_setting_value("application.version", "0.0.0")
    logger.info(f"   Application: {app_name} v{app_version}")
    
    # Features
    features = get_custom_setting_value("features", {})
    enabled_features = [name for name, enabled in features.items() if enabled]
    logger.info(f"   Enabled Features: {', '.join(enabled_features) if enabled_features else 'None'}")
    
    # Demo settings
    welcome_msg = get_custom_setting_value("demo_settings.welcome_message", "Hello!")
    max_connections = get_custom_setting_value("demo_settings.max_connections", 50)
    logger.info(f"   Welcome Message: {welcome_msg}")
    logger.info(f"   Max Connections: {max_connections}")
    
    # Performance
    caching_enabled = get_custom_setting_value("performance.enable_caching", False)
    logger.info(f"   Caching: {'Enabled' if caching_enabled else 'Disabled'}")
    
    # Security
    rate_limiting = get_custom_setting_value("security.enable_rate_limiting", False)
    logger.info(f"   Rate Limiting: {'Enabled' if rate_limiting else 'Disabled'}")
    
    logger.info(f"   Total Settings Sections: {len(all_settings)}")


if __name__ == "__main__":
    # Setup basic custom settings
    setup_basic_custom_settings()
    
    # Demonstrate usage
    demo_info = demonstrate_custom_settings_usage()
    
    # Create custom settings file
    settings_file = create_custom_settings_file()
    
    # Load from file
    load_custom_settings_from_file(settings_file)
    
    # Print summary
    print_custom_settings_summary()
    
    print("\n🎉 Custom settings demonstration completed!")
    print(f"📁 Custom settings file: {settings_file}")
    print("🔧 You can now use these settings in your basic server application.") 