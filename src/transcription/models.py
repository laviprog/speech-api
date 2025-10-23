from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.soft_delete_mixin import SoftDeleteMixin
from src.enums import BaseEnum
from src.transcription.enums import Language, Model

if TYPE_CHECKING:
    from src.api_keys.models import ApiKeyModel


class Status(BaseEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class TranscriptionTaskModel(SoftDeleteMixin, UUIDAuditBase):
    """Transcription Task model."""

    __tablename__ = "transcription_tasks"

    status: Mapped[Status] = mapped_column(
        SQLEnum(Status, name="task_status"), default=Status.PENDING, nullable=False
    )
    message: Mapped[str | None]

    model: Mapped[Model] = mapped_column(SQLEnum(Model, name="transcription_model"))
    language: Mapped[Language | None] = mapped_column(
        SQLEnum(Language, name="transcription_language")
    )
    recognition_mode: Mapped[bool] = mapped_column(default=False)
    num_speakers: Mapped[int | None]
    align_mode: Mapped[bool | None] = mapped_column(default=False)

    started_at: Mapped[datetime | None] = mapped_column(DateTimeUTC(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTimeUTC(timezone=True))

    duration_seconds: Mapped[float | None]
    file_size_bytes: Mapped[int | None]

    api_key_id: Mapped[UUID] = mapped_column(ForeignKey("api_keys.id"))
    api_key: Mapped[ApiKeyModel] = relationship(back_populates="transcription_tasks")

    result: Mapped[TranscriptionResultModel | None] = relationship(
        back_populates="task", lazy="noload", cascade="all, delete-orphan"
    )


class TranscriptionResultModel(UUIDAuditBase):
    """Transcription Result model - stores the heavy JSONB data separately."""

    __tablename__ = "transcription_results"

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("transcription_tasks.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    transcription_result: Mapped[dict] = mapped_column(JSONB(), nullable=False)

    task: Mapped[TranscriptionTaskModel] = relationship(back_populates="result")
