import src.database.models  # noqa
import src.workers.signals  # noqa
import src.workers.db  # noqa

from celery import Celery

from src.config import settings

celery_app = Celery(
    "transcription_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    result_expires=settings.TASK_RESULT_EXPIRES,
    task_time_limit=settings.TASK_TIME_LIMIT,
    task_soft_time_limit=settings.TASK_TIME_LIMIT - 60,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_transport_options={"visibility_timeout": settings.TASK_TIME_LIMIT + 600},
)

celery_app.autodiscover_tasks(["src.workers"])
