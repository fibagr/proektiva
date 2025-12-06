from app.domain.models import FullSurveyPayload
from app.domain.yandex_prompt_builder import yandex_build_prompt
from app.clients.yandex_client import yandex_chat_completion_ru


def yandex_generate_recommendations_text(payload: FullSurveyPayload) -> str:
    prompt = yandex_build_prompt(payload)
    return yandex_chat_completion_ru(prompt)
