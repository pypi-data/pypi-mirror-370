# API Responses

## Response Format

All responses from the API follow the JSON-RPC 2.0 specification. A typical response has the following structure:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "field1": "value1",
    "field2": "value2"
  },
  "id": 1
}
```

### Fields

- `jsonrpc`: Always "2.0"
- `result`: The result of the command execution (structure depends on the command)
- `id`: The same identifier as in the request

## Error Responses

If an error occurs during command execution, an error response is returned:

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

### Error Fields

- `code`: A numeric error code
- `message`: A brief description of the error
- `data`: (Optional) Additional information about the error

## Example Responses

### Successful Response

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

### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "details": "Required parameter 'name' is missing"
    }
  },
  "id": 1
}
```

## Batch Responses

For batch requests, the API returns an array of responses:

```json
[
  {
    "jsonrpc": "2.0",
    "result": {
      "message": "Hello, User 1!",
      "timestamp": 1620000000.0
    },
    "id": 1
  },
  {
    "jsonrpc": "2.0",
    "result": {
      "message": "Hello, User 2!",
      "timestamp": 1620000001.0
    },
    "id": 2
  }
]
```

The order of responses matches the order of requests in the batch. 