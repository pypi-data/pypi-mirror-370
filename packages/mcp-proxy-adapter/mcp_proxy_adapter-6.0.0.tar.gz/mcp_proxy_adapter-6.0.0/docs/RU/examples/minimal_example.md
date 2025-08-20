# Минимальный пример

Минимальный пример демонстрирует простейший возможный микросервис с одной командой.

## Структура

```
minimal_example/
├── __init__.py           # Инициализация пакета
├── config.yaml           # Файл конфигурации
├── README.md             # Документация
├── simple_server.py      # Сервер с одной командой
└── tests/                # Директория с тестами
```

## Ключевые компоненты

### Настройка сервера

Сервер инициализируется с минимальной конфигурацией:

```python
# Создание микросервиса
service = mcp.MicroService(
    title="Minimal Example Microservice",
    description="Simple example of microservice with a single command",
    version="1.0.0"
)

# Регистрация команды
service.register_command(HelloCommand)

# Запуск сервера
service.run(host="0.0.0.0", port=8000, reload=True)
```

### Реализация команды

В примере реализована простая команда `hello`, которая возвращает приветственное сообщение:

```python
class HelloCommand(Command):
    """Команда, которая возвращает приветственное сообщение."""
    
    name = "hello"
    result_class = HelloResult
    
    async def execute(self, name: str = "World") -> HelloResult:
        """
        Выполнение команды.
        
        Args:
            name: Имя для приветствия
            
        Returns:
            Результат приветствия
        """
        return HelloResult(f"Hello, {name}!")
```

### Реализация результата

Команда возвращает класс `HelloResult`:

```python
class HelloResult(SuccessResult):
    """Результат команды hello."""
    
    def __init__(self, message: str):
        """
        Инициализация результата.
        
        Args:
            message: Приветственное сообщение
        """
        self.message = message
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование результата в словарь.
        
        Returns:
            Представление в виде словаря
        """
        return {"message": self.message}
```

## Запуск примера

```bash
# Перейти в директорию проекта
cd examples/minimal_example

# Запустить сервер
python simple_server.py
```

Сервер будет доступен по адресу http://localhost:8000.

## Тестирование API

### Через веб-интерфейс

Откройте http://localhost:8000/docs в браузере для доступа к интерактивной документации Swagger UI.

### Через командную строку

```bash
# Вызов команды hello через JSON-RPC
curl -X POST "http://localhost:8000/api/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "hello", "params": {"name": "User"}, "id": 1}'

# Вызов команды hello через упрощенный эндпоинт
curl -X POST "http://localhost:8000/cmd" \
  -H "Content-Type: application/json" \
  -d '{"command": "hello", "params": {"name": "User"}}'
```

## Демонстрируемые концепции

1. Создание минимального микросервиса
2. Определение простой команды
3. Основные эндпоинты API
4. Работа с JSON-RPC
5. Структура результата команды
6. Генерация схемы для валидации 