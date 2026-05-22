r"""
共通 (シナリオ A〜C 共通): ナレッジ (Markdown / PDF) を File Search の Vector Store に登録。

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT = "<Foundry project endpoint>"
    python upload_knowledge.py ..\sample-knowledge\it-policy.md

⚠️ 本スクリプトは学習用に旧 API パターン (`client.agents.upload_file_and_poll`) を
   使用しています。新しいプロジェクトでは Responses API 経由が推奨です。
   詳細は各シナリオ README §5 を参照してください。
"""

import os
import sys

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def main(file_path: str) -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=endpoint, credential=cred, allow_preview=True
    ) as client:
        file = client.agents.upload_file_and_poll(
            file_path=file_path, purpose="assistants"
        )
        print(f"file_id           = {file.id}")
        vs = client.agents.create_vector_store_and_poll(
            file_ids=[file.id], name="it-policy-vs"
        )
        print(f"vector_store_id   = {vs.id}")
        print()
        print("次の値を環境変数に設定してください:")
        print(f'  $env:KNOWLEDGE_VECTOR_STORE_ID = "{vs.id}"')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python upload_knowledge.py <path-to-knowledge-file>")
        sys.exit(1)
    main(sys.argv[1])
