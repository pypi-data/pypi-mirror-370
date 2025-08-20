# Команда Plugins

## Описание

Команда `plugins` читает и отображает доступные плагины с настроенного сервера плагинов. Эта команда загружает JSON файл с URL сервера плагинов, который содержит список доступных плагинов с их метаданными.

## Результат

Команда возвращает объект `PluginsResult` со следующей структурой:

```python
{
    "success": True,
    "plugins_server": "https://plugins.techsup.od.ua/plugins.json",
    "plugins": [
        {
            "name": "test_command",
            "description": "Test command for loadable commands testing",
            "url": "https://plugins.techsup.od.ua/test_command.py",
            "version": "1.0.0",
            "author": "MCP Proxy Team"
        }
    ],
    "total_plugins": 1
}
```

## Команда

```python
class PluginsCommand(Command):
    name = "plugins"
    result_class = PluginsResult
    
    async def execute(self, **kwargs) -> PluginsResult:
        # Загружает список плагинов с настроенного сервера
        # Возвращает PluginsResult с доступными плагинами
```

## Детали реализации

Команда работает следующим образом:

1. **Проверка конфигурации**: Читает URL `plugins_server` из конфигурации
2. **HTTP запрос**: Загружает JSON файл с сервера плагинов
3. **Парсинг JSON**: Обрабатывает ответ для извлечения списка плагинов
4. **Генерация результата**: Возвращает структурированный результат с метаданными плагинов

Ожидаемая структура JSON с сервера плагинов:

```json
{
    "plugins": [
        {
            "name": "plugin_name",
            "description": "Plugin description",
            "url": "https://server.com/plugin.py",
            "version": "1.0.0",
            "author": "Author Name"
        }
    ]
}
```

## Примеры использования

### Python

```python
from mcp_proxy_adapter.commands.plugins_command import PluginsCommand

command = PluginsCommand()
result = await command.execute()

if result.data["success"]:
    print(f"Найдено {result.data['total_plugins']} плагинов")
    for plugin in result.data["plugins"]:
        print(f"- {plugin['name']}: {plugin['description']}")
```

### HTTP REST

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "plugins"}'
```

### JSON-RPC

```json
{
    "jsonrpc": "2.0",
    "method": "plugins",
    "id": 1
}
```

## Обработка ошибок

Команда обрабатывает различные сценарии ошибок:

- **Нет конфигурации**: Возвращает ошибку, если URL `plugins_server` не настроен
- **Сетевые ошибки**: Обрабатывает сбои HTTP запросов
- **Ошибки парсинга JSON**: Обрабатывает неправильно сформированные JSON ответы
- **Отсутствие библиотеки Requests**: Graceful fallback, если библиотека requests недоступна

## Конфигурация

Добавьте URL сервера плагинов в вашу конфигурацию:

```json
{
    "commands": {
        "plugins_server": "https://plugins.techsup.od.ua/plugins.json"
    }
}
```

## Случаи использования

- **Обнаружение плагинов**: Найти доступные плагины без ручного просмотра
- **Получение метаданных**: Получить информацию о плагинах перед загрузкой
- **Управление плагинами**: Создать интерфейсы для управления плагинами
- **Проверка версий**: Проверить доступность и версии плагинов 