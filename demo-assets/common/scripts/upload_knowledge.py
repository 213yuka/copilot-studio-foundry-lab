r"""
共通 (シナリオ A〜C 共通): ナレッジ (Markdown / PDF) を File Search の Vector Store に登録。

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT = "<Foundry project endpoint>"
    python upload_knowledge.py ..\sample-knowledge\it-policy.md

新しい Foundry projects (azure-ai-projects >= 2.0) は OpenAI 互換の Responses API 経由で
vector store を作成します (旧 `client.agents.upload_file_and_poll` API は削除済み)。

公式リファレンス:
- https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search
- https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/limits-quotas-regions (rate limit)

出力:
    file_id           = file_xxxxxxxx
    vector_store_id   = vs_xxxxxxxx
"""

from __future__ import annotations

import os
import random
import sys
import time
from typing import Callable, TypeVar

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

T = TypeVar("T")

# 公式の指示に従い指数バックオフ + ジッターでリトライする。
# 「If you receive a 429 response, implement exponential backoff with jitter.」
_MAX_RETRIES = 5
_BASE_DELAY_SECONDS = 2.0


def _with_retry(fn: Callable[[], T], description: str) -> T:
    """RateLimitError / 一時的 5xx を指数バックオフ + ジッターでリトライする。"""
    try:
        from openai import APIError, RateLimitError  # 遅延 import
    except Exception:  # noqa: BLE001
        APIError = RateLimitError = Exception  # type: ignore[assignment]

    last_exc: BaseException | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            return fn()
        except RateLimitError as exc:  # type: ignore[misc]
            last_exc = exc
            wait = _BASE_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 1)
            print(
                f"[retry] {description}: rate limited, sleeping {wait:.1f}s "
                f"(attempt {attempt + 1}/{_MAX_RETRIES})"
            )
            time.sleep(wait)
        except APIError as exc:  # type: ignore[misc]
            status = getattr(exc, "status_code", None)
            if status is None or status < 500:
                raise
            last_exc = exc
            wait = _BASE_DELAY_SECONDS * (2 ** attempt) + random.uniform(0, 1)
            print(
                f"[retry] {description}: server error {status}, sleeping {wait:.1f}s "
                f"(attempt {attempt + 1}/{_MAX_RETRIES})"
            )
            time.sleep(wait)
    raise RuntimeError(
        f"{description}: exceeded {_MAX_RETRIES} retries"
    ) from last_exc


def main(file_path: str, vs_name: str = "it-policy-vs") -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=endpoint, credential=cred, allow_preview=True
    ) as client:
        openai = client.get_openai_client()

        # 公式推奨の upload_and_poll を使い、ファイル アップロードと
        # ベクトル化の完了待ちを 1 呼び出しで実施する。
        # https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search
        if hasattr(openai.vector_stores, "files") and hasattr(
            openai.vector_stores.files, "upload_and_poll"
        ):
            with open(file_path, "rb") as f:
                vs = _with_retry(
                    lambda: openai.vector_stores.create(name=vs_name),
                    description="vector_stores.create",
                )
                vs_file = _with_retry(
                    lambda: openai.vector_stores.files.upload_and_poll(
                        vector_store_id=vs.id, file=f
                    ),
                    description="vector_stores.files.upload_and_poll",
                )
            print(f"file_id           = {vs_file.id}")
            print(f"vector_store_id   = {vs.id}")
            print(f"vector_store_name = {vs.name}")
        else:
            # 後方互換: 旧 SDK では files.create → vector_stores.create → 完了待ち
            with open(file_path, "rb") as f:
                uploaded = _with_retry(
                    lambda: openai.files.create(file=f, purpose="assistants"),
                    description="files.create",
                )
            print(f"file_id           = {uploaded.id}")
            vs = _with_retry(
                lambda: openai.vector_stores.create(
                    name=vs_name, file_ids=[uploaded.id]
                ),
                description="vector_stores.create",
            )
            # status が completed になるまでポーリング
            while True:
                refreshed = _with_retry(
                    lambda: openai.vector_stores.retrieve(vector_store_id=vs.id),
                    description="vector_stores.retrieve",
                )
                status = getattr(refreshed, "status", None)
                if status in ("completed", "failed"):
                    if status == "failed":
                        raise RuntimeError(
                            f"vector store ingestion failed: {refreshed}"
                        )
                    break
                time.sleep(2.0)
            print(f"vector_store_id   = {vs.id}")
            print(f"vector_store_name = {vs.name}")

        print()
        print("次の値を環境変数に設定してください:")
        print(f'  $env:KNOWLEDGE_VECTOR_STORE_ID = "{vs.id}"')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python upload_knowledge.py <path-to-knowledge-file>")
        sys.exit(1)
    main(sys.argv[1])

