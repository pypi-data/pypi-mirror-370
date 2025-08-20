# Основы использования

Это руководство объясняет основы использования сервиса MCP Proxy.

## Запуск сервиса

Для запуска сервиса MCP Proxy выполните:

```bash
mcp-proxy
```

По умолчанию сервис будет слушать на `0.0.0.0:8000`.

Вы можете указать пользовательский файл конфигурации с помощью опции `--config`:

```bash
mcp-proxy --config /path/to/config.json
```

## Доступные параметры командной строки

Сервис MCP Proxy поддерживает следующие параметры командной строки:

| Опция | Описание |
|-------|----------|
| `--config PATH` | Путь к файлу конфигурации |
| `--host HOST` | Хост для привязки (переопределяет файл конфигурации) |
| `--port PORT` | Порт для прослушивания (переопределяет файл конфигурации) |
| `--log-level LEVEL` | Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `--validate-config` | Проверить конфигурацию и выйти |
| `--version` | Показать версию и выйти |
| `--help` | Показать справочное сообщение и выйти |

## Выполнение API-запросов

Для выполнения запроса к API MCP Proxy отправьте JSON-RPC 2.0 запрос на эндпоинт `/api/v1/execute`:

### Пример запроса с использованием curl

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

### Пример ответа

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

## Проверка состояния сервиса

Для проверки работоспособности сервиса отправьте GET-запрос на эндпоинт `/api/health`:

```bash
curl http://localhost:8000/api/health
```

Ответ:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": 1620000000.0
}
```

## Получение списка доступных команд

Для получения списка доступных команд отправьте GET-запрос на эндпоинт `/api/commands`:

```bash
curl http://localhost:8000/api/commands
```

Ответ:

```json
{
  "commands": [
    {
      "name": "hello_world",
      "description": "Базовая команда-пример, которая возвращает приветственное сообщение с временной меткой",
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Имя для приветствия"
          }
        }
      }
    },
    {
      "name": "get_date",
      "description": "Возвращает текущую дату и время в формате ISO 8601",
      "schema": {
        "type": "object",
        "properties": {}
      }
    }
  ]
}
``` 