from datetime import datetime
from uuid import UUID

from src.schemas import BaseSchema
from src.transcription.models import Status, TranscriptionTaskModel


class ModelList(BaseSchema):
    models: list[str]


class LanguageList(BaseSchema):
    languages: list[str]


class TranscriptionSegment(BaseSchema):
    number: int
    content: str
    speaker: int | None = None
    start: float
    end: float


class TranscriptionResult(BaseSchema):
    result: list[TranscriptionSegment]


class TranscriptionTask(BaseSchema):
    task_id: UUID
    status: Status
    created_at: datetime
    message: str | None = None
    result: TranscriptionResult | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def from_model(
        cls,
        transcription_task_model: TranscriptionTaskModel,
    ):
        return TranscriptionTask(
            task_id=transcription_task_model.id,
            status=transcription_task_model.status,
            message=transcription_task_model.message,
            result=TranscriptionResult(
                result=[
                    TranscriptionSegment(
                        number=segment["number"],
                        content=segment["content"],
                        speaker=segment.get("speaker", None),
                        start=segment["start"],
                        end=segment["end"],
                    )
                    for segment in transcription_task_model.transcription_result
                ]
            )
            if transcription_task_model.transcription_result
            else None,
            created_at=transcription_task_model.created_at,
            started_at=transcription_task_model.started_at,
            completed_at=transcription_task_model.completed_at,
        )
