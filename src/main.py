import src.database.models  # noqa
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.middlewares import LogMiddleware

from .exceptions.handlers import setup_exception_handlers
from .exceptions.responses import error_responses
from .lifecycle import lifespan
from .logging import configure as configure_logging
from .routes import routes_register

configure_logging()

app = FastAPI(
    title="Speech Recognition API",
    version="0.0.1",
    docs_url="/docs/swagger",
    openapi_url="/openapi.json",
    root_path="/api/v1",
    responses=error_responses,
    lifespan=lifespan,
)

setup_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LogMiddleware)

routes_register(app)
