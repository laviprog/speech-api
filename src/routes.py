from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from src.schemas import HealthCheck

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
        openapi_url="/api/v1/openapi.json",
        title="Speech recognition API",
    )


@router.get("/docs/scalar", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


def routes_register(app: FastAPI) -> None:
    app.include_router(router=router)
