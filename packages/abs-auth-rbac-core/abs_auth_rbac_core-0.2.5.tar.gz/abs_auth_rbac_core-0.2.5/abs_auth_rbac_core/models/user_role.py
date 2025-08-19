from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from abs_auth_rbac_core.models.base_model import BaseModel


class UserRole(BaseModel):
    """Association table for User-Role relationship"""
    __tablename__ = "gov_user_roles"

    user_uuid = Column(
        String(36), ForeignKey("gov_users.uuid", ondelete="CASCADE"), nullable=False
    )
    role_uuid = Column(
        String(36), ForeignKey("gov_roles.uuid", ondelete="CASCADE"), nullable=False
    )

    # Corrected relationships
    user = relationship("Users", back_populates="user_roles",  overlaps="roles,users")
    role = relationship("Role", back_populates="user_roles",  overlaps="roles,users")
