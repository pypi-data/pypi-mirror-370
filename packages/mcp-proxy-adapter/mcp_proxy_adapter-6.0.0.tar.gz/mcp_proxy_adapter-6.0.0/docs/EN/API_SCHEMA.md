# API and Interaction Schema

## Basic Principles

1. **Single Entry Point for Commands**
   - All commands are executed through a unified mechanism, regardless of the calling method (REST or JSON-RPC)
   - The intermediate layer (adapter) transforms incoming requests into a unified format

2. **Supported Protocols**
   - JSON-RPC 2.0 (`/cmd`)
   - REST API (standard endpoints + `/cmd`)

3. **Response Format**
   - Always returns HTTP code 200
   - Response body is always in JSON-RPC 2.0 format
   - Errors are transmitted in the error field of the JSON-RPC response
   - HTTP codes 4xx and 5xx are not used

## Request and Response Structure

### JSON-RPC Format

```json
// Request
{
    "jsonrpc": "2.0",
    "method": "command_name",
    "params": {
        "param1": "value1",
        "param2": "value2"
    },
    "id": 1
}

// Successful response
{
    "jsonrpc": "2.0",
    "result": {
        "data": "command result"
    },
    "id": 1
}

// Error response
{
    "jsonrpc": "2.0",
    "error": {
        "code": -32000,
        "message": "Error description",
        "data": {
            "details": "Additional error info"
        }
    },
    "id": 1
}
```

### REST Format

```
GET /api/v1/commands           # List of available commands
GET /api/v1/commands/{name}    # Command information
POST /cmd                      # Command execution (similar to JSON-RPC)
```

The response is always wrapped in JSON-RPC format:

```json
// GET /api/v1/commands
{
    "jsonrpc": "2.0",
    "result": {
        "commands": [
            {
                "name": "command1",
                "description": "Command description",
                "params": {...}
            }
        ]
    },
    "id": null
}
```

## Intermediate Layer (Adapter)

```python
class CommandAdapter:
    """
    Intermediate layer for transforming REST/RPC requests
    into a unified command format
    """
    
    async def execute_command(self, command: str, params: dict) -> CommandResult:
        """Single point of command execution"""
        pass

    def to_jsonrpc_response(self, result: CommandResult) -> dict:
        """Converting the result to JSON-RPC format"""
        pass
```

## OpenAPI Schema

The schema must correspond to the MCP Proxy format (port 8001):

```yaml
openapi: 3.0.0
paths:
  /cmd:
    post:
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CommandRequest'
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/JsonRpcResponse'
components:
  schemas:
    CommandRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          enum: ['2.0']
        method:
          type: string
        params:
          type: object
        id:
          type: [integer, string, null]
    JsonRpcResponse:
      type: object
      properties:
        jsonrpc:
          type: string
          enum: ['2.0']
        result:
          type: object
        error:
          type: object
        id:
          type: [integer, string, null]
```

## Error Handling

All errors are returned in JSON-RPC format with HTTP code 200:

| Error Type | code | message |
|------------|------|---------|
| Parse error | -32700 | "Parse error" |
| Invalid Request | -32600 | "Invalid Request" |
| Method not found | -32601 | "Method not found" |
| Invalid params | -32602 | "Invalid params" |
| Internal error | -32603 | "Internal error" |
| Server error | -32000 to -32099 | "Server error" |

## Usage Examples

### REST Request
```bash
curl -X GET http://localhost:8000/api/v1/commands
```

### JSON-RPC Request
```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_status",
    "params": {},
    "id": 1
  }'
```

Both requests will be processed through a unified mechanism and return a response in JSON-RPC format. 