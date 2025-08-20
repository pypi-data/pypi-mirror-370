# Результаты команд и формирование схемы

## Базовый класс результата

Все команды возвращают результат, наследуемый от базового класса `CommandResult`:

```python
from typing import Any, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class CommandResult(ABC):
    """Базовый класс для результатов команд"""
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразует результат в словарь для сериализации"""
        pass
        
    @abstractmethod
    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        """Преобразует результат в JSON-RPC формат"""
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    @abstractmethod
    def get_schema(cls) -> Dict[str, Any]:
        """Возвращает OpenAPI схему результата"""
        pass
```

## Примеры реализации

### Простой результат

```python
@dataclass
class StatusResult(CommandResult):
    """Результат команды получения статуса"""
    status: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"status": self.status}
        if self.details:
            result["details"] = self.details
        return result

    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Статус операции"
                },
                "details": {
                    "type": "object",
                    "description": "Дополнительные детали",
                    "additionalProperties": True
                }
            }
        }
```

### Сложный результат с вложенными объектами

```python
@dataclass
class FileInfo:
    """Информация о файле"""
    name: str
    size: int
    modified: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "size": self.size,
            "modified": self.modified
        }

@dataclass
class FileListResult(CommandResult):
    """Результат команды получения списка файлов"""
    files: List[FileInfo]
    total_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "files": [f.to_dict() for f in self.files],
            "total_count": self.total_count
        }

    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "result": self.to_dict(),
            "id": id
        }

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["files", "total_count"],
            "properties": {
                "files": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "size", "modified"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Имя файла"
                            },
                            "size": {
                                "type": "integer",
                                "description": "Размер файла в байтах"
                            },
                            "modified": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Дата модификации"
                            }
                        }
                    }
                },
                "total_count": {
                    "type": "integer",
                    "description": "Общее количество файлов"
                }
            }
        }
```

## Интеграция с командами

Команды используют типизированные результаты:

```python
@registry.command
async def get_status() -> StatusResult:
    """
    Получает статус системы
    Returns:
        StatusResult: Текущий статус системы
    """
    return StatusResult(
        status="ok",
        details={"version": "1.0.0"}
    )

@registry.command
async def list_files(path: str) -> FileListResult:
    """
    Получает список файлов в директории
    Args:
        path: Путь к директории
    Returns:
        FileListResult: Список файлов и их метаданные
    """
    files = []
    # ... логика получения списка файлов
    return FileListResult(files=files, total_count=len(files))
```

## Формирование схемы

Схема OpenAPI формируется динамически на основе:
1. Метаданных команд (имя, описание, параметры)
2. Схем результатов команд
3. Базовой схемы JSON-RPC

### Процесс формирования

1. **Регистрация команды**
   ```python
   class CommandRegistry:
       def register(self, func: Callable) -> None:
           command = Command(
               name=func.__name__,
               func=func,
               doc=parse_docstring(func.__doc__),
               result_type=get_return_annotation(func)
           )
           self.commands[command.name] = command
   ```

2. **Получение схемы результата**
   ```python
   def get_command_schema(command: Command) -> Dict[str, Any]:
       # Получаем схему из типа результата
       result_schema = command.result_type.get_schema()
       
       # Добавляем в общую схему
       return {
           "type": "object",
           "properties": {
               "jsonrpc": {"type": "string", "enum": ["2.0"]},
               "result": result_schema,
               "id": {"type": ["string", "integer", "null"]}
           }
       }
   ```

3. **Формирование полной схемы**
   ```python
   def generate_schema(registry: CommandRegistry) -> Dict[str, Any]:
       schema = load_base_schema()
       
       for command in registry.commands.values():
           # Добавляем схему параметров
           add_params_schema(schema, command)
           
           # Добавляем схему результата
           add_result_schema(schema, command)
           
       return schema
   ```

## Преимущества подхода

1. **Типобезопасность**
   - Все результаты строго типизированы
   - IDE предоставляет автодополнение
   - Ошибки обнаруживаются на этапе компиляции

2. **Единообразие**
   - Все команды возвращают результаты в одном формате
   - JSON-RPC обертка добавляется автоматически
   - Схема формируется единообразно

3. **Расширяемость**
   - Легко добавлять новые типы результатов
   - Схема расширяется автоматически
   - Поддержка сложных вложенных структур

4. **Документация**
   - Схема автоматически документирует API
   - Типы результатов самодокументируемы
   - Поддержка OpenAPI инструментов

## Обработка ошибок

Ошибки также являются специальным типом результата:

```python
@dataclass
class CommandError(CommandResult):
    """Ошибка выполнения команды"""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None

    def to_jsonrpc(self, id: Optional[str] = None) -> Dict[str, Any]:
        error = {
            "code": self.code,
            "message": self.message
        }
        if self.details:
            error["data"] = self.details
            
        return {
            "jsonrpc": "2.0",
            "error": error,
            "id": id
        }
```

Это обеспечивает единообразную обработку как успешных результатов, так и ошибок. 