# Proxy Registration

## Overview

The MCP Proxy Adapter includes automatic proxy registration functionality that allows the server to register itself with an MCP proxy server during startup and unregister during shutdown.

## Configuration

### Proxy Registration Settings

Add the following section to your configuration file:

```json
{
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "mcp_proxy_adapter",
    "server_name": "MCP Proxy Adapter",
    "description": "JSON-RPC API for interacting with MCP Proxy",
    "registration_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5,
    "auto_register_on_startup": true,
    "auto_unregister_on_shutdown": true
  }
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | boolean | false | Enable/disable proxy registration |
| `proxy_url` | string | "http://localhost:3004" | URL of the MCP proxy server |
| `server_id` | string | "mcp_proxy_adapter" | Unique identifier for this server |
| `server_name` | string | "MCP Proxy Adapter" | Human-readable server name |
| `description` | string | "JSON-RPC API for interacting with MCP Proxy" | Server description |
| `registration_timeout` | integer | 30 | Timeout for registration requests (seconds) |
| `retry_attempts` | integer | 3 | Number of retry attempts on failure |
| `retry_delay` | integer | 5 | Delay between retry attempts (seconds) |
| `auto_register_on_startup` | boolean | true | Automatically register on server startup |
| `auto_unregister_on_shutdown` | boolean | true | Automatically unregister on server shutdown |

## Automatic Registration

### Startup Registration

When the server starts, it automatically:

1. Loads the proxy registration configuration
2. Determines the server URL based on SSL configuration
3. Attempts to register with the proxy server
4. Logs the registration result

### Shutdown Unregistration

When the server shuts down, it automatically:

1. Attempts to unregister from the proxy server
2. Logs the unregistration result

## Manual Registration

### Using the proxy_registration Command

You can manually manage proxy registration using the built-in `proxy_registration` command:

#### Check Registration Status

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "status"
    },
    "id": 1
  }'
```

#### Register with Proxy

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "register",
      "server_url": "http://localhost:8000"
    },
    "id": 1
  }'
```

#### Unregister from Proxy

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "unregister"
    },
    "id": 1
  }'
```

## Health Check Integration

The proxy registration status is included in the health check response:

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "health",
    "params": {},
    "id": 1
  }'
```

Response includes proxy registration status:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "data": {
      "status": "ok",
      "version": "1.0.0",
      "uptime": 123.45,
      "components": {
        "system": { ... },
        "process": { ... },
        "commands": { ... },
        "proxy_registration": {
          "enabled": true,
          "registered": true,
          "server_key": "mcp_proxy_adapter_1",
          "proxy_url": "http://localhost:3004"
        }
      }
    }
  },
  "id": 1
}
```

## API Integration

### Programmatic Usage

```python
from mcp_proxy_adapter.core.proxy_registration import (
    register_with_proxy,
    unregister_from_proxy,
    get_proxy_registration_status
)

# Register with proxy
success = await register_with_proxy("http://localhost:8000")

# Get registration status
status = get_proxy_registration_status()

# Unregister from proxy
success = await unregister_from_proxy()
```

### Manager Class

```python
from mcp_proxy_adapter.core.proxy_registration import ProxyRegistrationManager

manager = ProxyRegistrationManager()

# Set server URL
manager.set_server_url("http://localhost:8000")

# Register
success = await manager.register_server()

# Get status
status = manager.get_registration_status()

# Unregister
success = await manager.unregister_server()
```

## Error Handling

### Registration Failures

The system handles various failure scenarios:

1. **Proxy server unavailable**: Retries with exponential backoff
2. **Network errors**: Logs error and continues
3. **Invalid configuration**: Logs warning and skips registration
4. **Registration rejected**: Logs error with details

### Logging

All registration events are logged with appropriate levels:

- **INFO**: Successful registration/unregistration
- **WARNING**: Registration disabled or failed
- **ERROR**: Critical registration errors

## Examples

### Basic Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_service",
    "server_name": "My Service",
    "description": "My custom service"
  }
}
```

### SSL Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8443
  },
  "ssl": {
    "enabled": true,
    "cert_file": "server.crt",
    "key_file": "server.key"
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_ssl_service",
    "server_name": "My SSL Service"
  }
}
```

### MTLS Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 9443
  },
  "ssl": {
    "enabled": true,
    "mode": "mtls_only",
    "cert_file": "server.crt",
    "key_file": "server.key",
    "ca_cert": "ca.crt"
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_mtls_service",
    "server_name": "My MTLS Service"
  }
}
```

## Testing

### Unit Tests

Run the proxy registration tests:

```bash
pytest tests/core/test_proxy_registration.py -v
```

### Integration Tests

Test with a real proxy server:

```bash
# Start proxy server
python proxy_server.py

# Start MCP Proxy Adapter with registration enabled
python -m mcp_proxy_adapter.examples.basic_server.server --config config_with_proxy_registration.json

# Check registration status
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "proxy_registration", "params": {"action": "status"}, "id": 1}'
```

## Troubleshooting

### Common Issues

1. **Registration fails**: Check proxy server availability and configuration
2. **SSL errors**: Verify certificate paths and SSL configuration
3. **Network timeouts**: Increase `registration_timeout` value
4. **Retry failures**: Check `retry_attempts` and `retry_delay` settings

### Debug Mode

Enable debug logging to see detailed registration information:

```json
{
  "logging": {
    "level": "DEBUG"
  },
  "proxy_registration": {
    "enabled": true
  }
}
```

### Manual Verification

Check proxy server logs to verify registration requests:

```bash
# Check proxy server logs
tail -f proxy_server.log

# Test proxy registration endpoint directly
curl -X POST http://localhost:3004/register \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "test",
    "server_url": "http://localhost:8000",
    "server_name": "Test Server"
  }'
``` 