# Задачи по системе транспорта MCP Proxy Adapter

## 🚨 Критические задачи

### 1. Исправить SSL конфигурацию в uvicorn
**Файлы:** `server.py`, `ssl_utils.py`
**Проблема:** HTTPS сервер запускается по HTTP
**Решение:** Правильно передавать SSL параметры в uvicorn.run()

### 2. Создать Transport Middleware
**Файл:** `transport_middleware.py`
**Проблема:** Текущий protocol_middleware не подходит
**Решение:** Новый middleware для валидации транспорта

### 3. Обновить SSLUtils
**Файл:** `ssl_utils.py`
**Проблема:** Неправильная обработка новой конфигурации
**Решение:** Адаптировать под transport конфигурацию

## 🧪 Тестирование

### Модульные тесты
- [ ] `test_transport_manager.py`
- [ ] `test_transport_management_command.py`
- [ ] `test_transport_middleware.py`

### Интеграционные тесты
- [ ] `test_transport_integration.py`
- [ ] HTTP/HTTPS/MTLS серверы
- [ ] JSON-RPC команды

### Функциональные тесты
- [ ] Обновить `test_transport.py`
- [ ] Тестирование переключения транспортов
- [ ] Валидация конфигураций

## 📋 Чек-лист

### Критические исправления:
- [ ] SSL конфигурация в uvicorn
- [ ] Transport Middleware
- [ ] SSLUtils обновление
- [ ] Валидация SSL файлов

### Тестирование:
- [ ] Модульные тесты
- [ ] Интеграционные тесты
- [ ] Функциональные тесты
- [ ] Тесты производительности

### Документация:
- [ ] API документация
- [ ] Примеры конфигурации
- [ ] README обновление
- [ ] Руководство по миграции

## 🎯 Цели

### Функциональность:
- ✅ HTTP: 100% тестов
- ⚠️ HTTPS: 100% тестов (после исправлений)
- ❓ MTLS: 100% тестов (после тестирования)

### Производительность:
- HTTP latency < 10ms
- HTTPS latency < 20ms
- MTLS latency < 30ms
- Memory usage < 100MB

### Качество:
- Test coverage > 90%
- No security issues
- All linting pass
- Documentation > 95% 