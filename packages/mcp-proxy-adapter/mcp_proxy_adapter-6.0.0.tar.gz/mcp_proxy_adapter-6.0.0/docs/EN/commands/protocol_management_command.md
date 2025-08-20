# Protocol Management Command

## Description

The Protocol Management Command provides functionality for managing and querying protocol configurations, including HTTP, HTTPS, and MTLS protocols. This command allows you to:

- Get information about all configured protocols
- Check protocol validation status
- Get list of allowed protocols
- Validate protocol configurations
- Check specific protocol settings

## Result

The command returns a `SuccessResult` or `ErrorResult` with protocol information.

### Success Result Example

```json
{
  "success": true,
  "data": {
    "protocol_info": {
      "http": {
        "enabled": true,
        "allowed": true,
        "port": 8000,
        "requires_ssl": false,
        "ssl_context_available": null
      },
      "https": {
        "enabled": true,
        "allowed": true,
        "port": 8443,
        "requires_ssl": true,
        "ssl_context_available": true
      },
      "mtls": {
        "enabled": true,
        "allowed": true,
        "port": 9443,
        "requires_ssl": true,
        "ssl_context_available": true
      }
    },
    "allowed_protocols": ["http", "https", "mtls"],
    "validation_errors": [],
    "total_protocols": 3,
    "enabled_protocols": 3,
    "protocols_enabled": true
  },
  "message": "Protocol information retrieved successfully"
}
```

## Command

### Schema

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["get_info", "validate_config", "get_allowed", "check_protocol"],
      "description": "Action to perform"
    },
    "protocol": {
      "type": "string",
      "enum": ["http", "https", "mtls"],
      "description": "Protocol to check (for check_protocol action)"
    }
  },
  "required": ["action"]
}
```

### Actions

#### get_info

Retrieves comprehensive information about all protocols.

**Parameters:** None

**Example:**
```json
{
  "action": "get_info"
}
```

#### validate_config

Validates the current protocol configuration and returns any errors.

**Parameters:** None

**Example:**
```json
{
  "action": "validate_config"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "validation_errors": [],
    "error_count": 0
  },
  "message": "Configuration validation passed"
}
```

#### get_allowed

Returns the list of currently allowed protocols.

**Parameters:** None

**Example:**
```json
{
  "action": "get_allowed"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "allowed_protocols": ["http", "https", "mtls"],
    "count": 3
  },
  "message": "Allowed protocols retrieved successfully"
}
```

#### check_protocol

Checks the configuration and status of a specific protocol.

**Parameters:**
- `protocol` (required): Protocol name ("http", "https", or "mtls")

**Example:**
```json
{
  "action": "check_protocol",
  "protocol": "https"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "protocol": "https",
    "is_allowed": true,
    "port": 8443,
    "enabled": true,
    "requires_ssl": true,
    "ssl_context_available": true,
    "configuration": {
      "enabled": true,
      "port": 8443
    }
  },
  "message": "Protocol 'https' check completed"
}
```

## Implementation Details

The command integrates with the `ProtocolManager` class to provide protocol management functionality. It supports:

- **Protocol Validation**: Checks if protocols are properly configured
- **SSL Context Management**: Validates SSL contexts for HTTPS and MTLS protocols
- **Port Configuration**: Verifies port assignments for each protocol
- **Error Handling**: Provides detailed error messages for configuration issues

## Usage Examples

### Python

```python
from mcp_proxy_adapter.commands.protocol_management_command import ProtocolManagementCommand

# Create command instance
command = ProtocolManagementCommand()

# Get protocol information
result = await command.execute(action="get_info")
print(result.data["protocol_info"])

# Validate configuration
result = await command.execute(action="validate_config")
if result.data["is_valid"]:
    print("Configuration is valid")
else:
    print("Configuration errors:", result.data["validation_errors"])

# Check specific protocol
result = await command.execute(action="check_protocol", protocol="https")
if result.data["ssl_context_available"]:
    print("HTTPS is properly configured with SSL")
```

### HTTP REST

```bash
# Get protocol information
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "get_info"},
    "id": 1
  }'

# Validate configuration
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "validate_config"},
    "id": 1
  }'

# Check HTTPS protocol
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "check_protocol", "protocol": "https"},
    "id": 1
  }'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "protocol_management",
  "params": {
    "action": "get_info"
  },
  "id": 1
}
```

## Configuration

The command works with the `protocols` section in the configuration file:

```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "https", "mtls"],
    "http": {
      "enabled": true,
      "port": 8000
    },
    "https": {
      "enabled": true,
      "port": 8443
    },
    "mtls": {
      "enabled": true,
      "port": 9443
    }
  }
}
```

## Error Handling

The command provides detailed error messages for various scenarios:

- **Unknown Action**: When an invalid action is specified
- **Missing Protocol**: When `check_protocol` is called without a protocol parameter
- **Unknown Protocol**: When an unsupported protocol is specified
- **Configuration Errors**: When protocol configuration validation fails

## Related Components

- **ProtocolManager**: Core protocol management functionality
- **ProtocolMiddleware**: Middleware for protocol validation
- **SSL Configuration**: SSL/TLS settings for HTTPS and MTLS protocols 