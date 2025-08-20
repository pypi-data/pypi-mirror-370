# Конфигурация

Это руководство описывает, как настроить сервис MCP Proxy.

## Файл конфигурации

Сервис MCP Proxy настраивается с помощью JSON-файла конфигурации. По умолчанию он ищет файл с именем `config.json` в текущей директории.

Вы можете указать другой файл конфигурации с помощью опции командной строки `--config`:

```bash
mcp-proxy --config /path/to/config.json
```

## Параметры конфигурации

Конфигурация организована в секции. Вот доступные параметры:

### Конфигурация сервера

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| server.host | string | "0.0.0.0" | Хост для привязки сервиса |
| server.port | number | 8000 | Порт для прослушивания |
| server.debug | boolean | false | Включить режим отладки |
| server.log_level | string | "INFO" | Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

### Конфигурация логирования

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| logging.level | string | "INFO" | Уровень логирования |
| logging.log_dir | string | "./logs" | Директория для файлов логов |
| logging.log_file | string | "mcp_proxy_adapter.log" | Имя основного файла логов |
| logging.error_log_file | string | "mcp_proxy_adapter_error.log" | Имя файла логов ошибок |
| logging.access_log_file | string | "mcp_proxy_adapter_access.log" | Имя файла логов доступа |
| logging.max_file_size | string | "10MB" | Максимальный размер файла логов |
| logging.backup_count | number | 5 | Количество резервных файлов логов |
| logging.console_output | boolean | true | Включить логирование в консоль |
| logging.file_output | boolean | true | Включить логирование в файл |

### Конфигурация команд

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| commands.auto_discovery | boolean | true | Включить автоматическое обнаружение команд |
| commands.discovery_path | string | "mcp_proxy_adapter.commands" | **Путь к пакету с командами** |
| commands.custom_commands_path | string | null | Путь к пользовательским командам (устарел) |

**Важно**: Параметр `commands.discovery_path` указывает путь к Python пакету, где находятся ваши команды. Например:
- `"mcp_proxy_adapter.commands"` - встроенные команды
- `"myproject.commands"` - команды вашего проекта
- `"custom_commands.commands"` - пакет пользовательских команд

## Пример конфигурации

Вот пример файла конфигурации:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "log_level": "INFO"
  },
  "logging": {
    "level": "INFO",
    "log_dir": "./logs",
    "log_file": "mcp_proxy_adapter.log",
    "error_log_file": "mcp_proxy_adapter_error.log",
    "access_log_file": "mcp_proxy_adapter_access.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "console_output": true,
    "file_output": true
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "mcp_proxy_adapter.commands",
    "custom_commands_path": null
  }
}
```

### Пример с пользовательскими командами

Если у вас есть свои команды в пакете `myproject.commands`:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8001,
    "debug": true,
    "log_level": "DEBUG"
  },
  "logging": {
    "level": "DEBUG",
    "log_dir": "./logs",
    "log_file": "myproject.log"
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "myproject.commands"
  }
}
```

## Переменные окружения

Вы также можете настроить сервис с помощью переменных окружения. Переменные окружения имеют приоритет над файлом конфигурации.

Формат переменной окружения: `MCP_UPPERCASE_OPTION_NAME`. Например, чтобы установить порт:

```bash
export MCP_PORT=8000
```

## Тестирование конфигурации

Для проверки конфигурации вы можете запустить сервис с опцией `--validate-config`:

```bash
mcp-proxy --config /path/to/config.json --validate-config
```

Это проверит файл конфигурации и завершит работу без запуска сервиса. 