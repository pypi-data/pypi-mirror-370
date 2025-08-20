# get_date Command

## Description
Returns the current date and time in ISO 8601 format with timezone.

## Result

```python
@dataclass
class GetDateResult(CommandResult):
    """Result of getting current date"""
    date: str  # Date in ISO 8601 format

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
                    "description": "Current date and time in ISO 8601 format",
                    "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}[+-]\\d{2}:?\\d{2}$"
                }
            }
        }
```

## Command

```python
@registry.command
async def get_date() -> GetDateResult:
    """
    Returns current date and time in ISO 8601 format
    
    Returns:
        GetDateResult: Result with date in ISO 8601 format
        
    Examples:
        >>> await get_date()
        GetDateResult(date="2024-03-20T15:30:45+03:00")
        
        JSON-RPC request:
        {
            "jsonrpc": "2.0",
            "method": "get_date",
            "id": 1
        }
        
        JSON-RPC response:
        {
            "jsonrpc": "2.0",
            "result": {
                "date": "2024-03-20T15:30:45+03:00"
            },
            "id": 1
        }
    """
```

## Implementation Details

1. Uses standard `datetime` module for date and time handling
2. Date is returned in ISO 8601 format: YYYY-MM-DDThh:mm:ss±hh:mm
3. Timezone is automatically determined from system settings
4. Microseconds are not included in the result

## Usage Examples

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

### JSON-RPC via WebSocket
```javascript
// Request
{
    "jsonrpc": "2.0",
    "method": "get_date",
    "id": 1
}

// Response
{
    "jsonrpc": "2.0",
    "result": {
        "date": "2024-03-20T15:30:45+03:00"
    },
    "id": 1
}
```

## Date Formats

1. **Main format**: `YYYY-MM-DDThh:mm:ss±hh:mm`
   - YYYY: year (4 digits)
   - MM: month (2 digits)
   - DD: day (2 digits)
   - T: date and time separator
   - hh: hours (2 digits)
   - mm: minutes (2 digits)
   - ss: seconds (2 digits)
   - ±: timezone offset sign
   - hh:mm: timezone offset

2. **Examples**:
   - `2024-03-20T15:30:45+03:00` (Moscow)
   - `2024-03-20T12:30:45+00:00` (UTC)
   - `2024-03-20T07:30:45-05:00` (New York) 