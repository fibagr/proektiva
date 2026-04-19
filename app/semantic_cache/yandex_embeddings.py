from typing import Literal

import requests

from app.core.config import settings
from app.semantic_cache.config import semantic_cache_settings

YANDEX_EMBEDDING_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"


def _build_headers() -> dict[str, str]:
    if not settings.yandex_api_key:
        raise RuntimeError("Yandex API key is not configured")
    if not settings.yandex_folder_id:
        raise RuntimeError("Yandex folder id is not configured")

    return {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {settings.yandex_api_key}",
        "x-folder-id": settings.yandex_folder_id,
    }


def yandex_text_embedding(text: str, target: Literal["query", "doc"] = "query") -> list[float]:
    if not text.strip():
        raise ValueError("Text for embedding cannot be empty")

    model_name = (
        semantic_cache_settings.yandex_embedding_query_model
        if target == "query"
        else semantic_cache_settings.yandex_embedding_doc_model
    )
    payload = {
        "modelUri": f"emb://{settings.yandex_folder_id}/{model_name}/latest",
        "text": text,
    }

    try:
        response = requests.post(
            url=YANDEX_EMBEDDING_URL,
            headers=_build_headers(),
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"Error calling Yandex embeddings: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Yandex embeddings API error: {response.status_code} - {response.text}"
        )

    try:
        data = response.json()
        embedding = data["embedding"]
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("Yandex embeddings returned an unexpected response payload") from exc

    if not isinstance(embedding, list) or not embedding:
        raise RuntimeError("Yandex embeddings response did not include a valid embedding")

    return [float(value) for value in embedding]
