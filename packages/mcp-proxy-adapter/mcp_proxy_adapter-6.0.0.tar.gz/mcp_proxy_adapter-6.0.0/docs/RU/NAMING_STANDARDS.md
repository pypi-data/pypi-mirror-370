# Стандарты именования и расположения файлов

## Структура проекта

```
mcp_microservice/
├── __init__.py
├── api/                    # API интерфейсы
│   ├── __init__.py
│   ├── rest/              # REST API эндпоинты
│   └── jsonrpc/           # JSON-RPC обработчики
├── commands/              # Команды
│   ├── __init__.py
│   └── {command_name}_command.py
├── core/                  # Ядро системы
│   ├── __init__.py
│   ├── registry.py       # Реестр команд
│   ├── errors.py         # Обработка ошибок
│   └── types.py          # Базовые типы
├── models/               # Модели данных
│   ├── __init__.py
│   └── results.py        # Базовые классы результатов
└── utils/               # Вспомогательные функции
    └── __init__.py

tests/
├── __init__.py
├── conftest.py
└── commands/            # Тесты команд
    └── test_{command_name}_command.py

docs/
├── EN/                 # Документация на английском
└── RU/                 # Документация на русском
    ├── commands/       # Документация команд
    │   └── {command_name}_command.md
    └── api/            # Документация API
```

## Стандарты именования

### 1. Файлы Python

#### Команды
- Формат: `{command_name}_command.py`
- Примеры:
  ```
  get_status_command.py
  create_user_command.py
  delete_file_command.py
  ```

#### Тесты
- Формат: `test_{module_name}.py`
- Примеры:
  ```
  test_get_status_command.py
  test_registry.py
  test_errors.py
  ```

#### Модули
- Существительные в единственном числе
- Нижний регистр
- Разделитель `_`
- Примеры:
  ```
  registry.py
  error_handler.py
  type_converter.py
  ```

### 2. Классы Python

#### Результаты команд
- Формат: `{CommandName}Result`
- PascalCase
- Примеры:
  ```python
  class GetStatusResult(CommandResult):
  class CreateUserResult(CommandResult):
  class DeleteFileResult(CommandResult):
  ```

#### Исключения
- Суффикс `Error`
- PascalCase
- Примеры:
  ```python
  class ValidationError(Exception):
  class CommandNotFoundError(Exception):
  class ExecutionError(Exception):
  ```

### 3. Методы и функции

#### Команды
- Формат: `{command_name}`
- snake_case
- Глагол + существительное
- Примеры:
  ```python
  async def get_status():
  async def create_user():
  async def delete_file():
  ```

#### Внутренние методы
- Префикс `_` для protected
- Префикс `__` для private
- snake_case
- Примеры:
  ```python
  def _validate_input():
  def __prepare_context():
  ```

### 4. Документация

#### Файлы документации
- Формат: `{TOPIC_NAME}.md`
- UPPER_CASE
- Примеры:
  ```
  API_REFERENCE.md
  COMMAND_GUIDE.md
  ERROR_CODES.md
  ```

#### Документация команд
- Формат: `{command_name}_command.md`
- snake_case
- Примеры:
  ```
  get_status_command.md
  create_user_command.md
  ```

## Правила расположения кода в файле

### 1. Файл команды
```python
"""Описание модуля"""

# Импорты из стандартной библиотеки
import datetime
import uuid

# Импорты сторонних библиотек
from pydantic import BaseModel

# Импорты проекта
from mcp_proxy_adapter.core import CommandResult
from mcp_proxy_adapter.registry import registry

# Типы и константы
TIMEOUT = 30
MAX_RETRIES = 3

# Класс результата
@dataclass
class CommandResult:
    pass

# Вспомогательные функции
def _helper_function():
    pass

# Команда
@registry.command
async def command_name():
    pass
```

### 2. Файл теста
```python
"""Тесты для модуля"""

# Импорты
import pytest

# Фикстуры
@pytest.fixture
def fixture_name():
    pass

# Тесты успешных сценариев
def test_success_case():
    pass

# Тесты ошибок
def test_error_case():
    pass
```

## Рекомендации

1. **Именование переменных**
   - Использовать существительные
   - Избегать сокращений
   - Использовать типизацию

2. **Документация**
   - Docstring для всех публичных элементов
   - Примеры использования
   - Описание параметров и возвращаемых значений

3. **Организация импортов**
   - Группировка по типу
   - Сортировка по алфавиту
   - Пустая строка между группами

4. **Типизация**
   - Аннотации типов для всех параметров
   - Аннотации возвращаемых значений
   - Использование typing для сложных типов 