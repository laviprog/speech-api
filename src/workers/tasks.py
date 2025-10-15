import os

from ..transcription.enums import Language, Model
from .app import celery_app
from .hooks import DBReportingTask
from .state import get_transcriber


@celery_app.task(
    bind=True, name="transcribe_audio", base=DBReportingTask, max_retries=3, default_retry_delay=60
)
def transcribe_audio(
    self,
    *,
    audio_file: str,
    model: str,
    language: str,
    recognition_mode: bool,
    num_speakers: int | None,
) -> dict:
    transcriber = get_transcriber()

    segments = transcriber.transcribe(
        audio_file=audio_file,
        model=Model(model),
        language=Language(language),
        recognition_mode=recognition_mode,
        num_speakers=num_speakers,
    )

    result = [
        {
            "number": i + 1,
            "content": segment["text"].strip(),
            "speaker": int(segment["speaker"].split("_")[-1]) + 1
            if segment.get("speaker", None)
            else None,
            "start": segment["start"],
            "end": segment["end"],
        }
        for i, segment in enumerate(segments)
    ]

    try:
        os.remove(audio_file)
    except FileNotFoundError:
        pass

    return {
        "result": result,
    }
