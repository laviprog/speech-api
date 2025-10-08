from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Mapped


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None]

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self) -> None:
        self.deleted_at = None
