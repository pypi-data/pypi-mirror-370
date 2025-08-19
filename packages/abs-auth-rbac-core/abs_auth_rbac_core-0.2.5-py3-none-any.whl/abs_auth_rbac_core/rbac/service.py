from typing import List, Optional, Callable,Any,Tuple
import os
from pydantic import BaseModel
import casbin
from casbin_sqlalchemy_adapter import Adapter
from casbin_redis_watcher import RedisWatcher, WatcherOptions,new_watcher
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload
from ..schema import CreatePermissionSchema
from ..models import (
    Role,
    RolePermission,
    UserRole,
    Users,
    Permission,
    UserPermission
)
from abs_utils.logger import setup_logger

logger = setup_logger(__name__)
from abs_exception_core.exceptions import (
    DuplicatedError,
    NotFoundError,
    PermissionDeniedError
)

from ..models.gov_casbin_rule import GovCasbinRule
from redis import Redis

class RedisWatcherSchema(BaseModel):
    host: str
    port: int
    channel: str
    ssl: Optional[bool] = False
    password: Optional[str] = None

class RBACService:
    def __init__(self, session: Callable[...,Session],redis_config:Optional[RedisWatcherSchema]=None):
        """
        Service For Managing the RBAC
        Args:
            session: Callable[...,Session] -> Session of the SQLAlchemy database engine
        """
        self.db = session
        self.enforcer = None
        self._initialize_casbin(redis_config)
        self.watcher = None

    def _initialize_casbin(self,redis_config:Optional[RedisWatcherSchema]=None):
        """
        Initiates the casbin policy using the default rules
        """
        with self.db() as session:
            engine = session.get_bind()

            # Create the Casbin rule table if it doesn't exist
            adapter = Adapter(engine,db_class=GovCasbinRule)
            
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the path to the policy file
            policy_path = os.path.join(current_dir, "policy.conf")
            
            self.enforcer = casbin.Enforcer(
                policy_path, adapter
            )
            # Load policies
            self.enforcer.load_policy()

            if redis_config:
                try:
                    # Create Redis client with proper configuration
                    redis_client = Redis(
                        host=redis_config.host,
                        port=redis_config.port,
                        password=redis_config.password if hasattr(redis_config, 'password') else None,
                        ssl=redis_config.ssl,
                        decode_responses=True,
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30
                    )
                    
                    # Test Redis connection
                    redis_client.ping()

                    # Create Watcher and Options
                    test_option = WatcherOptions()
                    test_option.pub_client = redis_client
                    test_option.sub_client = redis_client
                    test_option.channel = redis_config.channel
                    test_option.optional_update_callback = lambda _: self.enforcer.load_policy()

                    # Create watcher
                    watcher = new_watcher(test_option)

                    self.enforcer.set_watcher(watcher)
                    self.watcher = watcher
                    self.enforcer.save_policy()
                    
                except Exception as e:
                    logger.error(f"Failed to initialize Redis watcher: {e}")
                    self.watcher = None
            else:
                logger.info("Redis watcher not configured - Casbin will work without real-time policy updates")

    def add_policy(self,role:str,resource:str,action:str,module:str):
        """
        Add a policy to the casbin enforcer
        """
        self.enforcer.add_policy(role,resource,action,module)
        self.enforcer.save_policy()

    def remove_policy(self,role:str,resource:str,action:str,module:str):
        """
        Remove a policy from the casbin enforcer
        """
        self.enforcer.remove_policy(role,resource,action,module)
        self.enforcer.save_policy()

    def add_policies(self,policies:List[Tuple[str,str,str,str]]):
        """
        Add a list of policies to the casbin enforcer
        """
        self.enforcer.add_policies(policies)
        self.enforcer.save_policy()

    def remove_policies(self,policies:List[List[str]]):
        """
        Remove a list of policies from the casbin enforcer
        """
        self.enforcer.remove_policies(policies)
        self.enforcer.save_policy()

    def enforce_policy(self,role:str,resource:str,action:str,module:str):
        """
        Enforce a policy
        """
        return self.enforcer.enforce(role,resource,action,module)
    
    def remove_filter_policy(self,index:int,value:str):
        """
        Remove a policy by filtering the policy
        Args:
            index: The index of the policy to remove
            value: The value of the policy to remove
        """
        self.enforcer.remove_filtered_policy(index,value)
        self.enforcer.save_policy()

    async def bulk_create_permissions(self,permissions:List[CreatePermissionSchema]):
        """
        Bulk create permissions for user
        """
        with self.db() as session:
            try:
                if not permissions:
                    return []
                
                if hasattr(permissions[0],'model_dump'):
                    add_permissions = [Permission(**permission.model_dump()) for permission in permissions]
                else:
                    add_permissions = [Permission(**permission) for permission in permissions]

                session.bulk_save_objects(add_permissions)
                session.commit()
                return add_permissions
            except Exception as e:
                raise e
            
    async def get_permissions_by_condition(self, condition: dict, use_filter_by: bool = True):
        """
        Get permission(s) based on a condition dict.
        If use_filter_by is True, assumes all conditions are `==`.
        """
        with self.db() as session:
            try:
                query = session.query(Permission)
                if use_filter_by:
                    query = query.filter_by(**condition)
                else:
                    filters = [getattr(Permission, k) == v for k, v in condition.items()]
                    query = query.filter(*filters)
                return query.all()
            except Exception as e:
                raise e
            
    async def delete_permission_by_uuids(self,permission_uuids:List[str]):
        """
        Delete a permission by uuids
        """
        with self.db() as session:
            try:
                user_permissions = session.query(UserPermission).filter(UserPermission.permission_uuid.in_(permission_uuids)).delete(synchronize_session=False)
                permissions = session.query(Permission).filter(Permission.uuid.in_(permission_uuids))
                for permission in permissions:
                    self.enforcer.remove_filtered_policy(1,permission.resource)
                self.enforcer.save_policy()
                permissions.delete(synchronize_session=False)
                session.commit()
                return True
            except Exception as e:
                raise e

    def assign_permissions_to_user(self,user_uuid:str,permission_uuids:List[str]):
        """
        Assign permissions to a user
        """
        with self.db() as session:
            try:
                current_permissions = session.query(UserPermission).filter(UserPermission.user_uuid==user_uuid).all()
                current_permission_uuids = [permission.permission_uuid for permission in current_permissions]
                remove_permissions = set(current_permission_uuids) - set(permission_uuids)
                add_permissions = set(permission_uuids) - set(current_permission_uuids)
                if remove_permissions:
                    self.revoke_user_permissions(user_uuid,list(remove_permissions))
                if add_permissions:
                    self.attach_permissions_to_user(user_uuid,list(add_permissions))
                return self.get_user_only_permissions(user_uuid)    
            except Exception as e:
                raise e

    def attach_permissions_to_user(self, user_uuid: str, permission_uuids: List[str]):
        with self.db() as session:
            try:
                user_permissions = [
                    UserPermission(user_uuid=user_uuid, permission_uuid=permission_uuid)
                    for permission_uuid in permission_uuids
                ]
                session.bulk_save_objects(user_permissions)
                session.commit()

                permissions = session.query(Permission).filter(Permission.uuid.in_(permission_uuids)).all()
                policies = [
                    [f"user:{user_uuid}", permission.resource, permission.action, permission.module]
                    for permission in permissions
                ]
                added_policies = self.enforcer.add_policies(policies)
                if added_policies:
                    self.enforcer.save_policy()
                    self.enforcer.load_policy()
                return self.get_user_only_permissions(user_uuid)
            except Exception as e:
                raise e

    def revoke_user_permissions(self, user_uuid: str, permission_uuids: List[str]):
        with self.db() as session:
            try:
                user_permissions = session.query(UserPermission).filter(
                    UserPermission.user_uuid == user_uuid,
                    UserPermission.permission_uuid.in_(permission_uuids)
                )

                permissions = session.query(Permission).filter(Permission.uuid.in_(permission_uuids)).all()
                policies = [
                    [f"user:{user_uuid}", permission.resource, permission.action, permission.module]
                    for permission in permissions
                ]
                removed_policies = self.enforcer.remove_policies(policies)
                if removed_policies:
                    self.enforcer.save_policy()
                    self.enforcer.load_policy()
                user_permissions.delete(synchronize_session=False)
                session.commit()
                return self.get_user_only_permissions(user_uuid)
            except Exception as e:
                raise e
            
    def list_roles(self) -> Any:
        """
        Get the list of all roles
        """
        with self.db() as session:
            try:
                """List all roles"""
                total = session.query(Role).count()
                roles = session.query(Role).all()
                return {"roles": roles, "total": total}
            except Exception as e:
                raise e

    def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        permission_ids: List[str] = None,
    ) -> Any:
        """
        Create role with the provided permissions
        
        Args:
            name: Name of the role
            description: Optional description of the role
            permission_ids: Optional list of permission UUIDs to assign to the role
            
        Returns:
            The created role object
            
        Raises:
            DuplicatedError: If a role with the same name already exists
            NotFoundError: If any of the provided permission IDs don't exist
        """
        with self.db() as session:
            try:
                # Check if role with same name already exists
                existing_role = session.query(Role).filter(Role.name == name).first()
                if existing_role:
                    raise DuplicatedError(detail="Role already exists")

                # Create the role
                role = Role(name=name, description=description)
                session.add(role)
                session.flush()  # Get the role UUID without committing

                # If permission IDs are provided, assign them to the role
                if permission_ids:
                    # Verify all permissions exist in a single query
                    permission_count = (
                        session.query(Permission)
                        .filter(Permission.uuid.in_(permission_ids))
                        .count()
                    )
                    
                    # Check if all permissions were found
                    if permission_count != len(permission_ids):
                        # Find which permissions are missing
                        existing_permissions = (
                            session.query(Permission)
                            .filter(Permission.uuid.in_(permission_ids))
                            .all()
                        )
                        found_permission_ids = {p.uuid for p in existing_permissions}
                        missing_ids = set(permission_ids) - found_permission_ids
                        raise NotFoundError(
                            detail=f"Permissions with UUIDs '{', '.join(missing_ids)}' not found"
                        )
                    
                    # Get all permissions for Casbin policy creation
                    existing_permissions = (
                        session.query(Permission)
                        .filter(Permission.uuid.in_(permission_ids))
                        .all()
                    )
                    
                    # Bulk create role permissions using bulk_insert_mappings for better performance
                    role_permissions = [
                        {"role_uuid": role.uuid, "permission_uuid": permission_uuid}
                        for permission_uuid in permission_ids
                    ]
                    session.bulk_insert_mappings(RolePermission, role_permissions)

                    # Batch add Casbin policies
                    policies = [
                        [role.uuid, permission.resource, permission.action, permission.module]
                        for permission in existing_permissions
                    ]
                    self.enforcer.add_policies(policies)
                    self.enforcer.save_policy()

                # Commit transaction
                session.commit()
                session.refresh(role)
                return role
            
            except Exception as e:
                raise e

    def get_role_with_permissions(self, role_uuid: str) -> Any:
        """Get role details including its permissions"""
        with self.db() as session:
            # Use joinedload to eagerly load permissions
            role = (
                session.query(Role)
                .options(joinedload(Role.permissions))
                .filter(Role.uuid == role_uuid)
                .first()
            )
            
            if not role:
                raise NotFoundError(detail="Requested role does not exist")
                
            return role

    def update_role_permissions(
        self,
        role_uuid: str,
        permissions: Optional[List[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Any:
        """Update role permissions by replacing all existing permissions with new ones"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(Role)
                    .options(joinedload(Role.permissions))
                    .filter(Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Update role information if provided
                if name is not None or description is not None:
                    if name:
                        # Check if new name already exists for a different role
                        existing_role = (
                            session.query(Role)
                            .filter(Role.name == name, Role.uuid != role_uuid)
                            .first()
                        )

                        if existing_role:
                            raise DuplicatedError(detail="Role already exists")
                        
                        if role.name != "super_admin":
                            role.name = name

                    if description is not None:
                        role.description = description

                if permissions is not None:
                    existing_permissions = role.permissions

                    # Remove Casbin policies for existing permissions
                    remove_policies = [
                        [role_uuid, existing_permission.resource, existing_permission.action, existing_permission.module]
                        for existing_permission in existing_permissions
                    ]
                    self.enforcer.remove_policies(remove_policies)
                    self.enforcer.save_policy()

                    # Delete existing role permissions
                    session.query(RolePermission).filter(
                        RolePermission.role_uuid == role_uuid
                    ).delete(synchronize_session=False)

                if permissions:
                    # Fetch all permissions in a single query
                    permissions_objs = (
                        session.query(Permission)
                        .filter(Permission.uuid.in_(permissions))
                        .all()
                    )

                    found_permission_ids = {p.uuid for p in permissions_objs}
                    missing_permission_ids = set(permissions) - found_permission_ids
                    if missing_permission_ids:
                        raise NotFoundError(
                            detail=f"Permissions with UUIDs '{', '.join(missing_permission_ids)}' not found"
                        )

                    # Bulk insert role permissions
                    role_permissions = [
                        {"role_uuid": role_uuid, "permission_uuid": permission.uuid}
                        for permission in permissions_objs
                    ]
                    session.bulk_insert_mappings(RolePermission, role_permissions)

                    # Add Casbin policies
                    policies = [
                        [role_uuid, permission.resource, permission.action, permission.module]
                        for permission in permissions_objs
                    ]
                    self.enforcer.add_policies(policies)
                    self.enforcer.save_policy()

                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                
                # Return the updated role with permissions
                return role

            except Exception as e:
                raise e

    def delete_role(self, role_uuid: str,exception_roles:List[str]=None):
        """Delete a role and its associated permissions"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with permissions eagerly loaded
                role = (
                    session.query(Role)
                    .options(joinedload(Role.permissions))
                    .filter(Role.uuid == role_uuid)
                    .first()
                )
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                if exception_roles and len(exception_roles) > 0 and role.name in exception_roles:
                    raise PermissionDeniedError(detail="You are not allowed to delete the requested role.")

                # Collect all policies to remove from the eagerly loaded permissions
                remove_policies = [
                    [role.uuid, permission.resource, permission.action, permission.module]
                    for permission in role.permissions
                ]
                
                # Remove all policies at once
                if remove_policies:

                    self.enforcer.remove_policies(remove_policies)
                    self.enforcer.save_policy()

                # Delete role (cascade will handle role_permissions and user_roles)
                session.delete(role)
                session.commit()

            except Exception as e:
                raise e

    def list_permissions(self) -> List[Any]:
        """Get all permissions with their resources and actions"""
        with self.db() as session:
            return session.query(Permission).all()
        
    def list_module_permissions(self,module:str) -> List[Any]:
        """Get all permissions for a module"""
        with self.db() as session:
            return session.query(Permission).filter(Permission.module == module).all()
        
    def get_user_only_permissions(self, user_uuid: str) -> List[Any]:
        """Get all allowed permissions for a user"""
        with self.db() as session:
            user_permissions = (
                session.query(UserPermission)
                .filter(UserPermission.user_uuid == user_uuid)
                .options(joinedload(UserPermission.permission))
                .all()
            )
            result = []
            for user_permission in user_permissions:
                result.append(
                    {
                        "permission_id": user_permission.permission.uuid,
                        "created_at": user_permission.permission.created_at,
                        "updated_at": user_permission.permission.updated_at,
                        "name": user_permission.permission.name,
                        "resource": user_permission.permission.resource,
                        "action": user_permission.permission.action,
                        "module": user_permission.permission.module
                    }
                )
            return result
        
    def get_user_permissions(self, user_uuid: str) -> List[Any]:
        """Get all allowed permissions for a user"""
        with self.db() as session:
            # Get user roles with eager loading of roles and their permissions
            user_roles = (
                session.query(UserRole)
                .join(Role, UserRole.role_uuid == Role.uuid)
                .options(
                    joinedload(UserRole.role).joinedload(Role.permissions)
                )
                .filter(UserRole.user_uuid == user_uuid)
                .all()
            )
            
            if not user_roles:
                return []

            # Build response directly from the eagerly loaded data
            result = []
            for user_role in user_roles:
                role = user_role.role
                for permission in role.permissions:
                    result.append(
                        {
                            "permission_id": permission.uuid,
                            "created_at": permission.created_at,
                            "role_id": role.uuid,
                            "updated_at": permission.updated_at,
                            "role_name": role.name,
                            "name": permission.name,
                            "resource": permission.resource,
                            "action": permission.action,
                            "module": permission.module
                        }
                    )

            return result

    def bulk_revoke_permissions(
        self, role_uuid: str, permission_uuids: List[str]
    ) -> Any:
        """Revoke multiple permissions from a role"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(Role)
                    .options(joinedload(Role.permissions))
                    .filter(Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Filter permissions to revoke from the eagerly loaded permissions
                permissions_to_revoke = [
                    p for p in role.permissions 
                    if p.uuid in permission_uuids
                ]

                if not permissions_to_revoke:
                    return role

                # Get UUIDs of permissions to revoke
                permission_uuids_to_revoke = [p.uuid for p in permissions_to_revoke]

                # Delete role permissions
                session.query(RolePermission).filter(
                    and_(
                        RolePermission.role_uuid == role_uuid,
                        RolePermission.permission_uuid.in_(permission_uuids_to_revoke),
                    )
                ).delete(synchronize_session=False)

                # Remove Casbin policies
                policies_to_remove = [
                    [role.uuid, permission.resource, permission.action, permission.module]
                    for permission in permissions_to_revoke
                ]
                self.enforcer.remove_policies(policies_to_remove)
                self.enforcer.save_policy()
                
                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                return role

            except Exception as e:
                raise e

    def bulk_attach_permissions(
        self, role_uuid: str, permission_uuids: List[str]
    ) -> Any:
        """Attach multiple permissions to a role"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                # Get role with eager loading of permissions
                role = (
                    session.query(Role)
                    .options(joinedload(Role.permissions))
                    .filter(Role.uuid == role_uuid)
                    .first()
                )
                
                if not role:
                    raise NotFoundError(detail="Requested role does not exist")

                # Get existing permission UUIDs from the eagerly loaded permissions
                existing_permission_uuids = {p.uuid for p in role.permissions}

                # Calculate new permission UUIDs to attach
                new_permission_uuids = set(permission_uuids) - existing_permission_uuids

                if not new_permission_uuids:
                    return role

                # Fetch new permissions in a single query
                new_permissions = (
                    session.query(Permission)
                    .filter(Permission.uuid.in_(new_permission_uuids))
                    .all()
                )

                # Verify all permissions were found
                if len(new_permissions) != len(new_permission_uuids):
                    found_permission_uuids = {p.uuid for p in new_permissions}
                    missing_permission_uuids = new_permission_uuids - found_permission_uuids
                    raise NotFoundError(
                        detail=f"Permissions with UUIDs '{', '.join(missing_permission_uuids)}' not found"
                    )

                # Bulk insert role permissions
                role_permissions = [
                    {"role_uuid": role_uuid, "permission_uuid": p.uuid}
                    for p in new_permissions
                ]
                session.bulk_insert_mappings(RolePermission, role_permissions)

                # Add Casbin policies
                policies_to_add = [
                    [role.uuid, permission.resource, permission.action, permission.module]
                    for permission in new_permissions
                ]
                self.enforcer.add_policies(policies_to_add)
                self.enforcer.save_policy()

                session.commit()

                # Refresh the role to get the updated permissions
                session.refresh(role)
                return role

            except Exception as e:
                raise e

    def get_user_roles(self, user_uuid: str,session: Optional[Session] = None) -> List[Any]:
        """Get user roles"""
        def query_roles(session: Session) -> List[Any]:
            return (
                session.query(Role)
                .join(
                    UserRole,
                    and_(
                        UserRole.role_uuid == Role.uuid,
                        UserRole.user_uuid == user_uuid
                    )
                )
                .options(joinedload(Role.permissions))
                .all()
            )

        if session:
            return query_roles(session)
        else:
            with self.db() as new_session:
                return query_roles(new_session)
            

    def bulk_assign_roles_to_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Assign multiple roles to a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(UserRole)
                    .options(joinedload(UserRole.role))
                    .filter(UserRole.user_uuid == user_uuid)
                    .all()
                )

                current_role_uuids = {role.role.uuid for role in current_roles}

                new_role_uuids = set(role_uuids) - current_role_uuids

                roles_to_remove = current_role_uuids - set(role_uuids)

                if roles_to_remove:
                    session.query(UserRole).filter(
                        and_(
                            UserRole.user_uuid == user_uuid,
                            UserRole.role_uuid.in_(roles_to_remove),
                        )
                    ).delete(synchronize_session=False)

                if new_role_uuids:
                    new_roles = (
                        session.query(Role).filter(Role.uuid.in_(new_role_uuids)).all()
                    )

                    if len(new_roles) != len(new_role_uuids):
                        raise NotFoundError(detail="One or more roles not found")

                    user_roles = [
                        UserRole(user_uuid=user_uuid, role_uuid=role.uuid)
                        for role in new_roles
                    ]
                    session.bulk_save_objects(user_roles)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    # Bulk Revoke Roles From User
    def bulk_revoke_roles_from_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Revoke multiple roles from a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(UserRole)
                    .options(joinedload(UserRole.role))
                    .filter(UserRole.user_uuid == user_uuid)
                    .filter(UserRole.role_uuid.in_(role_uuids))
                    .all()
                )

                if not current_roles:
                    return self.get_user_roles(user_uuid)

                role_uuids_to_revoke = {role.role.uuid for role in current_roles}

                session.query(UserRole).filter(
                    and_(
                        UserRole.user_uuid == user_uuid,
                        UserRole.role_uuid.in_(role_uuids_to_revoke),
                    )
                ).delete(synchronize_session=False)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    def bulk_attach_roles_to_user(
        self, user_uuid: str, role_uuids: List[str]
    ) -> List[Any]:
        """Attach multiple roles to a user"""
        with self.db() as session:
            try:
                if not session.is_active:
                    session.begin()

                current_roles = (
                    session.query(UserRole)
                    .options(joinedload(UserRole.role))
                    .filter(UserRole.user_uuid == user_uuid)
                    .all()
                )

                current_role_uuids = {role.role.uuid for role in current_roles}

                new_role_uuids = set(role_uuids) - current_role_uuids

                if not new_role_uuids:
                    return self.get_user_roles(user_uuid)

                new_roles = (
                    session.query(Role).filter(Role.uuid.in_(new_role_uuids)).all()
                )

                if len(new_roles) != len(new_role_uuids):
                    raise NotFoundError(detail="There are some roles that does not exist.")

                user_roles = [
                    UserRole(user_uuid=user_uuid, role_uuid=role.uuid) for role in new_roles
                ]
                session.bulk_save_objects(user_roles)

                session.commit()

                return self.get_user_roles(user_uuid,session)

            except Exception as e:
                raise e

    def check_permission(self, user_uuid: str, resource: str, action: str, module: str) -> bool:
        with self.db() as session:
            roles = (
                session.query(Role)
                .join(
                    UserRole,
                    and_(
                        UserRole.role_uuid == Role.uuid,
                        UserRole.user_uuid == user_uuid,
                    ),
                )
                .all()
            )
            for role in roles:
                # Try with module first
                if self.enforcer.enforce(role.uuid, resource, action, module):
                    return True
                if self.enforcer.enforce(role.name, resource, action, module):
                    return True
            return False

    def check_permission_by_role(
        self, role_uuid: str, resource: str, action: str, module: str
    ) -> bool:
        # Try with module first
        if self.enforcer.enforce(role_uuid, resource, action, module):
            return True
        return False
    
    def check_permission_by_user(self,user_uuid:str,resource:str,action:str,module:str) -> bool:
        if self.enforcer.enforce(f"user:{user_uuid}", resource, action, module):
            return True
        return False

    def get_role(self, role_uuid: str,session: Optional[Session] = None) -> Any:
        """Get role by uuid"""
        def query_role(session: Session) -> Any:
            role =  session.query(Role).filter(Role.uuid == role_uuid).first()
            if not role:
                raise NotFoundError(detail="Requested role does not exist.")
            return role

        if session:
            return query_role(session)
        else:
            with self.db() as session:
                return query_role(session)

    def is_watcher_active(self) -> bool:
        """Check if Redis watcher is active and connected"""
        return self.watcher is not None and hasattr(self.watcher, 'pub_client') and self.watcher.pub_client is not None

    def get_watcher_status(self) -> dict:
        """Get detailed watcher status information"""
        if not self.is_watcher_active():
            return {
                "active": False,
                "message": "Watcher not initialized or not active"
            }
        
        try:
            # Test Redis connection
            self.watcher.pub_client.ping()
            return {
                "active": True,
                "host": self.watcher.pub_client.connection_pool.connection_kwargs.get('host'),
                "port": self.watcher.pub_client.connection_pool.connection_kwargs.get('port'),
                "channel": getattr(self.watcher, 'channel', 'unknown'),
                "connected": True
            }
        except Exception as e:
            return {
                "active": False,
                "error": str(e),
                "message": "Watcher exists but Redis connection failed"
            }

    def reload_policies(self) -> bool:
        """Manually reload policies from database"""
        try:
            self.enforcer.load_policy()
            return True
        except Exception as e:
            logger.error(f"Failed to reload policies: {e}")
            return False

    def get_policy_count(self) -> int:
        """Get the total number of policies in the enforcer"""
        return len(self.enforcer.get_policy())

    def clear_all_policies(self) -> bool:
        """Clear all policies from the enforcer (use with caution)"""
        try:
            self.enforcer.clear_policy()
            self.enforcer.save_policy()
            return True
        except Exception as e:
            logger.error(f"Failed to clear policies: {e}")
            return False
