# Публикация пакета на PyPI

## Введение

В этом документе описан процесс публикации пакета `mcp_proxy_adapter` на PyPI (Python Package Index).

## Предварительные требования

1. Аккаунт на [PyPI](https://pypi.org/)
2. Установленные инструменты для сборки и публикации:
   ```bash
   pip install build twine
   ```
3. Настроенные учетные данные PyPI (можно использовать токен API)

## Способы публикации

Существует несколько способов опубликовать пакет:

### 1. Использование скрипта publish.py

Самый простой способ опубликовать пакет - использовать скрипт `publish.py` в корне проекта:

```bash
# Публикация в TestPyPI (тестовый сервер)
python publish.py --test

# Публикация в основной PyPI
python publish.py
```

Этот скрипт выполняет:
- Очистку предыдущих сборок
- Сборку нового пакета
- Запуск тестов установки
- Публикацию в PyPI

### 2. Использование скрипта scripts/publish.py

Альтернативный скрипт для публикации с дополнительными опциями:

```bash
# Только сборка пакета без загрузки
python scripts/publish.py --build-only

# Публикация в TestPyPI
python scripts/publish.py --test

# Публикация в основной PyPI без очистки директорий сборки
python scripts/publish.py --no-clean
```

### 3. Ручная публикация

Можно также выполнить процесс публикации вручную:

```bash
# Очистка предыдущих сборок
rm -rf build/ dist/ *.egg-info/

# Сборка пакета
python -m build

# Публикация в TestPyPI
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Публикация в основной PyPI
python -m twine upload dist/*
```

### 4. GitHub Actions

Проект настроен на автоматическую публикацию через GitHub Actions при создании тега версии:

1. Создайте и отправьте тег версии:
   ```bash
   git tag v3.0.1
   git push origin v3.0.1
   ```

2. GitHub Actions автоматически запустит тесты и опубликует пакет на PyPI после успешного прохождения тестов.

## Настройка учетных данных PyPI

### Вариант 1: Файл .pypirc

Создайте файл `~/.pypirc` со следующим содержимым:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJGYwMjU5YWVlLWEzYTktNGQwMy1iNWM1LTQzYmJmNjQ4NWY5MwACKlszLCJjMzZiMTJkNi00ZDJjLTQwYjAtOWI5ZS1mZjQ4YTUxNWNhOWEiXQAABiDhI_H_1wPtcPqxvbMeA9eCKHLDJj9UwMECE-XiO6vNNg

[testpypi]
username = __token__
password = pypi-AgENdGVzdC5weXBpLm9yZwIkZGE0MzE0NzAtMmQ5OS00YjIwLTk1NTYtMzI4ZDIwOTVhZGU0AAIqWzMsIjM0MTI5OGY2LWM5YzItNDdlMi05OGU2LThkOTA0MDQzYzIyOCJdAAAGIOQh9aXVQkIqwTfwDDnBPokEZuq1OuWDJYHpS-i7UR4c
```

Замените токены на ваши собственные.

### Вариант 2: Переменные окружения

Вместо файла конфигурации можно использовать переменные окружения:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmcCJGYwMjU5YWVlLWEzYTktNGQwMy1iNWM1LTQzYmJmNjQ4NWY5MwACKlszLCJjMzZiMTJkNi00ZDJjLTQwYjAtOWI5ZS1mZjQ4YTUxNWNhOWEiXQAABiDhI_H_1wPtcPqxvbMeA9eCKHLDJj9UwMECE-XiO6vNNg
```

## Подготовка к публикации

### 1. Обновление версии

Перед публикацией обновите версию пакета в файле `mcp_proxy_adapter/version.py`:

```python
__version__ = "3.0.1"
```

### 2. Обновление CHANGELOG.md

Добавьте информацию о новой версии в файлы:
- `CHANGELOG.md`
- `CHANGELOG_ru.md`

### 3. Проверка метаданных пакета

Убедитесь, что все метаданные в файле `pyproject.toml` актуальны.

## Проверка пакета после публикации

После публикации полезно убедиться, что пакет корректно устанавливается и работает:

```bash
# Создание временного окружения
python -m venv test_env
source test_env/bin/activate

# Установка пакета
pip install mcp-proxy-adapter

# Проверка импорта
python -c "import mcp_proxy_adapter; print(mcp_proxy_adapter.__version__)"

# Деактивация окружения
deactivate
rm -rf test_env
```

## Устранение проблем

### Ошибка аутентификации

Если вы получаете ошибку аутентификации, проверьте:
- Корректность токена
- Срок действия токена
- Права доступа токена (должны включать публикацию)

### Ошибка валидации метаданных

Если PyPI отклоняет пакет из-за проблем с метаданными:
- Проверьте наличие всех необходимых полей в `pyproject.toml`
- Убедитесь, что описание пакета корректно форматировано
- Проверьте уникальность имени пакета

## Дополнительные материалы

- [Официальная документация по публикации на PyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Документация Twine](https://twine.readthedocs.io/en/latest/)
- [Документация Build](https://pypa-build.readthedocs.io/en/latest/) 