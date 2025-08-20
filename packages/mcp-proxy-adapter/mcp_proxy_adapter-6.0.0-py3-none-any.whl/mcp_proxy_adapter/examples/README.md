# MCP Proxy Adapter Examples

This directory contains examples demonstrating different usage patterns of the MCP Proxy Adapter framework.

## Examples Overview

### 1. Basic Server (`basic_server/`)
Minimal server example with only built-in commands. Demonstrates:
- Basic framework setup
- Built-in command discovery
- Standard JSON-RPC API
- Backward compatibility with property setting

### 2. Custom Commands Server (`custom_commands/`)
Advanced server example with custom commands and hooks. Demonstrates:
- Custom command registration
- Basic hooks (before/after execution)
- Global hooks
- Performance and security monitoring
- Advanced hooks with data transformation and command interception

## Setting Application Title and Description

The framework supports two ways to set application properties:

### Method 1: During Creation (Recommended)
```python
from mcp_proxy_adapter import create_app

app = create_app(
    title="My Custom Server",
    description="My custom server description",
    version="2.0.0"
)
```

### Method 2: After Creation (Backward Compatible)
```python
from mcp_proxy_adapter import create_app

app = create_app()

# Set properties after creation
app.set_properties(
    new_title="My Custom Server",
    new_description="My custom server description",
    new_version="2.0.0"
)
```

## Running Examples

### Basic Server
```bash
cd mcp_proxy_adapter/examples/basic_server
python server.py
```

### Custom Commands Server
```bash
cd mcp_proxy_adapter/examples/custom_commands
python server.py
```

## Testing Examples

### Basic Server Commands
```bash
# Get help
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "help", "id": 1}'

# Get health
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "health", "id": 2}'
```

### Custom Commands Server Commands
```bash
# Test echo command
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello!"}, "id": 1}'

# Test data transformation
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "data_transform", "params": {"data": {"name": "test", "value": 123}}, "id": 2}'

# Test command interception (bypass_flag=0)
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "intercept", "params": {"bypass_flag": 0}, "id": 3}'

# Test command execution (bypass_flag=1)
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "intercept", "params": {"bypass_flag": 1}, "id": 4}'
```

## Features Demonstrated

### Basic Server
- ✅ Standard JSON-RPC API
- ✅ Built-in command discovery
- ✅ Basic logging
- ✅ OpenAPI schema generation
- ✅ Backward compatibility

### Custom Commands Server
- ✅ Custom command registration
- ✅ Command override with priority
- ✅ Basic hooks (before/after)
- ✅ Global hooks
- ✅ Performance monitoring
- ✅ Security monitoring
- ✅ Data transformation hooks
- ✅ Command interception hooks
- ✅ Conditional processing
- ✅ Smart interception
- ✅ Centralized logging
- ✅ Advanced error handling 