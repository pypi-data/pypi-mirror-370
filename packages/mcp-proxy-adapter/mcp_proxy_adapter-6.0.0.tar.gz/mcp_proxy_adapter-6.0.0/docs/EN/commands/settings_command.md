# Settings Command

The `settings` command provides comprehensive configuration management capabilities for the MCP Proxy Adapter framework.

## Description

The settings command allows you to:
- View all configuration settings
- Get specific configuration values
- Set configuration values dynamically
- Reload configuration from files

## Command Information

- **Name**: `settings`
- **Description**: Manage framework settings and configuration
- **Category**: Configuration Management

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `operation` | string | Yes | `"get_all"` | Operation to perform: `get`, `set`, `get_all`, `reload` |
| `key` | string | No | - | Configuration key in dot notation (e.g., `server.host`, `custom.feature_enabled`) |
| `value` | any | No | - | Configuration value to set (for `set` operation) |

### Operations

#### `get_all`
Retrieves all configuration settings.

**Parameters**: None required

**Example**:
```json
{
  "command": "settings",
  "params": {
    "operation": "get_all"
  }
}
```

#### `get`
Retrieves a specific configuration value.

**Parameters**:
- `key` (required): Configuration key in dot notation

**Example**:
```json
{
  "command": "settings",
  "params": {
    "operation": "get",
    "key": "server.host"
  }
}
```

#### `set`
Sets a configuration value dynamically.

**Parameters**:
- `key` (required): Configuration key in dot notation
- `value` (required): Value to set

**Example**:
```json
{
  "command": "settings",
  "params": {
    "operation": "set",
    "key": "custom.feature_enabled",
    "value": true
  }
}
```

#### `reload`
Reloads configuration from files and environment variables.

**Parameters**: None required

**Example**:
```json
{
  "command": "settings",
  "params": {
    "operation": "reload"
  }
}
```

## Response Format

### Success Response

```json
{
  "result": {
    "success": true,
    "operation": "get_all",
    "all_settings": {
      "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": true,
        "log_level": "DEBUG"
      },
      "logging": {
        "level": "DEBUG",
        "log_dir": "./logs",
        "log_file": "app.log"
      },
      "commands": {
        "auto_discovery": true,
        "discovery_path": "mcp_proxy_adapter.commands"
      },
      "custom": {
        "feature_enabled": true
      }
    }
  }
}
```

### Get Operation Response

```json
{
  "result": {
    "success": true,
    "operation": "get",
    "key": "server.host",
    "value": "127.0.0.1"
  }
}
```

### Set Operation Response

```json
{
  "result": {
    "success": true,
    "operation": "set",
    "key": "custom.feature_enabled",
    "value": true
  }
}
```

### Error Response

```json
{
  "result": {
    "success": false,
    "operation": "get",
    "error_message": "Key is required for 'get' operation"
  }
}
```

## Usage Examples

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

### Get Server Host

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

### Get Custom Setting

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get",
      "key": "custom.features.hooks_enabled"
    }
  }'
```

### Set Custom Setting

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "set",
      "key": "custom.debug_mode",
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

## Configuration Keys

### Server Settings

- `server.host` - Server host address
- `server.port` - Server port number
- `server.debug` - Debug mode flag
- `server.log_level` - Server log level

### Logging Settings

- `logging.level` - Logging level
- `logging.log_dir` - Log directory path
- `logging.log_file` - Main log file name
- `logging.error_log_file` - Error log file name
- `logging.access_log_file` - Access log file name
- `logging.max_file_size` - Maximum log file size
- `logging.backup_count` - Number of backup files
- `logging.format` - Log message format
- `logging.date_format` - Date format
- `logging.console_output` - Console output flag
- `logging.file_output` - File output flag

### Commands Settings

- `commands.auto_discovery` - Auto discovery flag
- `commands.discovery_path` - Command discovery path
- `commands.custom_commands_path` - Custom commands path

### Custom Settings

Any settings under the `custom` section can be accessed using dot notation:

- `custom.feature_enabled`
- `custom.api_version`
- `custom.features.hooks_enabled`
- `custom.nested.setting`

## Error Handling

The command provides comprehensive error handling:

- **Missing Key**: Returns error when key is required but not provided
- **Invalid Operation**: Returns error for unsupported operations
- **Configuration Errors**: Handles configuration loading errors gracefully

## Integration

The settings command integrates with:

- **Configuration System**: Uses the framework's configuration management
- **Logging System**: Respects logging configuration
- **Command Registry**: Available through the command registry
- **API Endpoints**: Accessible via `/cmd` and `/api/commands` endpoints

## Best Practices

1. **Use Dot Notation**: Access nested settings using dot notation (e.g., `custom.features.enabled`)
2. **Provide Defaults**: Always handle cases where settings might not exist
3. **Validate Values**: Validate configuration values before using them
4. **Reload Carefully**: Use reload operation carefully as it overwrites dynamic changes
5. **Error Handling**: Always check the `success` field in responses 