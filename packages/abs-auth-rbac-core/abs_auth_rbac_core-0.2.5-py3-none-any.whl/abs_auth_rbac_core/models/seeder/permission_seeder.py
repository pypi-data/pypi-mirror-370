from loguru import logger
from sqlalchemy.orm import Session
from typing import List,Callable

from ...util.permission_constants import (
    PermissionConstants
)
from ...models import ( Permission,Role,UserRole,Users)


def seed_permissions(db:Session,emails:List[str]=[]) -> None:
    """Seed permissions into the database"""
    logger.info("Starting permission seeding...")

    # Get all current permissions
    current_permissions = {p.name: p for p in db.query(Permission).all()}

    # Get all defined permissions from constants
    defined_permissions = {
        p.name: p for p in PermissionConstants.get_all_permissions()
    }

    logger.info(f"Found {len(current_permissions)} existing permissions")
    logger.info(f"Found {len(defined_permissions)} defined permissions")

    # Update or create permissions
    for name, permission_data in defined_permissions.items():
        if name in current_permissions:
            # Update existing permission
            existing_permission = current_permissions[name]
            existing_permission.description = permission_data.description
            existing_permission.resource = permission_data.resource
            existing_permission.action = permission_data.action
            existing_permission.module = permission_data.module
            logger.debug(f"Updated permission: {name}")
        else:
            # Create new permission
            new_permission = Permission(
                name=permission_data.name,
                description=permission_data.description,
                resource=permission_data.resource,
                action=permission_data.action,
                module=permission_data.module
            )
            db.add(new_permission)
            logger.debug(f"Created new permission: {name}")

    # Remove permissions that no longer exist in constants
    for name in current_permissions:
        if name not in defined_permissions:
            db.delete(current_permissions[name])
            logger.debug(f"Removed obsolete permission: {name}")

    logger.success("Permission seeding completed successfully!")

    # Create or get super admin role
    super_admin_role = db.query(Role).filter(Role.name == "super_admin").first()
    if not super_admin_role:
        super_admin_role = Role(
            name="super_admin",
            description="Super Administrator with all permissions",
        )
        db.add(super_admin_role)
        db.flush()  # Get the role UUID

    logger.info("Created super admin role.") 

    for email in emails:
        user = db.query(Users).filter(Users.email == email).first()
        if not user:
            # Create new user
            user = Users(
                email=email,
                name=email.split("@")[0],  # Use part before @ as name
                is_active=True,
            )
            db.add(user)
            db.flush()  # Get the user UUID
            logger.info(f"Created new user: {email}")

        # Check if user already has super admin role
        existing_role = (
            db.query(UserRole)
            .filter(
                UserRole.user_uuid == user.uuid,
                UserRole.role_uuid == super_admin_role.uuid,
            )
            .first()
        )

        if not existing_role:
            # Assign super admin role to user
            user_role = UserRole(
                user_uuid=user.uuid,
                role_uuid=super_admin_role.uuid,
            )
            db.add(user_role)
            logger.info(f"Assigned super admin role to user: {email}")

    db.commit()
    logger.success("Super admin seeding completed successfully!")
