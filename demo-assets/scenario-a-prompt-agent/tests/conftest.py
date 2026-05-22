"""pytest 共通 fixture (シナリオ A).

環境変数:
    FOUNDRY_PROJECT_ENDPOINT  (必須)
    FOUNDRY_AGENT_NAME        (任意 / 既定 helpdesk-prompt)

実行例:
    pytest tests/ -v
    pytest tests/ -v -k password   # password に絞り込み
"""

from __future__ import annotations

import os
import re
from typing import Iterator

import pytest


@pytest.fixture(scope="session")
def endpoint() -> str:
    ep = os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
    if not ep:
        pytest.skip("FOUNDRY_PROJECT_ENDPOINT が未設定のためスキップ")
    return ep


@pytest.fixture(scope="session")
def agent_name() -> str:
    return os.environ.get("FOUNDRY_AGENT_NAME", "helpdesk-prompt")


@pytest.fixture(scope="session")
def openai_client(endpoint: str) -> Iterator:
    from azure.ai.projects import AIProjectClient
    from azure.identity import DefaultAzureCredential

    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=endpoint, credential=cred, allow_preview=True
    ) as client:
        yield client.get_openai_client()


@pytest.fixture
def conversation(openai_client):
    """multi-turn 用 conversation を作成し、テスト終了時に削除を試みる。"""
    conv = None
    try:
        conv = openai_client.conversations.create()
    except Exception:
        pytest.skip("conversations API が利用できないためスキップ")
    try:
        yield conv
    finally:
        try:
            openai_client.conversations.delete(conv.id)
        except Exception:
            pass


_PII_PATTERNS = [
    (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "***@***"),
    (re.compile(r"\b0\d{1,4}-\d{1,4}-\d{4}\b"), "***-****-****"),
    (re.compile(r"\b\d{3}-\d{4}\b"), "***-****"),
]


def mask_pii(text: str) -> str:
    """ログ出力前に PII を緩くマスキングする補助関数。"""
    for pattern, repl in _PII_PATTERNS:
        text = pattern.sub(repl, text)
    return text
