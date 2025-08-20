# Система транспорта MCP Proxy Adapter - Доработки и тестирование

## 📋 Обзор

Документ описывает необходимые доработки и план тестирования для системы транспорта MCP Proxy Adapter после рефакторинга с мультипортовой системы на систему с одним транспортом.

## 🎯 Текущий статус

### ✅ Реализовано:
- **TransportManager** - управление конфигурацией транспорта
- **Автоматический выбор портов** - HTTP:8000, HTTPS:8443, MTLS:9443
- **Команда `transport_management`** - управление и мониторинг транспорта
- **HTTP транспорт** - 100% функциональность
- **Конфигурация транспорта** - поддержка всех 3 типов
- **Валидация конфигурации** - проверка корректности настроек

### ⚠️ Требует доработки:
- **SSL конфигурация в uvicorn** - передача SSL параметров
- **MTLS тестирование** - полное тестирование с клиентскими сертификатами
- **Middleware для транспорта** - замена protocol middleware

## 🔧 Необходимые доработки

### 1. Исправление SSL конфигурации в uvicorn

#### Проблема:
HTTPS сервер запускается по HTTP вместо HTTPS. SSL конфигурация не передается корректно в uvicorn.

#### Файлы для изменения:
- `mcp_proxy_adapter/examples/custom_commands/server.py`
- `mcp_proxy_adapter/core/ssl_utils.py`

#### Решение:
```python
# В server.py - исправить передачу SSL конфигурации
ssl_config = transport_manager.get_ssl_config()
if ssl_config and transport_manager.is_ssl_enabled():
    uvicorn_ssl_config = SSLUtils.get_ssl_config_for_uvicorn(ssl_config)
    # Убедиться, что все параметры передаются корректно
    uvicorn.run(
        app,
        host=server_settings['host'],
        port=transport_manager.get_port(),
        log_level=server_settings['log_level'].lower(),
        **uvicorn_ssl_config
    )
else:
    # HTTP режим без SSL
    uvicorn.run(
        app,
        host=server_settings['host'],
        port=transport_manager.get_port(),
        log_level=server_settings['log_level'].lower()
    )
```

#### Тестирование:
```bash
# Проверить HTTPS сервер
curl -k -s https://localhost:8443/health
# Должен вернуть JSON ответ

# Проверить SSL сертификат
openssl s_client -connect localhost:8443 -servername localhost
```

### 2. Создание Transport Middleware

#### Проблема:
Текущий `protocol_middleware.py` не подходит для новой системы транспорта.

#### Файлы для создания:
- `mcp_proxy_adapter/api/middleware/transport_middleware.py`

#### Решение:
```python
class TransportMiddleware(BaseHTTPMiddleware):
    """Middleware для валидации транспорта."""
    
    def __init__(self, app, transport_manager_instance=None):
        super().__init__(app)
        self.transport_manager = transport_manager_instance or transport_manager
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Определить тип транспорта из запроса
        transport_type = self._get_request_transport_type(request)
        
        # Проверить, соответствует ли запрос настроенному транспорту
        if not self._is_transport_allowed(transport_type):
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Transport not allowed",
                    "message": f"Transport '{transport_type}' is not allowed. Configured transport: {self.transport_manager.get_transport_type().value}",
                    "configured_transport": self.transport_manager.get_transport_type().value
                }
            )
        
        response = await call_next(request)
        return response
    
    def _get_request_transport_type(self, request: Request) -> str:
        """Определить тип транспорта из запроса."""
        if request.url.scheme == "https":
            # Проверить наличие клиентского сертификата для MTLS
            if self._has_client_certificate(request):
                return "mtls"
            return "https"
        return "http"
    
    def _has_client_certificate(self, request: Request) -> bool:
        """Проверить наличие клиентского сертификата."""
        # Реализация проверки клиентского сертификата
        pass
    
    def _is_transport_allowed(self, transport_type: str) -> bool:
        """Проверить, разрешен ли тип транспорта."""
        configured_type = self.transport_manager.get_transport_type().value
        return transport_type == configured_type
```

#### Тестирование:
```bash
# HTTP сервер должен принимать только HTTP запросы
curl -s http://localhost:8000/health  # ✅ OK
curl -k -s https://localhost:8000/health  # ❌ 403 Forbidden

# HTTPS сервер должен принимать только HTTPS запросы
curl -k -s https://localhost:8443/health  # ✅ OK
curl -s http://localhost:8443/health  # ❌ 403 Forbidden
```

### 3. Обновление SSLUtils для новой конфигурации

#### Проблема:
`SSLUtils.get_ssl_config_for_uvicorn()` может не корректно обрабатывать новую структуру конфигурации.

#### Файлы для изменения:
- `mcp_proxy_adapter/core/ssl_utils.py`

#### Решение:
```python
@staticmethod
def get_ssl_config_for_uvicorn(ssl_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получить SSL конфигурацию для uvicorn из transport конфигурации.
    
    Args:
        ssl_config: SSL конфигурация из transport manager
        
    Returns:
        Конфигурация для uvicorn
    """
    uvicorn_ssl = {}
    
    if not ssl_config:
        return uvicorn_ssl
    
    # Базовые SSL параметры
    if ssl_config.get("cert_file"):
        uvicorn_ssl["ssl_certfile"] = ssl_config["cert_file"]
    
    if ssl_config.get("key_file"):
        uvicorn_ssl["ssl_keyfile"] = ssl_config["key_file"]
    
    if ssl_config.get("ca_cert"):
        uvicorn_ssl["ssl_ca_certs"] = ssl_config["ca_cert"]
    
    # Настройки проверки клиента
    if ssl_config.get("verify_client", False):
        # Для MTLS - требовать клиентский сертификат
        uvicorn_ssl["ssl_verify_mode"] = ssl.CERT_REQUIRED
    else:
        # Для HTTPS - не требовать клиентский сертификат
        uvicorn_ssl["ssl_verify_mode"] = ssl.CERT_NONE
    
    return uvicorn_ssl
```

#### Тестирование:
```bash
# Проверить создание SSL контекста
python -c "
from mcp_proxy_adapter.core.ssl_utils import SSLUtils
config = {
    'cert_file': 'test_env/server/server.crt',
    'key_file': 'test_env/server/server.key',
    'ca_cert': 'test_env/ca/ca.crt',
    'verify_client': True
}
uvicorn_config = SSLUtils.get_ssl_config_for_uvicorn(config)
print('Uvicorn SSL config:', uvicorn_config)
"
```

### 4. Улучшение TransportManager

#### Проблема:
Некоторые методы могут быть улучшены для лучшей обработки ошибок и валидации.

#### Файлы для изменения:
- `mcp_proxy_adapter/core/transport_manager.py`

#### Доработки:
```python
def validate_ssl_files(self) -> bool:
    """Проверить существование SSL файлов."""
    if not self._config or not self._config.ssl_enabled:
        return True
    
    files_to_check = []
    if self._config.cert_file:
        files_to_check.append(self._config.cert_file)
    if self._config.key_file:
        files_to_check.append(self._config.key_file)
    if self._config.ca_cert:
        files_to_check.append(self._config.ca_cert)
    
    for file_path in files_to_check:
        if not Path(file_path).exists():
            logger.error(f"SSL file not found: {file_path}")
            return False
    
    return True

def get_uvicorn_config(self) -> Dict[str, Any]:
    """Получить конфигурацию для uvicorn."""
    config = {
        "host": "0.0.0.0",  # Можно вынести в настройки
        "port": self.get_port(),
        "log_level": "info"
    }
    
    if self.is_ssl_enabled():
        ssl_config = self.get_ssl_config()
        if ssl_config:
            from mcp_proxy_adapter.core.ssl_utils import SSLUtils
            uvicorn_ssl = SSLUtils.get_ssl_config_for_uvicorn(ssl_config)
            config.update(uvicorn_ssl)
    
    return config
```

## 🧪 План тестирования

### 1. Модульные тесты

#### Файлы для создания:
- `tests/core/test_transport_manager.py`
- `tests/commands/test_transport_management_command.py`
- `tests/api/middleware/test_transport_middleware.py`

#### Тесты для TransportManager:
```python
def test_load_config_http():
    """Тест загрузки HTTP конфигурации."""
    manager = TransportManager()
    config = {
        "transport": {
            "type": "http",
            "port": None,
            "ssl": {"enabled": False}
        }
    }
    
    assert manager.load_config(config) == True
    assert manager.get_transport_type() == TransportType.HTTP
    assert manager.get_port() == 8000
    assert manager.is_ssl_enabled() == False

def test_load_config_https():
    """Тест загрузки HTTPS конфигурации."""
    manager = TransportManager()
    config = {
        "transport": {
            "type": "https",
            "port": None,
            "ssl": {
                "enabled": True,
                "cert_file": "test_env/server/server.crt",
                "key_file": "test_env/server/server.key"
            }
        }
    }
    
    assert manager.load_config(config) == True
    assert manager.get_transport_type() == TransportType.HTTPS
    assert manager.get_port() == 8443
    assert manager.is_ssl_enabled() == True

def test_load_config_mtls():
    """Тест загрузки MTLS конфигурации."""
    manager = TransportManager()
    config = {
        "transport": {
            "type": "mtls",
            "port": None,
            "ssl": {
                "enabled": True,
                "cert_file": "test_env/server/server.crt",
                "key_file": "test_env/server/server.key",
                "ca_cert": "test_env/ca/ca.crt",
                "verify_client": True
            }
        }
    }
    
    assert manager.load_config(config) == True
    assert manager.get_transport_type() == TransportType.MTLS
    assert manager.get_port() == 9443
    assert manager.is_ssl_enabled() == True
    assert manager.is_mtls() == True
```

### 2. Интеграционные тесты

#### Файлы для создания:
- `tests/integration/test_transport_integration.py`

#### Тесты:
```python
async def test_http_transport_integration():
    """Интеграционный тест HTTP транспорта."""
    # Запустить HTTP сервер
    # Протестировать подключение
    # Протестировать JSON-RPC
    # Остановить сервер

async def test_https_transport_integration():
    """Интеграционный тест HTTPS транспорта."""
    # Запустить HTTPS сервер
    # Протестировать SSL подключение
    # Протестировать JSON-RPC
    # Остановить сервер

async def test_mtls_transport_integration():
    """Интеграционный тест MTLS транспорта."""
    # Запустить MTLS сервер
    # Протестировать с клиентским сертификатом
    # Протестировать JSON-RPC
    # Остановить сервер
```

### 3. Функциональные тесты

#### Обновить существующую утилиту:
- `scripts/test_transport.py`

#### Добавить тесты:
```python
async def test_transport_switching():
    """Тест переключения между транспортами."""
    # HTTP -> HTTPS -> MTLS -> HTTP
    # Проверить корректность переключения

async def test_transport_validation():
    """Тест валидации транспорта."""
    # Неправильные конфигурации
    # Отсутствующие файлы
    # Неправильные порты

async def test_transport_commands():
    """Тест команд управления транспортом."""
    # get_info
    # validate
    # reload
```

### 4. Тестирование производительности

#### Файлы для создания:
- `tests/performance/test_transport_performance.py`

#### Тесты:
```python
async def test_transport_performance():
    """Тест производительности транспорта."""
    # HTTP vs HTTPS vs MTLS
    # Latency измерения
    # Throughput измерения
    # Memory usage
```

## 📋 Чек-лист доработок

### Критические доработки:
- [ ] Исправить SSL конфигурацию в uvicorn
- [ ] Создать Transport Middleware
- [ ] Обновить SSLUtils
- [ ] Добавить валидацию SSL файлов

### Тестирование:
- [ ] Модульные тесты для TransportManager
- [ ] Модульные тесты для TransportManagementCommand
- [ ] Модульные тесты для Transport Middleware
- [ ] Интеграционные тесты
- [ ] Функциональные тесты
- [ ] Тесты производительности

### Документация:
- [ ] Обновить API документацию
- [ ] Создать примеры конфигурации
- [ ] Обновить README
- [ ] Создать руководство по миграции

### Дополнительные улучшения:
- [ ] Добавить логирование транспорта
- [ ] Добавить метрики транспорта
- [ ] Добавить мониторинг транспорта
- [ ] Добавить автоматическое переключение транспорта

## 🚀 План реализации

### Этап 1: Критические исправления (1-2 дня)
1. Исправить SSL конфигурацию в uvicorn
2. Создать базовый Transport Middleware
3. Обновить SSLUtils

### Этап 2: Тестирование (2-3 дня)
1. Написать модульные тесты
2. Написать интеграционные тесты
3. Обновить функциональные тесты

### Этап 3: Документация и улучшения (1-2 дня)
1. Обновить документацию
2. Добавить дополнительные улучшения
3. Финальное тестирование

## 📊 Метрики успеха

### Функциональные метрики:
- ✅ HTTP транспорт: 100% тестов проходят
- ✅ HTTPS транспорт: 100% тестов проходят
- ✅ MTLS транспорт: 100% тестов проходят
- ✅ Команды управления: 100% тестов проходят

### Производительность:
- HTTP latency < 10ms
- HTTPS latency < 20ms
- MTLS latency < 30ms
- Memory usage < 100MB

### Качество кода:
- Test coverage > 90%
- No critical security issues
- All linting checks pass
- Documentation coverage > 95%

## 🔍 Мониторинг и отладка

### Логирование:
```python
# Добавить в TransportManager
logger.info(f"Transport config loaded: {transport_type.value} on port {port}")
logger.debug(f"SSL config: {ssl_config}")
logger.warning(f"SSL file not found: {file_path}")
logger.error(f"Transport validation failed: {error}")
```

### Метрики:
```python
# Добавить метрики транспорта
transport_requests_total = Counter('transport_requests_total', 'Total transport requests', ['transport_type'])
transport_request_duration = Histogram('transport_request_duration', 'Transport request duration', ['transport_type'])
transport_errors_total = Counter('transport_errors_total', 'Total transport errors', ['transport_type', 'error_type'])
```

### Отладка:
```bash
# Включить debug логирование
export LOG_LEVEL=DEBUG

# Проверить SSL конфигурацию
openssl s_client -connect localhost:8443 -servername localhost

# Проверить сертификаты
openssl x509 -in test_env/server/server.crt -text -noout
```

## 📝 Заключение

Система транспорта MCP Proxy Adapter успешно рефакторирована с мультипортовой системы на систему с одним транспортом. Основная архитектура работает корректно, но требуются доработки для полной функциональности SSL/MTLS и улучшения тестирования.

После выполнения всех доработок система будет полностью готова к продакшн использованию с поддержкой всех типов транспорта (HTTP, HTTPS, MTLS) и полным набором тестов. 