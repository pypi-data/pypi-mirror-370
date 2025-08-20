"""
Custom Settings Manager Example

This module demonstrates how to create a custom settings manager
that extends the framework's settings system with application-specific settings.
"""

import json
import os
from typing import Dict, Any, Optional
from mcp_proxy_adapter.core.settings import (
    add_custom_settings,
    get_custom_settings,
    get_custom_setting_value,
    set_custom_setting_value
)
from mcp_proxy_adapter.core.logging import get_logger


class CustomSettingsManager:
    """
    Custom settings manager for the extended server example.
    
    This class demonstrates how to:
    1. Load custom settings from JSON files
    2. Add them to the framework's settings system
    3. Provide convenient access methods
    4. Handle settings validation and defaults
    """
    
    def __init__(self, config_file: str = "custom_settings.json"):
        """
        Initialize the custom settings manager.
        
        Args:
            config_file: Path to custom settings JSON file
        """
        self.config_file = config_file
        self.logger = get_logger("custom_settings_manager")
        self._load_custom_settings()
    
    def _load_custom_settings(self) -> None:
        """Load custom settings from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    custom_settings = json.load(f)
                
                self.logger.info(f"📁 Loaded custom settings from: {self.config_file}")
                self.logger.debug(f"📋 Custom settings: {custom_settings}")
                
                # Add to framework's settings system
                add_custom_settings(custom_settings)
                
            else:
                self.logger.warning(f"⚠️  Custom settings file not found: {self.config_file}")
                self.logger.info("📝 Using default custom settings")
                
                # Use default settings
                default_settings = self._get_default_settings()
                add_custom_settings(default_settings)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load custom settings: {e}")
            self.logger.info("📝 Using default custom settings")
            
            # Use default settings on error
            default_settings = self._get_default_settings()
            add_custom_settings(default_settings)
    
    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default custom settings."""
        return {
            "application": {
                "name": "Extended MCP Proxy Server",
                "version": "2.0.0",
                "environment": "development"
            },
            "features": {
                "advanced_hooks": True,
                "custom_commands": True,
                "data_transformation": True,
                "command_interception": True,
                "performance_monitoring": False
            },
            "security": {
                "enable_authentication": False,
                "max_request_size": "10MB",
                "rate_limiting": {
                    "enabled": False,
                    "requests_per_minute": 100
                }
            },
            "monitoring": {
                "enable_metrics": True,
                "metrics_interval": 60,
                "health_check_interval": 30
            },
            "custom_commands": {
                "auto_echo": {
                    "enabled": True,
                    "max_length": 1000
                },
                "data_transform": {
                    "enabled": True,
                    "transform_types": ["uppercase", "lowercase", "reverse"]
                },
                "intercept": {
                    "enabled": True,
                    "bypass_conditions": ["input_value == 0"]
                }
            }
        }
    
    def get_application_name(self) -> str:
        """Get application name."""
        return get_custom_setting_value("application.name", "Extended MCP Proxy Server")
    
    def get_application_version(self) -> str:
        """Get application version."""
        return get_custom_setting_value("application.version", "2.0.0")
    
    def get_environment(self) -> str:
        """Get application environment."""
        return get_custom_setting_value("application.environment", "development")
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return get_custom_setting_value(f"features.{feature_name}", False)
    
    def get_security_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get security setting."""
        return get_custom_setting_value(f"security.{setting_name}", default)
    
    def get_monitoring_setting(self, setting_name: str, default: Any = None) -> Any:
        """Get monitoring setting."""
        return get_custom_setting_value(f"monitoring.{setting_name}", default)
    
    def get_custom_command_setting(self, command_name: str, setting_name: str, default: Any = None) -> Any:
        """Get custom command setting."""
        return get_custom_setting_value(f"custom_commands.{command_name}.{setting_name}", default)
    
    def set_custom_setting(self, key: str, value: Any) -> None:
        """Set a custom setting."""
        set_custom_setting_value(key, value)
        self.logger.info(f"🔧 Set custom setting: {key} = {value}")
    
    def get_all_custom_settings(self) -> Dict[str, Any]:
        """Get all custom settings."""
        return get_custom_settings()
    
    def reload_settings(self) -> None:
        """Reload custom settings from file."""
        self.logger.info("🔄 Reloading custom settings...")
        self._load_custom_settings()
        self.logger.info("✅ Custom settings reloaded")
    
    def validate_settings(self) -> Dict[str, Any]:
        """
        Validate current settings and return validation results.
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate required settings
        required_settings = [
            "application.name",
            "application.version",
            "features.advanced_hooks"
        ]
        
        for setting in required_settings:
            if get_custom_setting_value(setting) is None:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Missing required setting: {setting}")
        
        # Validate feature dependencies
        if self.is_feature_enabled("data_transformation"):
            if not self.is_feature_enabled("custom_commands"):
                validation_results["warnings"].append(
                    "data_transformation requires custom_commands to be enabled"
                )
        
        # Validate security settings
        if self.get_security_setting("enable_authentication"):
            if not self.get_security_setting("rate_limiting.enabled"):
                validation_results["warnings"].append(
                    "Authentication enabled but rate limiting is disabled"
                )
        
        return validation_results
    
    def print_settings_summary(self) -> None:
        """Print a summary of current settings."""
        self.logger.info("📊 Custom Settings Summary:")
        self.logger.info(f"   Application: {self.get_application_name()} v{self.get_application_version()}")
        self.logger.info(f"   Environment: {self.get_environment()}")
        
        # Features
        features = []
        for feature in ["advanced_hooks", "custom_commands", "data_transformation", "command_interception"]:
            if self.is_feature_enabled(feature):
                features.append(feature)
        
        self.logger.info(f"   Enabled Features: {', '.join(features) if features else 'None'}")
        
        # Security
        auth_enabled = self.get_security_setting("enable_authentication", False)
        rate_limiting = self.get_security_setting("rate_limiting.enabled", False)
        self.logger.info(f"   Security: Auth={auth_enabled}, Rate Limiting={rate_limiting}")
        
        # Monitoring
        metrics_enabled = self.get_monitoring_setting("enable_metrics", False)
        self.logger.info(f"   Monitoring: Metrics={metrics_enabled}")


# Convenience functions for easy access
def get_app_name() -> str:
    """Get application name."""
    return get_custom_setting_value("application.name", "Extended MCP Proxy Server")


def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled."""
    return get_custom_setting_value(f"features.{feature_name}", False)


def get_security_setting(setting_name: str, default: Any = None) -> Any:
    """Get security setting."""
    return get_custom_setting_value(f"security.{setting_name}", default)


def get_monitoring_setting(setting_name: str, default: Any = None) -> Any:
    """Get monitoring setting."""
    return get_custom_setting_value(f"monitoring.{setting_name}", default) 