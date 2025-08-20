# Команда {CommandName}

**Содержание**: 1. Обзор • 2. Параметры • 3. Результат • 4. Имплементация • 5. Примеры • 6. Тестирование • 7. Детали реализации • 8. Обработка ошибок

> **Примечание по именованию**: 
> - `{CommandName}` = PascalCase (например, GetFileInfo)
> - `{command_name}` = snake_case (например, get_file_info)

## 1. Обзор

Краткое описание того, что делает команда и когда её следует использовать.

## 2. Параметры

| Имя | Тип | Обязательный | По умолчанию | Описание |
|-----|-----|--------------|--------------|----------|
| param1 | string | Да | - | Описание параметра 1 |
| param2 | integer | Нет | 0 | Описание параметра 2 |

## 3. Результат

Команда возвращает объект `{CommandName}Result` со следующей структурой:

```python
@dataclass
class {CommandName}Result(CommandResult):
    field1: str
    field2: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2
        }
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["field1"],
            "properties": {
                "field1": {
                    "type": "string",
                    "description": "Описание поля field1"
                },
                "field2": {
                    "type": "integer",
                    "description": "Описание поля field2"
                }
            }
        }
```

## 4. Имплементация

Пример реализации команды:

```python
# Файл: mcp_microservice/commands/{command_name}_command.py

from dataclasses import dataclass
from typing import Dict, Any, Optional

from mcp_proxy_adapter.common import CommandResult, Command
from mcp_proxy_adapter.validators import validate_string, validate_integer

@dataclass
class {CommandName}Result(CommandResult):
    field1: str
    field2: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field1": self.field1,
            "field2": self.field2
        }
        
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["field1"],
            "properties": {
                "field1": {
                    "type": "string",
                    "description": "Описание поля field1"
                },
                "field2": {
                    "type": "integer",
                    "description": "Описание поля field2"
                }
            }
        }


class {CommandName}Command(Command):
    """
    Реализация команды {CommandName}.
    
    Краткое описание назначения и функционала команды.
    """
    
    async def execute(self, param1: str, param2: int = 0) -> {CommandName}Result:
        """
        Выполняет команду {CommandName}.
        
        Args:
            param1: Описание параметра 1
            param2: Описание параметра 2
            
        Returns:
            {CommandName}Result: Результат выполнения команды
            
        Raises:
            ValidationError: Если параметры не проходят валидацию
            OperationError: Если возникла ошибка при выполнении операции
        """
        # Валидация параметров
        validate_string(param1, "param1", required=True)
        validate_integer(param2, "param2", required=False, default=0)
        
        # Логика команды
        # ...
        
        # Возврат результата
        return {CommandName}Result(
            field1="результат выполнения",
            field2=param2
        )
```

## 5. Примеры

### Пример использования на Python

```python
from mcp_proxy_adapter import execute_command

result = await execute_command("{command_name}", {
    "param1": "value1",
    "param2": 42
})

print(result.field1)  # Вывод: ожидаемый результат
```

### Пример JSON-RPC

Запрос:
```json
{
    "jsonrpc": "2.0",
    "method": "{command_name}",
    "params": {
        "param1": "value1",
        "param2": 42
    },
    "id": 1
}
```

Ответ:
```json
{
    "jsonrpc": "2.0",
    "result": {
        "field1": "ожидаемый результат",
        "field2": 42
    },
    "id": 1
}
```

### Пример HTTP REST

Запрос:
```
POST /api/v1/commands/{command_name}
Content-Type: application/json

{
    "param1": "value1",
    "param2": 42
}
```

Ответ:
```json
{
    "field1": "ожидаемый результат",
    "field2": 42
}
```

## 6. Тестирование

Пример тестирования команды:

```python
# Файл: tests/commands/test_{command_name}_command.py

import pytest
from mcp_proxy_adapter.commands.{command_name}_command import {CommandName}Command, {CommandName}Result

async def test_{command_name}_success():
    # Подготовка
    command = {CommandName}Command()
    
    # Выполнение
    result = await command.execute(param1="value1", param2=42)
    
    # Проверка
    assert isinstance(result, {CommandName}Result)
    assert result.field1 == "результат выполнения"
    assert result.field2 == 42
    
    # Проверка сериализации
    result_dict = result.to_dict()
    assert result_dict["field1"] == "результат выполнения"
    assert result_dict["field2"] == 42

async def test_{command_name}_validation_error():
    # Подготовка
    command = {CommandName}Command()
    
    # Выполнение и проверка
    with pytest.raises(ValidationError, match="Параметр 'param1' обязателен"):
        await command.execute(param1=None, param2=42)

async def test_{command_name}_schema():
    # Проверка схемы
    schema = {CommandName}Result.get_schema()
    assert schema["type"] == "object"
    assert "field1" in schema["required"]
    assert schema["properties"]["field1"]["type"] == "string"
    assert schema["properties"]["field2"]["type"] == "integer"
```

## 7. Детали реализации

Дополнительные примечания о деталях реализации, специфическом поведении или граничных случаях.

### Расположение в проекте
Команда должна быть размещена в структуре проекта следующим образом:
```
mcp_microservice/
├── commands/
│   ├── __init__.py
│   └── {command_name}_command.py  # Файл команды
└── ...

tests/
└── commands/
    ├── __init__.py
    └── test_{command_name}_command.py  # Тесты команды
```

### Связь с другими компонентами
- **Registry**: Команда автоматически регистрируется в глобальном реестре команд при импорте
- **API**: Доступна через REST API и JSON-RPC интерфейсы
- **Асинхронность**: Все методы команды являются асинхронными для обеспечения высокой производительности

См. [определение CommandResult](../GLOSSARY.md#commandresult) для получения дополнительной информации о формате результата.

## 8. Обработка ошибок

| Код ошибки | Условие | Сообщение |
|------------|---------|-----------|
| 400        | Отсутствует обязательный параметр | "Параметр 'param1' обязателен" |
| 422        | Неверный тип параметра | "Параметр 'param2' должен быть целым числом" |
| 500        | Внутренняя ошибка сервера | "Не удалось обработать запрос" |

Пример ответа с ошибкой:
```json
{
    "jsonrpc": "2.0",
    "error": {
        "code": 400,
        "message": "Параметр 'param1' обязателен"
    },
    "id": 1
}
``` 