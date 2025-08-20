# API Requests

## Request Format

All requests to the API must follow the JSON-RPC 2.0 specification. A typical request has the following structure:

```json
{
  "jsonrpc": "2.0",
  "method": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": 1
}
```

### Required Fields

- `jsonrpc`: Must be exactly "2.0"
- `method`: The name of the command to execute
- `id`: A unique identifier for the request (can be a string or number)

### Optional Fields

- `params`: An object containing the parameters for the command

## Example Requests

### Simple Request

```json
{
  "jsonrpc": "2.0",
  "method": "hello_world",
  "params": {
    "name": "User"
  },
  "id": 1
}
```

### Request Without Parameters

```json
{
  "jsonrpc": "2.0",
  "method": "get_status",
  "id": 2
}
```

## Batch Requests

The API supports batch requests. A batch request is an array of individual requests:

```json
[
  {
    "jsonrpc": "2.0",
    "method": "hello_world",
    "params": {
      "name": "User 1"
    },
    "id": 1
  },
  {
    "jsonrpc": "2.0",
    "method": "hello_world",
    "params": {
      "name": "User 2"
    },
    "id": 2
  }
]
```

Batch requests are processed in the order they are received, and responses are returned in the same order. 