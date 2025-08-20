# Установка

Это руководство описывает, как установить и развернуть сервис MCP Proxy.

## Предварительные требования

- Python 3.9 или выше
- Менеджер пакетов pip
- (Опционально) Docker для контейнеризированного развертывания

## Установка из PyPI

Самый простой способ установить пакет - через PyPI:

```bash
pip install mcp-proxy
```

## Установка из исходного кода

Для установки из исходного кода выполните следующие шаги:

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/organization/mcp-proxy.git
   cd mcp-proxy
   ```

2. Установите пакет:
   ```bash
   pip install -e .
   ```

## Установка с использованием Docker

Для использования Docker-образа:

1. Загрузите образ:
   ```bash
   docker pull organization/mcp-proxy:latest
   ```

2. Запустите контейнер:
   ```bash
   docker run -p 8000:8000 -v /path/to/config.json:/app/config.json organization/mcp-proxy:latest
   ```

## Проверка установки

Чтобы проверить успешность установки, выполните:

```bash
mcp-proxy --version
```

Это должно отобразить текущую версию сервиса MCP Proxy. 