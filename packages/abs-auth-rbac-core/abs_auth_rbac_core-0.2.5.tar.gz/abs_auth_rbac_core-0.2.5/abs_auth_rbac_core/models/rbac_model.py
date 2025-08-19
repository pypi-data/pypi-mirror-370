from abs_auth_rbac_core.models.base_model import BaseModel
from sqlalchemy import Column, String

class RBACBaseModel(BaseModel):
    """Base model for RBAC entities with common fields"""

    __abstract__ = True

    name = Column(String(100), index=True, unique=True)
    description = Column(String(500), nullable=True)
