# Команда Load

## Описание

Команда `load` позволяет динамически загружать модули команд из локальной файловой системы или удаленных HTTP/HTTPS URL. Эта команда автоматически определяет, является ли источник локальным путем или URL, и обрабатывает загрузку соответствующим образом.

Для локальных путей команда загружает Python модули, заканчивающиеся на '_command.py'. Для URL команда загружает Python код и загружает его как временный модуль.

Загруженные команды регистрируются в реестре команд и становятся немедленно доступными для выполнения. Только команды, которые наследуют от базового класса Command и правильно структурированы, будут загружены и зарегистрированы.

## Соображения безопасности

- Локальные пути проверяются на существование и правильное именование
- URL загружаются с защитой по таймауту
- Временные файлы автоматически очищаются после загрузки
- Принимаются только файлы, заканчивающиеся на '_command.py'

## Результат

```python
class LoadResult(SuccessResult):
    def __init__(self, success: bool, commands_loaded: int, loaded_commands: list, source: str, error: Optional[str] = None):
        data = {
            "success": success,
            "commands_loaded": commands_loaded,
            "loaded_commands": loaded_commands,
            "source": source
        }
        if error:
            data["error"] = error
```

## Команда

```python
class LoadCommand(Command):
    name = "load"
    result_class = LoadResult
    
    async def execute(self, source: str, **kwargs) -> LoadResult:
        """
        Выполнить команду загрузки.
        
        Args:
            source: Путь к источнику или URL для загрузки команды
            **kwargs: Дополнительные параметры
            
        Returns:
            LoadResult: Результат команды загрузки
        """
```

## Детали реализации

Команда использует следующую логику:

1. **Определение источника**: Парсит строку источника для определения, является ли она URL или локальным путем
2. **Локальная загрузка**: Для локальных путей проверяет существование файла и соглашение об именовании
3. **Удаленная загрузка**: Для URL загружает содержимое с таймаутом и создает временный файл
4. **Загрузка модуля**: Использует importlib Python для динамической загрузки модуля
5. **Регистрация команд**: Регистрирует найденные классы команд в реестре команд
6. **Очистка**: Удаляет временные файлы для удаленной загрузки

## Примеры использования

### Python

```python
# Загрузка из локального файла
result = await execute_command("load", {"source": "./my_command.py"})

# Загрузка из URL
result = await execute_command("load", {"source": "https://example.com/remote_command.py"})
```

### HTTP REST

```bash
# Загрузка из локального файла
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "load", "params": {"source": "./my_command.py"}}'

# Загрузка из URL
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "load", "params": {"source": "https://example.com/remote_command.py"}}'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "load",
  "params": {
    "source": "./my_command.py"
  },
  "id": 1
}
```

## Примеры

### Загрузка из локального файла

```json
{
  "command": "load",
  "params": {
    "source": "./custom_command.py"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "commands_loaded": 1,
    "loaded_commands": ["custom_command"],
    "source": "./custom_command.py"
  },
  "message": "Loaded 1 commands from ./custom_command.py"
}
```

### Загрузка из GitHub

```json
{
  "command": "load",
  "params": {
    "source": "https://raw.githubusercontent.com/user/repo/main/remote_command.py"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "commands_loaded": 1,
    "loaded_commands": ["remote_command"],
    "source": "https://raw.githubusercontent.com/user/repo/main/remote_command.py"
  },
  "message": "Loaded 1 commands from https://raw.githubusercontent.com/user/repo/main/remote_command.py"
}
```

### Ошибка - Файл не найден

```json
{
  "command": "load",
  "params": {
    "source": "/nonexistent/path/test_command.py"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "commands_loaded": 0,
    "loaded_commands": [],
    "source": "/nonexistent/path/test_command.py",
    "error": "Command file does not exist: /nonexistent/path/test_command.py"
  },
  "message": "Failed to load commands from /nonexistent/path/test_command.py: Command file does not exist: /nonexistent/path/test_command.py"
}
```

### Ошибка - Неверное имя файла

```json
{
  "command": "load",
  "params": {
    "source": "./invalid.py"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "commands_loaded": 0,
    "loaded_commands": [],
    "source": "./invalid.py",
    "error": "Command file must end with '_command.py': ./invalid.py"
  },
  "message": "Failed to load commands from ./invalid.py: Command file must end with '_command.py': ./invalid.py"
}
```

## Обработка ошибок

Команда обрабатывает различные сценарии ошибок:

- **Файл не найден**: Возвращает ошибку, когда локальный файл не существует
- **Неверное имя файла**: Возвращает ошибку, когда файл не заканчивается на '_command.py'
- **Ошибки сети**: Возвращает ошибку, когда загрузка URL не удается
- **Ошибки импорта**: Возвращает ошибку, когда Python модуль не может быть загружен
- **Отсутствие библиотеки Requests**: Возвращает ошибку, когда библиотека requests недоступна для загрузки URL

## Зависимости

- Библиотека `requests` для загрузки HTTP/HTTPS URL (опционально, корректно обрабатывается при отсутствии)
- `urllib.parse` для парсинга URL
- `tempfile` для управления временными файлами
- `importlib` для динамической загрузки модулей 