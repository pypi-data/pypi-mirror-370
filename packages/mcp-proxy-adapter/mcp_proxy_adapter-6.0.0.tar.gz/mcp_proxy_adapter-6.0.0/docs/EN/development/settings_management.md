# Settings Management

This document describes the settings management system in the MCP Proxy Adapter framework.

## Overview

The framework provides a comprehensive settings management system that allows you to:
- Load configuration from JSON files
- Read settings programmatically
- Set custom settings dynamically
- Reload configuration at runtime

## Core Components

### Settings Module

The main settings management is provided by the `mcp_proxy_adapter.core.settings` module:

```python
from mcp_proxy_adapter.core.settings import (
    Settings,
    ServerSettings,
    LoggingSettings,
    CommandsSettings,
    get_setting,
    set_setting,
    reload_settings
)
```

### Configuration Classes

#### Settings Class

Main settings management class with static methods:

```python
# Get all server settings
server_settings = Settings.get_server_settings()

# Get all logging settings
logging_settings = Settings.get_logging_settings()

# Get all commands settings
commands_settings = Settings.get_commands_settings()

# Get custom setting
custom_value = Settings.get_custom_setting("custom.feature_enabled", False)

# Set custom setting
Settings.set_custom_setting("custom.new_feature", True)

# Get all settings
all_settings = Settings.get_all_settings()

# Reload configuration
Settings.reload_config()
```

#### ServerSettings Class

Helper class for server-specific settings:

```python
host = ServerSettings.get_host()        # "127.0.0.1"
port = ServerSettings.get_port()        # 8000
debug = ServerSettings.get_debug()      # True
log_level = ServerSettings.get_log_level()  # "DEBUG"
```

#### LoggingSettings Class

Helper class for logging-specific settings:

```python
level = LoggingSettings.get_level()           # "DEBUG"
log_dir = LoggingSettings.get_log_dir()       # "./logs"
log_file = LoggingSettings.get_log_file()     # "app.log"
max_file_size = LoggingSettings.get_max_file_size()  # "10MB"
backup_count = LoggingSettings.get_backup_count()    # 5
```

#### CommandsSettings Class

Helper class for commands-specific settings:

```python
auto_discovery = CommandsSettings.get_auto_discovery()  # True
discovery_path = CommandsSettings.get_discovery_path()  # "mcp_proxy_adapter.commands"
```

### Convenience Functions

For quick access to common settings:

```python
from mcp_proxy_adapter.core.settings import (
    get_server_host,
    get_server_port,
    get_server_debug,
    get_logging_level,
    get_logging_dir,
    get_auto_discovery,
    get_discovery_path,
    get_setting,
    set_setting,
    reload_settings
)

# Quick access functions
host = get_server_host()
port = get_server_port()
debug = get_server_debug()
log_level = get_logging_level()

# Generic setting access
value = get_setting("custom.feature", default_value)
set_setting("custom.feature", new_value)
reload_settings()
```

## Configuration File Format

The framework uses JSON configuration files with the following structure:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true,
    "log_level": "DEBUG"
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "./logs",
    "log_file": "app.log",
    "error_log_file": "error.log",
    "access_log_file": "access.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "console_output": true,
    "file_output": true
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands",
    "custom_commands_path": null
  },
  "custom": {
    "feature_enabled": true,
    "api_version": "1.0.0",
    "nested": {
      "setting": "value"
    }
  }
}
```

## Loading Configuration

### Automatic Loading

The framework automatically loads configuration from `./config.json` on startup.

### Manual Loading

You can load configuration from a specific file:

```python
from mcp_proxy_adapter.config import config

# Load from specific file
config.load_from_file("/path/to/config.json")

# Reload current configuration
config.load_config()
```

### Environment Variables

Configuration can also be set via environment variables with the `SERVICE_` prefix:

```bash
export SERVICE_SERVER_HOST="0.0.0.0"
export SERVICE_SERVER_PORT="8080"
export SERVICE_LOGGING_LEVEL="INFO"
export SERVICE_CUSTOM_FEATURE_ENABLED="true"
```

## Settings Command

The framework includes a built-in `settings` command for managing configuration:

### Get All Settings

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get_all"
    }
  }'
```

### Get Specific Setting

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get",
      "key": "server.host"
    }
  }'
```

### Set Setting

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "set",
      "key": "custom.feature_enabled",
      "value": true
    }
  }'
```

### Reload Configuration

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "reload"
    }
  }'
```

## Usage Examples

### Basic Server with Configuration

```python
import os
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.core.settings import Settings, setup_logging

# Load configuration from file
config_path = os.path.join(os.path.dirname(__file__), "config.json")
if os.path.exists(config_path):
    from mcp_proxy_adapter.config import config
    config.load_from_file(config_path)

# Setup logging with configuration
setup_logging()

# Get settings
server_settings = Settings.get_server_settings()
custom_settings = Settings.get_custom_setting("custom", {})

# Create application with settings
app = create_app(
    title=custom_settings.get("server_name", "Default Server"),
    description=custom_settings.get("description", "Default description")
)

# Run server with settings
import uvicorn
uvicorn.run(
    app,
    host=server_settings["host"],
    port=server_settings["port"],
    log_level=server_settings["log_level"].lower()
)
```

### Conditional Feature Loading

```python
from mcp_proxy_adapter.core.settings import get_setting

# Check if feature is enabled
if get_setting("custom.features.hooks_enabled", False):
    register_hooks()

if get_setting("custom.features.custom_commands_enabled", False):
    register_custom_commands()
```

### Dynamic Configuration Updates

```python
from mcp_proxy_adapter.core.settings import set_setting, reload_settings

# Update configuration dynamically
set_setting("custom.feature_enabled", True)
set_setting("server.debug", False)

# Reload from file (overwrites dynamic changes)
reload_settings()
```

## Best Practices

1. **Use Configuration Files**: Store configuration in JSON files rather than hardcoding values
2. **Environment Variables**: Use environment variables for sensitive or environment-specific settings
3. **Default Values**: Always provide default values when reading settings
4. **Validation**: Validate configuration values before using them
5. **Reloading**: Use the reload functionality carefully as it overwrites dynamic changes
6. **Nested Settings**: Use dot notation for accessing nested configuration values

## Error Handling

The settings system provides graceful error handling:

```python
try:
    value = get_setting("custom.feature", default_value)
except Exception as e:
    logger.error(f"Failed to get setting: {e}")
    value = default_value
```

## Integration with Framework

The settings system is integrated throughout the framework:

- **Logging**: Automatically uses logging settings from configuration
- **Server**: Uses server settings for host, port, and debug mode
- **Commands**: Uses command discovery settings
- **Middleware**: Can be configured via settings
- **API**: Settings are accessible via the settings command 