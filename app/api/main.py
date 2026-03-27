from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.search import router as search_router
from app.api.routes.upload import router as upload_router
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    settings.ensure_directories()
    configure_logging()

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Semantic PDF search engine API.",
    )
    application.include_router(health_router)
    application.include_router(upload_router)
    application.include_router(search_router)
    return application


app = create_app()