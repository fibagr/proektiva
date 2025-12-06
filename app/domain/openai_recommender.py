from app.domain.models import FullSurveyPayload
from app.domain.openai_prompt_builder import openai_build_prompt
from app.clients.openai_client import openai_chat_completion_ru


def openai_generate_recommendations_text(payload: FullSurveyPayload) -> str:
    prompt = openai_build_prompt(payload)
    return openai_chat_completion_ru(prompt)
