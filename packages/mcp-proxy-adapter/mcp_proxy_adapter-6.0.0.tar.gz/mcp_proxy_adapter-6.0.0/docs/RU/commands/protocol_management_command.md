# Команда управления протоколами

## Описание

Команда управления протоколами предоставляет функциональность для управления и запроса конфигураций протоколов, включая HTTP, HTTPS и MTLS протоколы. Эта команда позволяет:

- Получать информацию о всех настроенных протоколах
- Проверять статус валидации протоколов
- Получать список разрешенных протоколов
- Валидировать конфигурации протоколов
- Проверять настройки конкретных протоколов

## Результат

Команда возвращает `SuccessResult` или `ErrorResult` с информацией о протоколах.

### Пример успешного результата

```json
{
  "success": true,
  "data": {
    "protocol_info": {
      "http": {
        "enabled": true,
        "allowed": true,
        "port": 8000,
        "requires_ssl": false,
        "ssl_context_available": null
      },
      "https": {
        "enabled": true,
        "allowed": true,
        "port": 8443,
        "requires_ssl": true,
        "ssl_context_available": true
      },
      "mtls": {
        "enabled": true,
        "allowed": true,
        "port": 9443,
        "requires_ssl": true,
        "ssl_context_available": true
      }
    },
    "allowed_protocols": ["http", "https", "mtls"],
    "validation_errors": [],
    "total_protocols": 3,
    "enabled_protocols": 3,
    "protocols_enabled": true
  },
  "message": "Protocol information retrieved successfully"
}
```

## Команда

### Схема

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": ["get_info", "validate_config", "get_allowed", "check_protocol"],
      "description": "Действие для выполнения"
    },
    "protocol": {
      "type": "string",
      "enum": ["http", "https", "mtls"],
      "description": "Протокол для проверки (для действия check_protocol)"
    }
  },
  "required": ["action"]
}
```

### Действия

#### get_info

Получает комплексную информацию о всех протоколах.

**Параметры:** Отсутствуют

**Пример:**
```json
{
  "action": "get_info"
}
```

#### validate_config

Валидирует текущую конфигурацию протоколов и возвращает ошибки.

**Параметры:** Отсутствуют

**Пример:**
```json
{
  "action": "validate_config"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "is_valid": true,
    "validation_errors": [],
    "error_count": 0
  },
  "message": "Configuration validation passed"
}
```

#### get_allowed

Возвращает список текущих разрешенных протоколов.

**Параметры:** Отсутствуют

**Пример:**
```json
{
  "action": "get_allowed"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "allowed_protocols": ["http", "https", "mtls"],
    "count": 3
  },
  "message": "Allowed protocols retrieved successfully"
}
```

#### check_protocol

Проверяет конфигурацию и статус конкретного протокола.

**Параметры:**
- `protocol` (обязательный): Название протокола ("http", "https" или "mtls")

**Пример:**
```json
{
  "action": "check_protocol",
  "protocol": "https"
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "protocol": "https",
    "is_allowed": true,
    "port": 8443,
    "enabled": true,
    "requires_ssl": true,
    "ssl_context_available": true,
    "configuration": {
      "enabled": true,
      "port": 8443
    }
  },
  "message": "Protocol 'https' check completed"
}
```

## Детали реализации

Команда интегрируется с классом `ProtocolManager` для предоставления функциональности управления протоколами. Она поддерживает:

- **Валидацию протоколов**: Проверяет правильность настройки протоколов
- **Управление SSL контекстами**: Валидирует SSL контексты для HTTPS и MTLS протоколов
- **Конфигурацию портов**: Проверяет назначение портов для каждого протокола
- **Обработку ошибок**: Предоставляет детальные сообщения об ошибках для проблем конфигурации

## Примеры использования

### Python

```python
from mcp_proxy_adapter.commands.protocol_management_command import ProtocolManagementCommand

# Создание экземпляра команды
command = ProtocolManagementCommand()

# Получение информации о протоколах
result = await command.execute(action="get_info")
print(result.data["protocol_info"])

# Валидация конфигурации
result = await command.execute(action="validate_config")
if result.data["is_valid"]:
    print("Конфигурация корректна")
else:
    print("Ошибки конфигурации:", result.data["validation_errors"])

# Проверка конкретного протокола
result = await command.execute(action="check_protocol", protocol="https")
if result.data["ssl_context_available"]:
    print("HTTPS правильно настроен с SSL")
```

### HTTP REST

```bash
# Получение информации о протоколах
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "get_info"},
    "id": 1
  }'

# Валидация конфигурации
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "validate_config"},
    "id": 1
  }'

# Проверка HTTPS протокола
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "protocol_management",
    "params": {"action": "check_protocol", "protocol": "https"},
    "id": 1
  }'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "protocol_management",
  "params": {
    "action": "get_info"
  },
  "id": 1
}
```

## Конфигурация

Команда работает с секцией `protocols` в файле конфигурации:

```json
{
  "protocols": {
    "enabled": true,
    "allowed_protocols": ["http", "https", "mtls"],
    "http": {
      "enabled": true,
      "port": 8000
    },
    "https": {
      "enabled": true,
      "port": 8443
    },
    "mtls": {
      "enabled": true,
      "port": 9443
    }
  }
}
```

## Обработка ошибок

Команда предоставляет детальные сообщения об ошибках для различных сценариев:

- **Неизвестное действие**: Когда указано недопустимое действие
- **Отсутствующий протокол**: Когда `check_protocol` вызывается без параметра протокола
- **Неизвестный протокол**: Когда указан неподдерживаемый протокол
- **Ошибки конфигурации**: Когда валидация конфигурации протоколов не проходит

## Связанные компоненты

- **ProtocolManager**: Основная функциональность управления протоколами
- **ProtocolMiddleware**: Middleware для валидации протоколов
- **SSL Configuration**: Настройки SSL/TLS для HTTPS и MTLS протоколов 