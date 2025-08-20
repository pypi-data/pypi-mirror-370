# Configuration Principles

## Overview

The configuration system in MCP Proxy Adapter is designed to be reliable, consistent, and flexible. This document outlines the key principles and practices related to configuration management.

## Core Principles

### 1. Single Source of Truth

The configuration file is the single source of truth for all application settings. This ensures consistency and prevents conflicts between different parts of the system.

- All component settings must come from the configuration file
- Hard-coded values are prohibited in the codebase
- Default values may be defined but must be overridden by configuration

### 2. Completeness Validation

The application validates configuration completeness at startup. If required settings are missing:

- A detailed error message is logged
- The application terminates gracefully
- The error message includes information about missing settings

### 3. Unified Logging

The logging system is configured through the central configuration:

- Log levels are defined in the configuration
- All components use the unified logger instance
- Log format and destinations are centrally configured
- Standard format includes timestamp, log level, component, and message

### 4. Hot Reload Capability

The configuration can be reloaded without restarting the application:

- Changes are detected and applied at runtime
- Components are notified about configuration changes
- The reload process is atomic and consistent
- Failed reloads do not affect the running system

### 5. Configuration Sources

Configuration is loaded from multiple sources in the following priority order:

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

### 6. Error Logging

All errors related to stderr are redirected to a dedicated file:

- Critical errors are written to a separate log file
- This ensures no important error messages are lost
- The stderr log file has its own rotation policy

### 7. System Service Integration

The application provides a complete system service integration:

- SystemV-compatible init scripts
- Graceful startup and shutdown
- Service status monitoring
- Support for reload signals

## Configuration File Format

The configuration uses JSON format and has the following top-level structure:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8000
    },
    "logging": {
        "level": "DEBUG",
        "file": "adapter.log",
        "rotation": {
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "stderr_file": "error.log"
    },
    "commands": {
        // Command-specific configuration
    }
}
```

## Environment Variables

Environment variables can override configuration values using the following format:

```
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=9000
MCP_LOGGING_LEVEL=INFO
MCP_CONFIG_PATH=/path/to/config.json
```

## Command-line Arguments

Command-line arguments have the highest priority and can specify:

```
--config-path /path/to/config.json
--host 127.0.0.1
--port 9000
--log-level INFO
```

## Implementation Details

The configuration system is implemented in the `config.py` module with the following key components:

- `Settings` class for managing configuration
- `_merge_configs` method for combining multiple sources
- `_ensure_dirs_exist` method for creating required directories
- `get_auth_config` for authentication settings

## Extending Configuration

The configuration system is designed to be extended for future projects. The core implementation is based on a class-based approach that allows for easy customization.

### Overriding the Reading Method

To extend the configuration functionality in future projects, you can inherit from the base `Settings` class and override the reading methods:

```python
from mcp_proxy_adapter.config import Settings

class ExtendedSettings(Settings):
    def _read_config_file(self, config_path):
        """
        Override the config file reading method to support additional formats
        or sources.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            dict: Loaded configuration data
        """
        # Check file extension to determine format
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return self._read_yaml_config(config_path)
        elif config_path.endswith('.toml'):
            return self._read_toml_config(config_path)
        else:
            # Fall back to the default JSON reader
            return super()._read_config_file(config_path)
    
    def _read_yaml_config(self, config_path):
        """Read configuration from YAML file"""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _read_toml_config(self, config_path):
        """Read configuration from TOML file"""
        import toml
        with open(config_path, 'r') as f:
            return toml.load(f)
```

### Extending Environment Variables Support

You can also override the environment variable processing to support more complex patterns:

```python
class EnhancedSettings(Settings):
    def _process_env_vars(self):
        """
        Override to support additional environment variable formats
        or nested structures.
        
        Returns:
            dict: Configuration extracted from environment variables
        """
        # Get the base implementation first
        config = super()._process_env_vars()
        
        # Add support for JSON values in environment variables
        import os
        import json
        
        for key, value in os.environ.items():
            if key.startswith('MCP_JSON_'):
                try:
                    # Parse JSON values from environment variables
                    section_name = key[9:].lower()  # Remove 'MCP_JSON_' prefix
                    json_value = json.loads(value)
                    config[section_name] = json_value
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse JSON from env var {key}")
        
        return config
```

### Adding Custom Validation Logic

Extend the validation process to add project-specific requirements:

```python
class ValidatedSettings(Settings):
    def validate_configuration(self):
        """
        Extend validation to check project-specific requirements.
        
        Raises:
            ConfigError: If validation fails
        """
        # Call the base validation first
        super().validate_configuration()
        
        # Add project-specific validation
        if 'database' in self.config:
            db_config = self.config['database']
            required_db_fields = ['host', 'port', 'username', 'password', 'database_name']
            
            missing_fields = [field for field in required_db_fields if field not in db_config]
            if missing_fields:
                raise ConfigError(f"Missing required database configuration fields: {', '.join(missing_fields)}")
            
            # Connection string validation
            if 'connection_string' in db_config and not db_config['connection_string'].startswith(('postgresql://', 'mysql://')):
                raise ConfigError("Invalid database connection string format")
```

### Integration in New Projects

To use the extended configuration in a new project:

```python
# In your project's initialization code
from myproject.config import ExtendedSettings

# Create an instance with all the extensions
settings = ExtendedSettings()

# Access configuration as usual
database_host = settings.database.host
```

This extension pattern allows for flexible configuration handling while maintaining the core principles of the configuration system.

## Usage Examples

```python
from mcp_proxy_adapter.config import Settings

# Load configuration
settings = Settings()

# Access configuration values
host = settings.server.host
port = settings.server.port

# Use the unified logger
logger = settings.get_logger("component_name")
logger.info("Component initialized")

# Register for configuration changes
settings.on_reload(handle_config_changed)
``` 

## Project Structure

This section provides an overview of the complete file structure of the project:

```
mcp_microservice/
├── __init__.py               # Package initialization
├── config.py                 # Configuration management class
├── api/                      # API implementation
│   ├── __init__.py
│   ├── app.py                # FastAPI application setup
│   ├── handlers.py           # Request handlers
│   ├── middleware.py         # API middleware components
│   └── schemas.py            # API schema definitions
├── commands/                 # Command implementations
│   ├── __init__.py
│   ├── base.py               # Base command class
│   ├── command_registry.py   # Command registration
│   └── result.py             # Command result classes
├── core/                     # Core functionality
│   ├── __init__.py
│   ├── errors.py             # Error definitions
│   ├── logging.py            # Logging setup
│   └── utils.py              # Utility functions
├── schemas/                  # JSON schemas
│   └── base_schema.json      # Base schema definition
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   ├── test_config.py        # Configuration tests
│   └── ...                   # Other test modules
└── main.py                   # Application entry point
```

This structure follows the design principles outlined in this document, with clear separation of concerns and a focus on maintainability and extensibility. 