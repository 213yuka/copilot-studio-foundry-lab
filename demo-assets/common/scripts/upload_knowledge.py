r"""
共通 (シナリオ A〜C 共通): ナレッジ (Markdown / PDF) を File Search の Vector Store に登録。

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT = "<Foundry project endpoint>"
    python upload_knowledge.py ..\sample-knowledge\it-policy.md

新しい Foundry projects (azure-ai-projects >= 2.0) は OpenAI 互換の Responses API 経由で
vector store を作成します (旧 `client.agents.upload_file_and_poll` API は削除済み)。

出力:
    file_id           = file_xxxxxxxx
    vector_store_id   = vs_xxxxxxxx
"""

import os
import sys

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main(file_path: str, vs_name: str = "it-policy-vs") -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=endpoint, credential=cred, allow_preview=True
    ) as client:
        openai = client.get_openai_client()

        with open(file_path, "rb") as f:
            uploaded = openai.files.create(file=f, purpose="assistants")
        print(f"file_id           = {uploaded.id}")

        vs = openai.vector_stores.create(name=vs_name, file_ids=[uploaded.id])
        # ingestion が完了するまで poll
        vs = openai.vector_stores.poll(vector_store_id=vs.id) if hasattr(
            openai.vector_stores, "poll"
        ) else vs
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
