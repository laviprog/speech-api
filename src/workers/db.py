from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.config import settings
from src.transcription.models import TranscriptionResultModel, TranscriptionTaskModel
from src.workers import log

_engine = None
_SessionLocal: Optional[sessionmaker] = None


def init_db_sync() -> None:
    global _engine, _SessionLocal
    log.debug("Initializing sync DB engine")
    if _engine is None:
        _engine = create_engine(
            settings.DB_URL_SYNC,
            pool_pre_ping=True,
            future=True,
        )
        _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
        log.debug("Sync DB sessionmaker created")


def dispose_db_sync() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def update_task_sync(task_id: UUID, **values) -> None:
    global _SessionLocal
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


def save_transcription_result_sync(task_id: UUID, transcription_result: dict) -> None:
    global _SessionLocal
    if _SessionLocal is None:
        raise RuntimeError("DB not initialized: call init_db_sync() first")

    try:
        with _SessionLocal() as session:
            # Check if result already exists
            stmt = select(TranscriptionResultModel).where(
                TranscriptionResultModel.task_id == task_id
            )
            existing_result = session.execute(stmt).scalar_one_or_none()

            if existing_result:
                # Update existing result
                log.debug("Updating existing transcription result", task_id=str(task_id))
                existing_result.transcription_result = transcription_result
                session.commit()
            else:
                # Create new result
                log.debug("Creating new transcription result", task_id=str(task_id))
                result_model = TranscriptionResultModel(
                    task_id=task_id, transcription_result=transcription_result
                )
                session.add(result_model)
                session.commit()
    except SQLAlchemyError as e:
        log.error("Failed to save transcription result", task_id=str(task_id), error=str(e))
        raise
