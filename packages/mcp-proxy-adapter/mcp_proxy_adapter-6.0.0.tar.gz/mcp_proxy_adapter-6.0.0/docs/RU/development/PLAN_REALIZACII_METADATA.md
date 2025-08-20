# План реализации улучшения метаданных команд

## Общий план

1. Добавление метода `get_metadata()` в базовый класс Command
2. Расширение CommandRegistry для доступа к метаданным 
3. Обновление HelpCommand для использования новых метаданных
4. Обновление HelpResult для структурированного вывода
5. Тестирование изменений
6. Обновление документации

## Детализация шагов

### Шаг 1: Модификация базового класса Command

**Файл:** `mcp_proxy_adapter/commands/base.py`

1. Импортировать необходимые модули:
   ```python
   import inspect
   from typing import Dict, Any, List, Optional
   ```

2. Добавить класс-метод `get_metadata()`:
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
   ```

3. Добавить приватный метод для генерации примеров:
   ```python
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

### Шаг 2: Расширение CommandRegistry

**Файл:** `mcp_proxy_adapter/commands/command_registry.py`

1. Добавить метод для получения метаданных конкретной команды:
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
   ```

2. Добавить метод для получения метаданных всех команд:
   ```python
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

### Шаг 3: Обновление HelpCommand

**Файл:** `mcp_proxy_adapter/commands/help_command.py`

1. Обновить метод execute для использования новых метаданных:
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

### Шаг 4: Обновление HelpResult

**Файл:** `mcp_proxy_adapter/commands/help_command.py`

1. Обновить класс HelpResult для работы с новой структурой метаданных:
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

### Шаг 5: Тестирование изменений

1. Создать тест для проверки метаданных команды:
   **Файл:** `tests/commands/test_command_metadata.py`
   ```python
   import pytest
   from mcp_proxy_adapter.commands.base import Command
   from mcp_proxy_adapter.commands.command_registry import CommandRegistry
   
   # Тестовая команда для проверки метаданных
   class TestCommand(Command):
       """
       Тестовая команда для проверки метаданных.
       
       Вторая строка описания.
       """
       
       name = "test_command"
       
       def __init__(self, param1: str, param2: int = 0, param3: bool = False):
           """
           Инициализация тестовой команды.
           
           Args:
               param1: Первый параметр (строка)
               param2: Второй параметр (число), по умолчанию 0
               param3: Третий параметр (флаг), по умолчанию False
           """
           self.param1 = param1
           self.param2 = param2
           self.param3 = param3
       
       async def execute(self) -> dict:
           """Выполнение команды"""
           return {"result": f"{self.param1}-{self.param2}-{self.param3}"}
   
   def test_command_metadata():
       """Тест получения метаданных команды"""
       metadata = TestCommand.get_metadata()
       
       # Проверка базовых полей
       assert metadata["name"] == "test_command"
       assert "Тестовая команда для проверки метаданных" in metadata["summary"]
       assert "Вторая строка описания" in metadata["description"]
       
       # Проверка информации о параметрах
       assert "param1" in metadata["params"]
       assert metadata["params"]["param1"]["required"] is True
       assert metadata["params"]["param2"]["required"] is False
       assert metadata["params"]["param2"]["default"] == 0
       
       # Проверка примеров
       assert len(metadata["examples"]) > 0
       assert any(example.get("command") == "test_command" for example in metadata["examples"])
   
   def test_command_registry_metadata():
       """Тест получения метаданных из реестра команд"""
       registry = CommandRegistry()
       registry.register(TestCommand)
       
       # Проверка получения метаданных одной команды
       metadata = registry.get_command_metadata("test_command")
       assert metadata["name"] == "test_command"
       
       # Проверка получения метаданных всех команд
       all_metadata = registry.get_all_metadata()
       assert "test_command" in all_metadata
       assert all_metadata["test_command"]["name"] == "test_command"
   ```

2. Создать тест для обновленной команды help:
   **Файл:** `tests/commands/test_help_command.py`
   ```python
   import pytest
   from mcp_proxy_adapter.commands.help_command import HelpCommand, HelpResult
   from mcp_proxy_adapter.commands.command_registry import CommandRegistry
   from mcp_proxy_adapter.commands.base import Command
   
   # Создаем тестовые команды
   class TestCommand1(Command):
       """Тестовая команда 1"""
       name = "test1"
       
       async def execute(self) -> dict:
           return {"result": "test1"}
   
   class TestCommand2(Command):
       """Тестовая команда 2"""
       name = "test2"
       
       async def execute(self, param: str) -> dict:
           return {"result": param}
   
   @pytest.fixture
   def registry():
       """Фикстура для создания реестра с тестовыми командами"""
       registry = CommandRegistry()
       registry.register(TestCommand1)
       registry.register(TestCommand2)
       registry.register(HelpCommand)
       return registry
   
   @pytest.mark.asyncio
   async def test_help_command_without_params(registry):
       """Тест команды help без параметров"""
       help_command = HelpCommand()
       result = await help_command.execute()
       
       # Проверка структуры ответа
       data = result.to_dict()
       assert "tool_info" in data
       assert "commands" in data
       assert "total" in data
       assert "note" in data
       
       # Проверка информации о командах
       assert "test1" in data["commands"]
       assert "test2" in data["commands"]
       assert "help" in data["commands"]
       
       # Проверка количества команд
       assert data["total"] == 3
   
   @pytest.mark.asyncio
   async def test_help_command_with_cmdname(registry):
       """Тест команды help с параметром cmdname"""
       help_command = HelpCommand()
       result = await help_command.execute(cmdname="test2")
       
       # Проверка структуры ответа
       data = result.to_dict()
       assert "cmdname" in data
       assert "info" in data
       
       # Проверка информации о команде
       assert data["cmdname"] == "test2"
       assert "description" in data["info"]
       assert "params" in data["info"]
       assert "examples" in data["info"]
       
       # Проверка параметров
       assert "param" in data["info"]["params"]
   ```

### Шаг 6: Обновление документации

1. Добавить информацию о новой функциональности в руководство разработчика
2. Обновить примеры использования команды help
3. Добавить информацию о новой функциональности в руководство по API

## График реализации

1. **День 1**: Модификация базового класса Command и CommandRegistry
2. **День 2**: Обновление HelpCommand и HelpResult
3. **День 3**: Тестирование и отладка
4. **День 4**: Обновление документации и финальная проверка

## Критерии успешной реализации

1. Все классы Command имеют метод get_metadata()
2. CommandRegistry обеспечивает доступ к метаданным команд
3. Команда help предоставляет расширенную информацию о командах
4. Все тесты успешно проходят
5. Документация обновлена и соответствует реализации 