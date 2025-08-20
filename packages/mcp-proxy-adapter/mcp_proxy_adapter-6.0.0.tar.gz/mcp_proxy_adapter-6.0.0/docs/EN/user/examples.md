# Usage Examples

This document provides practical examples of using the MCP Proxy service.

## Hello World Example

### Request

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

### Response

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

## Get Current Date Example

### Request

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_date",
    "id": 2
  }'
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "date": "2024-03-20T15:30:45+03:00"
  },
  "id": 2
}
```

## Generate UUID4 Example

### Request

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "new_uuid4",
    "id": 3
  }'
```

### Response

```json
{
  "jsonrpc": "2.0",
  "result": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000"
  },
  "id": 3
}
```

## Batch Request Example

### Request

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '[
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
      "method": "get_date",
      "id": 2
    }
  ]'
```

### Response

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
      "date": "2024-03-20T15:30:45+03:00"
    },
    "id": 2
  }
]
```

## Error Example

### Request with Invalid Parameters

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "hello_world",
    "params": {
      "name": 123  # Name should be a string
    },
    "id": 1
  }'
```

### Error Response

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "details": "Expected string for name parameter, received integer"
    }
  },
  "id": 1
}
``` 