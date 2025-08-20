# MCP Proxy Adapter

**MCP Proxy Adapter** - это фреймворк для создания микросервисов на основе JSON-RPC. Он предоставляет базовую инфраструктуру для создания команд, обработки запросов и возвращения ответов через JSON-RPC API.

**MCP Proxy Adapter** - это фреймворк для создания микросервисов на основе JSON-RPC. Он предоставляет базовую инфраструктуру для создания команд, обработки запросов и возвращения ответов через JSON-RPC API.

## Установка

```bash
pip install mcp-proxy-adapter
```

## Использование

1. Создайте свой проект и установите зависимость:

```bash
pip install mcp-proxy-adapter
```

2. Создайте свои команды:

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult

class YourCommand(Command):
    name = "your_command"
    
    async def execute(self, param1: str, param2: int = 0) -> SuccessResult:
        # Ваша логика
        result_data = {"param1": param1, "param2": param2}
        return SuccessResult(data=result_data)
```

3. Запустите сервер:

```python
import uvicorn
from mcp_proxy_adapter.api.app import create_app

# Регистрация ваших команд происходит автоматически
app = create_app()

uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Структура проекта

Проект представляет собой фреймворк с базовой инфраструктурой:

* **mcp_proxy_adapter/** - основной модуль фреймворка
  * **api/** - модуль API
  * **commands/** - базовые классы команд
  * **core/** - ядро фреймворка
  * **schemas/** - JSON-схемы
* **examples/** - примеры использования фреймворка
  * **basic_example/** - базовый пример
  * **minimal_example/** - минимальный пример
  * **complete_example/** - полный пример с Docker

## Базовые команды

Фреймворк включает следующие базовые команды:

- `help` - получение справки по доступным командам
- `health` - проверка состояния сервиса

## API

Фреймворк предоставляет следующие эндпоинты:

- `POST /api/jsonrpc` - основной JSON-RPC эндпоинт для выполнения команд
- `POST /api/command/{command_name}` - REST эндпоинт для выполнения конкретной команды
- `GET /api/commands` - получение списка доступных команд
- `GET /api/commands/{command_name}` - получение информации о конкретной команде
- `GET /health` - проверка состояния сервиса

## Запуск примеров

```bash
# Базовый пример
cd examples/basic_example
python main.py

# Минимальный пример
cd examples/minimal_example
python main.py

# Полный пример с Docker
cd examples/complete_example
docker-compose up -d
```

## Создание новой команды

Пример создания новой команды:

```python
from typing import Dict, Any, ClassVar, Type
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult

class CustomResult(SuccessResult):
    """
    Пользовательский класс результата.
    """
    
    def __init__(self, value: str):
        super().__init__(data={"value": value})
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string"}
                    },
                    "required": ["value"]
                }
            },
            "required": ["data"]
        }

class CustomCommand(Command):
    """
    Пользовательская команда.
    """
    
    name: ClassVar[str] = "custom"
    result_class: ClassVar[Type[SuccessResult]] = CustomResult
    
    async def execute(self, input_text: str) -> CustomResult:
        return CustomResult(value=f"Processed: {input_text}")
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input_text": {"type": "string"}
            },
            "required": ["input_text"],
            "additionalProperties": False
        } 