from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.enums import Role

if TYPE_CHECKING:
    from src.core.database.models.transactions import Transaction
    from src.core.database.models.admin_tokens import AdminToken


class User(Base):
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=True)
    role: Mapped[Enum[Role]] = mapped_column(Enum(Role), default=Role.user)
    registered_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    transactions: Mapped[list["Transaction"]] = relationship(lazy="selectin", back_populates="user")
    token: Mapped["AdminToken"] = relationship(lazy="selectin", back_populates="user")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
