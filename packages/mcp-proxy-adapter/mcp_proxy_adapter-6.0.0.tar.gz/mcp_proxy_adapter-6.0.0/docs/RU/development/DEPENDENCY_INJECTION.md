# Внедрение зависимостей (Dependency Injection)

В версии 3.1.6 библиотеки MCP Proxy Adapter добавлена поддержка внедрения зависимостей (DI).
Эта функциональность позволяет создавать более гибкие и тестируемые команды, которые
могут использовать общие сервисы и ресурсы.

## Основные понятия

**Dependency Injection (DI)** - это паттерн проектирования, при котором объект получает свои
зависимости извне, а не создает их самостоятельно. В контексте microservice-command-protocol:

1. **Команды** - классы, которые принимают зависимости через конструктор
2. **Зависимости** - сервисы, репозитории, другие объекты, необходимые для работы команд
3. **Контейнер** - объект для хранения и управления зависимостями
4. **Регистрация** - процесс добавления экземпляра команды в реестр

## Использование DI в командах

### 1. Создание команды с зависимостями

```python
from mcp_proxy_adapter.commands import Command, SuccessResult

class DatabaseService:
    """Сервис для работы с данными."""
    
    def get_data(self, key):
        # ... логика получения данных
        return {"result": f"Data for {key}"}


class DataCommand(Command):
    """Команда, использующая внедренную зависимость."""
    
    name = "get_data"
    result_class = SuccessResult
    
    def __init__(self, db_service: DatabaseService):
        """
        Инициализация команды с зависимостями.
        
        Args:
            db_service: Сервис для работы с данными
        """
        self.db_service = db_service
    
    async def execute(self, key: str) -> SuccessResult:
        """Выполнение команды."""
        data = self.db_service.get_data(key)
        return self.result_class(**data)
```

### 2. Регистрация команды с зависимостями

```python
from mcp_proxy_adapter.commands import registry, container

# Создание сервисов
db_service = DatabaseService()

# Регистрация в контейнере (опционально)
container.register("db_service", db_service)

# Создание экземпляра команды с зависимостями
data_command = DataCommand(db_service)

# Регистрация экземпляра
registry.register(data_command)
```

### 3. Выполнение команды через API

После регистрации команды с зависимостями, её можно вызывать через API точно так же, как и обычные команды. Система автоматически найдет зарегистрированный экземпляр команды:

```json
{
  "jsonrpc": "2.0",
  "method": "get_data",
  "params": {
    "key": "user_123"
  },
  "id": 1
}
```

## Типы регистрации и управление жизненным циклом

### 1. Регистрация экземпляра команды

```python
# Создание экземпляра
command = MyCommand(dependency)

# Регистрация экземпляра
registry.register(command)
```

### 2. Регистрация класса команды (для команд без зависимостей)

```python
# Регистрация класса
registry.register(MySimpleCommand)
```

## Контейнер зависимостей

MCP Proxy Adapter включает простой контейнер зависимостей (`DependencyContainer`), который можно использовать для централизованного управления зависимостями:

```python
from mcp_proxy_adapter.commands import container

# Регистрация простой зависимости
container.register("config", config_service)

# Регистрация фабрики (создает новый экземпляр при каждом запросе)
container.register_factory("logger", lambda: create_logger())

# Регистрация синглтона (создает экземпляр только при первом запросе)
container.register_singleton("db", lambda: create_db_connection())

# Получение зависимости
db = container.get("db")
```

## Пример полной интеграции

```python
import asyncio
from mcp_proxy_adapter import create_app
from mcp_proxy_adapter.commands import registry, container

# Создание сервисов
db_service = DatabaseService("sqlite://:memory:")
config_service = ConfigService("config.json")
time_service = TimeService()

# Регистрация в контейнере
container.register("db", db_service)
container.register("config", config_service)
container.register("time", time_service)

# Регистрация команд
registry.register(DataCommand(db_service, time_service))
registry.register(ConfigCommand(config_service))
registry.register(StatusCommand(db_service, config_service, time_service))

# Создание FastAPI приложения
app = create_app()

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Преимущества DI

1. **Тестируемость** - возможность подменять реальные зависимости на моки при тестировании
2. **Гибкость** - возможность изменять зависимости без изменения кода команд
3. **Управление жизненным циклом** - централизованное управление ресурсами
4. **Повторное использование** - возможность использовать одни и те же сервисы в разных командах

## Практические рекомендации

1. **Интерфейсы** - определяйте чёткие интерфейсы для сервисов
2. **Инициализация** - инициализируйте зависимости при запуске приложения
3. **Освобождение ресурсов** - добавляйте обработчики для корректного освобождения ресурсов
4. **Группировка** - группируйте логически связанные зависимости в одном сервисе

## Полные примеры

Полные примеры использования DI можно найти в директории `examples/di_example/` и `examples/commands/echo_command_di.py`.

## Совместимость с предыдущими версиями

Реализация DI полностью совместима с предыдущими версиями библиотеки. Команды без зависимостей продолжат работать без изменений. 