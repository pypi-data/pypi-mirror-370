# Команда new_uuid4

## Описание
Генерирует новый UUID версии 4 (случайный).

## Результат

```python
@dataclass
class NewUuid4Result(CommandResult):
    """Результат генерации UUID4"""
    uuid: str  # UUID в строковом формате

    def to_dict(self) -> Dict[str, Any]:
        return {"uuid": self.uuid}

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["uuid"],
            "properties": {
                "uuid": {
                    "type": "string",
                    "description": "Сгенерированный UUID4 в строковом формате",
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
                }
            }
        }
```

## Команда

```python
@registry.command
async def new_uuid4() -> NewUuid4Result:
    """
    Генерирует новый UUID версии 4 (случайный)
    
    Returns:
        NewUuid4Result: Результат с UUID в строковом формате
        
    Examples:
        >>> await new_uuid4()
        NewUuid4Result(uuid="123e4567-e89b-12d3-a456-426614174000")
        
        JSON-RPC запрос:
        {
            "jsonrpc": "2.0",
            "method": "new_uuid4",
            "id": 1
        }
        
        JSON-RPC ответ:
        {
            "jsonrpc": "2.0",
            "result": {
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            },
            "id": 1
        }
    """
```

## Особенности реализации

1. Использует стандартный модуль `uuid` для генерации UUID4
2. UUID всегда возвращается в нижнем регистре
3. Формат UUID соответствует RFC 4122
4. Генерация происходит с использованием криптографически стойкого генератора случайных чисел

## Примеры использования

### Python
```python
result = await new_uuid4()
print(result.uuid)  # 123e4567-e89b-12d3-a456-426614174000
```

### HTTP REST
```http
POST /api/v1/commands/new_uuid4
Content-Type: application/json

{}

Response:
{
    "uuid": "123e4567-e89b-12d3-a456-426614174000"
}
```

### JSON-RPC через WebSocket
```javascript
// Запрос
{
    "jsonrpc": "2.0",
    "method": "new_uuid4",
    "id": 1
}

// Ответ
{
    "jsonrpc": "2.0",
    "result": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000"
    },
    "id": 1
}
``` 