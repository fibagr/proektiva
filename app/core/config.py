import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str
    bot_api_key: str | None = None  # общий секрет с ботом
    app_name: str = "AI Recommendation Module"
    environment: str = "prod"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
