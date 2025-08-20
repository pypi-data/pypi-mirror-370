# Полный пример

Полный пример демонстрирует готовый к промышленному использованию микросервис с поддержкой Docker, конфигурациями для разных окружений и расширенными возможностями.

## Структура

```
complete_example/
├── __init__.py           # Инициализация пакета
├── cache/                # Директория кэша
├── commands/             # Директория с командами
│   ├── __init__.py
│   ├── health_command.py # Команда проверки работоспособности
│   ├── config_command.py # Команда управления конфигурацией
│   ├── file_command.py   # Команда для работы с файлами
│   └── system_command.py # Команда информации о системе
├── configs/              # Файлы конфигурации
│   ├── development.yaml  # Конфигурация для разработки
│   ├── production.yaml   # Конфигурация для продакшена
│   └── testing.yaml      # Конфигурация для тестирования
├── docker-compose.yml    # Конфигурация Docker Compose
├── Dockerfile            # Определение Docker образа
├── logs/                 # Директория для логов
├── README.md             # Документация
├── requirements.txt      # Зависимости Python
├── server.py             # Инициализация сервера
└── tests/                # Директория с тестами
    ├── conftest.py       # Конфигурация тестов
    └── ...               # Тесты команд
```

## Ключевые компоненты

### Поддержка Docker

Пример включает конфигурацию Docker для контейнеризированного развертывания:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV MCP_ENV=production
ENV CONFIG_PATH=/app/configs/production.yaml

CMD ["python", "server.py"]
```

И Docker Compose для оркестрации:

```yaml
version: '3'

services:
  microservice:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./configs:/app/configs
      - ./logs:/app/logs
      - ./cache:/app/cache
    environment:
      - MCP_ENV=production
      - CONFIG_PATH=/app/configs/production.yaml
    networks:
      - mcp-network

networks:
  mcp-network:
    external: true
```

### Конфигурация для разных окружений

Пример демонстрирует использование различных файлов конфигурации для разных окружений:

```
configs/
├── development.yaml  # Настройки для локальной разработки
├── production.yaml   # Настройки для продакшена
└── testing.yaml      # Настройки для тестового окружения
```

Загрузка конфигурации:

```python
# Загрузка конфигурации на основе окружения
env = os.getenv("MCP_ENV", "development")
config_path = os.getenv("CONFIG_PATH", f"configs/{env}.yaml")

service = mcp.MicroService(
    title="Complete Example Microservice",
    description="Complete example with Docker and advanced features",
    version="1.0.0",
    config_path=config_path
)
```

### Расширенные команды

#### Команда проверки работоспособности

```python
class HealthCommand(Command):
    """Команда для проверки работоспособности сервиса."""
    
    name = "health"
    result_class = HealthResult
    
    async def execute(self, check_type: str = "basic") -> HealthResult:
        """
        Проверка работоспособности сервиса.
        
        Args:
            check_type: Тип проверки (basic или detailed)
            
        Returns:
            Результат проверки работоспособности
        """
        # Получение базовой информации о системе
        system_info = {
            "hostname": socket.gethostname(),
            "pid": os.getpid(),
            "uptime": time.time() - psutil.Process(os.getpid()).create_time(),
            "memory_usage": psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024),
        }
        
        # Добавление детальных метрик для подробной проверки
        if check_type == "detailed":
            system_info.update({
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "open_files": len(psutil.Process(os.getpid()).open_files()),
                "connections": len(psutil.Process(os.getpid()).connections()),
            })
            
        return HealthResult(
            status="ok",
            timestamp=datetime.datetime.now().isoformat(),
            system_info=system_info
        )
```

## Запуск примера

### С использованием Docker

```bash
# Перейти в директорию проекта
cd examples/complete_example

# Собрать и запустить Docker контейнер
docker-compose up --build
```

### Без использования Docker

```bash
# Перейти в директорию проекта
cd examples/complete_example

# Установить зависимости
pip install -r requirements.txt

# Запустить сервер
python server.py
```

Сервер будет доступен по адресу http://localhost:8000.

## Демонстрируемые концепции

1. Контейнеризация с Docker
2. Конфигурация для разных окружений
3. Монтирование томов для логов и кэша
4. Проверки работоспособности и мониторинг
5. Команды для получения информации о системе
6. Управление конфигурацией
7. Готовая к промышленному использованию настройка
8. Внешняя конфигурация
9. Изоляция и управление ресурсами 