# Примеры использования

Этот документ предоставляет практические примеры использования сервиса MCP Proxy.

## Пример Hello World

### Запрос

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

### Ответ

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

## Пример получения текущей даты

### Запрос

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

### Ответ

```json
{
  "jsonrpc": "2.0",
  "result": {
    "date": "2024-03-20T15:30:45+03:00"
  },
  "id": 2
}
```

## Пример генерации UUID4

### Запрос

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

### Ответ

```json
{
  "jsonrpc": "2.0",
  "result": {
    "uuid": "123e4567-e89b-12d3-a456-426614174000"
  },
  "id": 3
}
```

## Пример пакетного запроса

### Запрос

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

### Ответ

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

## Пример ошибки

### Запрос с недопустимыми параметрами

```bash
curl -X POST http://localhost:8000/api/v1/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "jsonrpc": "2.0",
    "method": "hello_world",
    "params": {
      "name": 123  # Имя должно быть строкой
    },
    "id": 1
  }'
```

### Ответ с ошибкой

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