# Простой пример с пользовательскими командами

Этот пример показывает, как настроить `discovery_path` в конфигурации для автоматического обнаружения команд из вашего проекта.

## Структура проекта

```
simple_custom_commands/
├── config.json          # Конфигурация с discovery_path
├── main.py              # Точка входа
├── my_commands/         # Пакет с командами
│   ├── __init__.py
│   ├── hello_command.py
│   └── calc_command.py
└── README.md
```

## Конфигурация (config.json)

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
    "log_file": "simple_commands.log"
  },
  "commands": {
    "auto_discovery": true,
    "discovery_path": "my_commands"
  }
}
```

**Ключевой момент**: В `discovery_path` указан путь `"my_commands"` - это пакет, где находятся команды.

## Команды

### hello_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class HelloCommand(Command):
    """Простая команда приветствия."""
    
    name = "hello"
    
    def execute(self, name: str = "World") -> CommandResult:
        return CommandResult(
            success=True, 
            data={"message": f"Hello, {name}!"}
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "name": {
                "type": "string",
                "description": "Имя для приветствия",
                "required": False,
                "default": "World"
            }
        }
```

### calc_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class CalcCommand(Command):
    """Простая команда калькулятора."""
    
    name = "calc"
    
    def execute(self, a: float, b: float, operation: str = "add") -> CommandResult:
        if operation == "add":
            result = a + b
        elif operation == "sub":
            result = a - b
        elif operation == "mul":
            result = a * b
        elif operation == "div":
            if b == 0:
                return CommandResult(success=False, error="Division by zero")
            result = a / b
        else:
            return CommandResult(success=False, error=f"Unknown operation: {operation}")
        
        return CommandResult(
            success=True, 
            data={"result": result, "operation": operation}
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "a": {
                "type": "number",
                "description": "Первое число",
                "required": True
            },
            "b": {
                "type": "number", 
                "description": "Второе число",
                "required": True
            },
            "operation": {
                "type": "string",
                "description": "Операция (add, sub, mul, div)",
                "required": False,
                "default": "add"
            }
        }
```

## Запуск

```bash
python main.py
```

При запуске сервис автоматически обнаружит команды из пакета `my_commands` благодаря настройке `discovery_path` в конфигурации.

## Тестирование

```bash
# Приветствие
curl -X POST http://127.0.0.1:8001/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "hello", "params": {"name": "Alice"}}'

# Калькулятор
curl -X POST http://127.0.0.1:8001/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "calc", "params": {"a": 10, "b": 5, "operation": "add"}}'
```

## Результат

Сервис автоматически обнаружит и зарегистрирует команды `hello` и `calc` из пакета `my_commands`, указанного в `discovery_path`. 