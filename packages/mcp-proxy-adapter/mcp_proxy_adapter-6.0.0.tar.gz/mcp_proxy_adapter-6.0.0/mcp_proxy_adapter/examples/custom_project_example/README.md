# Пример пользовательского проекта с командами

Этот пример показывает, как создать свой проект с командами и настроить `discovery_path` для их автоматического обнаружения.

## Структура проекта

```
myproject/
├── config.json
├── main.py
├── myproject/
│   ├── __init__.py
│   └── commands/
│       ├── __init__.py
│       ├── echo_command.py
│       └── info_command.py
└── README.md
```

## Конфигурация

В файле `config.json` указываем путь к нашим командам:

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

## Команды

### echo_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class EchoCommand(Command):
    """Echo command that returns the input text."""
    
    name = "echo"
    
    def execute(self, text: str) -> CommandResult:
        return CommandResult(success=True, data={"echo": text})
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {
            "text": {
                "type": "string",
                "description": "Text to echo",
                "required": True
            }
        }
```

### info_command.py

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import CommandResult

class InfoCommand(Command):
    """Info command that returns project information."""
    
    name = "info"
    
    def execute(self) -> CommandResult:
        return CommandResult(
            success=True, 
            data={
                "project": "myproject",
                "version": "1.0.0",
                "description": "Example project with custom commands"
            }
        )
    
    @classmethod
    def get_param_info(cls) -> dict:
        return {}
```

## Запуск

```bash
python main.py
```

При запуске сервис автоматически обнаружит команды из пакета `myproject.commands` благодаря настройке `discovery_path` в конфигурации. 