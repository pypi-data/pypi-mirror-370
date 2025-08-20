# Управление настройками

Этот документ описывает систему управления настройками в фреймворке MCP Proxy Adapter.

## Обзор

Фреймворк предоставляет комплексную систему управления настройками, которая позволяет:
- Загружать конфигурацию из JSON файлов
- Читать настройки программно
- Устанавливать пользовательские настройки динамически
- Перезагружать конфигурацию во время выполнения

## Основные компоненты

### Модуль настроек

Основное управление настройками предоставляется модулем `mcp_proxy_adapter.core.settings`:

```python
from mcp_proxy_adapter.core.settings import (
    Settings,
    ServerSettings,
    LoggingSettings,
    CommandsSettings,
    get_setting,
    set_setting,
    reload_settings
)
```

### Классы конфигурации

#### Класс Settings

Основной класс управления настройками со статическими методами:

```python
# Получить все настройки сервера
server_settings = Settings.get_server_settings()

# Получить все настройки логирования
logging_settings = Settings.get_logging_settings()

# Получить все настройки команд
commands_settings = Settings.get_commands_settings()

# Получить пользовательскую настройку
custom_value = Settings.get_custom_setting("custom.feature_enabled", False)

# Установить пользовательскую настройку
Settings.set_custom_setting("custom.new_feature", True)

# Получить все настройки
all_settings = Settings.get_all_settings()

# Перезагрузить конфигурацию
Settings.reload_config()
```

#### Класс ServerSettings

Вспомогательный класс для настроек сервера:

```python
host = ServerSettings.get_host()        # "127.0.0.1"
port = ServerSettings.get_port()        # 8000
debug = ServerSettings.get_debug()      # True
log_level = ServerSettings.get_log_level()  # "DEBUG"
```

#### Класс LoggingSettings

Вспомогательный класс для настроек логирования:

```python
level = LoggingSettings.get_level()           # "DEBUG"
log_dir = LoggingSettings.get_log_dir()       # "./logs"
log_file = LoggingSettings.get_log_file()     # "app.log"
max_file_size = LoggingSettings.get_max_file_size()  # "10MB"
backup_count = LoggingSettings.get_backup_count()    # 5
```

#### Класс CommandsSettings

Вспомогательный класс для настроек команд:

```python
auto_discovery = CommandsSettings.get_auto_discovery()  # True
discovery_path = CommandsSettings.get_discovery_path()  # "mcp_proxy_adapter.commands"
```

### Функции для быстрого доступа

Для быстрого доступа к общим настройкам:

```python
from mcp_proxy_adapter.core.settings import (
    get_server_host,
    get_server_port,
    get_server_debug,
    get_logging_level,
    get_logging_dir,
    get_auto_discovery,
    get_discovery_path,
    get_setting,
    set_setting,
    reload_settings
)

# Функции быстрого доступа
host = get_server_host()
port = get_server_port()
debug = get_server_debug()
log_level = get_logging_level()

# Общий доступ к настройкам
value = get_setting("custom.feature", default_value)
set_setting("custom.feature", new_value)
reload_settings()
```

## Формат файла конфигурации

Фреймворк использует JSON файлы конфигурации со следующей структурой:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true,
    "log_level": "DEBUG"
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "./logs",
    "log_file": "app.log",
    "error_log_file": "error.log",
    "access_log_file": "access.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
    "console_output": true,
    "file_output": true
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands",
    "custom_commands_path": null
  },
  "custom": {
    "feature_enabled": true,
    "api_version": "1.0.0",
    "nested": {
      "setting": "value"
    }
  }
}
```

## Загрузка конфигурации

### Автоматическая загрузка

Фреймворк автоматически загружает конфигурацию из `./config.json` при запуске.

### Ручная загрузка

Вы можете загрузить конфигурацию из конкретного файла:

```python
from mcp_proxy_adapter.config import config

# Загрузить из конкретного файла
config.load_from_file("/path/to/config.json")

# Перезагрузить текущую конфигурацию
config.load_config()
```

### Переменные окружения

Конфигурация также может быть установлена через переменные окружения с префиксом `SERVICE_`:

```bash
export SERVICE_SERVER_HOST="0.0.0.0"
export SERVICE_SERVER_PORT="8080"
export SERVICE_LOGGING_LEVEL="INFO"
export SERVICE_CUSTOM_FEATURE_ENABLED="true"
```

## Команда settings

Фреймворк включает встроенную команду `settings` для управления конфигурацией:

### Получить все настройки

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get_all"
    }
  }'
```

### Получить конкретную настройку

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get",
      "key": "server.host"
    }
  }'
```

### Установить настройку

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "set",
      "key": "custom.feature_enabled",
      "value": true
    }
  }'
```

### Перезагрузить конфигурацию

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "reload"
    }
  }'
```

## Примеры использования

### Базовый сервер с конфигурацией

```python
import os
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.core.settings import Settings, setup_logging

# Загрузить конфигурацию из файла
config_path = os.path.join(os.path.dirname(__file__), "config.json")
if os.path.exists(config_path):
    from mcp_proxy_adapter.config import config
    config.load_from_file(config_path)

# Настроить логирование с конфигурацией
setup_logging()

# Получить настройки
server_settings = Settings.get_server_settings()
custom_settings = Settings.get_custom_setting("custom", {})

# Создать приложение с настройками
app = create_app(
    title=custom_settings.get("server_name", "Default Server"),
    description=custom_settings.get("description", "Default description")
)

# Запустить сервер с настройками
import uvicorn
uvicorn.run(
    app,
    host=server_settings["host"],
    port=server_settings["port"],
    log_level=server_settings["log_level"].lower()
)
```

### Условная загрузка функций

```python
from mcp_proxy_adapter.core.settings import get_setting

# Проверить, включена ли функция
if get_setting("custom.features.hooks_enabled", False):
    register_hooks()

if get_setting("custom.features.custom_commands_enabled", False):
    register_custom_commands()
```

### Динамические обновления конфигурации

```python
from mcp_proxy_adapter.core.settings import set_setting, reload_settings

# Обновить конфигурацию динамически
set_setting("custom.feature_enabled", True)
set_setting("server.debug", False)

# Перезагрузить из файла (перезаписывает динамические изменения)
reload_settings()
```

## Лучшие практики

1. **Используйте файлы конфигурации**: Храните конфигурацию в JSON файлах вместо жесткого кодирования значений
2. **Переменные окружения**: Используйте переменные окружения для чувствительных или специфичных для среды настроек
3. **Значения по умолчанию**: Всегда предоставляйте значения по умолчанию при чтении настроек
4. **Валидация**: Проверяйте значения конфигурации перед их использованием
5. **Перезагрузка**: Используйте функцию перезагрузки осторожно, так как она перезаписывает динамические изменения
6. **Вложенные настройки**: Используйте точечную нотацию для доступа к вложенным значениям конфигурации

## Обработка ошибок

Система настроек обеспечивает корректную обработку ошибок:

```python
try:
    value = get_setting("custom.feature", default_value)
except Exception as e:
    logger.error(f"Failed to get setting: {e}")
    value = default_value
```

## Интеграция с фреймворком

Система настроек интегрирована во всем фреймворке:

- **Логирование**: Автоматически использует настройки логирования из конфигурации
- **Сервер**: Использует настройки сервера для хоста, порта и режима отладки
- **Команды**: Использует настройки обнаружения команд
- **Middleware**: Может быть настроен через настройки
- **API**: Настройки доступны через команду settings 