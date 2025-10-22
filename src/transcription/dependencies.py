from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends

from src.database.config import sqlalchemy_config
from src.transcription.services import TranscriptionTaskService


async def provide_transcription_task_service() -> AsyncGenerator[TranscriptionTaskService, None]:
    async with TranscriptionTaskService.new(config=sqlalchemy_config) as service:
        yield service


TranscriptionTaskServiceDep: TypeAlias = Annotated[
    TranscriptionTaskService, Depends(provide_transcription_task_service)
]
