# Улучшение кастомизации OpenAPI

## Проблема

В текущей реализации фреймворка MCP Proxy Adapter параметры OpenAPI схемы (такие как `title`, `description`, `version`) захардкожены в базовой схеме `mcp_proxy_adapter/schemas/openapi_schema.json`:

```json
"info": {
  "title": "MCP Microservice API",
  "description": "API для выполнения команд микросервиса",
  "version": "1.0.0"
}
```

Это ограничивает возможности кастомизации при использовании фреймворка в конкретных проектах.

Кроме того, текущая реализация не содержит полных метаданных для инструментов и команды help, что затрудняет понимание доступных команд и их использования.

## Предлагаемое решение

1. Реализовать возможность настройки параметров OpenAPI схемы через функцию `create_app()` и передавать их в генератор OpenAPI схемы.

2. Улучшить генерацию метаданных для инструментов и усовершенствовать команду help для предоставления более полной информации.

## План реализации

### 1. Кастомизация OpenAPI

1. Модифицировать функцию `create_app()` для принятия параметров OpenAPI:

```python
def create_app(
    title: str = "MCP Microservice API",
    description: str = "API для выполнения команд микросервиса",
    version: str = "1.0.0",
    **kwargs
) -> FastAPI:
    """
    Creates and configures FastAPI application.

    Args:
        title: API title for OpenAPI schema
        description: API description for OpenAPI schema
        version: API version for OpenAPI schema
        **kwargs: Additional parameters for FastAPI

    Returns:
        Configured FastAPI application.
    """
    # Create application
    app = FastAPI(
        title=title,
        description=description,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        **kwargs
    )
    
    # ... остальной код ...
```

2. Модифицировать генератор OpenAPI схемы для использования параметров из FastAPI приложения:

```python
def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    Create a custom OpenAPI schema for the FastAPI application.
    
    Args:
        app: The FastAPI application.
        
    Returns:
        Dict containing the custom OpenAPI schema.
    """
    generator = CustomOpenAPIGenerator()
    openapi_schema = generator.generate(
        title=app.title,
        description=app.description,
        version=app.version
    )
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    
    return openapi_schema
```

3. Обновить класс `CustomOpenAPIGenerator` для учета параметров OpenAPI:

```python
def generate(self, title: str = None, description: str = None, version: str = None) -> Dict[str, Any]:
    """
    Generate the complete OpenAPI schema compatible with MCP-Proxy.
    
    Args:
        title: API title for OpenAPI schema
        description: API description for OpenAPI schema
        version: API version for OpenAPI schema
        
    Returns:
        Dict containing the complete OpenAPI schema.
    """
    # Deep copy the base schema to avoid modifying it
    schema = deepcopy(self.base_schema)
    
    # Update info if provided
    if title:
        schema["info"]["title"] = title
    if description:
        schema["info"]["description"] = description
    if version:
        schema["info"]["version"] = version
    
    # Add commands to schema
    self._add_commands_to_schema(schema)
    
    logger.info(f"Generated OpenAPI schema with {len(registry.get_all_commands())} commands")
    
    return schema
```

### 2. Улучшение команды Help и метаданных инструмента

1. Улучшить класс `HelpCommand` для предоставления более полной информации:

```python
class HelpCommand(Command):
    """
    Command for getting help information about available commands.
    
    Usage:
    - Without parameters: Returns a list of available commands with brief descriptions and usage instructions
    - With cmdname parameter: Returns detailed information about the specified command
    """
    
    # ... существующий код ...
    
    async def execute(self, cmdname: Optional[str] = None) -> HelpResult:
        # ... существующий код ...
        
        # При получении списка всех команд добавить информацию об инструменте
        # и о способах использования help
        if not cmdname:
            commands_info = {}
            
            # Добавляем мета-информацию о команде help и инструменте
            commands_info["help_usage"] = {
                "description": "Получение информации о командах",
                "examples": [
                    {"command": "help", "description": "Список всех доступных команд"},
                    {"command": "help", "params": {"cmdname": "command_name"}, "description": "Подробная информация о конкретной команде"}
                ]
            }
            
            commands_info["tool_info"] = {
                "name": "MCP-Proxy API Service",
                "description": "JSON-RPC API для выполнения команд микросервиса",
                "version": "1.0.0"
            }
            
            # Добавляем информацию о командах
            for name, cmd_class in commands.items():
                # ... существующий код ...
                # Добавляем краткую информацию об использовании
                commands_info[name] = {
                    "description": description,
                    "summary": _get_first_line(description),
                    "params_count": len(cmd_class.get_param_info())
                }
            
            return HelpResult(commands_info=commands_info)
```

2. Улучшить класс `HelpResult` для поддержки расширенных метаданных:

```python
class HelpResult(CommandResult):
    # ... существующий код ...
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary.
        
        Returns:
            Dict[str, Any]: Result as dictionary
        """
        if self.command_info:
            return {
                "cmdname": self.command_info["name"],
                "info": {
                    "description": self.command_info["description"],
                    "summary": _get_first_line(self.command_info["description"]),
                    "params": self.command_info["params"],
                    # Добавить пример использования команды
                    "examples": _generate_examples(self.command_info)
                }
            }
        
        # Для списка всех команд включаем метаинформацию
        result = {"commands": {}}
        
        # Копируем специальные мета-поля
        if "help_usage" in self.commands_info:
            result["help_usage"] = self.commands_info.pop("help_usage")
        
        if "tool_info" in self.commands_info:
            result["tool_info"] = self.commands_info.pop("tool_info")
        
        # Добавляем информацию о доступных командах
        result["commands"] = self.commands_info
        result["total"] = len(self.commands_info)
        
        # Добавляем подсказку о формате вызова help с параметром
        result["note"] = "Для получения информации о конкретной команде вызовите help с параметром: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Поддерживается только параметр 'cmdname'. Вызов 'help <command>' (с пробелом) НЕ поддерживается."
        
        return result
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        # ... обновить схему для поддержки расширенных метаданных ...
```

3. Добавить утилитные функции для форматирования информации:

```python
def _get_first_line(text: str) -> str:
    """
    Extract the first non-empty line from text.
    """
    if not text:
        return ""
    
    lines = [line.strip() for line in text.strip().split("\n")]
    return next((line for line in lines if line), "")


def _generate_examples(command_info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate usage examples for a command.
    """
    name = command_info["name"]
    params = command_info["params"]
    
    # Простой пример без параметров
    examples = [{"command": name}]
    
    # Пример с обязательными параметрами
    required_params = {k: v for k, v in params.items() if v.get("required", False)}
    if required_params:
        example_params = {}
        for param_name, param_info in required_params.items():
            # Генерируем примерное значение на основе типа
            param_type = param_info.get("type", "")
            if "string" in param_type.lower():
                example_params[param_name] = f"example_{param_name}"
            elif "int" in param_type.lower():
                example_params[param_name] = 123
            elif "float" in param_type.lower():
                example_params[param_name] = 123.45
            elif "bool" in param_type.lower():
                example_params[param_name] = True
            else:
                example_params[param_name] = f"value_{param_name}"
        
        examples.append({"command": name, "params": example_params})
    
    return examples
```

4. Расширить метод `get_command_info` в классе `CommandRegistry`:

```python
def get_command_info(self, command_name: str) -> Dict[str, Any]:
    """
    Gets information about a command.

    Args:
        command_name: Command name.

    Returns:
        Dictionary with command information.

    Raises:
        NotFoundError: If command is not found.
    """
    command_class = self.get_command(command_name)
    
    # Получаем docstring и форматируем его
    doc = command_class.__doc__ or ""
    description = inspect.cleandoc(doc) if doc else ""
    
    param_info = command_class.get_param_info()
    
    # Добавляем больше информации для каждого параметра
    for param_name, param in param_info.items():
        # Извлекаем информацию из docstring, если есть
        param_doc = _extract_param_doc(doc, param_name)
        if param_doc:
            param["description"] = param_doc
    
    return {
        "name": command_name,
        "description": description,
        "params": param_info,
        "schema": command_class.get_schema(),
        "result_schema": command_class.get_result_schema()
    }
```

5. Улучшить OpenAPI схему с дополнительной информацией об инструменте:

```python
def _add_commands_to_schema(self, schema: Dict[str, Any]) -> None:
    # ... существующий код ...
    
    # Добавляем описание инструмента в description операции
    endpoint_path = "/cmd"
    if endpoint_path in schema["paths"]:
        cmd_endpoint = schema["paths"][endpoint_path]["post"]
        
        # Расширяем описание эндпоинта
        cmd_endpoint["description"] = """
        Выполняет команду через JSON-RPC протокол.
        
        Этот эндпоинт поддерживает два формата запросов:
        1. Простой формат команды: {"command": "command_name", "params": {...}}
        2. Формат JSON-RPC: {"jsonrpc": "2.0", "method": "command_name", "params": {...}, "id": 123}
        
        Для получения справки о доступных командах вызовите:
        - {"command": "help"} - Список всех доступных команд
        - {"command": "help", "params": {"cmdname": "command_name"}} - Подробная информация о конкретной команде
        """
```

## Ожидаемые результаты

### 1. Улучшенный ответ команды help без параметров:

```json
{
  "help_usage": {
    "description": "Получение информации о командах",
    "examples": [
      {"command": "help", "description": "Список всех доступных команд"},
      {"command": "help", "params": {"cmdname": "command_name"}, "description": "Подробная информация о конкретной команде"}
    ]
  },
  "tool_info": {
    "name": "MCP-Proxy API Service",
    "description": "JSON-RPC API для выполнения команд микросервиса",
    "version": "1.0.0"
  },
  "commands": {
    "help": {
      "summary": "Команда для получения справочной информации о доступных командах",
      "description": "Команда для получения справочной информации о доступных командах.\n\nИспользование:\n- Без параметров: Возвращает список доступных команд...",
      "params_count": 1
    },
    ...другие команды...
  },
  "total": 4,
  "note": "Для получения информации о конкретной команде вызовите help с параметром: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Поддерживается только параметр 'cmdname'. Вызов 'help <command>' (с пробелом) НЕ поддерживается."
}
```

### 2. Улучшенный ответ команды help с параметром:

```json
{
  "cmdname": "echo",
  "info": {
    "description": "Команда, возвращающая входное сообщение.\n\nЭта команда демонстрирует простую обработку параметров.",
    "summary": "Команда, возвращающая входное сообщение",
    "params": {
      "message": {
        "name": "message",
        "required": true,
        "type": "str",
        "description": "Сообщение для возврата"
      }
    },
    "examples": [
      {"command": "echo"},
      {"command": "echo", "params": {"message": "example_message"}}
    ]
  }
}
```

## Преимущества

1. Более гибкая настройка фреймворка для конкретных проектов
2. Возможность указать собственные заголовок, описание и версию API
3. Лучшее соответствие принципам проектирования фреймворков
4. Улучшенный пользовательский опыт при работе с API
5. Расширенная документация и возможности самоописания
6. Лучшие метаданные инструмента для интеграции с другими системами

## Пример использования после изменений

```python
from mcp_proxy_adapter import create_app

# Создание приложения с кастомными параметрами OpenAPI
app = create_app(
    title="Мой микросервис",
    description="API для работы с текстовыми данными",
    version="2.1.3"
) 