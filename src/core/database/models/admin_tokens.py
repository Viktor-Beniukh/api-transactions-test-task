from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.db_settings.base import Base
from src.core.database.models.mixins import UserRelationMixin


class AdminToken(UserRelationMixin, Base):
    __tablename__ = "admin_tokens"

    _user_id_unique = True
    _user_back_populates = "token"

    token: Mapped[str] = mapped_column(String(255), nullable=True)
