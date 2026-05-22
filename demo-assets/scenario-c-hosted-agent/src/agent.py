"""
Foundry Hosted Agent — IT Helpdesk サンプル
- File Search で社内 IT 規定 (it-policy.md) を引用
- CreateTicket tool でチケット起票

⚠️ Hosted agents API は Public Preview。最新の API 名・package 名は
   https://github.com/microsoft-foundry/foundry-samples の
   samples/python/hosted-agents を要確認。
   本ファイルは README §5.1 (Microsoft Agent Framework 版) の最小実装に揃えて
   あります。実環境で動かす前に上記サンプルの最新版と差分を確認してください。
"""

import os

import httpx
from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential
from pydantic import Field
from typing_extensions import Annotated


ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL = os.environ.get(
    "AZURE_AI_MODEL_DEPLOYMENT_NAME",
    os.environ.get("FOUNDRY_MODEL_NAME", "gpt-4.1-mini"),
)
VS_ID = os.environ.get("KNOWLEDGE_VECTOR_STORE_ID")
# PORT はプラットフォーム側で自動管理 (Foundry Hosted agent は内部で 8088 を listen)。
# 公式サンプル (microsoft-foundry/foundry-samples/.../responses/01-basic/main.py) は
# server.run() を引数なしで呼び出している。引数を渡すと SDK バージョンによっては
# TypeError が発生するため、明示指定はしない。


INSTRUCTIONS = """
あなたは Contoso 株式会社の社内 IT ヘルプデスク アシスタントです。

ガイドライン:
- 添付されたナレッジ (社内 IT 利用規定) から根拠を引用 [filename] 付きで回答してください。
- ナレッジに記載がない、または手順実行で解決しない場合に限り、ユーザーの同意を得たうえで CreateTicket ツールを呼んでチケットを起票してください。
- パスワード・MFA コード・PIN など秘密情報をユーザーに尋ねないでください。
- 緊急インシデント (情報漏えい・進行中の攻撃) は CSIRT ホットライン (内線 119) を案内してください。
"""


@tool(approval_mode="never_require")
def create_ticket(
    summary: Annotated[str, Field(description="問題の要約 (80 字以内)")],
    priority: Annotated[
        str, Field(description="low / medium / high / critical")
    ],
    category: Annotated[
        str,
        Field(
            description="account / network / device / software / security / other"
        ),
    ],
) -> str:
    """ユーザーが報告した IT 問題のチケットを起票する"""
    r = httpx.post(
        "https://httpbin.org/post",
        json={
            "summary": summary,
            "priority": priority,
            "category": category,
            "user_consent": True,
        },
        timeout=10.0,
    )
    return f"Ticket created: {r.json().get('json', {})}"


def main() -> None:
    client = FoundryChatClient(
        project_endpoint=ENDPOINT,
        model=MODEL,
        credential=DefaultAzureCredential(),
    )

    # File Search を使う場合は agent 作成時に vector_store_ids を渡す
    # (公式サンプルの最新版に合わせる)
    agent_kwargs = {
        "client": client,
        "instructions": INSTRUCTIONS,
        "tools": [create_ticket],
        "default_options": {"store": False},  # Foundry 側で履歴管理
    }
    if VS_ID:
        agent_kwargs["file_search_vector_store_ids"] = [VS_ID]

    agent = Agent(**agent_kwargs)

    server = ResponsesHostServer(agent)
    # 公式サンプル準拠: server.run() に host / port を渡さない。
    # ローカル動作確認では既定で localhost:8088 で listen される。
    server.run()


if __name__ == "__main__":
    main()
