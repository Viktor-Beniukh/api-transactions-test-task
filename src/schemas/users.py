from datetime import datetime
from typing import Annotated, Optional

from annotated_types import MinLen, MaxLen
from pydantic import BaseModel, ConfigDict

from src.core.database.models.enums import Role
from src.schemas.transactions import TransactionResponse


class UserBase(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(32)]


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    registered_at: datetime
    updated_at: datetime
    is_active: bool
    role: Role
    transactions: Optional[list[TransactionResponse]] = []
    id: int
