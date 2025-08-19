from functools import wraps
from typing import Dict, List, Union
from fastapi import Request
from abs_exception_core.exceptions import PermissionDeniedError
from .service import RBACService

def rbac_require_permission(permissions: Union[str, List[str]]):
    """
    Decorator to enforce all required permissions for a user.

    Args:
        permissions (str | list[str]): One or more "resource:action" strings.

    Raises:
        PermissionDeniedError: If the user lacks any one of the required permissions.
    """
    if isinstance(permissions, str):
        permissions = [permissions]

    def decorator(func):
        @wraps(func)
        async def wrapper(
            request:Request,
            *args,rbac_service:RBACService, **kwargs,
        ):
            current_user_uuid = request.state.user.uuid
            if not current_user_uuid:
                raise PermissionDeniedError(
                    detail="User not found (missing 'uuid')."
                )
            for perm in permissions:
                try:
                    module, resource, action = perm.split(":")
                except ValueError:
                    raise ValueError(
                        f"Invalid permission format: '{perm}'. Expected 'module:resource:action'."
                    )
                
                has_permission = rbac_service.check_permission(
                    user_uuid=current_user_uuid, resource=resource, action=action,module=module
                )

                if not has_permission:
                    raise PermissionDeniedError(
                        detail=f"Permission denied: {action} on {resource} in {module}"
                    )
            return await func(*args,request=request,rbac_service=rbac_service, **kwargs)
        return wrapper
    return decorator
