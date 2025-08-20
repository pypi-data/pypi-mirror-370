# /cmd Endpoint

## Description

The `/cmd` endpoint is a universal interface for executing microservice commands. It provides a simplified way to interact with commands compared to the full JSON-RPC protocol.

Endpoint features:
- Single URL for all commands
- Simplified request and response format
- Standardized error handling
- Compatibility with MCP Proxy format

## Request Format

The request to the `/cmd` endpoint has the following format:

```json
{
    "command": "command_name",
    "params": {
        "param1": "value1",
        "param2": "value2"
    }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Command name to execute |
| `params` | object | No | Command parameters (depend on command type) |

## Response Format

A successful response from the `/cmd` endpoint has the following format:

```json
{
    "result": {
        // Command execution result
    }
}
```

In case of an error, the response has the following format:

```json
{
    "error": {
        "code": -32601,
        "message": "Command not found",
        "data": {
            // Additional error information (optional)
        }
    }
}
```

### Standard Error Codes

| Code | Description |
|------|-------------|
| -32700 | Parse error - JSON parsing error |
| -32600 | Invalid Request - invalid request format |
| -32601 | Method not found - command not found |
| -32602 | Invalid params - invalid parameters |
| -32603 | Internal error - internal server error |
| -32000 to -32099 | Custom errors |

## Implementation

The `/cmd` endpoint is implemented using FastAPI. The main request processing includes:

1. Extracting the command name and parameters from the request body
2. Checking if the command exists in the registry
3. Executing the command with the provided parameters
4. Forming a response based on the result or error

An important feature of the implementation is that all responses, including errors, are returned with HTTP code 200. Error information is contained in the response body.

## Examples

### Request with help command

```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "help"
}
```

### Response

```json
{
    "result": {
        "commands": {
            "help": {
                "description": "Get help information about available commands"
            },
            "health": {
                "description": "Check server health"
            }
        }
    }
}
```

### Request with health command

```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "health",
    "params": {
        "check_type": "detailed"
    }
}
```

### Response

```json
{
    "result": {
        "status": "ok",
        "uptime": 3600,
        "memory_usage": {
            "total": 1024,
            "used": 512
        },
        "services": {
            "database": "connected",
            "cache": "connected"
        }
    }
}
```

### Request with non-existent command

```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "non_existent_command"
}
```

### Response

```json
{
    "error": {
        "code": -32601,
        "message": "Command 'non_existent_command' not found"
    }
}
```

## Differences from JSON-RPC

The format of requests and responses of the `/cmd` endpoint has the following differences from the JSON-RPC 2.0 standard:

1. **Simplified request format**:
   - `command` field instead of `method`
   - No `jsonrpc` and `id` fields

2. **Simplified response format**:
   - No `jsonrpc` and `id` fields
   - Result or error returned at the top level 