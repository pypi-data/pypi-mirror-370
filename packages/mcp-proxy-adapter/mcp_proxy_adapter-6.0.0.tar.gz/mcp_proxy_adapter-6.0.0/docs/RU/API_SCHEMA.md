# API и схема взаимодействия

## Основные принципы

1. **Единая точка входа для команд**
   - Все команды выполняются через единый механизм, независимо от способа вызова (REST или JSON-RPC)
   - Промежуточный слой (adapter) преобразует входящие запросы в унифицированный формат

2. **Поддерживаемые протоколы**
   - JSON-RPC 2.0 (`/cmd`)
   - REST API (стандартные эндпоинты + `/cmd`)

3. **Формат ответа**
   - Всегда возвращается HTTP код 200
   - Тело ответа всегда в формате JSON-RPC 2.0
   - Ошибки передаются в поле error JSON-RPC ответа
   - HTTP коды 4xx и 5xx не используются

## Структура запросов и ответов

### JSON-RPC формат

```json
// Запрос
{
    "jsonrpc": "2.0",
    "method": "command_name",
    "params": {
        "param1": "value1",
        "param2": "value2"
    },
    "id": 1
}

// Успешный ответ
{
    "jsonrpc": "2.0",
    "result": {
        "data": "command result"
    },
    "id": 1
}

// Ответ с ошибкой
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

### REST формат

```
GET /api/v1/commands           # Список доступных команд
GET /api/v1/commands/{name}    # Информация о команде
POST /cmd                      # Выполнение команды (аналогично JSON-RPC)
```

Ответ всегда оборачивается в JSON-RPC формат:

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

## Промежуточный слой (Adapter)

```python
class CommandAdapter:
    """
    Промежуточный слой для преобразования REST/RPC запросов
    в унифицированный формат команд
    """
    
    async def execute_command(self, command: str, params: dict) -> CommandResult:
        """Единая точка выполнения команд"""
        pass

    def to_jsonrpc_response(self, result: CommandResult) -> dict:
        """Преобразование результата в JSON-RPC формат"""
        pass
```

## Схема OpenAPI

Схема должна соответствовать формату MCP Proxy (порт 8001):

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

## Обработка ошибок

Все ошибки возвращаются в формате JSON-RPC с кодом HTTP 200:

| Тип ошибки | code | message |
|------------|------|---------|
| Parse error | -32700 | "Parse error" |
| Invalid Request | -32600 | "Invalid Request" |
| Method not found | -32601 | "Method not found" |
| Invalid params | -32602 | "Invalid params" |
| Internal error | -32603 | "Internal error" |
| Server error | -32000 to -32099 | "Server error" |

## Примеры использования

### REST запрос
```bash
curl -X GET http://localhost:8000/api/v1/commands
```

### JSON-RPC запрос
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

Оба запроса будут обработаны через единый механизм и вернут ответ в формате JSON-RPC. 