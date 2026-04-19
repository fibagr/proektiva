from typing import Literal, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- выбор провайдера ИИ ---
    ai_provider: Literal["openai", "yandex"] = "openai"

    # --- OpenAI ---
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    # --- YandexGPT (Responses API) ---
    yandex_api_key: Optional[str] = None
    yandex_folder_id: Optional[str] = None
    yandex_model: str = "yandexgpt-lite"  # например: yandexgpt-lite, yandexgpt

    # --- прочее, как было ---
    bot_api_key: str | None = None  # общий секрет с ботом
    app_name: str = "AI Recommendation Module"
    environment: str = "prod"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
