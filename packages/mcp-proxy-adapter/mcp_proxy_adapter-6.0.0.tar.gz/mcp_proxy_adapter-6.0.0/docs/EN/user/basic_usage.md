# Basic Usage

This guide explains the basic usage of the MCP Proxy service.

## Starting the Service

To start the MCP Proxy service, run:

```bash
mcp-proxy
```

By default, the service will listen on `0.0.0.0:8000`.

You can specify a custom configuration file using the `--config` option:

```bash
mcp-proxy --config /path/to/config.json
```

## Available Command-Line Options

The MCP Proxy service supports the following command-line options:

| Option | Description |
|--------|-------------|
| `--config PATH` | Path to the configuration file |
| `--host HOST` | Host to bind to (overrides config file) |
| `--port PORT` | Port to listen on (overrides config file) |
| `--log-level LEVEL` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--validate-config` | Validate configuration and exit |
| `--version` | Show version and exit |
| `--help` | Show help message and exit |

## Making API Requests

To make a request to the MCP Proxy API, send a JSON-RPC 2.0 request to the `/api/v1/execute` endpoint:

### Example Request using curl

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "hello_world",
    "params": {
      "name": "User"
    },
    "id": 1
  }'
```

### Example Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "message": "Hello, User!",
    "timestamp": 1620000000.0
  },
  "id": 1
}
```

## Checking Service Health

To check the health of the service, send a GET request to the `/api/health` endpoint:

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": 1620000000.0
}
```

## Getting Available Commands

To get a list of available commands, send a GET request to the `/api/commands` endpoint:

```bash
curl http://localhost:8000/api/commands
```

Response:

```json
{
  "commands": [
    {
      "name": "hello_world",
      "description": "A basic example command that returns a greeting message with a timestamp",
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "The name to greet"
          }
        }
      }
    },
    {
      "name": "get_date",
      "description": "Returns the current date and time in ISO 8601 format",
      "schema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
``` 