# Команда get_date

## Описание
Возвращает текущую дату и время в формате ISO 8601 с учетом временной зоны.

## Результат

```python
@dataclass
class GetDateResult(CommandResult):
    """Результат получения текущей даты"""
    date: str  # Дата в формате ISO 8601

    def to_dict(self) -> Dict[str, Any]:
        return {"date": self.date}

    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "required": ["date"],
            "properties": {
                "date": {
                    "type": "string",
                    "description": "Текущая дата и время в формате ISO 8601",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:?\\d{2}$"
                }
            }
        }
```

## Команда

```python
@registry.command
async def get_date() -> GetDateResult:
    """
    Возвращает текущую дату и время в формате ISO 8601
    
    Returns:
        GetDateResult: Результат с датой в формате ISO 8601
        
    Examples:
        >>> await get_date()
        GetDateResult(date="2024-03-20T15:30:45+03:00")
        
        JSON-RPC запрос:
        {
            "jsonrpc": "2.0",
            "method": "get_date",
            "id": 1
        }
        
        JSON-RPC ответ:
        {
            "jsonrpc": "2.0",
            "result": {
                "date": "2024-03-20T15:30:45+03:00"
            },
            "id": 1
        }
    """
```

## Особенности реализации

1. Использует стандартный модуль `datetime` для работы с датой и временем
2. Дата возвращается в формате ISO 8601: YYYY-MM-DDThh:mm:ss±hh:mm
3. Временная зона определяется автоматически из системных настроек
4. Микросекунды не включаются в результат

## Примеры использования

### Python
```python
result = await get_date()
print(result.date)  # 2024-03-20T15:30:45+03:00
```

### HTTP REST
```http
POST /api/v1/commands/get_date
Content-Type: application/json

{}

Response:
{
    "date": "2024-03-20T15:30:45+03:00"
}
```

### JSON-RPC через WebSocket
```javascript
// Запрос
{
    "jsonrpc": "2.0",
    "method": "get_date",
    "id": 1
}

// Ответ
{
    "jsonrpc": "2.0",
    "result": {
        "date": "2024-03-20T15:30:45+03:00"
    },
    "id": 1
}
```

## Форматы даты

1. **Основной формат**: `YYYY-MM-DDThh:mm:ss±hh:mm`
   - YYYY: год (4 цифры)
   - MM: месяц (2 цифры)
   - DD: день (2 цифры)
   - T: разделитель даты и времени
   - hh: часы (2 цифры)
   - mm: минуты (2 цифры)
   - ss: секунды (2 цифры)
   - ±: знак смещения временной зоны
   - hh:mm: смещение временной зоны

2. **Примеры**:
   - `2024-03-20T15:30:45+03:00` (Москва)
   - `2024-03-20T12:30:45+00:00` (UTC)
   - `2024-03-20T07:30:45-05:00` (Нью-Йорк) 