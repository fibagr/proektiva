from app.domain.models import FullSurveyPayload
from app.domain.prompt_builder import build_prompt
from app.clients.openai_client import chat_completion_ru


def generate_recommendations_text(payload: FullSurveyPayload) -> str:
    prompt = build_prompt(payload)
    return chat_completion_ru(prompt)
