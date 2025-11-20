from fastapi import FastAPI
from app.core.config import settings
from app.core.logging_config import configure_logging
from app.api.v1_recommendations import router as recommendations_router

configure_logging()

app = FastAPI(title=settings.app_name)

app.include_router(
    recommendations_router,
    prefix="/api/v1",
    tags=["recommendations"],
)
