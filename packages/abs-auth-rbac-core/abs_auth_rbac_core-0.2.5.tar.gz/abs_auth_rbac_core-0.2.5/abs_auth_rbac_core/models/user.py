from sqlalchemy import Boolean, Column, DateTime, String, Integer
from sqlalchemy.orm import relationship

from abs_auth_rbac_core.models.base_model import BaseModel


class Users(BaseModel):
    """User model representing the user in the system"""
    __tablename__ = "gov_users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    roles = relationship(
        "Role", secondary="gov_user_roles", back_populates="users", lazy="joined", overlaps="user_roles"
    )
    user_roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete-orphan",
        overlaps="roles"
    )

    user_permissions = relationship(
        "UserPermission",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    eagers = ["roles","user_permissions"]
