import structlog
from celery.signals import (
    worker_process_init,
    worker_process_shutdown,
)

from src.workers.db import dispose_db_sync, init_db_sync

log = structlog.get_logger()


@worker_process_init.connect
def _proc_init(**_):
    from src.transcription.enums import Model
    from src.workers.state import get_transcriber

    log.info("Initializing resources...")
    init_db_sync()
    get_transcriber(preload=[Model.TURBO])
    log.info("Initialization complete")


@worker_process_shutdown.connect
def _proc_shutdown(**_):
    from src.workers.state import cleanup_transcriber

    log.info("Cleaning up resources...")
    dispose_db_sync()
    cleanup_transcriber()
    log.info("Shutdown complete")
