from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any

from app.semantic_cache.config import semantic_cache_settings


@dataclass
class SemanticCacheHit:
    response_text: str
    distance: float


class ChromaSemanticCacheStore:
    def __init__(self) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "chromadb is required for semantic cache. Install dependencies first."
            ) from exc

        self._client = chromadb.PersistentClient(
            path=semantic_cache_settings.semantic_cache_chroma_path
        )
        self._collection = self._client.get_or_create_collection(
            name=semantic_cache_settings.semantic_cache_collection,
            metadata={"hnsw:space": "cosine"},
        )

    def lookup(self, embedding: list[float]) -> SemanticCacheHit | None:
        for candidate in self.query_candidates(embedding):
            distance_value = candidate.distance
            if distance_value <= semantic_cache_settings.semantic_cache_max_distance:
                return candidate

        return None

    def query_candidates(
        self, embedding: list[float], n_results: int | None = None
    ) -> list[SemanticCacheHit]:
        result = self._collection.query(
            query_embeddings=[embedding],
            n_results=n_results or semantic_cache_settings.semantic_cache_top_k,
            include=["documents", "distances", "metadatas"],
        )

        documents = (result.get("documents") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]

        candidates: list[SemanticCacheHit] = []
        for document, distance, metadata in zip(documents, distances, metadatas):
            if not document or distance is None:
                continue
            if _is_stale(metadata):
                continue
            if _is_version_mismatch(metadata):
                continue
            candidates.append(
                SemanticCacheHit(response_text=document, distance=float(distance))
            )

        return candidates

    def upsert(self, query_text: str, response_text: str, embedding: list[float]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        cache_id = sha256(
            f"{semantic_cache_settings.semantic_cache_prompt_version}:{query_text}".encode(
                "utf-8"
            )
        ).hexdigest()
        self._collection.upsert(
            ids=[cache_id],
            embeddings=[embedding],
            documents=[response_text],
            metadatas=[
                {
                    "created_at": now,
                    "prompt_version": semantic_cache_settings.semantic_cache_prompt_version,
                    "query_preview": query_text[:180],
                }
            ],
        )


def _is_version_mismatch(metadata: Any) -> bool:
    if not isinstance(metadata, dict):
        return False
    value = metadata.get("prompt_version")
    return value not in (None, semantic_cache_settings.semantic_cache_prompt_version)


def _is_stale(metadata: Any) -> bool:
    ttl_hours = semantic_cache_settings.semantic_cache_ttl_hours
    if ttl_hours <= 0 or not isinstance(metadata, dict):
        return False

    created_at = metadata.get("created_at")
    if not created_at or not isinstance(created_at, str):
        return False

    try:
        created_dt = datetime.fromisoformat(created_at)
    except ValueError:
        return False

    if created_dt.tzinfo is None:
        created_dt = created_dt.replace(tzinfo=timezone.utc)

    return datetime.now(timezone.utc) - created_dt > timedelta(hours=ttl_hours)
