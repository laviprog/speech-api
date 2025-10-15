from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from .models import TranscriptionTaskModel


class TranscriptionTaskRepository(SQLAlchemyAsyncRepository[TranscriptionTaskModel]):
    """Transcription task repository"""

    model_type = TranscriptionTaskModel
