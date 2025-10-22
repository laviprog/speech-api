from typing import Annotated, AsyncGenerator, TypeAlias

from fastapi import Depends

from src.api_keys.services import ApiKeyService
from src.database.config import sqlalchemy_config


async def provide_api_key_service() -> AsyncGenerator[ApiKeyService, None]:
    async with ApiKeyService.new(config=sqlalchemy_config) as service:
        yield service


ApiKeyServiceDep: TypeAlias = Annotated[ApiKeyService, Depends(provide_api_key_service)]
