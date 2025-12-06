from fastapi import APIRouter, Response, Header, HTTPException
from app.core.config import settings
from app.domain.models import FullSurveyPayload
from app.domain.openai_recommender import openai_generate_recommendations_text
from app.domain.openai_pdf_generator import openai_render_text_to_pdf
from app.domain.yandex_recommender import yandex_generate_recommendations_text
from app.domain.yandex_pdf_generator import yandex_render_text_to_pdf
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/recommendations", response_class=Response)
async def create_recommendations(
    payload: FullSurveyPayload,
    x_api_key: str | None = Header(default=None),
):
    # простая авторизация по ключу
    if settings.bot_api_key and x_api_key != settings.bot_api_key:
        logger.warning("Unauthorized request: wrong X-API-KEY")
        raise HTTPException(status_code=401, detail="Unauthorized")

    #logger.info("Received payload for chatId=%s", payload.chatId)

    if settings.ai_provider == "openai":
        text = openai_generate_recommendations_text(payload)
        pdf_bytes = openai_render_text_to_pdf(text)
        
    else: #elif settings.ai_provider == "yandex":
        text = yandex_generate_recommendations_text(payload)
        pdf_bytes = yandex_render_text_to_pdf(text,payload)

    headers = {
        "Content-Disposition": 'attachment; filename="recommendations.pdf"'
    }
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers=headers
    )
