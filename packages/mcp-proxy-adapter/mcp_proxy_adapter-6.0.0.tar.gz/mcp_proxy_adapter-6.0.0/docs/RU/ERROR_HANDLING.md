# Система обработки ошибок

## Введение

Система обработки ошибок в данном микросервисе разработана для обеспечения согласованных, предсказуемых ответов об ошибках в соответствии со спецификацией JSON-RPC 2.0. Этот документ описывает иерархию ошибок, коды ошибок и лучшие практики обработки ошибок.

## Структура ошибки

Согласно спецификации JSON-RPC 2.0, ответы с ошибками имеют следующую структуру:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Сообщение об ошибке",
    "data": {
      "detail1": "value1",
      "detail2": "value2"
    }
  },
  "id": "request-id"
}
```

Где:
- `code` - числовой код ошибки
- `message` - человекочитаемое описание ошибки
- `data` - (опционально) дополнительные детали ошибки

## Иерархия ошибок

Все ошибки в системе наследуются от базового класса `MicroserviceError`, который реализован в `core/errors.py`. Иерархия следующая:

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

## Стандартные коды ошибок

Наш микросервис следует спецификации JSON-RPC 2.0 для кодов ошибок:

| Диапазон кодов | Описание |
|----------------|----------|
| -32700 | Ошибка разбора (некорректный JSON) |
| -32600 | Некорректный запрос (не соответствует спецификации JSON-RPC) |
| -32601 | Метод не найден |
| -32602 | Некорректные параметры |
| -32603 | Внутренняя ошибка |
| -32000 to -32099 | Ошибка сервера (определяется реализацией) |

Конкретные коды ошибок в нашей системе:

| Код | Класс ошибки | Описание |
|-----|--------------|----------|
| -32700 | ParseError | Ошибка при разборе JSON запроса |
| -32600 | InvalidRequestError | Некорректный формат запроса JSON-RPC |
| -32601 | MethodNotFoundError | Метод не найден |
| -32602 | InvalidParamsError, ValidationError | Некорректные параметры или ошибка валидации |
| -32603 | InternalError, ConfigurationError | Внутренняя ошибка сервера |
| -32000 | CommandError | Общая ошибка выполнения команды |
| -32001 | AuthenticationError | Ошибка аутентификации |
| -32002 | AuthorizationError | Ошибка авторизации |
| -32003 | TimeoutError | Ошибка таймаута |
| -32004 | ResourceNotFoundError | Ресурс не найден |
| -32005 | ResourceExistsError | Ресурс уже существует |
| -32007 | ConnectionError | Ошибка соединения |

## Использование ошибок в командах

При реализации команд следует использовать соответствующий класс ошибки для сигнализации об ошибках. Ошибка будет преобразована в правильный формат JSON-RPC на уровне API.

Пример вызова ошибки в команде:

```python
from mcp_proxy_adapter.core.errors import ValidationError, ResourceNotFoundError

# Ошибка валидации
raise ValidationError("Недопустимое значение параметра", data={"param": "value", "reason": "Должно быть положительным"})

# Ресурс не найден
raise ResourceNotFoundError("Пользователь не найден", data={"user_id": 123})
```

## Обработка ошибок в базовом классе Command

Базовый класс `Command` в `commands/base.py` обрабатывает ошибки, возникающие при выполнении команды, и преобразует их в экземпляры `ErrorResult`:

```python
try:
    # Выполнение команды
    result = await command.execute(**validated_params)
    return result
except ValidationError as e:
    return ErrorResult(message=str(e), code=e.code, details=e.data)
except CommandError as e:
    return ErrorResult(message=str(e), code=e.code, details=e.data)
except Exception as e:
    return ErrorResult(
        message=f"Ошибка выполнения команды: {str(e)}", 
        code=-32603, 
        details={"original_error": str(e)}
    )
```

## Обработка ошибок на уровне API

Уровень API (`api/handlers.py`) преобразует ошибки команд в ответы об ошибках JSON-RPC:

```python
try:
    # Выполнение команды
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

## Обработка ошибок в middleware

`ErrorHandlingMiddleware` в `api/middleware/error_handling.py` перехватывает необработанные исключения на уровне API и преобразует их в соответствующие HTTP-ответы:

- `ValidationError` → HTTP 400 Bad Request
- `AuthenticationError` → HTTP 401 Unauthorized
- `AuthorizationError` → HTTP 403 Forbidden
- `ResourceNotFoundError` → HTTP 404 Not Found
- `CommandError` → HTTP 400 Bad Request
- Другие ошибки → HTTP 500 Internal Server Error

## Лучшие практики

1. **Используйте конкретные типы ошибок**: Всегда используйте наиболее специфичный класс ошибки, который подходит для вашей ситуации.

2. **Включайте полезные данные**: Добавляйте соответствующие данные в ошибку, чтобы помочь в устранении проблемы.

3. **Следуйте соглашениям о кодах ошибок**: Используйте стандартные коды ошибок, определенные в спецификации JSON-RPC.

4. **Логируйте ошибки**: Все ошибки должны быть правильно зарегистрированы для отладки.

5. **Согласованные ответы об ошибках**: Обеспечьте согласованность ответов об ошибках во всех конечных точках и форматах.

6. **Валидация**: Используйте валидацию для раннего обнаружения ошибок, до выполнения команды.

7. **Безопасные сообщения об ошибках**: Не раскрывайте чувствительную информацию в сообщениях об ошибках или деталях.

## Примеры ответов об ошибках

### Некорректный запрос
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

### Метод не найден
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

### Ошибка валидации
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32602,
    "message": "Invalid parameters",
    "data": {
      "errors": {
        "name": "Поле обязательно",
        "age": "Должно быть положительным числом"
      }
    }
  },
  "id": "123"
}
```

### Внутренняя ошибка
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Internal error",
    "data": {
      "original_error": "Таймаут соединения с базой данных"
    }
  },
  "id": "123"
}
``` 