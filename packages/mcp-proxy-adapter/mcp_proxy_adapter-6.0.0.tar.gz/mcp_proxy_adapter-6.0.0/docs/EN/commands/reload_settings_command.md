# Reload Settings Command

The `reload_settings` command allows you to reload configuration settings from files and environment variables at runtime.

## Description

The reload settings command provides the ability to:
- Reload configuration from JSON files
- Reload environment variables
- Update custom settings
- Get current custom settings after reload

## Command Information

- **Name**: `reload_settings`
- **Description**: Reload configuration settings from files and environment variables
- **Category**: Configuration Management

## Parameters

This command does not accept any parameters.

## Response Format

### Success Response

```json
{
  "result": {
    "success": true,
    "message": "Settings reloaded successfully from configuration files and environment variables",
    "custom_settings": {
      "application": {
        "name": "Extended MCP Proxy Server with Custom Settings",
        "version": "2.1.0",
        "environment": "development"
      },
      "features": {
        "advanced_hooks": true,
        "custom_commands": true,
        "data_transformation": true
      },
      "security": {
        "enable_authentication": false,
        "max_request_size": "15MB"
      }
    }
  }
}
```

### Error Response

```json
{
  "result": {
    "success": false,
    "message": "Failed to reload settings",
    "custom_settings": {},
    "error_message": "Failed to reload settings: Configuration file not found"
  }
}
```

## Usage Examples

### Basic Usage

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "reload_settings",
    "params": {}
  }'
```

### Python Example

```python
import requests

response = requests.post(
    "http://localhost:8000/cmd",
    json={
        "command": "reload_settings",
        "params": {}
    }
)

result = response.json()
if result["result"]["success"]:
    print("✅ Settings reloaded successfully")
    print(f"📋 Custom settings: {result['result']['custom_settings']}")
else:
    print(f"❌ Failed to reload settings: {result['result']['error_message']}")
```

## What Gets Reloaded

When you execute the `reload_settings` command, the following happens:

1. **Configuration Files**: Reloads settings from `config.json` and other configuration files
2. **Environment Variables**: Reloads settings from environment variables with `SERVICE_` prefix
3. **Custom Settings**: Updates custom settings that were added via `add_custom_settings()`
4. **Framework Settings**: Updates server, logging, and commands settings

## Integration with Custom Settings

The command works seamlessly with the custom settings system:

```python
from mcp_proxy_adapter.core.settings import add_custom_settings, reload_settings

# Add custom settings
add_custom_settings({
    "application": {
        "name": "My Custom App",
        "version": "1.0.0"
    }
})

# Reload all settings (including custom ones)
reload_settings()
```

## Error Handling

The command provides comprehensive error handling:

- **File Not Found**: Gracefully handles missing configuration files
- **Invalid JSON**: Reports JSON parsing errors
- **Permission Errors**: Handles file access permission issues
- **Environment Variables**: Safely handles missing or invalid environment variables

## Best Practices

1. **Use After Configuration Changes**: Call this command after modifying configuration files
2. **Monitor Response**: Always check the `success` field in the response
3. **Handle Errors**: Implement proper error handling for failed reloads
4. **Validate Settings**: Use the returned custom settings to verify the reload was successful
5. **Log Operations**: Log reload operations for debugging and monitoring

## Related Commands

- **`settings`**: Get, set, and manage individual settings
- **`config`**: Access framework configuration
- **`reload`**: Reload commands and configuration (more comprehensive)

## Use Cases

### Development Environment

```bash
# After modifying config.json
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
```

### Production Environment

```bash
# After updating environment variables
export SERVICE_SERVER_PORT=8080
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
```

### Custom Settings Management

```python
# After adding custom settings programmatically
from mcp_proxy_adapter.core.settings import add_custom_settings

add_custom_settings({"feature_enabled": True})

# Reload to ensure all settings are up to date
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
``` 