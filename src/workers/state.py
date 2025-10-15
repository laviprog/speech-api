from __future__ import annotations

import threading
from typing import Optional, Sequence

from src.config import settings
from src.transcription.enums import Model
from src.workers.speech_transcriber import SpeechTranscriber

_TRANSCRIBER: Optional[SpeechTranscriber] = None
_LOCK = threading.Lock()


def get_transcriber(
    *,
    preload: Sequence[Model] | None = None,
) -> SpeechTranscriber:
    global _TRANSCRIBER
    if _TRANSCRIBER is None:
        with _LOCK:
            if _TRANSCRIBER is None:
                _TRANSCRIBER = SpeechTranscriber(
                    device=settings.DEVICE,
                    compute_type=settings.COMPUTE_TYPE,
                    download_root=settings.DOWNLOAD_ROOT,
                    init_models=list(preload or []),
                    batch_size=settings.BATCH_SIZE,
                    chunk_size=settings.CHUNK_SIZE,
                    hf_token=settings.HF_TOKEN,
                )
    return _TRANSCRIBER


def cleanup_transcriber():
    global _TRANSCRIBER
    with _LOCK:
        if _TRANSCRIBER is not None:
            try:
                _TRANSCRIBER.clean()
            finally:
                _TRANSCRIBER = None
