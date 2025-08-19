from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from abs_auth_rbac_core.models.rbac_model import RBACBaseModel


class Permission(RBACBaseModel):
    """Permission model representing system permissions"""

    __tablename__ = "gov_permissions"

    resource = Column(
        String(100), index=True
    )  # The resource this permission applies to
    
    action = Column(
        String(50), index=True
    )  # The action allowed (e.g., read, write, delete)

    module = Column(String(100), index=True)
    # The module this permission applies to

    # Relationships
    roles = relationship(
        "Role", secondary="gov_role_permissions", back_populates="permissions"
    )

    user_permissions = relationship(
        "UserPermission",
        back_populates="permission",
        cascade="all, delete-orphan"
    )
