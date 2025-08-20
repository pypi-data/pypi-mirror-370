# Руководство по расширению проекта

## Обзор

Это руководство предоставляет пошаговые инструкции по расширению проекта MCP Proxy Adapter для решения реальных задач. Оно охватывает процесс от начальной настройки до добавления пользовательской команды и развертывания приложения.

## Процесс расширения

### 1. Настройка проекта

```
# Клонирование базового репозитория
git clone https://github.com/your-organization/mcp_microservice.git my_project
cd my_project

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Установка зависимостей для разработки
pip install -r requirements-dev.txt
```

### 2. Настройка конфигурации проекта

Создайте или измените файл конфигурации в соответствии с вашими требованиями:

```json
{
    "server": {
        "host": "0.0.0.0",
        "port": 8000
    },
    "logging": {
        "level": "INFO",
        "file": "application.log",
        "rotation": {
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "stderr_file": "error.log"
    },
    "commands": {
        "enabled": ["echo", "get_date", "new_uuid4"]
    }
}
```

### 3. Создание новой команды

Для этого примера мы создадим команду `echo`, которая возвращает входное сообщение.

#### 3.1. Определение класса результата команды

Создайте файл `src/commands/echo_command.py`:

```python
"""
Модуль команды Echo.

Этот модуль реализует простую команду echo, которая возвращает входное сообщение.
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

from mcp_proxy_adapter.interfaces.command_result import CommandResult
from mcp_proxy_adapter.interfaces.command import Command


@dataclass
class EchoResult(CommandResult):
    """
    Результат команды echo.
    
    Attributes:
        message: Возвращаемое сообщение
    """
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразование результата в словарь.
        
        Returns:
            Dict[str, Any]: Словарное представление результата
        """
        return {
            "message": self.message
        }
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Получение JSON-схемы для этого результата.
        
        Returns:
            Dict[str, Any]: JSON-схема
        """
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Возвращаемое сообщение"
                }
            },
            "required": ["message"]
        }


class EchoCommand(Command):
    """
    Команда, которая возвращает заданное сообщение.
    
    Это простая демонстрационная команда, которая возвращает входное сообщение.
    """
    
    async def execute(self, message: str, prefix: Optional[str] = None) -> EchoResult:
        """
        Выполнение команды echo.
        
        Args:
            message: Сообщение для возврата
            prefix: Опциональный префикс для добавления к сообщению
            
        Returns:
            EchoResult: Результат, содержащий возвращаемое сообщение
        """
        if prefix:
            final_message = f"{prefix}: {message}"
        else:
            final_message = message
            
        self.logger.debug(f"Возвращаем сообщение: {final_message}")
        return EchoResult(message=final_message)
    
    @classmethod
    def get_schema(cls) -> Dict[str, Any]:
        """
        Получение JSON-схемы для этой команды.
        
        Returns:
            Dict[str, Any]: JSON-схема
        """
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Сообщение для возврата"
                },
                "prefix": {
                    "type": "string",
                    "description": "Опциональный префикс для добавления к сообщению"
                }
            },
            "required": ["message"]
        }
```

#### 3.2. Регистрация команды

Создайте или измените `src/commands/__init__.py` для регистрации вашей команды:

```python
from mcp_proxy_adapter.commands.echo_command import EchoCommand
from mcp_proxy_adapter.commands.get_date_command import GetDateCommand
from mcp_proxy_adapter.commands.new_uuid4_command import NewUUID4Command

# Реестр команд
COMMANDS = {
    "echo": EchoCommand,
    "get_date": GetDateCommand,
    "new_uuid4": NewUUID4Command
}
```

### 4. Написание тестов для команды

Создайте тестовый файл `tests/unit/commands/test_echo_command.py`:

```python
import pytest
from mcp_proxy_adapter.commands.echo_command import EchoCommand, EchoResult


class TestEchoCommand:
    """Тесты для команды Echo."""
    
    @pytest.fixture
    def command(self):
        """Создание экземпляра команды для тестирования."""
        return EchoCommand()
    
    @pytest.mark.asyncio
    async def test_echo_basic(self, command):
        """Тест базовой функциональности echo."""
        result = await command.execute(message="Hello, World!")
        assert isinstance(result, EchoResult)
        assert result.message == "Hello, World!"
        
    @pytest.mark.asyncio
    async def test_echo_with_prefix(self, command):
        """Тест echo с префиксом."""
        result = await command.execute(message="Hello, World!", prefix="PREFIX")
        assert result.message == "PREFIX: Hello, World!"
    
    def test_result_to_dict(self):
        """Тест сериализации результата."""
        result = EchoResult(message="Test message")
        data = result.to_dict()
        assert data == {"message": "Test message"}
    
    def test_schema(self, command):
        """Тест генерации схемы."""
        schema = command.get_schema()
        assert schema["type"] == "object"
        assert "message" in schema["properties"]
        assert "prefix" in schema["properties"]
        assert "message" in schema["required"]
```

### 5. Создание документации для команды

Создайте файлы документации для обоих языков:

Для русского языка: `docs/RU/commands/echo_command.md`:

```markdown
# Команда Echo

## Описание

Команда echo возвращает входное сообщение, опционально с префиксом.

## Результат

```python
@dataclass
class EchoResult(CommandResult):
    message: str
```

## Команда

```python
class EchoCommand(Command):
    async def execute(self, message: str, prefix: Optional[str] = None) -> EchoResult:
        # Детали реализации...
```

## Параметры

| Параметр  | Тип    | Обязательный | Описание                            |
|-----------|--------|--------------|-------------------------------------|
| message   | string | Да           | Сообщение для возврата              |
| prefix    | string | Нет          | Опциональный префикс для сообщения  |

## Примеры

### Python

```python
from mcp_proxy_adapter.client import Client

client = Client("http://localhost:8000")
result = await client.execute("echo", {"message": "Hello, World!"})
print(result.message)  # Вывод: Hello, World!

# С префиксом
result = await client.execute("echo", {"message": "Hello, World!", "prefix": "ECHO"})
print(result.message)  # Вывод: ECHO: Hello, World!
```

### HTTP REST

Запрос:

```
POST /api/commands/echo
Content-Type: application/json

{
    "message": "Hello, World!",
    "prefix": "ECHO"
}
```

Ответ:

```
200 OK
Content-Type: application/json

{
    "message": "ECHO: Hello, World!"
}
```

### JSON-RPC

Запрос:

```json
{
    "jsonrpc": "2.0",
    "method": "echo",
    "params": {
        "message": "Hello, World!",
        "prefix": "ECHO"
    },
    "id": 1
}
```

Ответ:

```json
{
    "jsonrpc": "2.0",
    "result": {
        "message": "ECHO: Hello, World!"
    },
    "id": 1
}
```

## Обработка ошибок

| Код ошибки | Описание                     | Причина                            |
|------------|------------------------------|-----------------------------------|
| 400        | Bad Request                  | Отсутствует обязательный параметр |
| 500        | Internal Server Error        | Непредвиденная ошибка сервера     |
```

Создайте английскую версию в `docs/EN/commands/echo_command.md`.

### 6. Настройка расширенных параметров (опционально)

Если вам нужно пользовательское поведение конфигурации, создайте пользовательский класс настроек:

```python
# src/config.py
from mcp_proxy_adapter.config import Settings

class ExtendedSettings(Settings):
    def _read_config_file(self, config_path):
        """Поддержка файлов конфигурации YAML."""
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            return self._read_yaml_config(config_path)
        return super()._read_config_file(config_path)
    
    def _read_yaml_config(self, config_path):
        """Чтение файла конфигурации YAML."""
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_configuration(self):
        """Добавление пользовательской валидации."""
        super().validate_configuration()
        
        # Валидация пользовательских элементов конфигурации
        if 'commands' not in self.config:
            raise ValueError("Отсутствует раздел 'commands' в конфигурации")
        
        if 'enabled' not in self.config['commands']:
            raise ValueError("Отсутствует список 'enabled' в конфигурации commands")
```

### 7. Запуск тестов

```
# Запуск всех тестов
pytest

# Запуск определенных тестов
pytest tests/unit/commands/test_echo_command.py
```

### 8. Запуск сервиса

```
# Режим разработки
python -m mcp_microservice.server --config-path /path/to/config.json

# Производственный режим
gunicorn -k uvicorn.workers.UvicornWorker mcp_microservice.server:app
```

### 9. Проверка вашей команды

Используя curl:

```
curl -X POST http://localhost:8000/api/commands/echo \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello, MCP!", "prefix": "TEST"}'
```

Ответ:

```json
{
    "message": "TEST: Hello, MCP!"
}
```

### 10. Создание интеграции с системными сервисами

Создайте файл службы systemd `/etc/systemd/system/mcp-service.service`:

```ini
[Unit]
Description=MCP Proxy Adapter
After=network.target

[Service]
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp_microservice
ExecStart=/opt/mcp_microservice/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker mcp_microservice.server:app
Restart=on-failure
Environment=MCP_CONFIG_PATH=/etc/mcp_microservice/config.json

[Install]
WantedBy=multi-user.target
```

Создайте скрипт инициализации SystemV `/etc/init.d/mcp-service`:

```bash
#!/bin/bash
### BEGIN INIT INFO
# Provides:          mcp-service
# Required-Start:    $network $local_fs $remote_fs
# Required-Stop:     $network $local_fs $remote_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: MCP Proxy Adapter
# Description:       MCP Proxy Adapter
### END INIT INFO

NAME="mcp-service"
DAEMON="/opt/mcp_microservice/venv/bin/gunicorn"
DAEMON_OPTS="-k uvicorn.workers.UvicornWorker mcp_microservice.server:app"
DAEMON_USER="mcp"
PIDFILE="/var/run/$NAME.pid"
LOGFILE="/var/log/$NAME.log"

# Загрузка функций инициализации
. /lib/lsb/init-functions

# Экспорт переменных окружения
export MCP_CONFIG_PATH="/etc/mcp_microservice/config.json"

do_start() {
    log_daemon_msg "Запуск $NAME"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile \
        --chuid $DAEMON_USER --chdir /opt/mcp_microservice \
        --exec $DAEMON -- $DAEMON_OPTS >> $LOGFILE 2>&1
    log_end_msg $?
}

do_stop() {
    log_daemon_msg "Остановка $NAME"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

do_reload() {
    log_daemon_msg "Перезагрузка $NAME"
    start-stop-daemon --stop --signal HUP --pidfile $PIDFILE
    log_end_msg $?
}

case "$1" in
    start)
        do_start
        ;;
    stop)
        do_stop
        ;;
    restart)
        do_stop
        do_start
        ;;
    reload)
        do_reload
        ;;
    status)
        status_of_proc -p $PIDFILE "$DAEMON" "$NAME"
        ;;
    *)
        echo "Использование: $NAME {start|stop|restart|reload|status}"
        exit 1
        ;;
esac

exit 0
```

Сделайте скрипт исполняемым:

```bash
chmod +x /etc/init.d/mcp-service
```

### 11. Развертывание

```bash
# Копирование файлов приложения
mkdir -p /opt/mcp_microservice
cp -r . /opt/mcp_microservice

# Настройка виртуального окружения
cd /opt/mcp_microservice
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Создание директории конфигурации
mkdir -p /etc/mcp_microservice
cp config.json /etc/mcp_microservice/

# Настройка службы
systemctl daemon-reload
systemctl enable mcp-service
systemctl start mcp-service

# Или для SystemV
update-rc.d mcp-service defaults
service mcp-service start
```

## Полный пример проекта

Вот полная структура проекта с командой echo:

```
mcp_microservice/
├── config.json
├── docs/
│   ├── EN/
│   │   ├── commands/
│   │   │   ├── echo_command.md
│   │   │   ├── get_date_command.md
│   │   │   └── new_uuid4_command.md
│   │   ├── CONFIGURATION_PRINCIPLES.md
│   │   ├── PROJECT_EXTENSION_GUIDE.md
│   │   └── другие файлы документации...
│   └── RU/
│       ├── commands/
│       │   ├── echo_command.md
│       │   ├── get_date_command.md
│       │   └── new_uuid4_command.md
│       ├── CONFIGURATION_PRINCIPLES.md
│       ├── PROJECT_EXTENSION_GUIDE.md
│       └── другие файлы документации...
├── mcp_microservice/
│   ├── __init__.py
│   ├── server.py
│   ├── config.py
│   ├── adapter.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── echo_command.py
│   │   ├── get_date_command.py
│   │   └── new_uuid4_command.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── command_registry.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── command.py
│   │   └── command_result.py
│   └── utils/
│       ├── __init__.py
│       └── validation.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── tests/
    ├── unit/
    │   ├── commands/
    │   │   ├── test_echo_command.py
    │   │   ├── test_get_date_command.py
    │   │   └── test_new_uuid4_command.py
    │   └── test_config.py
    └── integration/
        ├── test_api.py
        └── test_commands.py
```

## Лучшие практики

1. **Следуйте принципу единственной ответственности**: Каждая команда должна делать одну вещь хорошо.
2. **Обеспечьте правильную документацию**: Документируйте свой код и создавайте документацию команд на обоих языках.
3. **Пишите всесторонние тесты**: Стремитесь к высокому покрытию тестами с помощью модульных и интеграционных тестов.
4. **Валидируйте входные параметры**: Всегда проверяйте входные данные команд для обеспечения безопасности и надежности.
5. **Следуйте существующим шаблонам**: Используйте установленную структуру проекта и соглашения по кодированию.
6. **Используйте подсказки типов**: Делайте свой код более поддерживаемым с помощью правильной типизации.
7. **Сохраняйте обратную совместимость**: Убедитесь, что изменения не нарушают работу существующих клиентов.
8. **Используйте логирование соответствующим образом**: Используйте единый логгер с соответствующими уровнями логирования.
9. **Учитывайте безопасность**: Защищайте конфиденциальные данные и проверяйте входные данные.
10. **Проверяйте производительность**: Убедитесь, что ваши команды эффективны и избегайте блокирующих операций.

Следуя этому руководству, вы можете успешно расширить проект MCP Proxy Adapter с помощью пользовательских команд для ваших конкретных потребностей. 