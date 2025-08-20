# Карта документации

**Содержание**: 1. Обзор • 2. Обязательные файлы • 3. Навигатор по документации • 4. Индекс поиска

## 1. Обзор

Этот документ представляет собой навигационный обзор всей доступной документации проекта MCP Microservice.
Этот документ служит централизованной картой документации MCP Microservice. Он предоставляет ссылки на ключевые файлы документации и помогает ориентироваться в структуре документации.

## 2. Обязательные файлы

Следующие файлы должны существовать в обеих языковых версиях:

### 2.1. Основная документация

| Документация | Английский | Русский |
|---------------|---------|---------|
| Правила проекта | [PROJECT_RULES.md](../EN/PROJECT_RULES.md) | [PROJECT_RULES.md](./PROJECT_RULES.md) |
| Стандарты именования | [NAMING_STANDARDS.md](../EN/NAMING_STANDARDS.md) | [NAMING_STANDARDS.md](./NAMING_STANDARDS.md) |
| Архитектура проекта | [BASIC_ARCHITECTURE.md](../EN/BASIC_ARCHITECTURE.md) | [BASIC_ARCHITECTURE.md](./BASIC_ARCHITECTURE.md) |
| Структура проекта | [PROJECT_STRUCTURE.md](../EN/PROJECT_STRUCTURE.md) | [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) |
| Идеология проекта | [PROJECT_IDEOLOGY.md](../EN/PROJECT_IDEOLOGY.md) | [PROJECT_IDEOLOGY.md](./PROJECT_IDEOLOGY.md) |
| Схема API | [API_SCHEMA.md](../EN/API_SCHEMA.md) | [API_SCHEMA.md](./API_SCHEMA.md) |
| Стандарты документации | [DOCUMENTATION_STANDARDS.md](../EN/DOCUMENTATION_STANDARDS.md) | [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md) |
| Шаблон команды | [COMMAND_TEMPLATE.md](../EN/COMMAND_TEMPLATE.md) | [COMMAND_TEMPLATE.md](./COMMAND_TEMPLATE.md) |
| Чек-лист команды | [COMMAND_CHECKLIST.md](../EN/COMMAND_CHECKLIST.md) | [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md) |
| Логирование | [LOGGING_SYSTEM.md](../EN/LOGGING_SYSTEM.md) | [LOGGING_SYSTEM.md](./LOGGING_SYSTEM.md) |
| Обработка ошибок | [ERROR_HANDLING.md](../EN/ERROR_HANDLING.md) | [ERROR_HANDLING.md](./ERROR_HANDLING.md) |
| Результаты команд | [COMMAND_RESULTS.md](../EN/COMMAND_RESULTS.md) | [COMMAND_RESULTS.md](./COMMAND_RESULTS.md) |
| Принципы конфигурации | [CONFIGURATION_PRINCIPLES.md](../EN/CONFIGURATION_PRINCIPLES.md) | [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md) |
| Расширение проекта | [PROJECT_EXTENSION_GUIDE.md](../EN/PROJECT_EXTENSION_GUIDE.md) | [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md) |
| Публикация на PyPI | [PUBLISHING_TO_PYPI.md](../EN/PUBLISHING_TO_PYPI.md) | [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md) |
| Автоматизированная публикация | [AUTOMATED_PUBLISHING.md](../EN/AUTOMATED_PUBLISHING.md) | [AUTOMATED_PUBLISHING.md](./AUTOMATED_PUBLISHING.md) |

### 2.2. Документация команд

| Команда | Английский | Русский |
|---------|---------|---------|
| get_date | [get_date_command.md](../EN/commands/get_date_command.md) | [get_date_command.md](./commands/get_date_command.md) |
| new_uuid4 | [new_uuid4_command.md](../EN/commands/new_uuid4_command.md) | [new_uuid4_command.md](./commands/new_uuid4_command.md) |

## 3. Навигатор по документации

### 3.1. Для разработчиков

- **Новичок в проекте?** Начните с [PROJECT_RULES.md](./PROJECT_RULES.md)
- **Добавляете команду?** Следуйте [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md) и используйте [COMMAND_TEMPLATE.md](./COMMAND_TEMPLATE.md)
- **Соглашения об именовании?** См. [NAMING_STANDARDS.md](./NAMING_STANDARDS.md)
- **Руководство по документации?** Прочтите [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md)
- **Справочник терминологии?** Проверьте [GLOSSARY.md](./GLOSSARY.md)
- **Настройка конфигурации?** См. [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)
- **Расширение проекта?** Следуйте [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md)
- **Обработка ошибок?** Изучите [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- **Публикация пакета?** Следуйте [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md)

### 3.2. Для контрибьюторов

- **Чек-лист реализации команды** - [COMMAND_CHECKLIST.md](./COMMAND_CHECKLIST.md)
- **Требования к документации** - [DOCUMENTATION_STANDARDS.md](./DOCUMENTATION_STANDARDS.md)
- **Соглашения об именовании** - [NAMING_STANDARDS.md](./NAMING_STANDARDS.md)
- **Руководство по конфигурации** - [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)
- **Шаги по расширению проекта** - [PROJECT_EXTENSION_GUIDE.md](./PROJECT_EXTENSION_GUIDE.md)
- **Руководство по обработке ошибок** - [ERROR_HANDLING.md](./ERROR_HANDLING.md)
- **Руководство по публикации** - [PUBLISHING_TO_PYPI.md](./PUBLISHING_TO_PYPI.md)

### 3.3. Для пользователей API

- **Доступные команды** - Просмотрите [директорию команд](./commands/)
- **Примеры использования команд** - Документация каждой команды включает примеры на Python, JSON-RPC и HTTP REST
- **Обработка ошибок** - См. [ERROR_HANDLING.md](./ERROR_HANDLING.md) и раздел 6 в документации каждой команды
- **Конфигурация сервиса** - [CONFIGURATION_PRINCIPLES.md](./CONFIGURATION_PRINCIPLES.md)

## 4. Индекс поиска

### 4.1. По теме

- **Команды** - [Шаблон команды](./COMMAND_TEMPLATE.md), [Чек-лист команд](./COMMAND_CHECKLIST.md)
- **Стандарты** - [Стандарты именования](./NAMING_STANDARDS.md), [Стандарты документации](./DOCUMENTATION_STANDARDS.md)
- **Информация о проекте** - [Правила проекта](./PROJECT_RULES.md)
- **Справочник** - [Глоссарий](./GLOSSARY.md)
- **Конфигурация** - [Принципы конфигурации](./CONFIGURATION_PRINCIPLES.md)
- **Разработка** - [Руководство по расширению проекта](./PROJECT_EXTENSION_GUIDE.md)
- **Ошибки и исключения** - [Обработка ошибок](./ERROR_HANDLING.md)
- **Публикация** - [Публикация на PyPI](./PUBLISHING_TO_PYPI.md)

### 4.2. По роли

- **Разработчик** - [Чек-лист команд](./COMMAND_CHECKLIST.md), [Стандарты именования](./NAMING_STANDARDS.md), [Принципы конфигурации](./CONFIGURATION_PRINCIPLES.md), [Руководство по расширению проекта](./PROJECT_EXTENSION_GUIDE.md), [Обработка ошибок](./ERROR_HANDLING.md), [Публикация на PyPI](./PUBLISHING_TO_PYPI.md)
- **Технический писатель** - [Стандарты документации](./DOCUMENTATION_STANDARDS.md), [Шаблон команды](./COMMAND_TEMPLATE.md)
- **Менеджер проекта** - [Правила проекта](./PROJECT_RULES.md)
- **Потребитель API** - Документация команд в [директории команд](./commands/), [Обработка ошибок](./ERROR_HANDLING.md)
- **Системный администратор** - [Принципы конфигурации](./CONFIGURATION_PRINCIPLES.md), [Руководство по расширению проекта](./PROJECT_EXTENSION_GUIDE.md), [Публикация на PyPI](./PUBLISHING_TO_PYPI.md) 