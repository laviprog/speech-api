from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import create_engine, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.transcription.models import TranscriptionTaskModel
from src.workers import log

_engine = None
_SessionLocal: Optional[sessionmaker] = None


def init_db_sync() -> None:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(
            settings.DB_URL_SYNC,
            pool_pre_ping=True,
            future=True,
        )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)


def dispose_db_sync() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def update_task_sync(task_id: UUID, **values) -> None:
    if _SessionLocal is None:
        raise RuntimeError("DB not initialized: call init_db_sync() first")

    try:
        with _SessionLocal() as session:
            stmt = (
                update(TranscriptionTaskModel)
                .where(TranscriptionTaskModel.id == task_id)
                .values(**values)
            )
            session.execute(stmt)
            session.commit()
    except SQLAlchemyError as e:
        log.error("Sync DB update failed", task_id=str(task_id), error=str(e))
