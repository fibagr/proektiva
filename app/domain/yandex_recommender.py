import logging

from app.clients.yandex_client import yandex_chat_completion_ru
from app.domain.models import FullSurveyPayload
from app.domain.yandex_prompt_builder import yandex_build_prompt
from app.semantic_cache import get_semantic_cache_service

logger = logging.getLogger(__name__)


def yandex_generate_recommendations_text(payload: FullSurveyPayload) -> str:
    prompt = yandex_build_prompt(payload)

    try:
        cache_service = get_semantic_cache_service()
    except Exception as exc:
        logger.warning("Semantic cache initialization failed: %s", exc)
        cache_service = None

    if cache_service is not None:
        try:
            cached_response = cache_service.get_cached_response(payload)
            if cached_response is not None:
                logger.info("Semantic cache hit for Yandex request")
                return cached_response
        except Exception as exc:
            logger.warning("Semantic cache lookup failed, fallback to YandexGPT: %s", exc)

    response_text = yandex_chat_completion_ru(prompt)

    if cache_service is not None:
        try:
            cache_service.save_response(payload, response_text)
        except Exception as exc:
            logger.warning("Semantic cache save failed: %s", exc)

    return response_text
