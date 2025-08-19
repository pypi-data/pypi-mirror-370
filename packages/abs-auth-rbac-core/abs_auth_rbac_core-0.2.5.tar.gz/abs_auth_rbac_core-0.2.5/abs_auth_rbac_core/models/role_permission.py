from sqlalchemy import Column, ForeignKey, String

from abs_auth_rbac_core.models.base_model import BaseModel


class RolePermission(BaseModel):
    """Association model between roles and permissions"""

    __tablename__ = "gov_role_permissions"

    role_uuid = Column(String(36), ForeignKey("gov_roles.uuid"), index=True)
    permission_uuid = Column(String(36), ForeignKey("gov_permissions.uuid"), index=True)
