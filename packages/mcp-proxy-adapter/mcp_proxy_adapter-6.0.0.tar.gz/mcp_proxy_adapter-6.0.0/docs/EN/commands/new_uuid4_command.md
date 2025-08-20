# new_uuid4 Command

## Description
Generates a new UUID version 4 (random).

## Result

```python
@dataclass
class NewUuid4Result(CommandResult):
    """Result of UUID4 generation"""
    uuid: str  # UUID in string format

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
                    "description": "Generated UUID4 in string format",
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
                }
            }
        }
```

## Command

```python
@registry.command
async def new_uuid4() -> NewUuid4Result:
    """
    Generates a new UUID version 4 (random)
    
    Returns:
        NewUuid4Result: Result with UUID in string format
        
    Examples:
        >>> await new_uuid4()
        NewUuid4Result(uuid="123e4567-e89b-12d3-a456-426614174000")
        
        JSON-RPC request:
        {
            "jsonrpc": "2.0",
            "method": "new_uuid4",
            "id": 1
        }
        
        JSON-RPC response:
        {
            "jsonrpc": "2.0",
            "result": {
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            },
            "id": 1
        }
    """
```

## Implementation Details

1. Uses standard `uuid` module for UUID4 generation
2. UUID is always returned in lowercase
3. UUID format complies with RFC 4122
4. Generation uses cryptographically secure random number generator

## Usage Examples

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

### JSON-RPC via WebSocket
```javascript
// Request
{
    "jsonrpc": "2.0",
    "method": "new_uuid4",
    "id": 1
}

// Response
{
    "jsonrpc": "2.0",
    "result": {
        "uuid": "123e4567-e89b-12d3-a456-426614174000"
    },
    "id": 1
}
``` 