# Базовый пример

Базовый пример демонстрирует более структурированный микросервис с несколькими командами в отдельных файлах и комплексными тестами.

## Структура

```
basic_example/
├── __init__.py           # Инициализация пакета
├── config.yaml           # Файл конфигурации
├── README.md             # Документация
├── server.py             # Инициализация сервера
├── commands/             # Директория с командами
│   ├── __init__.py
│   ├── echo_command.py   # Реализация команды echo
│   ├── math_command.py   # Команда математических операций
│   └── time_command.py   # Команда для работы со временем
├── docs/                 # Документация
└── tests/                # Директория с тестами
    ├── conftest.py       # Конфигурация тестов
    ├── test_echo.py      # Тесты команды echo
    ├── test_math.py      # Тесты команды math
    └── test_time.py      # Тесты команды time
```

## Ключевые компоненты

### Настройка сервера

Сервер инициализируется с более структурированным подходом:

```python
def main():
    """Запуск микросервиса."""
    # Создание микросервиса
    service = mcp.MicroService(
        title="Basic Example Microservice",
        description="Basic example of microservice with multiple commands",
        version="1.0.0",
        config_path="config.yaml"
    )
    
    # Регистрация команд из отдельных файлов
    service.register_command(EchoCommand)
    service.register_command(MathCommand)
    service.register_command(TimeCommand)
    
    # Запуск сервера
    service.run(host="0.0.0.0", port=8000, reload=True)
```

### Организация команд

Каждая команда реализована в отдельном файле для лучшей организации кода:

```
commands/
├── echo_command.py  # Простая команда echo
├── math_command.py  # Математические операции
└── time_command.py  # Операции, связанные со временем
```

### Пример команды: Math Command

Команда Math предоставляет базовые математические операции:

```python
class MathCommand(Command):
    """Команда для выполнения математических операций."""
    
    name = "math"
    result_class = MathResult
    
    async def execute(self, operation: str, a: float, b: float) -> MathResult:
        """
        Выполнение математической операции.
        
        Args:
            operation: Операция для выполнения (add, subtract, multiply, divide)
            a: Первое число
            b: Второе число
            
        Returns:
            Результат операции
            
        Raises:
            InvalidParamsError: Если операция недопустима
            CommandError: При попытке деления на ноль
        """
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                raise CommandError("Деление на ноль")
            result = a / b
        else:
            raise InvalidParamsError(f"Неизвестная операция: {operation}")
            
        return MathResult(operation, a, b, result)
```

### Комплексное тестирование

Базовый пример включает комплексные тесты для всех команд с использованием pytest и плагина pytest-asyncio для тестирования асинхронного кода:

```python
@pytest.mark.asyncio
async def test_math_add():
    """Тест операции сложения."""
    command = MathCommand()
    result = await command.execute(operation="add", a=5, b=3)
    
    assert result.operation == "add"
    assert result.a == 5
    assert result.b == 3
    assert result.result == 8
```

## Запуск примера

```bash
# Перейти в директорию проекта
cd examples/basic_example

# Запустить сервер
python server.py
```

Сервер будет доступен по адресу http://localhost:8000.

## Тестирование API

### Через веб-интерфейс

Откройте http://localhost:8000/docs в браузере для доступа к интерактивной документации Swagger UI.

### Через командную строку

```bash
# Вызов команды echo
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "echo", "params": {"message": "Hello World"}, "id": 1}'

# Вызов команды math
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "math", "params": {"operation": "add", "a": 5, "b": 3}, "id": 2}'

# Вызов команды time
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "time", "params": {"format": "iso"}, "id": 3}'
```

## Демонстрируемые концепции

1. Структурированная организация команд в отдельных файлах
2. Несколько типов команд с различной функциональностью
3. Управление конфигурацией
4. Комплексная стратегия тестирования
5. Обработка ошибок
6. Валидация параметров
7. Различные типы результатов 