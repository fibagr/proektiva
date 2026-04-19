from pydantic_settings import BaseSettings, SettingsConfigDict


class SemanticCacheSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    semantic_cache_enabled: bool = True
    semantic_cache_chroma_path: str = ".chroma"
    semantic_cache_collection: str = "yandex_semantic_cache"
    semantic_cache_top_k: int = 3
    semantic_cache_max_distance: float = 0.10
    semantic_cache_ttl_hours: int = 720
    semantic_cache_prompt_version: str = "v1"

    yandex_embedding_query_model: str = "text-search-query"
    yandex_embedding_doc_model: str = "text-search-doc"


semantic_cache_settings = SemanticCacheSettings()
