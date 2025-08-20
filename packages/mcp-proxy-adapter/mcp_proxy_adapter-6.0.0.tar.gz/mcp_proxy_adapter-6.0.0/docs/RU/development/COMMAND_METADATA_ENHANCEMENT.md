# Улучшение метаданных команд

## Проблема

В настоящее время реестр команд хранит классы команд, но не предоставляет удобного способа доступа к метаданным команды без создания экземпляра команды. Метаданные о командах должны быть более доступны и структурированы для:

1. Улучшения документации
2. Предоставления AI-инструментам подробной информации о доступных командах
3. Улучшения результатов работы команды help
4. Обеспечения лучших возможностей интроспекции

## Предлагаемое решение

Улучшить классы Command и CommandRegistry для поддержки комплексного извлечения метаданных:

1. Добавить класс-метод `get_metadata()` в базовый класс Command
2. Обновить CommandRegistry для обеспечения доступа к метаданным команд
3. Сохранить существующее хранилище классов команд для обратной совместимости

## План реализации

### 1. Улучшение базового класса Command

Добавить новый класс-метод `get_metadata()` в базовый класс Command:

```python
@classmethod
def get_metadata(cls) -> Dict[str, Any]:
    """
    Возвращает полные метаданные о команде.
    
    Предоставляет единую точку доступа ко всем метаданным команды.
    
    Returns:
        Dict с метаданными команды
    """
    # Получение и форматирование docstring
    doc = cls.__doc__ or ""
    description = inspect.cleandoc(doc) if doc else ""
    
    # Извлечение первой строки для краткого описания
    summary = description.split("\n")[0] if description else ""
    
    # Получение информации о параметрах
    param_info = cls.get_param_info()
    
    # Генерация примеров на основе параметров
    examples = cls._generate_examples(param_info)
    
    return {
        "name": cls.name,
        "summary": summary,
        "description": description,
        "params": param_info,
        "examples": examples,
        "schema": cls.get_schema(),
        "result_schema": cls.get_result_schema(),
        "result_class": cls.result_class.__name__ if hasattr(cls, "result_class") else None,
    }

@classmethod
def _generate_examples(cls, params: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Генерирует примеры использования команды на основе её параметров.
    
    Args:
        params: Информация о параметрах команды
        
    Returns:
        Список примеров
    """
    examples = []
    
    # Простой пример без параметров, если все параметры опциональны
    if not any(param.get("required", False) for param in params.values()):
        examples.append({
            "command": cls.name,
            "description": f"Вызов команды {cls.name} без параметров"
        })
    
    # Пример со всеми обязательными параметрами
    required_params = {k: v for k, v in params.items() if v.get("required", False)}
    if required_params:
        example_params = {}
        for param_name, param_info in required_params.items():
            # Генерация подходящего примера значения на основе типа параметра
            param_type = param_info.get("type", "")
            if "str" in param_type.lower():
                example_params[param_name] = f"example_{param_name}"
            elif "int" in param_type.lower():
                example_params[param_name] = 123
            elif "float" in param_type.lower():
                example_params[param_name] = 123.45
            elif "bool" in param_type.lower():
                example_params[param_name] = True
            else:
                example_params[param_name] = f"value_for_{param_name}"
        
        examples.append({
            "command": cls.name,
            "params": example_params,
            "description": f"Вызов команды {cls.name} с обязательными параметрами"
        })
    
    # Добавление примера со всеми параметрами, если есть опциональные
    optional_params = {k: v for k, v in params.items() if not v.get("required", False)}
    if optional_params and required_params:
        full_example_params = dict(example_params) if 'example_params' in locals() else {}
        
        for param_name, param_info in optional_params.items():
            # Получение значения по умолчанию или генерация подходящего примера
            if "default" in param_info:
                full_example_params[param_name] = param_info["default"]
            else:
                # Генерация подходящего примера значения на основе типа параметра
                param_type = param_info.get("type", "")
                if "str" in param_type.lower():
                    full_example_params[param_name] = f"optional_{param_name}"
                elif "int" in param_type.lower():
                    full_example_params[param_name] = 456
                elif "float" in param_type.lower():
                    full_example_params[param_name] = 45.67
                elif "bool" in param_type.lower():
                    full_example_params[param_name] = False
                else:
                    full_example_params[param_name] = f"optional_value_for_{param_name}"
        
        examples.append({
            "command": cls.name,
            "params": full_example_params,
            "description": f"Вызов команды {cls.name} со всеми параметрами"
        })
    
    return examples
```

### 2. Улучшение CommandRegistry

Обновить CommandRegistry для обеспечения доступа к метаданным команд:

```python
def get_command_metadata(self, command_name: str) -> Dict[str, Any]:
    """
    Получить полные метаданные для команды.
    
    Args:
        command_name: Имя команды
        
    Returns:
        Dict с метаданными команды
        
    Raises:
        NotFoundError: Если команда не найдена
    """
    command_class = self.get_command(command_name)
    return command_class.get_metadata()

def get_all_metadata(self) -> Dict[str, Dict[str, Any]]:
    """
    Получить метаданные для всех зарегистрированных команд.
    
    Returns:
        Dict с именами команд в качестве ключей и метаданными в качестве значений
    """
    metadata = {}
    for name, command_class in self._commands.items():
        metadata[name] = command_class.get_metadata()
    return metadata
```

### 3. Обновление команды Help

Улучшить HelpCommand для использования новых метаданных:

```python
async def execute(self, cmdname: Optional[str] = None) -> HelpResult:
    """
    Выполнить команду help.
    
    Args:
        cmdname: Имя команды, о которой нужно получить информацию (опционально)
        
    Returns:
        HelpResult: Результат выполнения команды help
        
    Raises:
        NotFoundError: Если указанная команда не найдена
    """
    # Если cmdname указан, вернуть информацию о конкретной команде
    if cmdname:
        try:
            # Получить метаданные команды из реестра
            command_metadata = registry.get_command_metadata(cmdname)
            return HelpResult(command_info=command_metadata)
        except NotFoundError:
            # Если команда не найдена, вызвать ошибку
            raise NotFoundError(f"Команда '{cmdname}' не найдена")
    
    # В противном случае вернуть информацию обо всех доступных командах
    # и метаданные инструмента
    
    # Получить метаданные для всех команд
    all_metadata = registry.get_all_metadata()
    
    # Подготовить формат ответа с метаданными инструмента
    result = {
        "tool_info": {
            "name": "MCP-Proxy API Service",
            "description": "JSON-RPC API для выполнения команд микросервиса",
            "version": "1.0.0"
        },
        "help_usage": {
            "description": "Получить информацию о командах",
            "examples": [
                {"command": "help", "description": "Список всех доступных команд"},
                {"command": "help", "params": {"cmdname": "command_name"}, "description": "Получить подробную информацию о конкретной команде"}
            ]
        },
        "commands": {}
    }
    
    # Добавить краткую информацию о командах
    for name, metadata in all_metadata.items():
        result["commands"][name] = {
            "summary": metadata["summary"],
            "params_count": len(metadata["params"])
        }
    
    return HelpResult(commands_info=result)
```

### 4. Обновление класса HelpResult

```python
class HelpResult(CommandResult):
    """
    Результат выполнения команды help.
    """
    
    def __init__(self, commands_info: Optional[Dict[str, Any]] = None, command_info: Optional[Dict[str, Any]] = None):
        """
        Инициализация результата команды help.
        
        Args:
            commands_info: Информация обо всех командах (для запроса без параметров)
            command_info: Информация о конкретной команде (для запроса с параметром cmdname)
        """
        self.commands_info = commands_info
        self.command_info = command_info
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразовать результат в словарь.
        
        Returns:
            Dict[str, Any]: Результат в виде словаря
        """
        if self.command_info:
            return {
                "cmdname": self.command_info["name"],
                "info": {
                    "description": self.command_info["description"],
                    "summary": self.command_info["summary"],
                    "params": self.command_info["params"],
                    "examples": self.command_info["examples"]
                }
            }
        
        # Для списка всех команд, вернуть как есть (уже отформатировано)
        result = self.commands_info.copy()
        
        # Добавить общее количество и примечание по использованию
        result["total"] = len(result["commands"])
        result["note"] = "Чтобы получить подробную информацию о конкретной команде, вызовите help с параметром: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Поддерживается только параметр 'cmdname'."
        
        return result
```

## Ожидаемые результаты

### 1. Подробная информация о команде

```json
{
  "cmdname": "echo",
  "info": {
    "description": "Команда, которая возвращает входное сообщение.\n\nЭта команда демонстрирует простую обработку параметров.",
    "summary": "Команда, которая возвращает входное сообщение",
    "params": {
      "message": {
        "name": "message",
        "required": true,
        "type": "str",
        "description": "Сообщение для возврата"
      }
    },
    "examples": [
      {
        "command": "echo",
        "params": {"message": "example_message"},
        "description": "Вызов команды echo с обязательными параметрами"
      }
    ]
  }
}
```

### 2. Улучшенный список команд с метаданными

```json
{
  "tool_info": {
    "name": "MCP-Proxy API Service",
    "description": "JSON-RPC API для выполнения команд микросервиса",
    "version": "1.0.0"
  },
  "help_usage": {
    "description": "Получить информацию о командах",
    "examples": [
      {"command": "help", "description": "Список всех доступных команд"},
      {"command": "help", "params": {"cmdname": "command_name"}, "description": "Получить подробную информацию о конкретной команде"}
    ]
  },
  "commands": {
    "help": {
      "summary": "Команда для получения справочной информации о доступных командах",
      "params_count": 1
    },
    "echo": {
      "summary": "Команда, которая возвращает входное сообщение",
      "params_count": 1
    },
    "math": {
      "summary": "Команда для выполнения базовых математических операций",
      "params_count": 3
    }
  },
  "total": 3,
  "note": "Чтобы получить подробную информацию о конкретной команде, вызовите help с параметром: POST /cmd {\"command\": \"help\", \"params\": {\"cmdname\": \"<command_name>\"}}. Поддерживается только параметр 'cmdname'."
}
```

## Преимущества

1. Более полные метаданные команд
2. Улучшенные возможности документирования
3. Расширенный вывод команды help с примерами использования
4. Улучшенное самоописание API
5. Лучшая поддержка интеграции с AI-инструментами
6. Более четкое разделение между метаданными и реализацией 