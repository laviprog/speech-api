from datetime import datetime, timezone
from uuid import UUID

from celery import Task

from src.transcription.models import Status
from src.workers import log
from src.workers.db import update_task_sync


class DBReportingTask(Task):
    def before_start(self, task_id, args, kwargs):
        try:
            update_task_sync(
                UUID(task_id), status=Status.IN_PROGRESS, started_at=datetime.now(timezone.utc)
            )
        except Exception as e:
            log.error("before_start update failed", task_id=task_id, error=str(e))

    def on_success(self, retval, task_id, args, kwargs):
        try:
            update_task_sync(
                UUID(task_id),
                status=Status.COMPLETED,
                completed_at=datetime.now(timezone.utc),
                transcription_result=retval.get("result"),
                message="Completed successfully",
            )
        except Exception as e:
            log.error("on_success update failed", task_id=task_id, error=str(e))

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            update_task_sync(
                UUID(task_id),
                status=Status.FAILED,
                completed_at=datetime.now(timezone.utc),
                message=str(exc) or "Failed transcription",
            )
        except Exception as e:
            log.error("on_failure update failed", task_id=task_id, error=str(e))
