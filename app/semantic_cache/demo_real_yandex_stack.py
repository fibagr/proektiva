from __future__ import annotations

import os
import time
import uuid

from app.clients.yandex_client import yandex_chat_completion_ru
from app.core.config import settings
from app.domain.models import (
    AnxietyBlock,
    ConcentrationBlock,
    FullSurveyPayload,
    SleepBlock,
    StressBlock,
)
from app.domain.yandex_prompt_builder import yandex_build_prompt
from app.semantic_cache.config import semantic_cache_settings
from app.semantic_cache.service import SemanticCacheService
from app.semantic_cache.store import ChromaSemanticCacheStore
from app.semantic_cache.yandex_embeddings import yandex_text_embedding


def _payload(
    total: int,
    concentration_avg: float,
    anxiety: float,
    anxiety_level: str,
    stress: float,
    stress_level: str,
    sleep: float,
    sleep_level: str,
) -> FullSurveyPayload:
    return FullSurveyPayload(
        language="ru",
        concentration=ConcentrationBlock(total=total, average=concentration_avg),
        anxiety=AnxietyBlock(total=anxiety, average=anxiety / 7, level=anxiety_level),
        stress=StressBlock(total=stress, average=stress / 7, level=stress_level),
        sleep=SleepBlock(total=sleep, average=sleep / 7, level=sleep_level),
    )


def _print_candidates(store: ChromaSemanticCacheStore, embedding: list[float]) -> None:
    candidates = store.query_candidates(embedding, n_results=3)
    if not candidates:
        print("  candidates: none")
        return

    for idx, candidate in enumerate(candidates, start=1):
        similarity = (1.0 - candidate.distance) * 100.0
        preview = candidate.response_text.replace("\n", " ")[:120]
        print(
            f"  candidate_{idx}: similarity={similarity:6.2f}% "
            f"distance={candidate.distance:.4f} preview='{preview}...'"
        )


def _require_yandex_credentials() -> None:
    if not settings.yandex_api_key:
        raise RuntimeError("Yandex API key is not configured")
    if not settings.yandex_folder_id:
        raise RuntimeError("Yandex folder id is not configured")


def main() -> None:
    _require_yandex_credentials()

    semantic_cache_settings.semantic_cache_enabled = True
    semantic_cache_settings.semantic_cache_max_distance = 0.10
    semantic_cache_settings.semantic_cache_top_k = 3
    semantic_cache_settings.semantic_cache_prompt_version = "real-demo-v1"
    semantic_cache_settings.semantic_cache_chroma_path = ".chroma"
    semantic_cache_settings.semantic_cache_collection = (
        f"yandex_real_demo_{uuid.uuid4().hex[:8]}"
    )

    store = ChromaSemanticCacheStore()
    service = SemanticCacheService(store=store)

    dataset = [
        (
            "base_a",
            _payload(
                total=18,
                concentration_avg=2.3,
                anxiety=11.0,
                anxiety_level="moderate",
                stress=10.0,
                stress_level="moderate",
                sleep=8.0,
                sleep_level="moderate",
            ),
        ),
        (
            "similar_a",
            _payload(
                total=19,
                concentration_avg=2.4,
                anxiety=11.3,
                anxiety_level="moderate",
                stress=10.5,
                stress_level="moderate",
                sleep=8.3,
                sleep_level="moderate",
            ),
        ),
        (
            "base_b",
            _payload(
                total=8,
                concentration_avg=1.0,
                anxiety=22.0,
                anxiety_level="high",
                stress=21.0,
                stress_level="high",
                sleep=18.0,
                sleep_level="high",
            ),
        ),
        (
            "similar_b",
            _payload(
                total=9,
                concentration_avg=1.1,
                anxiety=21.4,
                anxiety_level="high",
                stress=20.8,
                stress_level="high",
                sleep=17.7,
                sleep_level="high",
            ),
        ),
        (
            "almost_a",
            _payload(
                total=15,
                concentration_avg=1.9,
                anxiety=13.5,
                anxiety_level="medium",
                stress=13.7,
                stress_level="medium",
                sleep=12.7,
                sleep_level="medium",
            ),
        ),
        (
            "different",
            _payload(
                total=30,
                concentration_avg=3.8,
                anxiety=3.0,
                anxiety_level="low",
                stress=4.0,
                stress_level="low",
                sleep=3.0,
                sleep_level="low",
            ),
        ),
    ]

    print("REAL semantic cache test")
    print(f"Chroma path: {os.path.abspath(semantic_cache_settings.semantic_cache_chroma_path)}")
    print(f"Collection: {semantic_cache_settings.semantic_cache_collection}")
    print("Stack: ChromaDB + Yandex Embedding + YandexGPT")
    print("Threshold: 90% similarity (distance <= 0.10)")
    print("-" * 80)

    for idx, (name, payload) in enumerate(dataset, start=1):
        print(f"[{idx}] Query: {name}")
        started = time.perf_counter()

        cache_text = service._build_cache_text(payload)
        query_embedding = yandex_text_embedding(cache_text, target="query")
        _print_candidates(store, query_embedding)

        cached = store.lookup(query_embedding)
        if cached is not None:
            similarity = (1.0 - cached.distance) * 100.0
            print(
                f"  result: HIT from cache | similarity={similarity:6.2f}% "
                f"distance={cached.distance:.4f}"
            )
            elapsed = time.perf_counter() - started
            print(f"  elapsed: {elapsed:.2f}s")
            print("-" * 80)
            continue

        print("  result: MISS -> calling YandexGPT")
        prompt = yandex_build_prompt(payload)
        response_text = yandex_chat_completion_ru(prompt)
        response_preview = response_text.replace("\n", " ")[:160]
        doc_embedding = yandex_text_embedding(cache_text, target="doc")
        store.upsert(query_text=cache_text, response_text=response_text, embedding=doc_embedding)
        print("  saved: yes")
        print(f"  gpt_preview: '{response_preview}...'")
        elapsed = time.perf_counter() - started
        print(f"  elapsed: {elapsed:.2f}s")
        print("-" * 80)


if __name__ == "__main__":
    main()
