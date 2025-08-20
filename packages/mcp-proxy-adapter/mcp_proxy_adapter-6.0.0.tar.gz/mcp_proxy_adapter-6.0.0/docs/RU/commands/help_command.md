# Команда help

## Описание

Команда `help` предназначена для получения справочной информации о доступных командах в системе. Может использоваться в двух режимах:
1. **Без параметров**: возвращает список всех доступных команд с кратким описанием
2. **С параметром `cmdname`**: возвращает детальную информацию о конкретной команде

## Результат

Результат выполнения команды представлен классом `HelpResult` и имеет следующую структуру:

```python
class HelpResult(CommandResult):
    """
    Результат выполнения команды help.
    """
    
    def __init__(self, commands_info: Optional[Dict[str, Any]] = None, command_info: Optional[Dict[str, Any]] = None):
        """
        Инициализация результата команды help.
        
        Args:
            commands_info: Информация о всех командах (для запроса без параметров)
            command_info: Информация о конкретной команде (для запроса с параметром cmdname)
        """
        self.commands_info = commands_info
        self.command_info = command_info
```

## Команда

Команда `help` реализована в классе `HelpCommand`:

```python
class HelpCommand(Command):
    """
    Команда для получения справочной информации о доступных командах.
    """
    
    name = "help"
    result_class = HelpResult
    
    async def execute(self, cmdname: Optional[str] = None) -> HelpResult:
        """
        Выполнение команды help.
        
        Args:
            cmdname: Имя команды для получения справки (опционально)
            
        Returns:
            HelpResult: Результат выполнения команды
            
        Raises:
            NotFoundError: Если указанная команда не найдена
        """
        # Код реализации команды
```

## Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|-------------|----------|
| `cmdname` | `string` | Нет | Имя команды, о которой нужно получить подробную информацию |

## Детали реализации

Команда `help` взаимодействует с реестром команд (`CommandRegistry`) для получения информации о зарегистрированных командах. При запросе без параметров, команда возвращает список всех команд с их краткими описаниями. При запросе с параметром `cmdname`, команда возвращает детальную информацию о конкретной команде, включая:
- Имя команды
- Полное описание
- Информацию о параметрах
- Схему результата

Команда `help` является системной и регистрируется в реестре команд при инициализации приложения.

## Примеры использования

### Python

```python
from mcp_proxy_adapter.commands.help_command import HelpCommand

# Получение списка всех команд
help_cmd = HelpCommand()
result = await help_cmd.execute()
commands = result.to_dict()

# Получение информации о конкретной команде
result = await help_cmd.execute(cmdname="health")
command_info = result.to_dict()
```

### HTTP REST (эндпоинт /cmd)

**Запрос для получения списка всех команд:**
```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "help"
}
```

**Ответ:**
```json
{
    "result": {
        "commands": {
            "help": {
                "description": "Получение справочной информации о доступных командах"
            },
            "health": {
                "description": "Проверка состояния сервера"
            },
            "echo": {
                "description": "Возвращает переданные параметры"
            }
        }
    }
}
```

**Запрос для получения информации о конкретной команде:**
```http
POST /cmd HTTP/1.1
Content-Type: application/json

{
    "command": "help",
    "params": {
        "cmdname": "health"
    }
}
```

**Ответ:**
```json
{
    "result": {
        "command": {
            "name": "health",
            "description": "Проверка состояния сервера",
            "params": {
                "check_type": {
                    "type": "string",
                    "description": "Тип проверки (basic или detailed)",
                    "required": false,
                    "default": "basic"
                }
            },
            "schema": {
                "type": "object",
                "properties": {
                    "check_type": {
                        "type": "string",
                        "enum": ["basic", "detailed"]
                    }
                }
            },
            "result_schema": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string"
                    },
                    "uptime": {
                        "type": "number"
                    }
                }
            }
        }
    }
}
```

### JSON-RPC

**Запрос для получения списка всех команд:**
```json
{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {},
    "id": 1
}
```

**Ответ:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "commands": {
            "help": {
                "description": "Получение справочной информации о доступных командах"
            },
            "health": {
                "description": "Проверка состояния сервера"
            }
        }
    },
    "id": 1
}
```

**Запрос для получения информации о конкретной команде:**
```json
{
    "jsonrpc": "2.0",
    "method": "help",
    "params": {
        "cmdname": "health"
    },
    "id": 2
}
```

**Ответ:**
```json
{
    "jsonrpc": "2.0",
    "result": {
        "command": {
            "name": "health",
            "description": "Проверка состояния сервера",
            "params": {
                "check_type": {
                    "type": "string",
                    "description": "Тип проверки (basic или detailed)",
                    "required": false,
                    "default": "basic"
                }
            }
        }
    },
    "id": 2
}
``` 