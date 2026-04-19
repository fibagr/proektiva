from __future__ import annotations

import json
from typing import Protocol

from app.domain.models import FullSurveyPayload
from app.semantic_cache.config import semantic_cache_settings
from app.semantic_cache.store import ChromaSemanticCacheStore
from app.semantic_cache.yandex_embeddings import yandex_text_embedding


class _CacheStore(Protocol):
    def lookup(self, embedding: list[float]): ...

    def upsert(self, query_text: str, response_text: str, embedding: list[float]): ...


class SemanticCacheService:
    def __init__(self, store: _CacheStore | None) -> None:
        self._store = store

    def get_cached_response(self, payload: FullSurveyPayload) -> str | None:
        if self._store is None:
            return None

        cache_text = self._build_cache_text(payload)
        query_embedding = yandex_text_embedding(cache_text, target="query")
        hit = self._store.lookup(query_embedding)
        if hit is None:
            return None
        return hit.response_text

    def save_response(self, payload: FullSurveyPayload, response_text: str) -> None:
        if self._store is None:
            return

        cache_text = self._build_cache_text(payload)
        doc_embedding = yandex_text_embedding(cache_text, target="doc")
        self._store.upsert(
            query_text=cache_text,
            response_text=response_text,
            embedding=doc_embedding,
        )

    @staticmethod
    def _build_cache_text(payload: FullSurveyPayload) -> str:
        payload_dict = payload.model_dump(mode="json", exclude_none=True)
        return json.dumps(payload_dict, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


_service_instance: SemanticCacheService | None = None


def get_semantic_cache_service() -> SemanticCacheService:
    global _service_instance

    if _service_instance is not None:
        return _service_instance

    if semantic_cache_settings.semantic_cache_enabled:
        _service_instance = SemanticCacheService(store=ChromaSemanticCacheStore())
    else:
        _service_instance = SemanticCacheService(store=None)

    return _service_instance
