# Чеклист добавления команды

## 1. Создание файла команды
- [ ] Создать файл `{command_name}_command.py` в директории команд
- [ ] Добавить необходимые импорты:
  ```python
  from typing import Dict, Any, Optional
  from dataclasses import dataclass
  from mcp_proxy_adapter.models import CommandResult
  from mcp_proxy_adapter.registry import registry
  ```

## 2. Создание класса результата
- [ ] Определить класс результата, наследующийся от `CommandResult`
- [ ] Добавить все необходимые поля через `@dataclass`
- [ ] Реализовать метод `to_dict()`
- [ ] Реализовать метод `get_schema()`
- [ ] Если нужно, переопределить метод `to_jsonrpc()`

## 3. Создание класса команды
- [ ] Определить класс команды с необходимыми параметрами
- [ ] Добавить аннотации типов для всех параметров
- [ ] Добавить значения по умолчанию для опциональных параметров
- [ ] Реализовать метод `execute()` с бизнес-логикой
- [ ] Добавить подробную документацию (docstring)

## 4. Регистрация команды
- [ ] Добавить декоратор `@registry.command`
- [ ] Проверить что команда возвращает корректный тип результата

## 5. Тестирование
- [ ] Создать тест-кейсы для команды
- [ ] Создать тест-кейсы для результата
- [ ] Проверить валидацию параметров
- [ ] Проверить сериализацию результата
- [ ] Проверить генерацию схемы

## 6. Документация
- [ ] Добавить примеры использования в docstring
- [ ] Добавить описание всех параметров
- [ ] Добавить описание возвращаемого результата
- [ ] Добавить примеры JSON-RPC запросов/ответов

## Пример структуры файла команды

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass
from mcp_proxy_adapter.models import CommandResult
from mcp_proxy_adapter.registry import registry

@dataclass
class GetStatusResult(CommandResult):
    """Результат выполнения команды получения статуса"""
    status: str
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"status": self.status}
        if self.details:
            result["details"] = self.details
        return result

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

@registry.command
async def get_status() -> GetStatusResult:
    """
    Получает текущий статус системы
    
    Returns:
        GetStatusResult: Результат со статусом и деталями
        
    Examples:
        >>> await get_status()
        GetStatusResult(status="ok", details={"version": "1.0.0"})
        
        JSON-RPC запрос:
        {
            "jsonrpc": "2.0",
            "method": "get_status",
            "id": 1
        }
        
        JSON-RPC ответ:
        {
            "jsonrpc": "2.0",
            "result": {
                "status": "ok",
                "details": {"version": "1.0.0"}
            },
            "id": 1
        }
    """
    # Реализация бизнес-логики
    return GetStatusResult(
        status="ok",
        details={"version": "1.0.0"}
    )
```

## 7. Проверка после добавления
- [ ] Запустить все тесты
- [ ] Проверить генерацию OpenAPI схемы
- [ ] Проверить работу команды через JSON-RPC
- [ ] Проверить работу команды через REST API
- [ ] Проверить документацию в Swagger UI

## 8. Правила и рекомендации

1. **Один файл - одна команда**
   - Каждая команда должна быть в отдельном файле
   - В файле должны быть только классы и функции, относящиеся к этой команде
   - Имя файла должно отражать назначение команды

2. **Структура файла**
   - Сначала идут импорты
   - Затем класс результата
   - Затем функция команды
   - Вспомогательные функции/классы (если нужны) в конце файла

3. **Именование**
   - Имя файла: `{command_name}_command.py`
   - Имя класса результата: `{CommandName}Result`
   - Имя функции команды: `{command_name}`

4. **Документация**
   - Docstring должен быть у класса результата
   - Docstring должен быть у функции команды
   - Все параметры должны быть описаны
   - Должны быть примеры использования

5. **Типизация**
   - Все параметры должны иметь аннотации типов
   - Все методы должны иметь аннотации возвращаемых значений
   - Использовать типы из модуля typing где это возможно 