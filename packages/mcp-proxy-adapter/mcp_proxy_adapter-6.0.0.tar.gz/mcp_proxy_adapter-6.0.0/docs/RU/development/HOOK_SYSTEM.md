# Система хуков

## Обзор

Система хуков в MCP Proxy Adapter предоставляет гибкий способ расширения функциональности приложения без изменения основного кода. Она позволяет:

- Выполнять пользовательский код до и после обработки запросов
- Переопределять стандартные команды `help` и `health` пользовательскими реализациями
- Добавлять возможности логирования, валидации, мониторинга и аналитики
- Реализовывать ограничение скорости и другую middleware функциональность

## Архитектура

Система хуков состоит из нескольких ключевых компонентов:

### HookManager

Центральный менеджер, который обрабатывает регистрацию и выполнение хуков:

```python
from mcp_proxy_adapter.core.hooks import hook_manager

# Регистрация хуков
hook_manager.register_hook(HookType.PRE_REQUEST, my_pre_hook)
hook_manager.register_hook(HookType.POST_REQUEST, my_post_hook)

# Регистрация пользовательских команд
hook_manager.register_custom_command("help", CustomHelpCommand)
hook_manager.register_custom_command("health", CustomHealthCommand)
```

### HookContext

Dataclass, который содержит всю релевантную информацию о запросе и ответе:

```python
@dataclass
class HookContext:
    command_name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None
    execution_time: Optional[float] = None
```

### Типы хуков

Доступные типы хуков:

- `PRE_REQUEST`: Выполняется до обработки команды
- `POST_REQUEST`: Выполняется после обработки команды
- `CUSTOM_HELP`: Для пользовательской реализации команды help
- `CUSTOM_HEALTH`: Для пользовательской реализации команды health

## Примеры использования

### Pre-Request хуки

Pre-request хуки полезны для:

- Логирования и мониторинга
- Валидации и модификации параметров
- Ограничения скорости
- Аутентификации и авторизации

```python
import asyncio
from mcp_proxy_adapter.core.hooks import register_pre_request_hook, HookContext

async def logging_hook(context: HookContext) -> None:
    """Логирование детальной информации о запросе."""
    print(f"Обработка команды: {context.command_name}")
    print(f"Параметры: {context.params}")

async def validation_hook(context: HookContext) -> None:
    """Валидация и модификация параметров."""
    if context.command_name == "echo":
        message = context.params.get("message", "")
        if len(message) > 1000:
            context.params["message"] = message[:1000] + "..."

# Регистрация хуков
register_pre_request_hook(logging_hook)
register_pre_request_hook(validation_hook)
```

### Post-Request хуки

Post-request хуки полезны для:

- Сбора аналитики и метрик
- Логирования ответов
- Мониторинга производительности
- Отслеживания ошибок

```python
import time
from mcp_proxy_adapter.core.hooks import register_post_request_hook, HookContext

async def analytics_hook(context: HookContext) -> None:
    """Сбор аналитических данных."""
    analytics_data = {
        "command": context.command_name,
        "execution_time": context.execution_time,
        "success": context.error is None,
        "timestamp": time.time()
    }
    
    # Отправка в аналитический сервис
    print(f"Аналитика: {analytics_data}")

async def performance_hook(context: HookContext) -> None:
    """Мониторинг производительности."""
    if context.execution_time and context.execution_time > 1.0:
        print(f"Обнаружена медленная команда: {context.command_name} заняла {context.execution_time}s")

# Регистрация хуков
register_post_request_hook(analytics_hook)
register_post_request_hook(performance_hook)
```

### Пользовательские команды

Вы можете переопределить стандартные команды `help` и `health` пользовательскими реализациями:

```python
from mcp_proxy_adapter.commands.base import Command
from mcp_proxy_adapter.commands.result import SuccessResult
from mcp_proxy_adapter.core.hooks import register_custom_help_command

class CustomHelpCommand(Command):
    """Пользовательская команда help с расширенными возможностями."""
    
    name = "help"
    result_class = SuccessResult
    
    async def execute(self, cmdname: Optional[str] = None, **kwargs):
        # Пользовательская реализация help
        return SuccessResult(data={
            "custom_help": True,
            "command": cmdname or "all"
        })

# Регистрация пользовательской команды
register_custom_help_command(CustomHelpCommand)
```

## Точки интеграции

### Поток выполнения команд

Система хуков интегрирована в поток выполнения команд:

1. **Pre-request хуки** выполняются до обработки команды
2. **Проверка пользовательских команд** - если зарегистрирована пользовательская команда, используется она вместо стандартной
3. **Выполнение команды** - команда выполняется
4. **Post-request хуки** выполняются после обработки команды

```python
# В функции execute_command
context = HookContext(command_name=command_name, params=params, request_id=request_id)

# Выполнение pre-request хуков
await hook_manager.execute_hooks(HookType.PRE_REQUEST, context)

# Проверка пользовательских команд
if hook_manager.has_custom_command(command_name):
    command_class = hook_manager.get_custom_command(command_name)
else:
    command_class = registry.get_command(command_name)

# Выполнение команды
result = await command_class.run(**params)

# Обновление контекста для post-request хуков
context.response_data = result.to_dict()
context.execution_time = execution_time

# Выполнение post-request хуков
await hook_manager.execute_hooks(HookType.POST_REQUEST, context)
```

## Лучшие практики

### Дизайн хуков

1. **Держите хуки легковесными** - избегайте тяжелых операций, которые могут замедлить обработку запросов
2. **Обрабатывайте ошибки gracefully** - хуки не должны ломать основной поток выполнения
3. **Используйте async хуки** - для I/O операций используйте async функции
4. **Модифицируйте контекст осторожно** - помните, что модификации контекста влияют на последующие хуки

### Соображения производительности

1. **Ограничивайте количество хуков** - слишком много хуков может повлиять на производительность
2. **Используйте async операции** - для запросов к БД, API вызовов и т.д.
3. **Кэшируйте дорогие операции** - избегайте повторных дорогих вычислений
4. **Мониторьте время выполнения хуков** - отслеживайте, сколько времени занимают хуки

### Обработка ошибок

Хуки выполняются в try-catch блоке, поэтому ошибки в хуках не ломают основное выполнение:

```python
async def safe_hook(context: HookContext) -> None:
    try:
        # Ваша логика хука здесь
        pass
    except Exception as e:
        # Логируйте ошибку, но не поднимайте исключение
        logger.error(f"Ошибка хука: {e}")
```

## Продвинутое использование

### Хук ограничения скорости

```python
import time
from mcp_proxy_adapter.core.hooks import register_pre_request_hook

class RateLimiter:
    def __init__(self):
        self.requests = {}
    
    async def rate_limit_hook(self, context: HookContext) -> None:
        current_time = time.time()
        command = context.command_name
        
        # Очистка старых записей
        self.requests = {
            k: v for k, v in self.requests.items()
            if current_time - v["timestamp"] < 60
        }
        
        if command not in self.requests:
            self.requests[command] = {"count": 1, "timestamp": current_time}
        else:
            self.requests[command]["count"] += 1
            
            if self.requests[command]["count"] > 10:
                raise Exception(f"Превышен лимит скорости для {command}")

rate_limiter = RateLimiter()
register_pre_request_hook(rate_limiter.rate_limit_hook)
```

### Аналитический хук

```python
import json
from mcp_proxy_adapter.core.hooks import register_post_request_hook

async def analytics_hook(context: HookContext) -> None:
    """Отправка аналитических данных во внешний сервис."""
    analytics_data = {
        "command": context.command_name,
        "execution_time": context.execution_time,
        "success": context.error is None,
        "timestamp": time.time(),
        "params_count": len(context.params) if context.params else 0
    }
    
    # Отправка в аналитический сервис (пример)
    try:
        # await analytics_service.send(analytics_data)
        print(f"Аналитика отправлена: {json.dumps(analytics_data)}")
    except Exception as e:
        logger.error(f"Не удалось отправить аналитику: {e}")

register_post_request_hook(analytics_hook)
```

## Тестирование

Система хуков включает комплексные тесты. Вы можете тестировать свои хуки:

```python
import pytest
from mcp_proxy_adapter.core.hooks import hook_manager, HookContext, HookType

@pytest.mark.asyncio
async def test_my_hook():
    hook_called = False
    
    async def test_hook(context: HookContext) -> None:
        nonlocal hook_called
        hook_called = True
        assert context.command_name == "test_command"
    
    hook_manager.register_hook(HookType.PRE_REQUEST, test_hook)
    
    context = HookContext(command_name="test_command")
    await hook_manager.execute_hooks(HookType.PRE_REQUEST, context)
    
    assert hook_called
```

## Конфигурация

Хуки могут быть настроены при запуске приложения:

```python
from mcp_proxy_adapter.core.hooks import (
    register_pre_request_hook, register_post_request_hook,
    register_custom_help_command, register_custom_health_command
)

def setup_hooks():
    """Настройка всех хуков приложения."""
    
    # Регистрация хуков мониторинга
    register_pre_request_hook(logging_hook)
    register_post_request_hook(analytics_hook)
    
    # Регистрация пользовательских команд при необходимости
    if config.get("use_custom_help"):
        register_custom_help_command(CustomHelpCommand)
    
    if config.get("use_custom_health"):
        register_custom_health_command(CustomHealthCommand)

# Вызов при запуске приложения
setup_hooks()
```

## Устранение неполадок

### Распространенные проблемы

1. **Хуки не выполняются**: Проверьте, что хуки зарегистрированы до выполнения команд
2. **Проблемы производительности**: Мониторьте время выполнения хуков и оптимизируйте медленные хуки
3. **Утечки памяти**: Убедитесь, что хуки не накапливают данные бесконечно
4. **Распространение ошибок**: Хуки должны обрабатывать свои ошибки gracefully

### Отладка

Включите debug логирование для просмотра выполнения хуков:

```python
import logging
logging.getLogger("mcp_proxy_adapter.core.hooks").setLevel(logging.DEBUG)
```

Это покажет детальную информацию о регистрации и выполнении хуков. 