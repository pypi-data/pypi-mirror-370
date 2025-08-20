# Examples of Classes for mcp_microservice Architecture

## 1. Abstract BaseCommand Class

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCommand(ABC):
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Return metadata describing the command, its parameters, types, required flags, defaults, etc.
        Example:
        {
            "name": "add_note",
            "description": "Add a new note",
            "parameters": {
                "text": {"type": "string", "description": "Note text", "required": True}
            },
            "returns": {"type": "object", "description": "Created note object"}
        }
        """
        pass

    @abstractmethod
    async def execute(self, **params) -> Any:
        """
        Execute the command with given parameters.
        """
        pass
```

## 2. Example of a Concrete Command

```python
class AddNoteCommand(BaseCommand):
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "add_note",
            "description": "Add a new note",
            "parameters": {
                "text": {"type": "string", "description": "Note text", "required": True}
            },
            "returns": {"type": "object", "description": "Created note object"}
        }

    async def execute(self, text: str) -> dict:
        # Business logic here
        note = {"id": 1, "text": text}
        return note
```

## 3. Command Registry Class

```python
class CommandRegistry:
    def __init__(self):
        self.commands = {}

    def register(self, command: BaseCommand):
        meta = command.get_metadata()
        self.commands[meta["name"]] = command

    def get_metadata(self):
        return {name: cmd.get_metadata() for name, cmd in self.commands.items()}

    async def execute(self, name: str, **params):
        if name not in self.commands:
            raise KeyError(f"Unknown command: {name}")
        return await self.commands[name].execute(**params)
```

## 4. Command Manager

```python
class CommandManager:
    def __init__(self, registry: CommandRegistry):
        self.registry = registry

    async def handle_request(self, request: dict) -> dict:
        # Extract command and params from request
        command = request["method"]
        params = request.get("params", {})
        result = await self.registry.execute(command, **params)
        return {"jsonrpc": "2.0", "result": result, "id": request.get("id")}
``` 