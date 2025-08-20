# Ответы API

## Формат ответа

Все ответы от API соответствуют спецификации JSON-RPC 2.0. Типичный ответ имеет следующую структуру:

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

### Поля

- `jsonrpc`: Всегда "2.0"
- `result`: Результат выполнения команды (структура зависит от команды)
- `id`: Тот же идентификатор, что и в запросе

## Ответы с ошибками

Если при выполнении команды возникает ошибка, возвращается ответ с ошибкой:

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

### Поля ошибки

- `code`: Числовой код ошибки
- `message`: Краткое описание ошибки
- `data`: (Опционально) Дополнительная информация об ошибке

## Примеры ответов

### Успешный ответ

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

### Ответ с ошибкой

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

## Пакетные ответы

Для пакетных запросов API возвращает массив ответов:

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

Порядок ответов соответствует порядку запросов в пакете. 