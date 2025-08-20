# API Errors

## Error Format

All errors returned by the API follow the JSON-RPC 2.0 specification. An error response has the following structure:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "details": "Additional error information"
    }
  },
  "id": 1
}
```

## Standard Error Codes

The API uses the standard JSON-RPC 2.0 error codes:

| Code | Message | Description |
|------|---------|-------------|
| -32700 | Parse error | Invalid JSON was received by the server |
| -32600 | Invalid request | The JSON sent is not a valid Request object |
| -32601 | Method not found | The method does not exist or is not available |
| -32602 | Invalid params | Invalid method parameter(s) |
| -32603 | Internal error | Internal JSON-RPC error |
| -32000 to -32099 | Server error | Reserved for implementation-defined server errors |

## Custom Error Codes

In addition to the standard error codes, the API defines custom error codes for specific error conditions:

| Code | Message | Description |
|------|---------|-------------|
| -32001 | Validation error | The request parameters failed validation |
| -32002 | Authorization error | The request lacks valid authentication credentials |
| -32003 | Resource not found | The requested resource could not be found |
| -32004 | Resource conflict | The request conflicts with the current state of the resource |
| -32005 | Rate limit exceeded | The request rate limit has been exceeded |
| -32006 | Command execution error | An error occurred while executing the command |

## Error Data

The `data` field of the error object contains additional information about the error. The structure of the data field depends on the error code:

### Validation Error (-32001)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Validation error",
    "data": {
      "errors": [
        {
          "field": "name",
          "message": "This field is required"
        },
        {
          "field": "age",
          "message": "Must be a positive integer"
        }
      ]
    }
  },
  "id": 1
}
```

### Command Execution Error (-32006)

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32006,
    "message": "Command execution error",
    "data": {
      "command": "hello_world",
      "reason": "Invalid name parameter",
      "details": "Name must be a string"
    }
  },
  "id": 1
}
```

## Error Handling Best Practices

1. Always check for errors in the response
2. Handle specific error codes appropriately
3. Log error details for debugging
4. Retry requests with exponential backoff for transient errors (server errors)
5. Display user-friendly error messages to the end user 