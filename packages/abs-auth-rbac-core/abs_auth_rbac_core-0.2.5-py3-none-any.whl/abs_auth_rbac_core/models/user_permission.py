from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from abs_auth_rbac_core.models.base_model import BaseModel


class UserPermission(BaseModel):
    """Association model between users and permissions"""

    __tablename__ = "gov_user_permissions"

    user_uuid = Column(String(36), ForeignKey("gov_users.uuid"), index=True)
    permission_uuid = Column(String(36), ForeignKey("gov_permissions.uuid"), index=True)

    user = relationship("Users", back_populates="user_permissions")
    permission = relationship("Permission", back_populates="user_permissions")