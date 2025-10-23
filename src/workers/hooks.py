from datetime import datetime, timezone
from uuid import UUID

from celery import Task

from src.transcription.models import Status
from src.workers import log
from src.workers.db import save_transcription_result_sync, update_task_sync


class DBReportingTask(Task):
    def before_start(self, task_id, args, kwargs):
        try:
            update_task_sync(
                UUID(task_id),
                status=Status.IN_PROGRESS,
                started_at=datetime.now(timezone.utc),
                message="Processing transcription...",
            )
        except Exception as e:
            log.error("before_start update failed", task_id=task_id, error=str(e))

    def on_success(self, retval, task_id, args, kwargs):
        try:
            task_uuid = UUID(task_id)

            # Update task metadata
            update_task_sync(
                task_uuid,
                status=Status.COMPLETED,
                completed_at=datetime.now(timezone.utc),
                message="Completed successfully",
            )

            # Save transcription result separately if it exists
            if retval and isinstance(retval, dict) and "result" in retval:
                transcription_result = retval.get("result")
                if transcription_result:
                    save_transcription_result_sync(task_uuid, transcription_result)
                    log.debug("Transcription result saved", task_id=task_id)
                else:
                    log.warning("No transcription result in retval", task_id=task_id)
            else:
                log.warning(
                    "Unexpected retval format in on_success",
                    task_id=task_id,
                    retval_type=type(retval).__name__,
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
