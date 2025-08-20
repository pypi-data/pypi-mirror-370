# Руководство по развертыванию

В этом руководстве описаны различные методы развертывания сервиса MCP Proxy Adapter.

## Требования

- Python 3.9 или выше
- Docker и Docker Compose (для контейнеризованного развертывания)
- Доступ к целевой среде развертывания

## Методы развертывания

### 1. Прямая установка Python

Для простых развертываний или сред разработки:

1. Установите пакет:
   ```bash
   pip install mcp-microservice
   ```

2. Создайте файл конфигурации:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Запустите сервис:
   ```bash
   mcp-microservice --config config.json
   ```

### 2. Docker-контейнер

Для контейнеризованного развертывания:

1. Загрузите Docker-образ:
   ```bash
   docker pull organization/mcp-microservice:latest
   ```

2. Создайте файл конфигурации:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Запустите контейнер:
   ```bash
   docker run -p 8000:8000 -v $(pwd)/config.json:/app/config.json -v $(pwd)/logs:/app/logs organization/mcp-microservice:latest
   ```

### 3. Docker Compose

Для более сложных развертываний:

1. Создайте файл docker-compose.yml:
   ```yaml
   version: '3'

   services:
     mcp-microservice:
       image: organization/mcp-microservice:latest
       ports:
         - "8000:8000"
       volumes:
         - ./config.json:/app/config.json
         - ./logs:/app/logs
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
         interval: 30s
         timeout: 10s
         retries: 3
         start_period: 5s
   ```

2. Создайте файл конфигурации:
   ```bash
   cat > config.json << EOF
   {
     "host": "0.0.0.0",
     "port": 8000,
     "log_level": "INFO",
     "log_file": "logs/mcp_proxy.log",
     "cors_origins": ["*"],
     "api_keys": ["your-api-key-here"]
   }
   EOF
   ```

3. Запустите сервис:
   ```bash
   docker-compose up -d
   ```

### 4. Автоматизированное развертывание

Для непрерывного развертывания:

1. Настройте сервер развертывания с SSH-доступом
2. Настройте переменные окружения для секретов
3. Используйте включенный скрипт развертывания:
   ```bash
   ./scripts/deploy.sh production
   ```

4. Или интегрируйте с системами CI/CD, такими как GitHub Actions или Jenkins

## Конфигурации для разных сред

Мы предоставляем примеры конфигураций для различных сред:

- `config.development.json`: Для локальной разработки
- `config.staging.json`: Для среды предпроизводственного тестирования
- `config.production.json`: Для производственной среды

Выберите соответствующую конфигурацию для вашей среды развертывания.

## Проверка после развертывания

После развертывания убедитесь, что сервис работает корректно:

1. Проверьте эндпоинт health:
   ```bash
   curl http://your-server:8000/api/health
   ```

2. Протестируйте простую команду:
   ```bash
   curl -X POST http://your-server:8000/api/v1/execute \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"jsonrpc": "2.0", "method": "hello_world", "params": {"name": "User"}, "id": 1}'
   ```

3. Проверьте логи на наличие ошибок:
   ```bash
   tail -f logs/mcp_proxy.log
   ```

## Устранение неполадок

Если вы столкнулись с проблемами при развертывании:

1. Проверьте логи на наличие сообщений об ошибках
2. Убедитесь, что файл конфигурации является действительным JSON
3. Убедитесь, что переменные окружения настроены правильно
4. Проверьте, что порты не заняты
5. Убедитесь, что API-ключи настроены правильно 