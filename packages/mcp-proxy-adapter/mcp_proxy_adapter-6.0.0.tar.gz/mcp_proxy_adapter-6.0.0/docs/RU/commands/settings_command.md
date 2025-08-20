# Команда Settings

Команда `settings` предоставляет комплексные возможности управления конфигурацией для фреймворка MCP Proxy Adapter.

## Описание

Команда settings позволяет:
- Просматривать все настройки конфигурации
- Получать конкретные значения конфигурации
- Устанавливать значения конфигурации динамически
- Перезагружать конфигурацию из файлов

## Информация о команде

- **Имя**: `settings`
- **Описание**: Управление настройками и конфигурацией фреймворка
- **Категория**: Управление конфигурацией

## Параметры

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|----------|-----|--------------|--------------|----------|
| `operation` | string | Да | `"get_all"` | Операция для выполнения: `get`, `set`, `get_all`, `reload` |
| `key` | string | Нет | - | Ключ конфигурации в точечной нотации (например, `server.host`, `custom.feature_enabled`) |
| `value` | any | Нет | - | Значение конфигурации для установки (для операции `set`) |

### Операции

#### `get_all`
Получает все настройки конфигурации.

**Параметры**: Не требуются

**Пример**:
```json
{
  "command": "settings",
  "params": {
    "operation": "get_all"
  }
}
```

#### `get`
Получает конкретное значение конфигурации.

**Параметры**:
- `key` (обязательный): Ключ конфигурации в точечной нотации

**Пример**:
```json
{
  "command": "settings",
  "params": {
    "operation": "get",
    "key": "server.host"
  }
}
```

#### `set`
Устанавливает значение конфигурации динамически.

**Параметры**:
- `key` (обязательный): Ключ конфигурации в точечной нотации
- `value` (обязательный): Значение для установки

**Пример**:
```json
{
  "command": "settings",
  "params": {
    "operation": "set",
    "key": "custom.feature_enabled",
    "value": true
  }
}
```

#### `reload`
Перезагружает конфигурацию из файлов и переменных окружения.

**Параметры**: Не требуются

**Пример**:
```json
{
  "command": "settings",
  "params": {
    "operation": "reload"
  }
}
```

## Формат ответа

### Успешный ответ

```json
{
  "result": {
    "success": true,
    "operation": "get_all",
    "all_settings": {
      "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "debug": true,
        "log_level": "DEBUG"
      },
      "logging": {
        "level": "DEBUG",
        "log_dir": "./logs",
        "log_file": "app.log"
      },
      "commands": {
        "auto_discovery": true,
        "discovery_path": "mcp_proxy_adapter.commands"
      },
      "custom": {
        "feature_enabled": true
      }
    }
  }
}
```

### Ответ операции get

```json
{
  "result": {
    "success": true,
    "operation": "get",
    "key": "server.host",
    "value": "127.0.0.1"
  }
}
```

### Ответ операции set

```json
{
  "result": {
    "success": true,
    "operation": "set",
    "key": "custom.feature_enabled",
    "value": true
  }
}
```

### Ответ с ошибкой

```json
{
  "result": {
    "success": false,
    "operation": "get",
    "error_message": "Key is required for 'get' operation"
  }
}
```

## Примеры использования

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

### Получить хост сервера

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

### Получить пользовательскую настройку

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "get",
      "key": "custom.features.hooks_enabled"
    }
  }'
```

### Установить пользовательскую настройку

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "settings",
    "params": {
      "operation": "set",
      "key": "custom.debug_mode",
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

## Ключи конфигурации

### Настройки сервера

- `server.host` - Адрес хоста сервера
- `server.port` - Номер порта сервера
- `server.debug` - Флаг режима отладки
- `server.log_level` - Уровень логирования сервера

### Настройки логирования

- `logging.level` - Уровень логирования
- `logging.log_dir` - Путь к директории логов
- `logging.log_file` - Имя основного файла лога
- `logging.error_log_file` - Имя файла лога ошибок
- `logging.access_log_file` - Имя файла лога доступа
- `logging.max_file_size` - Максимальный размер файла лога
- `logging.backup_count` - Количество резервных файлов
- `logging.format` - Формат сообщения лога
- `logging.date_format` - Формат даты
- `logging.console_output` - Флаг вывода в консоль
- `logging.file_output` - Флаг вывода в файл

### Настройки команд

- `commands.auto_discovery` - Флаг автоматического обнаружения
- `commands.discovery_path` - Путь обнаружения команд
- `commands.custom_commands_path` - Путь к пользовательским командам

### Пользовательские настройки

Любые настройки в разделе `custom` можно получить с помощью точечной нотации:

- `custom.feature_enabled`
- `custom.api_version`
- `custom.features.hooks_enabled`
- `custom.nested.setting`

## Обработка ошибок

Команда обеспечивает комплексную обработку ошибок:

- **Отсутствующий ключ**: Возвращает ошибку, когда ключ требуется, но не предоставлен
- **Неверная операция**: Возвращает ошибку для неподдерживаемых операций
- **Ошибки конфигурации**: Корректно обрабатывает ошибки загрузки конфигурации

## Интеграция

Команда settings интегрируется с:

- **Системой конфигурации**: Использует управление конфигурацией фреймворка
- **Системой логирования**: Соблюдает конфигурацию логирования
- **Реестром команд**: Доступна через реестр команд
- **API эндпоинтами**: Доступна через эндпоинты `/cmd` и `/api/commands`

## Лучшие практики

1. **Используйте точечную нотацию**: Получайте доступ к вложенным настройкам с помощью точечной нотации (например, `custom.features.enabled`)
2. **Предоставляйте значения по умолчанию**: Всегда обрабатывайте случаи, когда настройки могут не существовать
3. **Проверяйте значения**: Проверяйте значения конфигурации перед их использованием
4. **Перезагружайте осторожно**: Используйте операцию перезагрузки осторожно, так как она перезаписывает динамические изменения
5. **Обработка ошибок**: Всегда проверяйте поле `success` в ответах 