from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from src.api_keys import ApiKeyModel


class UserModel(SoftDeleteMixin, UUIDAuditBase):
    """User model."""

    __tablename__ = "users"

    is_active: Mapped[bool] = mapped_column(default=True)
    company_name: Mapped[str | None] = mapped_column(String(255))

    api_keys: Mapped[list["ApiKeyModel"]] = relationship(back_populates="user")
