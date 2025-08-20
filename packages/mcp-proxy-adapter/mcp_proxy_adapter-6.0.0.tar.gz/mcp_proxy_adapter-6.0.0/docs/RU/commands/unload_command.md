# Команда Unload

## Описание

Команда `unload` позволяет удалять динамически загруженные команды из реестра команд. Только команды, которые были загружены через команду 'load' или из директории команд, могут быть выгружены. Встроенные команды и пользовательские команды, зарегистрированные с более высоким приоритетом, не могут быть выгружены с помощью этой команды.

Когда команда выгружается:
- Класс команды удаляется из реестра загруженных команд
- Любые экземпляры команды также удаляются
- Команда становится недоступной для выполнения
- Встроенные и пользовательские команды с тем же именем остаются незатронутыми

Это полезно для:
- Удаления устаревших или проблемных команд
- Управления использованием памяти путем выгрузки неиспользуемых команд
- Тестирования различных версий команд
- Очистки временных команд, загруженных для тестирования

Примечание: Выгрузка команды не влияет на другие команды и не требует перезапуска системы. Команда может быть перезагружена позже при необходимости.

## Результат

```python
class UnloadResult(SuccessResult):
    def __init__(self, success: bool, command_name: str, message: str, error: Optional[str] = None):
        data = {
            "success": success,
            "command_name": command_name
        }
        if error:
            data["error"] = error
```

## Команда

```python
class UnloadCommand(Command):
    name = "unload"
    result_class = UnloadResult
    
    async def execute(self, command_name: str, **kwargs) -> UnloadResult:
        """
        Выполнить команду выгрузки.
        
        Args:
            command_name: Имя команды для выгрузки
            **kwargs: Дополнительные параметры
            
        Returns:
            UnloadResult: Результат команды выгрузки
        """
```

## Детали реализации

Команда использует следующую логику:

1. **Проверка команды**: Проверяет, существует ли указанная команда в реестре загруженных команд
2. **Проверка разрешений**: Проверяет, что команда является загруженной командой (не встроенной или пользовательской)
3. **Процесс удаления**: Удаляет класс команды и любые связанные экземпляры
4. **Обновление реестра**: Обновляет реестр команд для отражения изменений
5. **Генерация результата**: Возвращает информацию об успехе или ошибке

## Примеры использования

### Python

```python
# Выгрузить ранее загруженную команду
result = await execute_command("unload", {"command_name": "test_command"})
```

### HTTP REST

```bash
# Выгрузить команду
curl -X POST http://localhost:8000/cmd \
  -H "Content-Type: application/json" \
  -d '{"command": "unload", "params": {"command_name": "test_command"}}'
```

### JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "method": "unload",
  "params": {
    "command_name": "test_command"
  },
  "id": 1
}
```

## Примеры

### Успешная выгрузка

```json
{
  "command": "unload",
  "params": {
    "command_name": "test_command"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": true,
    "command_name": "test_command"
  },
  "message": "Command 'test_command' unloaded successfully"
}
```

### Ошибка - Команда не найдена

```json
{
  "command": "unload",
  "params": {
    "command_name": "nonexistent_command"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "command_name": "nonexistent_command",
    "error": "Command 'nonexistent_command' is not a loaded command or does not exist"
  },
  "message": "Failed to unload commands from nonexistent_command: Command 'nonexistent_command' is not a loaded command or does not exist"
}
```

### Ошибка - Встроенная команда

```json
{
  "command": "unload",
  "params": {
    "command_name": "help"
  }
}
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "success": false,
    "command_name": "help",
    "error": "Command 'help' is not a loaded command or does not exist"
  },
  "message": "Failed to unload commands from help: Command 'help' is not a loaded command or does not exist"
}
```

## Обработка ошибок

Команда обрабатывает различные сценарии ошибок:

- **Команда не найдена**: Возвращает ошибку, когда указанная команда не существует
- **Не загруженная команда**: Возвращает ошибку при попытке выгрузить встроенные или пользовательские команды
- **Ошибки реестра**: Возвращает ошибку при проблемах с реестром команд

## Приоритет команд

Команда unload соблюдает иерархию приоритетов команд:

1. **Пользовательские команды** (высший приоритет) - Не могут быть выгружены
2. **Встроенные команды** - Не могут быть выгружены
3. **Загруженные команды** (низший приоритет) - Могут быть выгружены

Это обеспечивает стабильность системы, предотвращая удаление критически важных команд.

## Пример рабочего процесса

```python
# 1. Загрузить команду
load_result = await execute_command("load", {"source": "./my_command.py"})

# 2. Использовать загруженную команду
use_result = await execute_command("my_command", {"param": "value"})

# 3. Выгрузить команду, когда она больше не нужна
unload_result = await execute_command("unload", {"command_name": "my_command"})

# 4. Команда больше не доступна
# Это не сработает:
# error_result = await execute_command("my_command", {"param": "value"})
```

## Лучшие практики

1. **Загрузить перед использованием**: Всегда загружайте команды перед попыткой их использования
2. **Выгрузить когда закончили**: Выгружайте команды, когда они больше не нужны, чтобы освободить память
3. **Проверить статус**: Используйте ответ команды load для проверки успешной загрузки перед выгрузкой
4. **Обработка ошибок**: Всегда проверяйте статус успеха операций выгрузки
5. **Повторное использование**: Команды могут быть перезагружены после выгрузки, если они снова понадобятся 