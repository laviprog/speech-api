from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from src.config import settings
from src.schemas import HealthCheck
from src.transcription.routes import router as speech_recognition_router

router = APIRouter(tags=["Monitoring"])


@router.get(
    "/healthcheck",
    summary="Health Check",
    description="""
        Checks whether the API service is operational and responding
    """,
    responses={
        200: {
            "description": "Service is running",
        },
    },
)
async def healthcheck() -> HealthCheck:
    return HealthCheck()


@router.get("/docs", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=f"{settings.ROOT_PATH}/openapi.json",
        title="Speech recognition API",
    )


@router.get("/docs/scalar", include_in_schema=False)
async def redirect_to_docs(request: Request):
    docs_url = str(request.url_for("scalar_html"))
    return RedirectResponse(url=docs_url)


def routes_register(app: FastAPI) -> None:
    app.include_router(router=router)
    app.include_router(router=speech_recognition_router)
