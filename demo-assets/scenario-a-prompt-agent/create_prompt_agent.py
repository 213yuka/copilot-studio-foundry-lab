"""
シナリオ A: Prompt agent (GA) を 1 体作成。
CS の Topic / 分岐ロジックを instructions に「言語化」して集約。

実行前に:
    $env:FOUNDRY_PROJECT_ENDPOINT     = "<Foundry プロジェクト endpoint>"
    $env:KNOWLEDGE_VECTOR_STORE_ID    = "<common/scripts/upload_knowledge.py の出力 vs id>"
    $env:FOUNDRY_MODEL_NAME           = "gpt-4.1-mini"   # (省略可)
"""

import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FileSearchTool,
    OpenApiTool,
    OpenApiFunctionDefinition,
)


ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
MODEL = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-4.1-mini")
VS_ID = os.environ["KNOWLEDGE_VECTOR_STORE_ID"]

# 共通 OpenAPI 定義を ../common/tools/ から読み込む
OPENAPI_PATH = (
    Path(__file__).resolve().parent.parent
    / "common" / "tools" / "create-ticket.openapi.yaml"
)
OPENAPI_SPEC = OPENAPI_PATH.read_text(encoding="utf-8")


# CS の Topic / 分岐ロジックを言語化したガイドライン
INSTRUCTIONS = """
あなたは Contoso 株式会社の社内 IT ヘルプデスク アシスタントです。

# 基本ルール
- 添付されたナレッジ (社内 IT 利用規定) から根拠を [filename] 付きで引用して回答する
- パスワード / MFA コード / PIN など秘密情報をユーザーに尋ねない
- 緊急インシデント (情報漏えい・進行中の攻撃) は CSIRT ホットライン (内線 119) を案内する

# Topic: パスワード忘れ / ロックアウト
ユーザーが「パスワードを忘れた」「ロックアウト」と言ったとき:
  1. まず「社内 PC からのご利用ですか、社外 PC ですか?」と確認する
  2. 「社内」と答えた場合:
       セルフサービス リセット ポータル (https://passwordreset.contoso.local) を案内する
  3. 「社外」と答えた場合:
       IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) を案内する
  4. アカウント ロックアウトは 5 回失敗で発生し 30 分後に自動解除される旨を補足する

# Topic: VPN 接続不可
ユーザーが「VPN がつながらない」と言ったとき:
  1. 社外ネットワークに接続されているか確認させる
  2. Microsoft Authenticator 通知を承認したか確認させる
  3. VPN クライアントの再起動を案内する
  4. 解決しなければ CreateTicket でチケットを起票する

# チケット起票ルール
- ナレッジでセルフサービス手順が見つからない、または手順実行後も解決しなかった場合のみ
- 起票前に必ずユーザーの同意を得ること
- summary (80 字以内) / priority / category を判断して埋める
"""


def main() -> None:
    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=ENDPOINT, credential=cred, allow_preview=True
    ) as client:
        agent = client.agents.create_version(
            agent_name="helpdesk-prompt",
            definition=PromptAgentDefinition(
                model=MODEL,
                instructions=INSTRUCTIONS,
                tools=[
                    FileSearchTool(vector_store_ids=[VS_ID]),
                    OpenApiTool(
                        openapi=OpenApiFunctionDefinition(
                            name="ticket_api",
                            description="ユーザーが報告した IT 問題のチケットを起票する",
                            spec=OPENAPI_SPEC,
                            auth={"type": "anonymous"},
                        )
                    ),
                ],
            ),
        )
        print(f"agent_name        = helpdesk-prompt")
        print(f"agent_version_id  = {agent.id}")


if __name__ == "__main__":
    main()
