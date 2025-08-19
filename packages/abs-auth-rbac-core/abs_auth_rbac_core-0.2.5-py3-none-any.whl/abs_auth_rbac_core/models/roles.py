from sqlalchemy.orm import relationship

from abs_auth_rbac_core.models.rbac_model import RBACBaseModel


class Role(RBACBaseModel):
    """Role model representing user roles in the system"""
    __tablename__ = "gov_roles"

    # Relationships
    permissions = relationship(
        "Permission", secondary="gov_role_permissions", back_populates="roles"
    )
    users = relationship(
        "Users", secondary="gov_user_roles", back_populates="roles", overlaps="user_roles"
    )
    user_roles = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan", overlaps="users,roles"
    )

    eagers = ["permissions", "users"]
