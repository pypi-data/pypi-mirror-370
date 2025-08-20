# Тестирование MCP Proxy Adapter

В этом документе описывается система тестирования для MCP Proxy Adapter.

## Обзор

Система тестирования базируется на фреймворке pytest и включает в себя различные типы тестов:

1. **Модульные тесты (Unit tests)** - тестируют отдельные компоненты системы в изоляции
2. **Интеграционные тесты (Integration tests)** - тестируют взаимодействие между компонентами
3. **Функциональные тесты (Functional tests)** - тестируют конечные точки API и функциональность системы
4. **Тесты производительности (Performance tests)** - проверяют скорость и эффективность работы системы

## Структура тестов

```
mcp_microservice/tests/
├── __init__.py
├── conftest.py             # Общие фикстуры для тестов
├── unit/                   # Модульные тесты
│   ├── __init__.py
│   ├── test_base_command.py
│   └── test_config.py
├── integration/            # Интеграционные тесты
│   ├── __init__.py
│   └── test_integration.py
├── functional/             # Функциональные тесты
│   ├── __init__.py
│   └── test_api.py
└── performance/            # Тесты производительности
    ├── __init__.py
    └── test_performance.py
```

## Запуск тестов

### Запуск всех тестов

```bash
python -m pytest mcp_microservice/tests
```

### Запуск определенного типа тестов

```bash
# Модульные тесты
python -m pytest mcp_microservice/tests/unit

# Интеграционные тесты
python -m pytest mcp_microservice/tests/integration

# Функциональные тесты
python -m pytest mcp_microservice/tests/functional

# Тесты производительности
python -m pytest mcp_microservice/tests/performance
```

### Запуск тестов по маркерам

```bash
# Модульные тесты
python -m pytest mcp_microservice/tests -m unit

# Интеграционные тесты
python -m pytest mcp_microservice/tests -m integration

# Функциональные тесты
python -m pytest mcp_microservice/tests -m functional

# Тесты производительности
python -m pytest mcp_microservice/tests -m performance
```

### Запуск с отчетом о покрытии

```bash
python -m pytest mcp_microservice/tests --cov=mcp_microservice
```

## Фикстуры

Для тестирования используются различные фикстуры, определенные в файле `conftest.py`:

1. `test_config` - создает тестовую конфигурацию
2. `test_client` - создает тестовый HTTP-клиент для API
3. `clean_registry` - очищает реестр команд перед и после теста
4. `json_rpc_request` - создает базовый JSON-RPC запрос
5. `async_client` - создает асинхронный HTTP-клиент для тестов производительности

## Создание новых тестов

### Модульные тесты

```python
import pytest

@pytest.mark.unit
def test_example():
    # Тестовый код
    assert True
```

### Интеграционные тесты

```python
import pytest

@pytest.mark.integration
def test_integration_example(clean_registry):
    # Тестовый код
    assert True
```

### Функциональные тесты

```python
import pytest

@pytest.mark.functional
def test_api_example(test_client):
    # Тестовый код
    response = test_client.get("/health")
    assert response.status_code == 200
```

### Тесты производительности

```python
import pytest
import time

@pytest.mark.performance
@pytest.mark.asyncio
async def test_performance_example(async_client):
    # Тестовый код
    start_time = time.time()
    # Выполнение операции
    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 1.0  # Проверка производительности
```

## Непрерывная интеграция (CI)

Тесты автоматически запускаются в GitHub Actions при каждом pull request и push в основные ветки.

Файл конфигурации `.github/workflows/tests.yml` определяет следующие шаги:

1. Запуск линтера (flake8)
2. Проверка форматирования кода (black)
3. Запуск всех типов тестов
4. Измерение покрытия кода тестами
5. Загрузка отчета о покрытии

## Лучшие практики

1. Все тесты должны быть независимыми и не иметь побочных эффектов
2. Используйте подходящие фикстуры для настройки и очистки среды
3. Добавляйте соответствующие маркеры к тестам
4. Используйте отдельные тесты для отдельных аспектов функциональности
5. Для тестов API используйте test_client, а для тестов производительности - async_client
6. Не забывайте проверять успешные и неуспешные сценарии

## Расширение системы тестирования

Для добавления новых типов тестов:

1. Создайте новую директорию в `mcp_microservice/tests/`
2. Добавьте соответствующий маркер в `pytest.ini`
3. Создайте фикстуры в `conftest.py` при необходимости
4. Добавьте тесты в новую директорию с соответствующими маркерами 