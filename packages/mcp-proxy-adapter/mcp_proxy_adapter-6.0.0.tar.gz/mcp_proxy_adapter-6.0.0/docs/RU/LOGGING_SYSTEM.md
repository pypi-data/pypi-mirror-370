# Система логирования

## Содержание

1. [Введение](#введение)
2. [Конфигурация логирования](#конфигурация-логирования)
3. [Форматирование логов](#форматирование-логов)
4. [Ротация логов](#ротация-логов)
5. [Уровни логирования](#уровни-логирования)
6. [Контекстное логирование](#контекстное-логирование)
7. [Использование логирования в коде](#использование-логирования-в-коде)
8. [Примеры](#примеры)

## Введение

Система логирования в микросервисе предназначена для отслеживания работы приложения, диагностики ошибок и мониторинга производительности. Она поддерживает различные уровни логирования, форматирование сообщений, ротацию файлов логов и контекстное логирование для запросов.

Основные компоненты системы логирования:

1. **Базовое логирование** - стандартные функции логирования для всех модулей
2. **Контекстное логирование** - специализированное логирование с контекстом запроса
3. **Ротация логов** - автоматическое управление размером файлов логов
4. **Форматирование** - настраиваемый формат вывода логов

## Конфигурация логирования

Настройки логирования задаются в файле конфигурации `config.json`:

```json
{
    "logging": {
        "level": "DEBUG",
        "file": "logs/app.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "rotation": {
            "type": "size",
            "max_bytes": 10485760,
            "backup_count": 5,
            "when": "D",
            "interval": 1
        },
        "levels": {
            "uvicorn": "INFO",
            "uvicorn.access": "WARNING",
            "fastapi": "INFO"
        }
    }
}
```

### Параметры конфигурации

| Параметр | Описание | Значение по умолчанию |
|----------|----------|------------------------|
| `level` | Уровень логирования | `"INFO"` |
| `file` | Путь к файлу лога | `null` (только вывод в консоль) |
| `format` | Формат сообщений лога | `"%(asctime)s - %(name)s - %(levelname)s - %(message)s"` |
| `date_format` | Формат даты/времени | `"%Y-%m-%d %H:%M:%S"` |
| `rotation.type` | Тип ротации логов (`"size"` или `"time"`) | `"size"` |
| `rotation.max_bytes` | Максимальный размер файла лога (байт) | `10485760` (10 МБ) |
| `rotation.backup_count` | Количество файлов ротации | `5` |
| `rotation.when` | Единицы времени для ротации по времени (`"S"`, `"M"`, `"H"`, `"D"`, `"W0"`-`"W6"`) | `"D"` (день) |
| `rotation.interval` | Интервал ротации | `1` |
| `levels` | Уровни логирования для внешних библиотек | `{}` |

## Форматирование логов

Система логирования использует два разных форматтера:

1. **ConsoleFormatter** - для вывода в консоль с цветовым оформлением
2. **FileFormatter** - для вывода в файл с стандартным форматированием

### Консольный форматтер

```
2023-05-10 12:34:56 - mcp_microservice - INFO - Сообщение лога
```

С цветовой индикацией уровня логирования:
- DEBUG - серый
- INFO - серый
- WARNING - желтый
- ERROR - красный
- CRITICAL - яркий красный

### Файловый форматтер

```
2023-05-10 12:34:56 - mcp_microservice - INFO - Сообщение лога
```

## Ротация логов

Система логирования поддерживает два типа ротации логов:

### 1. Ротация по размеру

Файл лога ротируется, когда его размер превышает заданное значение `max_bytes`.

Пример конфигурации:
```json
"rotation": {
    "type": "size",
    "max_bytes": 10485760,
    "backup_count": 5
}
```

Эта конфигурация создаст следующие файлы:
```
app.log
app.log.1
app.log.2
app.log.3
app.log.4
app.log.5
```

### 2. Ротация по времени

Файл лога ротируется через заданные интервалы времени.

Пример конфигурации:
```json
"rotation": {
    "type": "time",
    "when": "D",
    "interval": 1,
    "backup_count": 7
}
```

Эта конфигурация создаст следующие файлы:
```
app.log
app.log.2023-05-09
app.log.2023-05-08
app.log.2023-05-07
app.log.2023-05-06
app.log.2023-05-05
app.log.2023-05-04
app.log.2023-05-03
```

## Уровни логирования

Система поддерживает стандартные уровни логирования:

- **DEBUG** - Подробная информация для отладки
- **INFO** - Общая информация о работе приложения
- **WARNING** - Предупреждения о потенциальных проблемах
- **ERROR** - Сообщения об ошибках, которые произошли
- **CRITICAL** - Критические ошибки, которые могут привести к сбою приложения

### Специальные правила логирования

#### Запросы к OpenAPI схеме

Запросы к `/openapi.json` автоматически логируются на уровне **DEBUG** вместо **INFO** для уменьшения шума в логах:

```
# До (уровень INFO - шумно)
2025-08-12 20:15:17 [    INFO] Request started: GET http://192.168.252.17:8060/openapi.json | Client: 192.168.252.17

# После (уровень DEBUG - тихо)
2025-08-12 20:15:17 [   DEBUG] Request started: GET http://192.168.252.17:8060/openapi.json | Client: 192.168.252.17
```

Это применяется к:
- Логированию начала запроса
- Логированию завершения запроса
- Логированию ошибок запроса

Чтобы увидеть эти логи, установите уровень логирования в DEBUG:

```json
{
    "logging": {
        "level": "DEBUG"
    }
}
```

## Контекстное логирование

Контекстное логирование используется для связывания логов с конкретным запросом. Каждый запрос получает уникальный идентификатор (`request_id`), который добавляется к сообщениям лога.

### Класс RequestLogger

Класс `RequestLogger` предоставляет контекстное логирование для запросов:

```python
from mcp_proxy_adapter.core.logging import RequestLogger

# Создание логгера для запроса
request_id = "unique-request-id"
logger = RequestLogger("module_name", request_id)

# Логирование с контекстом
logger.info("Обработка запроса начата")
logger.debug("Детали запроса")
logger.error("Ошибка обработки запроса")
```

Формат сообщений контекстного логирования:
```
2023-05-10 12:34:56 - module_name - INFO - [unique-request-id] Обработка запроса начата
```

## Использование логирования в коде

### Базовое логирование

```python
from mcp_proxy_adapter.core.logging import logger, get_logger

# Использование глобального логгера
logger.info("Сервис запущен")

# Создание модульного логгера
module_logger = get_logger(__name__)
module_logger.debug("Детальная информация")
```

### Контекстное логирование для запросов

```python
from mcp_proxy_adapter.core.logging import RequestLogger

# В обработчике запроса
async def handle_request(request):
    request_id = getattr(request.state, "request_id", None)
    req_logger = RequestLogger("api.handler", request_id)
    
    req_logger.info("Запрос получен")
    # Обработка запроса
    req_logger.info("Запрос обработан успешно")
```

### Логирование исключений

```python
try:
    # Код, который может вызвать исключение
    result = process_data()
except Exception as e:
    # Логирование исключения с трассировкой стека
    logger.exception("Ошибка обработки данных")
    # или с контекстным логгером
    req_logger.exception("Ошибка обработки данных")
```

## Примеры

### Пример лога запуска приложения

```
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Initializing logging configuration
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log level: DEBUG
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log file: logs/app.log
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log rotation type: size
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log rotation: when size reaches 10.0 MB
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Log backups: 5
2023-05-10 12:00:00 - mcp_microservice.main - INFO - Starting server on 0.0.0.0:8000
2023-05-10 12:00:01 - mcp_microservice - INFO - Application started with 5 commands registered
```

### Пример лога обработки запроса

```
2023-05-10 12:01:00 - mcp_microservice.api.middleware - INFO - [bc1e3d4a] Request started: POST /api/jsonrpc | Client: 127.0.0.1
2023-05-10 12:01:00 - mcp_microservice.api.handlers - INFO - [bc1e3d4a] Executing JSON-RPC method: hello_world
2023-05-10 12:01:00 - mcp_microservice.api.handlers - INFO - [bc1e3d4a] Command 'hello_world' executed in 0.015 sec
2023-05-10 12:01:00 - mcp_microservice.api.middleware - INFO - [bc1e3d4a] Request completed: POST /api/jsonrpc | Status: 200 | Time: 0.020s
```

### Пример лога с ошибкой

```
2023-05-10 12:02:00 - mcp_microservice.api.middleware - INFO - [cd2f4e5b] Request started: POST /api/jsonrpc | Client: 127.0.0.1
2023-05-10 12:02:00 - mcp_microservice.api.handlers - INFO - [cd2f4e5b] Executing JSON-RPC method: unknown_command
2023-05-10 12:02:00 - mcp_microservice.api.handlers - WARNING - [cd2f4e5b] Method not found: unknown_command
2023-05-10 12:02:00 - mcp_microservice.api.middleware - INFO - [cd2f4e5b] Request completed: POST /api/jsonrpc | Status: 200 | Time: 0.005s
``` 