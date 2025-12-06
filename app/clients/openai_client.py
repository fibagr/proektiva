from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def openai_chat_completion_ru(prompt: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Ты психолог, даёшь мягкие, практичные рекомендации."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
        max_tokens=1200
    )
    content = completion.choices[0].message.content

    if content is None:
        raise RuntimeError("ChatGPT вернул пустой ответ")
    
    return content