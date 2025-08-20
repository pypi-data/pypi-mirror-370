# Команда Reload Settings

Команда `reload_settings` позволяет перезагружать настройки конфигурации из файлов и переменных окружения во время выполнения.

## Описание

Команда reload settings предоставляет возможность:
- Перезагружать конфигурацию из JSON файлов
- Перезагружать переменные окружения
- Обновлять пользовательские настройки
- Получать текущие пользовательские настройки после перезагрузки

## Информация о команде

- **Имя**: `reload_settings`
- **Описание**: Перезагрузить настройки конфигурации из файлов и переменных окружения
- **Категория**: Управление конфигурацией

## Параметры

Эта команда не принимает никаких параметров.

## Формат ответа

### Успешный ответ

```json
{
  "result": {
    "success": true,
    "message": "Settings reloaded successfully from configuration files and environment variables",
    "custom_settings": {
      "application": {
        "name": "Extended MCP Proxy Server with Custom Settings",
        "version": "2.1.0",
        "environment": "development"
      },
      "features": {
        "advanced_hooks": true,
        "custom_commands": true,
        "data_transformation": true
      },
      "security": {
        "enable_authentication": false,
        "max_request_size": "15MB"
      }
    }
  }
}
```

### Ответ с ошибкой

```json
{
  "result": {
    "success": false,
    "message": "Failed to reload settings",
    "custom_settings": {},
    "error_message": "Failed to reload settings: Configuration file not found"
  }
}
```

## Примеры использования

### Базовое использование

```bash
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{
    "command": "reload_settings",
    "params": {}
  }'
```

### Пример на Python

```python
import requests

response = requests.post(
    "http://localhost:8000/cmd",
    json={
        "command": "reload_settings",
        "params": {}
    }
)

result = response.json()
if result["result"]["success"]:
    print("✅ Settings reloaded successfully")
    print(f"📋 Custom settings: {result['result']['custom_settings']}")
else:
    print(f"❌ Failed to reload settings: {result['result']['error_message']}")
```

## Что перезагружается

При выполнении команды `reload_settings` происходит следующее:

1. **Файлы конфигурации**: Перезагружает настройки из `config.json` и других файлов конфигурации
2. **Переменные окружения**: Перезагружает настройки из переменных окружения с префиксом `SERVICE_`
3. **Пользовательские настройки**: Обновляет пользовательские настройки, добавленные через `add_custom_settings()`
4. **Настройки фреймворка**: Обновляет настройки сервера, логирования и команд

## Интеграция с пользовательскими настройками

Команда работает бесшовно с системой пользовательских настроек:

```python
from mcp_proxy_adapter.core.settings import add_custom_settings, reload_settings

# Добавить пользовательские настройки
add_custom_settings({
    "application": {
        "name": "My Custom App",
        "version": "1.0.0"
    }
})

# Перезагрузить все настройки (включая пользовательские)
reload_settings()
```

## Обработка ошибок

Команда обеспечивает комплексную обработку ошибок:

- **Файл не найден**: Корректно обрабатывает отсутствующие файлы конфигурации
- **Неверный JSON**: Сообщает об ошибках парсинга JSON
- **Ошибки прав доступа**: Обрабатывает проблемы с правами доступа к файлам
- **Переменные окружения**: Безопасно обрабатывает отсутствующие или неверные переменные окружения

## Лучшие практики

1. **Используйте после изменений конфигурации**: Вызывайте эту команду после изменения файлов конфигурации
2. **Мониторьте ответ**: Всегда проверяйте поле `success` в ответе
3. **Обрабатывайте ошибки**: Реализуйте правильную обработку ошибок для неудачных перезагрузок
4. **Проверяйте настройки**: Используйте возвращенные пользовательские настройки для проверки успешности перезагрузки
5. **Логируйте операции**: Логируйте операции перезагрузки для отладки и мониторинга

## Связанные команды

- **`settings`**: Получать, устанавливать и управлять отдельными настройками
- **`config`**: Доступ к конфигурации фреймворка
- **`reload`**: Перезагрузить команды и конфигурацию (более комплексно)

## Случаи использования

### Среда разработки

```bash
# После изменения config.json
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
```

### Продакшн среда

```bash
# После обновления переменных окружения
export SERVICE_SERVER_PORT=8080
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
```

### Управление пользовательскими настройками

```python
# После добавления пользовательских настроек программно
from mcp_proxy_adapter.core.settings import add_custom_settings

add_custom_settings({"feature_enabled": True})

# Перезагрузить для обеспечения актуальности всех настроек
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "reload_settings", "params": {}}'
``` 