# MCP Security Framework - Примеры использования

**Версия:** 1.0.0  
**Дата:** 17 августа 2025  

## 🚀 Быстрый старт

### Установка

```bash
pip install mcp-security
```

### Минимальный пример

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Базовая настройка безопасности
SecurityMiddleware.setup(app, {
    "auth_enabled": True,
    "ssl": {"enabled": False},  # HTTP для простоты
    "roles": {"enabled": False}  # Без ролей для начала
})

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 🔐 Аутентификация

### API Key аутентификация

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка API Key аутентификации
config = {
    "auth_enabled": True,
    "auth": {
        "enabled": True,
        "api_keys": {
            "user1": "api_key_12345",
            "admin": "admin_key_67890"
        },
        "public_paths": ["/docs", "/health"]
    }
}

SecurityMiddleware.setup(app, config)

@app.get("/secure")
async def secure_endpoint():
    return {"message": "This endpoint requires API key"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### JWT Token аутентификация

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка JWT аутентификации
config = {
    "auth_enabled": True,
    "ssl": {
        "enabled": True,
        "mode": "https_only",
        "token_auth": {
            "enabled": True,
            "jwt_secret": "your-super-secret-key-change-in-production",
            "token_expiry": 3600,
            "header_name": "Authorization",
            "token_prefix": "Bearer"
        }
    }
}

SecurityMiddleware.setup(app, config)

@app.get("/api/data")
async def get_data():
    return {"data": "sensitive information"}
```

## 🎭 Ролевая система (RBAC)

### Создание схемы ролей

```python
from mcp_security.schemas.models import (
    RolesSchema, Role, Permission, RoleHierarchy, DefaultPolicy
)
from mcp_security.utils import SchemaLoader

# Создание разрешений
permissions = {
    "read": Permission(description="Read access", level=1),
    "write": Permission(description="Write access", level=2),
    "delete": Permission(description="Delete access", level=3),
    "admin": Permission(description="Admin access", level=4)
}

# Создание ролей
roles = {
    "admin": Role(
        description="Administrator",
        allowed_servers=["*"],
        allowed_clients=["*"],
        permissions=["read", "write", "delete", "admin"],
        priority=100
    ),
    "user": Role(
        description="Regular user",
        allowed_servers=["basic_commands"],
        allowed_clients=["admin", "user"],
        permissions=["read"],
        priority=10
    )
}

# Создание иерархии ролей
role_hierarchy = RoleHierarchy(roles={
    "admin": ["user"]
})

# Создание политики по умолчанию
default_policy = DefaultPolicy(
    deny_by_default=True,
    require_role_match=True,
    case_sensitive=False,
    allow_wildcard=True
)

# Создание схемы ролей
roles_schema = RolesSchema(
    roles=roles,
    permissions=permissions,
    role_hierarchy=role_hierarchy,
    default_policy=default_policy
)

# Сохранение схемы
SchemaLoader.save_roles_schema(roles_schema, "roles_schema.json")
```

### Использование ролевой системы

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware
from mcp_security.utils import PermissionValidator, SchemaLoader

app = FastAPI()

# Загрузка схемы ролей
roles_schema = SchemaLoader.load_roles_schema("roles_schema.json")

# Создание валидатора
validator = PermissionValidator(roles_schema)

# Настройка безопасности с ролями
config = {
    "auth_enabled": True,
    "roles": {
        "enabled": True,
        "config_file": "roles_schema.json"
    }
}

SecurityMiddleware.setup(app, config)

@app.get("/admin/data")
async def admin_data():
    # Проверка доступа
    result = validator.validate_access(
        user_roles=["admin"],
        required_permissions=["read", "admin"],
        server_role="admin_panel"
    )
    
    if not result.is_valid:
        return {"error": "Access denied", "details": result.error_message}
    
    return {"data": "admin only data"}

@app.get("/user/data")
async def user_data():
    result = validator.validate_access(
        user_roles=["user"],
        required_permissions=["read"],
        server_role="basic_commands"
    )
    
    if not result.is_valid:
        return {"error": "Access denied"}
    
    return {"data": "user data"}
```

## 🔒 SSL/TLS и mTLS

### HTTPS настройка

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка HTTPS
config = {
    "ssl": {
        "enabled": True,
        "mode": "https_only",
        "cert_file": "./certs/server.crt",
        "key_file": "./certs/server.key",
        "min_tls_version": "1.2",
        "max_tls_version": "1.3",
        "cipher_suites": [
            "TLS_AES_256_GCM_SHA384",
            "TLS_CHACHA20_POLY1305_SHA256"
        ]
    }
}

SecurityMiddleware.setup(app, config)
```

### mTLS настройка

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка mTLS
config = {
    "ssl": {
        "enabled": True,
        "mode": "mtls",
        "cert_file": "./certs/server.crt",
        "key_file": "./certs/server.key",
        "ca_cert": "./certs/ca.crt",
        "verify_client": True,
        "client_cert_required": True
    },
    "roles": {
        "enabled": True,
        "config_file": "roles_schema.json"
    }
}

SecurityMiddleware.setup(app, config)

@app.get("/mtls-secure")
async def mtls_secure():
    return {"message": "mTLS secured endpoint"}
```

## ⚡ Rate Limiting

### Настройка ограничений

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка rate limiting
config = {
    "rate_limit": {
        "enabled": True,
        "requests_per_minute": 100,
        "time_window": 60,
        "by_ip": True,
        "by_user": True,
        "public_paths": ["/docs", "/health"]
    }
}

SecurityMiddleware.setup(app, config)

@app.get("/api/resource")
async def limited_resource():
    return {"message": "Rate limited resource"}
```

## 🛠️ Утилиты

### Валидация разрешений

```python
from mcp_security.utils import PermissionValidator, SchemaLoader

# Загрузка схемы
schema = SchemaLoader.load_roles_schema("roles_schema.json")

# Создание валидатора
validator = PermissionValidator(schema)

# Проверка различных сценариев
test_cases = [
    {
        "user_roles": ["admin"],
        "required_permissions": ["read", "write"],
        "server_role": "kubernetes_manager",
        "expected": True
    },
    {
        "user_roles": ["user"],
        "required_permissions": ["admin"],
        "server_role": "admin_panel",
        "expected": False
    },
    {
        "user_roles": ["user"],
        "required_permissions": ["read"],
        "server_role": "basic_commands",
        "expected": True
    }
]

for case in test_cases:
    result = validator.validate_access(
        user_roles=case["user_roles"],
        required_permissions=case["required_permissions"],
        server_role=case["server_role"]
    )
    
    print(f"Test: {case['user_roles']} -> {case['required_permissions']}")
    print(f"Result: {result.is_valid} (expected: {case['expected']})")
    if not result.is_valid:
        print(f"Error: {result.error_message}")
    print()
```

### Сериализация/десериализация

```python
from mcp_security.utils import SecuritySerializer, SchemaLoader
from mcp_security.schemas.models import SecurityConfig

# Создание конфигурации
config = SecurityConfig(
    auth_enabled=True,
    ssl_enabled=True
)

# Сериализация в JSON
serializer = SecuritySerializer()
json_data = serializer.serialize_security_config(config)
print("Serialized config:")
print(json_data)

# Десериализация из JSON
loaded_config = serializer.deserialize_security_config(json_data)
print(f"Loaded config auth_enabled: {loaded_config.auth_enabled}")

# Загрузка и сохранение схемы ролей
schema = SchemaLoader.create_default_roles_schema()
SchemaLoader.save_roles_schema(schema, "default_roles.json")

loaded_schema = SchemaLoader.load_roles_schema("default_roles.json")
print(f"Loaded schema has {len(loaded_schema.roles)} roles")
```

## 🔧 CLI команды

### Валидация схем

```bash
# Валидация схемы ролей
mcp-security validate-schema roles_schema.json

# Создание схемы по умолчанию
mcp-security create-default-schema --output default_roles.json

# Проверка конфигурации
mcp-security validate-config security_config.json
```

### Валидация разрешений

```bash
# Проверка доступа пользователя
mcp-security validate-permissions \
    --user admin \
    --permission read,write \
    --server kubernetes_manager \
    --schema roles_schema.json

# Проверка иерархии ролей
mcp-security check-role-hierarchy \
    --user-role admin \
    --required-role user \
    --schema roles_schema.json
```

### Генерация сертификатов

```bash
# Создание CA сертификата
mcp-security generate-certificates \
    --ca \
    --common-name "My CA" \
    --output-dir ./certs

# Создание серверного сертификата
mcp-security generate-certificates \
    --server \
    --common-name "server.example.com" \
    --ca-cert ./certs/ca.crt \
    --ca-key ./certs/ca.key \
    --output-dir ./certs

# Создание клиентского сертификата
mcp-security generate-certificates \
    --client \
    --common-name "client.example.com" \
    --ca-cert ./certs/ca.crt \
    --ca-key ./certs/ca.key \
    --output-dir ./certs
```

## 🔍 Интеграционные примеры

### Полная интеграция с FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from mcp_security.middleware import SecurityMiddleware
from mcp_security.utils import PermissionValidator, SchemaLoader

app = FastAPI(title="Secure API", version="1.0.0")

# Загрузка конфигурации
security_config = {
    "auth_enabled": True,
    "ssl": {
        "enabled": True,
        "mode": "https_only",
        "cert_file": "./certs/server.crt",
        "key_file": "./certs/server.key"
    },
    "roles": {
        "enabled": True,
        "config_file": "schemas/roles_schema.json"
    },
    "rate_limit": {
        "enabled": True,
        "requests_per_minute": 100
    }
}

# Настройка безопасности
SecurityMiddleware.setup(app, security_config)

# Загрузка схемы ролей
roles_schema = SchemaLoader.load_roles_schema("schemas/roles_schema.json")
validator = PermissionValidator(roles_schema)

# Зависимость для проверки разрешений
def require_permissions(permissions: list, server_role: str = None):
    def dependency(request):
        # Получение ролей пользователя из request.state
        user_roles = getattr(request.state, 'user_roles', [])
        
        result = validator.validate_access(
            user_roles=user_roles,
            required_permissions=permissions,
            server_role=server_role
        )
        
        if not result.is_valid:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: {result.error_message}"
            )
        
        return result
    
    return dependency

@app.get("/api/admin/users")
async def get_users(
    result=Depends(require_permissions(["read", "admin"], "admin_panel"))
):
    return {"users": ["user1", "user2", "user3"]}

@app.post("/api/admin/users")
async def create_user(
    user_data: dict,
    result=Depends(require_permissions(["write", "admin"], "admin_panel"))
):
    return {"message": "User created", "user": user_data}

@app.get("/api/public/info")
async def get_public_info():
    return {"info": "Public information"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8443,
        ssl_keyfile="./certs/server.key",
        ssl_certfile="./certs/server.crt"
    )
```

### Тестирование безопасности

```python
import pytest
from fastapi.testclient import TestClient
from mcp_security.utils import PermissionValidator, SchemaLoader

def test_permission_validation():
    # Загрузка тестовой схемы
    schema = SchemaLoader.create_default_roles_schema()
    validator = PermissionValidator(schema)
    
    # Тест 1: Админ имеет доступ к чтению
    result = validator.validate_access(
        user_roles=["admin"],
        required_permissions=["read"],
        server_role="any_server"
    )
    assert result.is_valid
    
    # Тест 2: Пользователь не имеет админских прав
    result = validator.validate_access(
        user_roles=["user"],
        required_permissions=["admin"],
        server_role="admin_panel"
    )
    assert not result.is_valid
    
    # Тест 3: Проверка иерархии ролей
    assert validator.check_role_hierarchy("admin", "user")
    assert not validator.check_role_hierarchy("user", "admin")

def test_fastapi_integration():
    from fastapi import FastAPI
    from mcp_security.middleware import SecurityMiddleware
    
    app = FastAPI()
    
    # Минимальная конфигурация для тестов
    config = {
        "auth_enabled": False,  # Отключаем для тестов
        "ssl": {"enabled": False},
        "roles": {"enabled": False}
    }
    
    SecurityMiddleware.setup(app, config)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json() == {"message": "test"}
```

## 📊 Мониторинг и аудит

### Логирование безопасности

```python
import logging
from mcp_security.utils import SecurityAuditor

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("security")

# Создание аудитора
auditor = SecurityAuditor(config)

# Запуск аудита
audit_report = auditor.run_security_audit()

logger.info(f"Security score: {audit_report.score}")
logger.info(f"Vulnerabilities found: {len(audit_report.vulnerabilities)}")

for vuln in audit_report.vulnerabilities:
    logger.warning(f"Vulnerability: {vuln.description}")
    logger.warning(f"Severity: {vuln.severity}")
    logger.warning(f"Recommendation: {vuln.recommendation}")
```

### Метрики безопасности

```python
from mcp_security.utils import SecurityMetrics

# Создание метрик
metrics = SecurityMetrics()

# Регистрация событий
metrics.record_auth_attempt(success=True, method="api_key")
metrics.record_auth_attempt(success=False, method="jwt")
metrics.record_permission_check(success=True, user_role="admin")

# Получение статистики
stats = metrics.get_statistics()
print(f"Auth success rate: {stats.auth_success_rate:.2%}")
print(f"Permission check success rate: {stats.permission_success_rate:.2%}")
print(f"Total auth attempts: {stats.total_auth_attempts}")
```
