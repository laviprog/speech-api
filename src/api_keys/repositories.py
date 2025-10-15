from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from .models import ApiKeyModel


class ApiKeyRepository(SQLAlchemyAsyncRepository[ApiKeyModel]):
    """Api key repository"""

    model_type = ApiKeyModel
