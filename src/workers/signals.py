from celery.signals import worker_process_init, worker_process_shutdown

from src.transcription.enums import Model
from src.workers.db import dispose_db_sync, init_db_sync
from src.workers.state import get_transcriber


@worker_process_init.connect
def _warmup(**_):
    init_db_sync()
    get_transcriber(preload=[Model.SMALL])


@worker_process_shutdown.connect
def _shutdown_proc(**_):
    dispose_db_sync()
