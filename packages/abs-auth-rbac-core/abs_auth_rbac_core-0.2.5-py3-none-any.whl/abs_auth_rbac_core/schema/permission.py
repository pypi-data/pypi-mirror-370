from pydantic import BaseModel
from typing import Optional

class CreatePermissionSchema(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    module: str
