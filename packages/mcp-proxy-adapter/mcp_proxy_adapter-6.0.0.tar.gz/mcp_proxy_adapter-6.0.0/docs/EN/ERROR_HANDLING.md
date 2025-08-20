# Error Handling System

## Introduction

The error handling system in this microservice is designed to provide consistent, predictable error responses according to the JSON-RPC 2.0 specification. This document describes the error hierarchy, error codes, and best practices for error handling.

## Error Structure

According to JSON-RPC 2.0, error responses have the following structure:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error message",
    "data": {
      "detail1": "value1",
      "detail2": "value2"
    }
  },
  "id": "request-id"
}
```

Where:
- `code` - a numeric error code
- `message` - a human-readable error description
- `data` - (optional) additional error details

## Error Hierarchy

All errors in the system inherit from the base `MicroserviceError` class, which is implemented in `core/errors.py`. The hierarchy is as follows:

```
MicroserviceError
├── ParseError
├── InvalidRequestError
├── MethodNotFoundError
├── InvalidParamsError
├── InternalError
├── CommandError
│   ├── ValidationError
│   ├── AuthenticationError
│   ├── AuthorizationError
│   ├── ResourceNotFoundError
│   ├── ResourceExistsError
│   ├── TimeoutError
│   └── ConnectionError
└── ConfigurationError
```

## Standard Error Codes

Our microservice follows the JSON-RPC 2.0 specification for error codes:

| Code Range | Description |
|------------|-------------|
| -32700 | Parse error (invalid JSON) |
| -32600 | Invalid Request (not conforming to JSON-RPC spec) |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32000 to -32099 | Server error (implementation-defined) |

Specific error codes in our system:

| Code | Error Class | Description |
|------|-------------|-------------|
| -32700 | ParseError | Error while parsing JSON request |
| -32600 | InvalidRequestError | Invalid JSON-RPC request format |
| -32601 | MethodNotFoundError | Method not found |
| -32602 | InvalidParamsError, ValidationError | Invalid parameters or validation error |
| -32603 | InternalError, ConfigurationError | Internal server error |
| -32000 | CommandError | General command execution error |
| -32001 | AuthenticationError | Authentication error |
| -32002 | AuthorizationError | Authorization error |
| -32003 | TimeoutError | Timeout error |
| -32004 | ResourceNotFoundError | Resource not found |
| -32005 | ResourceExistsError | Resource already exists |
| -32007 | ConnectionError | Connection error |

## Using Errors in Commands

When implementing commands, you should use the appropriate error class to signal errors. The error will be converted to the correct JSON-RPC format in the API layer.

Example of raising an error in a command:

```python
from mcp_proxy_adapter.core.errors import ValidationError, ResourceNotFoundError

# Validation error
raise ValidationError("Invalid parameter value", data={"param": "value", "reason": "Must be positive"})

# Resource not found
raise ResourceNotFoundError("User not found", data={"user_id": 123})
```

## Error Handling in Command Base Class

The `Command` base class in `commands/base.py` handles errors thrown during command execution and converts them to `ErrorResult` instances:

```python
try:
    # Execute command
    result = await command.execute(**validated_params)
    return result
except ValidationError as e:
    return ErrorResult(message=str(e), code=e.code, details=e.data)
except CommandError as e:
    return ErrorResult(message=str(e), code=e.code, details=e.data)
except Exception as e:
    return ErrorResult(
        message=f"Command execution error: {str(e)}", 
        code=-32603, 
        details={"original_error": str(e)}
    )
```

## Error Handling in API Layer

The API layer (`api/handlers.py`) transforms command errors into JSON-RPC error responses:

```python
try:
    # Execute command
    result = await execute_command(method, params, request_id)
    return {
        "jsonrpc": "2.0",
        "result": result,
        "id": request_id
    }
except MicroserviceError as e:
    return {
        "jsonrpc": "2.0",
        "error": e.to_dict(),
        "id": request_id
    }
```

## Middleware Error Handling

The `ErrorHandlingMiddleware` in `api/middleware/error_handling.py` catches unhandled exceptions in the API layer and converts them to appropriate HTTP responses:

- `ValidationError` → HTTP 400 Bad Request
- `AuthenticationError` → HTTP 401 Unauthorized
- `AuthorizationError` → HTTP 403 Forbidden
- `ResourceNotFoundError` → HTTP 404 Not Found
- `CommandError` → HTTP 400 Bad Request
- Other errors → HTTP 500 Internal Server Error

## Best Practices

1. **Use Specific Error Types**: Always use the most specific error class that applies to your situation.

2. **Include Helpful Data**: Add relevant data to the error to help troubleshoot the issue.

3. **Follow Error Code Conventions**: Use the standard error codes defined in the JSON-RPC specification.

4. **Log Errors**: All errors should be properly logged for debugging.

5. **Consistent Error Responses**: Ensure error responses are consistent across all endpoints and formats.

6. **Validation**: Use validation to catch errors early, before command execution.

7. **Secure Error Messages**: Do not expose sensitive information in error messages or details.

## Example Error Responses

### Invalid Request
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32600,
    "message": "Invalid Request. Method is required"
  },
  "id": null
}
```

### Method Not Found
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found: unknown_method"
  },
  "id": "123"
}
```

### Validation Error
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid parameters",
    "data": {
      "errors": {
        "name": "Field required",
        "age": "Must be positive integer"
      }
    }
  },
  "id": "123"
}
```

### Internal Error
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "original_error": "Database connection timeout"
    }
  },
  "id": "123"
}
``` 