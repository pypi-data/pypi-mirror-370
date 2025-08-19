# ABS Auth RBAC Core

A comprehensive authentication and Role-Based Access Control (RBAC) package for FastAPI applications. This package provides robust JWT-based authentication and flexible role-based permission management using Casbin with Redis support for real-time policy updates.

## 🚀 Features

- **🔐 JWT-based Authentication**: Secure token-based authentication with customizable expiration
- **🔒 Password Security**: Secure password storage using bcrypt with passlib
- **👥 Role-Based Access Control (RBAC)**: Flexible permission management using Casbin
- **⚡ Real-time Policy Updates**: Redis integration for live policy synchronization
- **🔄 User-Role Management**: Dynamic role assignment and revocation
- **🛡️ Permission Enforcement**: Decorator-based permission checking
- **🔌 Middleware Integration**: Seamless FastAPI middleware integration
- **📝 Comprehensive Error Handling**: Built-in exception handling for security scenarios
- **🏗️ Dependency Injection Ready**: Compatible with dependency-injector
- **📊 Permission Constants**: Predefined permission constants and enums

## 📦 Installation

```bash
pip install abs-auth-rbac-core
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   Auth Middleware│    │   RBAC Service  │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Routes    │ │◄──►│ │JWT Validation│ │◄──►│ │Permission   │ │
│ │             │ │    │ │User Fetch   │ │    │ │Checking     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Database      │    │   Redis         │    │   Casbin        │
│   (Users,       │    │   (Policy       │    │   (Policy       │
│    Roles,       │    │    Updates)     │    │    Engine)      │
│    Permissions) │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Basic Setup

```python
from abs_auth_rbac_core.auth.jwt_functions import JWTFunctions
from abs_auth_rbac_core.rbac import RBACService
from abs_auth_rbac_core.schema.permission import RedisWatcherSchema
import os

# Initialize JWT functions
jwt_functions = JWTFunctions(
    secret_key=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
)

# Initialize RBAC service with database session
rbac_service = RBACService(
    session=your_db_session,
    redis_config=RedisWatcherSchema(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        channel=os.getenv("REDIS_CHANNEL", "casbin_policy_updates"),
        password=os.getenv("REDIS_PASSWORD"),
        ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
    )
)
```

### 2. Authentication Setup

#### Option 1: Using Package Middleware (Recommended)

```python
from abs_auth_rbac_core.auth.middleware import auth_middleware
from fastapi import FastAPI, Depends

app = FastAPI()

# Create authentication middleware
auth_middleware = auth_middleware(
    db_session=your_db_session,
    jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256")
)

# Apply to specific routers
app.include_router(
    protected_router,
    dependencies=[Depends(auth_middleware)]
)

# Public routes (no middleware)
app.include_router(public_router)
```

**How it works:**
1. ✅ Validates JWT token from Authorization header
2. ✅ Extracts user UUID from token payload
3. ✅ Fetches user from database using UUID
4. ✅ Sets user object in `request.state.user`
5. ✅ Returns user object for route handlers

**Accessing the user in routes:**
```python
@router.get("/profile")
async def get_profile(request: Request):
    user = request.state.user
    return {"user_id": user.uuid, "email": user.email}
```

#### Option 2: Custom Authentication Function

```python
from abs_auth_rbac_core.auth.jwt_functions import JWTFunctions
from fastapi import Security, HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from abs_exception_core.exceptions import UnauthorizedError

security = HTTPBearer(auto_error=False)
jwt_functions = JWTFunctions(
    secret_key=os.getenv("JWT_SECRET_KEY"),
    algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    expire_minutes=int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Dict:
    try:
        if not credentials:
            raise UnauthorizedError(detail="No authorization token provided")

        token = credentials.credentials
        if token.lower().startswith("bearer "):
            token = token[7:]

        decoded_token = jwt_functions.decode_jwt(token)
        if not decoded_token:
            raise UnauthorizedError(detail="Invalid or expired token")

        return decoded_token
    except Exception as e:
        raise UnauthorizedError(detail=str(e))

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user.get('name')}"}
```

### 3. RBAC Operations

```python
# Create a role with permissions
role = rbac_service.create_role(
    name="admin",
    description="Administrator role with full access",
    permission_ids=["permission_uuid1", "permission_uuid2"]
)

# Assign roles to user
rbac_service.bulk_assign_roles_to_user(
    user_uuid="user_uuid",
    role_uuids=["role_uuid1", "role_uuid2"]
)

# Check user permissions
has_permission = rbac_service.check_permission(
    user_uuid="user_uuid",
    resource="USER_MANAGEMENT",
    action="VIEW",
    module="USER_MANAGEMENT"
)

# Get user permissions and roles
user_permissions = rbac_service.get_user_permissions(user_uuid="user_uuid")
user_roles = rbac_service.get_user_roles(user_uuid="user_uuid")
```

## 🏛️ Core Components

### Authentication (`auth/`)
- **`jwt_functions.py`**: JWT token management and password hashing
- **`middleware.py`**: Authentication middleware for FastAPI
- **`auth_functions.py`**: Core authentication functions

### RBAC (`rbac/`)
- **`service.py`**: Main RBAC service with role and permission management
- **`decorator.py`**: Decorators for permission checking
- **`policy.conf`**: Casbin policy configuration

### Models (`models/`)
- **`user.py`**: User model
- **`roles.py`**: Role model
- **`permissions.py`**: Permission model
- **`user_role.py`**: User-Role association model
- **`role_permission.py`**: Role-Permission association model
- **`user_permission.py`**: User-Permission association model
- **`rbac_model.py`**: Base RBAC model
- **`base_model.py`**: Base model with common fields
- **`gov_casbin_rule.py`**: Casbin rule model

### Schema (`schema/`)
- **`permission.py`**: Permission-related schemas

### Utilities (`util/`)
- **`permission_constants.py`**: Predefined permission constants and enums

## 🔧 Complete Implementation Example

### 1. Dependency Injection Setup

```python
from dependency_injector import containers, providers
from abs_auth_rbac_core.auth.middleware import auth_middleware
from abs_auth_rbac_core.rbac import RBACService
from abs_auth_rbac_core.schema.permission import RedisWatcherSchema
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource
)

class Container(containers.DeclarativeContainer):
    # Configure wiring for dependency injection
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.auth_route",
            "src.api.endpoints.rbac.permission_route",
            "src.api.endpoints.rbac.role_route",
            "src.api.endpoints.rbac.users_route",
        ]
    )
    
    # Database session provider
    db_session = providers.Factory(your_db_session_factory)
    
    # RBAC service provider
    rbac_service = providers.Singleton(
        RBACService,
        session=db_session,
        redis_config=RedisWatcherSchema(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            channel=os.getenv("REDIS_CHANNEL", "casbin_policy_updates"),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
        )
    )
    
    # Auth middleware provider
    get_auth_middleware = providers.Factory(
        auth_middleware,
        db_session=db_session,
        jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )

# Initialize container
container = Container()
app.container = container
```

### 2. Application Setup

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dependency_injector.wiring import Provide, inject
from src.core.container import Container

class CreateApp:
    def __init__(self):
        self.container = Container()
        self.db = self.container.db()
        self.auth_middleware = self.container.get_auth_middleware()

        self.app = FastAPI(
            title="Your Service",
            description="Service Description", 
            version="0.2.0"
        )
        
        # Apply CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Public routes (no authentication required)
        self.app.include_router(auth_router, tags=["Auth"])
        self.app.include_router(public_router_v1)
        
        # Protected routes (authentication required)
        self.app.include_router(
            router_v1,
            dependencies=[Depends(self.auth_middleware)]
        )
        
        # Register exception handlers
        register_exception_handlers(self.app)

# Initialize application
application = CreateApp()
app = application.app
```

### 3. Route Implementation with Permissions

```python
from fastapi import APIRouter, Depends, Request
from dependency_injector.wiring import Provide, inject
from abs_auth_rbac_core.rbac import rbac_require_permission
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource
)

# Protected router (requires authentication)
router = APIRouter(prefix="/users")

# Public route example
@router.post("/all", response_model=FindUserResult)
@inject
async def get_user_list(
    request: Request,
    find_query: FindUser = Body(...),
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
    service: UserService = Depends(Provide[Container.user_service]),
):
    """Get the list of users with filtering, sorting and pagination"""
    find_query.searchable_fields = find_query.searchable_fields or ["name"]
    users = service.get_list(schema=find_query)
    return users

# Protected route with permission check
@router.get("/{user_id}", response_model=UserProfile)
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
)
async def get_user(
    user_id: int,
    request: Request,
    service: UserService = Depends(Provide[Container.user_service]),
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Get user profile with permissions and roles"""
    return service.get_user_profile("id", user_id, rbac_service)
```

## 🔐 Permission System

### Permission Format
Permissions follow the format: `module:resource:action`

- **Module**: The system module (e.g., `USER_MANAGEMENT`, `EMAIL_PROCESS`)
- **Resource**: The specific resource within the module (e.g., `USER_MANAGEMENT`, `ROLE_MANAGEMENT`)
- **Action**: The action being performed (e.g., `VIEW`, `CREATE`, `EDIT`, `DELETE`)

### Using Permission Constants

```python
from abs_auth_rbac_core.util.permission_constants import (
    PermissionAction,
    PermissionModule,
    PermissionResource,
    PermissionConstants
)

# Using enums
permission_string = f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}"

# Using predefined constants
user_view_permission = PermissionConstants.RBAC_USER_MANAGEMENT_VIEW
permission_string = f"{user_view_permission.module}:{user_view_permission.resource}:{user_view_permission.action}"
```

### Multiple Permissions

```python
@rbac_require_permission([
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.USER_MANAGEMENT.value}:{PermissionAction.VIEW.value}",
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
])
async def get_user_with_roles():
    # User needs both permissions to access this endpoint
    pass
```

## ⚙️ Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_MINUTES=1440

# Redis Configuration (for real-time policy updates)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_CHANNEL=casbin_policy_updates
REDIS_SSL=false

# Database Configuration
DATABASE_URI=postgresql://user:password@localhost/dbname
```

### Casbin Policy Configuration

The package uses a default policy configuration that supports:
- Role-based access control
- Resource-based permissions
- Module-based organization
- Super admin bypass

Policy format: `[role] [resource] [action] [module]`

## 🛠️ Advanced Usage

### User Profile with Permissions

```python
def get_user_profile(self, attr: str, value: any, rbac_service: RBACService) -> UserProfile:
    """Get user profile with permissions and roles"""
    user = self.user_repository.read_by_attr(attr, value, eager=True)
    
    # Get user permissions and roles
    permissions = rbac_service.get_user_permissions(user_uuid=user.uuid)
    user_permissions = rbac_service.get_user_only_permissions(user_uuid=user.uuid)
    roles = rbac_service.get_user_roles(user_uuid=user.uuid)
    
    # Convert roles to response models
    role_models = [UserRoleResponse.model_validate(role) for role in roles]
    
    return UserProfile(
        id=user.id,
        uuid=user.uuid,
        email=user.email,
        name=user.name,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        permissions=permissions,
        user_permissions=user_permissions,
        roles=role_models,
    )
```

### Role and Permission Management

```python
@router.get("/roles")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.VIEW.value}"
)
async def get_roles(
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Get all roles"""
    return rbac_service.list_roles()

@router.post("/roles")
@inject
@rbac_require_permission(
    f"{PermissionModule.USER_MANAGEMENT.value}:{PermissionResource.ROLE_MANAGEMENT.value}:{PermissionAction.CREATE.value}"
)
async def create_role(
    role: CreateRoleSchema,
    request: Request,
    rbac_service: RBACService = Depends(Provide[Container.rbac_service]),
):
    """Create a new role with permissions"""
    return rbac_service.create_role(
        name=role.name,
        description=role.description,
        permission_ids=role.permission_ids
    )
```

## 🔍 Authentication Flow

```
1. Client Request
   ┌─────────────────┐
   │ Authorization:  │
   │ Bearer <token>  │
   └─────────────────┘
           │
           ▼
2. Auth Middleware
   ┌──────────────────────┐
   │ Validate JWT         │
   │ Extract User ID      │
   │ Fetch User           │
   │ Set in Request state │
   └──────────────────────┘
           │
           ▼
3. RBAC Decorator
   ┌─────────────────┐
   │ Get User UUID   │
   │ Check Permissions│
   │ Allow/Deny      │
   └─────────────────┘
           │
           ▼
4. Route Handler
   ┌─────────────────┐
   │ Execute Logic   │
   │ Return Response │
   └─────────────────┘
```

## 🚨 Error Handling

The package includes comprehensive error handling:

```python
from abs_exception_core.exceptions import (
    UnauthorizedError,
    PermissionDeniedError,
    ValidationError,
    DuplicatedError,
    NotFoundError
)

# Handle authentication errors
try:
    user = await auth_middleware(request)
except UnauthorizedError as e:
    return {"error": "Authentication failed", "detail": str(e)}

# Handle permission errors
try:
    # Protected operation
    pass
except PermissionDeniedError as e:
    return {"error": "Permission denied", "detail": str(e)}
```

## 📊 Monitoring and Logging

```python
import logging
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)

# Log authentication events
logger.info(f"User {user_uuid} authenticated successfully")

# Log permission checks
logger.info(f"Permission check: {user_uuid} -> {resource}:{action}:{module}")

# Log role assignments
logger.info(f"Roles assigned to user {user_uuid}: {role_uuids}")
```

## 🏥 Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "rbac_watcher": rbac_service.is_watcher_active(),
        "policy_count": rbac_service.get_policy_count()
    }
```

## 🔧 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Authentication Fails** | Check JWT secret key, token expiration, user existence |
| **Permission Denied** | Verify user roles, role-permission assignments, permission format |
| **Redis Connection Issues** | Check Redis server status, connection parameters, pub/sub support |
| **Policy Not Updating** | Verify Redis watcher configuration, policy format, Redis logs |

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check RBAC service status
print(f"Watcher active: {rbac_service.is_watcher_active()}")
print(f"Policy count: {rbac_service.get_policy_count()}")
```

## 📋 Dependencies

### Core Dependencies
- **pyjwt** (>=2.10.1,<3.0.0): JWT token handling
- **fastapi[standard]** (>=0.115.12,<0.116.0): Web framework
- **passlib** (>=1.7.4,<2.0.0): Password hashing
- **sqlalchemy** (>=2.0.40,<3.0.0): Database ORM
- **casbin** (>=1.41.0,<2.0.0): RBAC policy engine
- **casbin-sqlalchemy-adapter** (>=1.4.0,<2.0.0): Database adapter
- **casbin-redis-watcher** (>=1.3.0,<2.0.0): Real-time policy updates

### Internal Dependencies
- **abs-exception-core** (>=0.1.4,<0.2.0): Exception handling
- **psycopg2-binary** (>=2.9.10,<3.0.0): PostgreSQL adapter

## 🚀 Best Practices

### Security
- ✅ Use environment variables for sensitive data
- ✅ Implement proper password policies
- ✅ Regularly rotate JWT secret keys
- ✅ Use HTTPS in production
- ✅ Implement rate limiting for authentication endpoints

### Permission Design
- ✅ Use descriptive permission names
- ✅ Group related permissions by module
- ✅ Implement least privilege principle
- ✅ Document permission requirements

### Performance
- ✅ Use Redis for real-time policy updates
- ✅ Implement caching for frequently accessed permissions
- ✅ Optimize database queries with eager loading
- ✅ Monitor policy enforcement performance

### Maintenance
- ✅ Regularly audit user permissions
- ✅ Implement permission cleanup for inactive users
- ✅ Monitor and log security events
- ✅ Keep dependencies updated

## 📚 API Reference

### RBACService Methods

| Method | Description |
|--------|-------------|
| `create_role(name, description, permission_ids)` | Create a new role |
| `assign_role_to_user(user_uuid, role_uuid)` | Assign role to user |
| `bulk_assign_roles_to_user(user_uuid, role_uuids)` | Assign multiple roles |
| `check_permission(user_uuid, resource, action, module)` | Check user permission |
| `get_user_permissions(user_uuid)` | Get all user permissions |
| `get_user_roles(user_uuid)` | Get user roles |
| `list_roles()` | List all roles |
| `is_watcher_active()` | Check Redis watcher status |

### JWT Functions

| Method | Description |
|--------|-------------|
| `create_access_token(data)` | Create JWT access token |
| `decode_jwt(token)` | Decode and validate JWT |
| `hash_password(password)` | Hash password with bcrypt |
| `verify_password(password, hashed)` | Verify password hash |

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Email: info@autobridgesystems.com
- Documentation: [Link to documentation]
- Issues: [GitHub Issues]

---

**Version**: 0.2.0  
**Last Updated**: 2024  
**Python Version**: >=3.12,<4.0
