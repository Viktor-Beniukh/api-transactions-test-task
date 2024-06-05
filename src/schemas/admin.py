from datetime import datetime
from typing import Annotated

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict

from src.core.database.models.enums import Role


class AdminBase(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(32)]


class AdminRegister(AdminBase):
    password: Annotated[str, MinLen(8), MaxLen(1024)]


class AdminResponse(AdminBase):
    model_config = ConfigDict(from_attributes=True)

    registered_at: datetime
    updated_at: datetime
    is_active: bool
    role: Role
    id: int


class AdminMessageResponse(BaseModel):
    message: str
