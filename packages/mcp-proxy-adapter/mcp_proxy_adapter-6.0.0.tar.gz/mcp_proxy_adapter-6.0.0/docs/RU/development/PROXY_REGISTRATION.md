# Регистрация на прокси

## Обзор

MCP Proxy Adapter включает автоматическую функциональность регистрации на прокси, которая позволяет серверу регистрироваться на MCP прокси-сервере при запуске и дерегистрироваться при остановке.

## Конфигурация

### Настройки регистрации на прокси

Добавьте следующую секцию в файл конфигурации:

```json
{
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "mcp_proxy_adapter",
    "server_name": "MCP Proxy Adapter",
    "description": "JSON-RPC API for interacting with MCP Proxy",
    "registration_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 5,
    "auto_register_on_startup": true,
    "auto_unregister_on_shutdown": true
  }
}
```

### Параметры конфигурации

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `enabled` | boolean | false | Включить/отключить регистрацию на прокси |
| `proxy_url` | string | "http://localhost:3004" | URL MCP прокси-сервера |
| `server_id` | string | "mcp_proxy_adapter" | Уникальный идентификатор сервера |
| `server_name` | string | "MCP Proxy Adapter" | Человекочитаемое имя сервера |
| `description` | string | "JSON-RPC API for interacting with MCP Proxy" | Описание сервера |
| `registration_timeout` | integer | 30 | Таймаут для запросов регистрации (секунды) |
| `retry_attempts` | integer | 3 | Количество попыток повтора при ошибке |
| `retry_delay` | integer | 5 | Задержка между попытками повтора (секунды) |
| `auto_register_on_startup` | boolean | true | Автоматически регистрироваться при запуске сервера |
| `auto_unregister_on_shutdown` | boolean | true | Автоматически дерегистрироваться при остановке сервера |

## Автоматическая регистрация

### Регистрация при запуске

При запуске сервера автоматически:

1. Загружается конфигурация регистрации на прокси
2. Определяется URL сервера на основе SSL конфигурации
3. Выполняется попытка регистрации на прокси-сервере
4. Логируется результат регистрации

### Дерегистрация при остановке

При остановке сервера автоматически:

1. Выполняется попытка дерегистрации с прокси-сервера
2. Логируется результат дерегистрации

## Ручная регистрация

### Использование команды proxy_registration

Вы можете вручную управлять регистрацией на прокси с помощью встроенной команды `proxy_registration`:

#### Проверка статуса регистрации

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "status"
    },
    "id": 1
  }'
```

#### Регистрация на прокси

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "register",
      "server_url": "http://localhost:8000"
    },
    "id": 1
  }'
```

#### Дерегистрация с прокси

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "proxy_registration",
    "params": {
      "action": "unregister"
    },
    "id": 1
  }'
```

## Интеграция с проверкой здоровья

Статус регистрации на прокси включен в ответ проверки здоровья:

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "health",
    "params": {},
    "id": 1
  }'
```

Ответ включает статус регистрации на прокси:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "data": {
      "status": "ok",
      "version": "1.0.0",
      "uptime": 123.45,
      "components": {
        "system": { ... },
        "process": { ... },
        "commands": { ... },
        "proxy_registration": {
          "enabled": true,
          "registered": true,
          "server_key": "mcp_proxy_adapter_1",
          "proxy_url": "http://localhost:3004"
        }
      }
    }
  },
  "id": 1
}
```

## API интеграция

### Программное использование

```python
from mcp_proxy_adapter.core.proxy_registration import (
    register_with_proxy,
    unregister_from_proxy,
    get_proxy_registration_status
)

# Регистрация на прокси
success = await register_with_proxy("http://localhost:8000")

# Получение статуса регистрации
status = get_proxy_registration_status()

# Дерегистрация с прокси
success = await unregister_from_proxy()
```

### Класс менеджера

```python
from mcp_proxy_adapter.core.proxy_registration import ProxyRegistrationManager

manager = ProxyRegistrationManager()

# Установка URL сервера
manager.set_server_url("http://localhost:8000")

# Регистрация
success = await manager.register_server()

# Получение статуса
status = manager.get_registration_status()

# Дерегистрация
success = await manager.unregister_server()
```

## Обработка ошибок

### Ошибки регистрации

Система обрабатывает различные сценарии ошибок:

1. **Прокси-сервер недоступен**: Повторы с экспоненциальной задержкой
2. **Сетевые ошибки**: Логирование ошибки и продолжение работы
3. **Неверная конфигурация**: Логирование предупреждения и пропуск регистрации
4. **Отклонение регистрации**: Логирование ошибки с деталями

### Логирование

Все события регистрации логируются с соответствующими уровнями:

- **INFO**: Успешная регистрация/дерегистрация
- **WARNING**: Регистрация отключена или не удалась
- **ERROR**: Критические ошибки регистрации

## Примеры

### Базовая конфигурация

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_service",
    "server_name": "My Service",
    "description": "My custom service"
  }
}
```

### SSL конфигурация

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8443
  },
  "ssl": {
    "enabled": true,
    "cert_file": "server.crt",
    "key_file": "server.key"
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_ssl_service",
    "server_name": "My SSL Service"
  }
}
```

### MTLS конфигурация

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 9443
  },
  "ssl": {
    "enabled": true,
    "mode": "mtls_only",
    "cert_file": "server.crt",
    "key_file": "server.key",
    "ca_cert": "ca.crt"
  },
  "proxy_registration": {
    "enabled": true,
    "proxy_url": "http://localhost:3004",
    "server_id": "my_mtls_service",
    "server_name": "My MTLS Service"
  }
}
```

## Тестирование

### Модульные тесты

Запуск тестов регистрации на прокси:

```bash
pytest tests/core/test_proxy_registration.py -v
```

### Интеграционные тесты

Тестирование с реальным прокси-сервером:

```bash
# Запуск прокси-сервера
python proxy_server.py

# Запуск MCP Proxy Adapter с включенной регистрацией
python -m mcp_proxy_adapter.examples.basic_server.server --config config_with_proxy_registration.json

# Проверка статуса регистрации
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "proxy_registration", "params": {"action": "status"}, "id": 1}'
```

## Устранение неполадок

### Частые проблемы

1. **Регистрация не удается**: Проверьте доступность прокси-сервера и конфигурацию
2. **SSL ошибки**: Проверьте пути к сертификатам и SSL конфигурацию
3. **Сетевые таймауты**: Увеличьте значение `registration_timeout`
4. **Ошибки повтора**: Проверьте настройки `retry_attempts` и `retry_delay`

### Режим отладки

Включите отладочное логирование для просмотра детальной информации о регистрации:

```json
{
  "logging": {
    "level": "DEBUG"
  },
  "proxy_registration": {
    "enabled": true
  }
}
```

### Ручная проверка

Проверьте логи прокси-сервера для подтверждения запросов регистрации:

```bash
# Проверка логов прокси-сервера
tail -f proxy_server.log

# Тестирование эндпоинта регистрации прокси напрямую
curl -X POST http://localhost:3004/register \
  -H "Content-Type: application/json" \
  -d '{
    "server_id": "test",
    "server_url": "http://localhost:8000",
    "server_name": "Test Server"
  }'
``` 