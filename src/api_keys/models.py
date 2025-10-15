from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.soft_delete_mixin import SoftDeleteMixin

if TYPE_CHECKING:
    from src.transcription.models import TranscriptionTaskModel
    from src.users.models import UserModel


class ApiKeyModel(SoftDeleteMixin, UUIDAuditBase):
    """API Keys model."""

    __tablename__ = "api_keys"

    key_hash: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    key_prefix: Mapped[str] = mapped_column(String(15))
    is_active: Mapped[bool] = mapped_column(default=True)
    last_used_at: Mapped[datetime | None]
    name: Mapped[str | None] = mapped_column(String(255))

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped[UserModel] = relationship(back_populates="api_keys")

    transcription_tasks: Mapped[list[TranscriptionTaskModel]] = relationship(
        back_populates="api_key",
    )
