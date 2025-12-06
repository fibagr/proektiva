from openai import OpenAI
from app.core.config import settings
import requests

client = OpenAI(api_key=settings.openai_api_key)


def yandex_chat_completion_ru(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {settings.yandex_api_key}",
        "x-folder-id": settings.yandex_folder_id
    }

    payload = {
        "modelUri": f"gpt://{settings.yandex_folder_id}/yandexgpt/latest",
        "completionOptions": {
            "stream": False,
            "temperature": 0.3,
            "maxTokens": 4000
        },
        "messages": [
            {
                "role": "system",
                "text": "Ты - опытный психолог, специалист по ментальному здоровью и сенсорной интеграции. Твоя задача - предоставлять профессиональные, научно-обоснованные рекомендации на основе данных тестирования."
            },
            {
                "role": "user",
                "text": prompt
            }
        ]
    }

    try:
        response = requests.post(
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            return result['result']['alternatives'][0]['message']['text']
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

    except Exception as e:
        raise Exception(f"Error calling YandexGPT: {str(e)}")