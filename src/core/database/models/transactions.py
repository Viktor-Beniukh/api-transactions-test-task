from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.db_settings.base import Base
from src.core.database.models.mixins import UserRelationMixin


class Transaction(UserRelationMixin, Base):
    _user_back_populates = "transactions"

    type: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    amount: Mapped[float] = mapped_column(DECIMAL(precision=10, scale=2), default=0.00)

    def __repr__(self):
        return self.type
