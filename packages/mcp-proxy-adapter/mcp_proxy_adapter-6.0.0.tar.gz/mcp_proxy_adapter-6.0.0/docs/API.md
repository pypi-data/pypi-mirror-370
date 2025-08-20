# MCP Security Framework API Documentation

**Версия:** 1.0.0  
**Дата:** 17 августа 2025  

## 📚 Обзор

MCP Security Framework предоставляет комплексный API для управления безопасностью в MCP приложениях. API включает в себя модели данных, валидаторы, middleware и утилиты.

## 🏗️ Архитектура API

### Основные компоненты:

1. **Schemas** - Pydantic модели для конфигурации и данных
2. **Core** - Основные валидаторы и утилиты
3. **Middleware** - FastAPI middleware компоненты
4. **Utils** - Вспомогательные функции и утилиты
5. **Commands** - CLI команды

## 📋 Schemas API

### Models

#### Permission
```python
class Permission(BaseModel):
    description: str
    level: int  # 1-10
```

**Поля:**
- `description` (str): Описание разрешения
- `level` (int): Уровень разрешения (1-10)

**Валидация:**
- `level` должен быть в диапазоне 1-10

#### Role
```python
class Role(BaseModel):
    description: str
    allowed_servers: List[str] = ["*"]
    allowed_clients: List[str] = ["*"]
    permissions: List[str]
    priority: int  # 1-1000
```

**Поля:**
- `description` (str): Описание роли
- `allowed_servers` (List[str]): Разрешенные серверы
- `allowed_clients` (List[str]): Разрешенные клиенты
- `permissions` (List[str]): Список разрешений
- `priority` (int): Приоритет роли (1-1000)

**Валидация:**
- `priority` должен быть в диапазоне 1-1000
- `allowed_servers` и `allowed_clients` не могут быть пустыми

#### RolesSchema
```python
class RolesSchema(BaseModel):
    roles: Dict[str, Role]
    permissions: Dict[str, Permission]
    role_hierarchy: RoleHierarchy
    default_policy: DefaultPolicy
    server_roles: Dict[str, Dict[str, Any]] = {}
```

**Методы:**
- `get_role(role_name: str) -> Optional[Role]`
- `get_permission(permission_name: str) -> Optional[Permission]`
- `has_role(role_name: str) -> bool`
- `has_permission(permission_name: str) -> bool`

#### SecurityConfig
```python
class SecurityConfig(BaseModel):
    auth: AuthConfig = Field(default_factory=AuthConfig)
    ssl: SSLConfig = Field(default_factory=SSLConfig)
    roles: RoleConfig = Field(default_factory=RoleConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
```

**Методы:**
- `to_dict() -> Dict[str, Any]`
- `from_dict(data: Dict[str, Any]) -> SecurityConfig`

## 🔧 Core API

### AuthValidator

```python
class AuthValidator:
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    
    def validate_auth(
        self, 
        auth_data: Dict[str, Any], 
        auth_type: str = "auto"
    ) -> AuthValidationResult
    
    def validate_certificate(
        self, 
        cert_path: Optional[str], 
        cert_type: str = "server"
    ) -> AuthValidationResult
    
    def validate_token(
        self, 
        token: Optional[str], 
        token_type: str = "jwt"
    ) -> AuthValidationResult
```

**Методы:**
- `validate_auth()` - Универсальная валидация аутентификации
- `validate_certificate()` - Валидация сертификатов
- `validate_token()` - Валидация токенов

### CertificateUtils

```python
class CertificateUtils:
    @staticmethod
    def create_ca_certificate(
        common_name: str, 
        output_dir: str,
        validity_days: int = 365,
        key_size: int = 2048
    ) -> Dict[str, str]
    
    @staticmethod
    def create_server_certificate(
        common_name: str,
        ca_cert_path: str,
        ca_key_path: str,
        output_dir: str,
        validity_days: int = 365
    ) -> Dict[str, str]
    
    @staticmethod
    def extract_roles_from_certificate_object(
        cert: x509.Certificate
    ) -> List[str]
```

### RoleUtils

```python
class RoleUtils:
    def __init__(self, roles_schema: Optional[Dict[str, Any]] = None)
    
    def validate_role_access(
        self, 
        user_roles: List[str], 
        required_role: str
    ) -> bool
    
    def get_role_hierarchy(self, role: str) -> List[str]
    
    def compare_roles(
        self, 
        role1: str, 
        role2: str, 
        case_sensitive: bool = False
    ) -> bool
```

## 🛡️ Middleware API

### SecurityMiddleware

```python
class SecurityMiddleware:
    def __init__(self, app: FastAPI, config: Dict[str, Any])
    
    @classmethod
    def setup(cls, app: FastAPI, config: Dict[str, Any]) -> None
```

**Использование:**
```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка безопасности
SecurityMiddleware.setup(app, {
    "auth_enabled": True,
    "ssl": {"enabled": True, "mode": "https_only"},
    "roles": {"enabled": True, "config_file": "roles_schema.json"}
})
```

### AuthMiddleware

```python
class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self, 
        app, 
        api_keys: Dict[str, str] = None,
        public_paths: List[str] = None,
        auth_enabled: bool = True
    )
```

### MTLSMiddleware

```python
class MTLSMiddleware(BaseMiddleware):
    def __init__(self, app, mtls_config: Dict[str, Any])
    
    async def before_request(self, request: Request) -> None
```

### RolesMiddleware

```python
class RolesMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, roles_config_path: str)
    
    async def dispatch(self, request: Request, call_next)
```

## 🛠️ Utils API

### SchemaLoader

```python
class SchemaLoader:
    @staticmethod
    def load_roles_schema(file_path: Union[str, Path]) -> Optional[RolesSchema]
    
    @staticmethod
    def save_roles_schema(schema: RolesSchema, file_path: Union[str, Path]) -> bool
    
    @staticmethod
    def load_security_config(file_path: Union[str, Path]) -> Optional[SecurityConfig]
    
    @staticmethod
    def save_security_config(config: SecurityConfig, file_path: Union[str, Path]) -> bool
    
    @staticmethod
    def create_default_roles_schema() -> RolesSchema
```

### PermissionValidator

```python
class PermissionValidator:
    def __init__(self, roles_schema: RolesSchema)
    
    def validate_access(
        self,
        user_roles: List[str],
        required_permissions: List[str],
        server_role: str = None
    ) -> ValidationResult
    
    def check_role_hierarchy(self, user_role: str, required_role: str) -> bool
    
    def get_effective_permissions(self, roles: List[str]) -> Set[str]
```

### SecuritySerializer

```python
class SecuritySerializer:
    @staticmethod
    def serialize_roles_schema(schema: RolesSchema) -> str
    
    @staticmethod
    def deserialize_roles_schema(data: str) -> RolesSchema
    
    @staticmethod
    def serialize_security_config(config: SecurityConfig) -> str
    
    @staticmethod
    def deserialize_security_config(data: str) -> SecurityConfig
```

## 🚀 Commands API

### CLI Commands

```bash
# Валидация схемы ролей
mcp-security validate-schema roles_schema.json

# Создание схемы по умолчанию
mcp-security create-default-schema --output roles.json

# Валидация разрешений
mcp-security validate-permissions --user admin --permission read

# Генерация сертификатов
mcp-security generate-certificates --ca --server --client

# Проверка конфигурации
mcp-security validate-config security_config.json
```

## 📊 Error Codes

### JSON-RPC Error Codes

```python
# Общие ошибки
-32600: "Invalid Request"
-32601: "Method not found"
-32602: "Invalid params"
-32603: "Internal error"

# Ошибки аутентификации
-32001: "Authentication disabled"
-32002: "Invalid configuration"
-32003: "Certificate validation failed"
-32004: "Token validation failed"
-32005: "MTLS validation failed"
-32006: "SSL validation failed"
-32007: "Role validation failed"
-32008: "Certificate expired"
-32009: "Certificate not found"
-32010: "Token expired"
-32011: "Token not found"
```

## 🔍 Примеры использования

### Базовый пример

```python
from mcp_security import SecurityConfig, RolesSchema, PermissionValidator
from mcp_security.utils import SchemaLoader

# Загрузка конфигурации
config = SchemaLoader.load_security_config("security_config.json")
roles_schema = SchemaLoader.load_roles_schema("roles_schema.json")

# Создание валидатора
validator = PermissionValidator(roles_schema)

# Проверка доступа
result = validator.validate_access(
    user_roles=["admin"],
    required_permissions=["read", "write"],
    server_role="kubernetes_manager"
)

if result.is_valid:
    print("Access granted")
else:
    print(f"Access denied: {result.error_message}")
```

### FastAPI интеграция

```python
from fastapi import FastAPI
from mcp_security.middleware import SecurityMiddleware

app = FastAPI()

# Настройка безопасности
security_config = {
    "auth_enabled": True,
    "ssl": {
        "enabled": True,
        "mode": "mtls",
        "cert_file": "./certs/server.crt",
        "key_file": "./certs/server.key",
        "ca_cert": "./certs/ca.crt"
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

SecurityMiddleware.setup(app, security_config)

@app.get("/secure-endpoint")
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}
```

## 📝 Конфигурация

### Пример конфигурации безопасности

```json
{
  "auth_enabled": true,
  "ssl": {
    "enabled": true,
    "mode": "mtls",
    "cert_file": "./certs/server.crt",
    "key_file": "./certs/server.key",
    "ca_cert": "./certs/ca.crt",
    "verify_client": true,
    "client_cert_required": true
  },
  "roles": {
    "enabled": true,
    "config_file": "schemas/roles_schema.json",
    "default_policy": {
      "deny_by_default": true,
      "require_role_match": true,
      "case_sensitive": false,
      "allow_wildcard": true
    }
  },
  "rate_limit": {
    "enabled": true,
    "requests_per_minute": 100,
    "time_window": 60,
    "by_ip": true,
    "by_user": true
  }
}
```

## 🔒 Безопасность

### Рекомендации по безопасности

1. **Сертификаты**: Используйте сильные ключи (2048+ бит)
2. **Токены**: Используйте длинные секретные ключи (32+ символов)
3. **Роли**: Применяйте принцип наименьших привилегий
4. **Rate Limiting**: Настройте разумные лимиты
5. **Логирование**: Ведите аудит доступа

### Аудит безопасности

```python
from mcp_security.utils import SecurityAuditor

auditor = SecurityAuditor(config)
audit_report = auditor.run_security_audit()

print(f"Security score: {audit_report.score}")
print(f"Vulnerabilities: {audit_report.vulnerabilities}")
```
