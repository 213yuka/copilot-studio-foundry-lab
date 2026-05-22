# シナリオ C: Copilot Studio → Foundry **Hosted agent (Preview)** 移行 完全手順書

> **位置付け**: 4 シナリオの中で **最大の自由度・最大の工数**
> **状態**: ⚠️ **Public Preview** (SLA 対象外、本番運用は非推奨)
> **想定工数**: 3〜10 人日

Copilot Studio の Topic / 分岐 / HITL を **すべて Python コードで再実装**し、コンテナ化して Azure Container Registry (ACR) に push、Foundry に **Hosted agent** として登録する移行パターン。既存の LangGraph / Semantic Kernel / Microsoft Agent Framework のコード資産を最大限活用できます。

---

## 0. 全体フロー

```
[Phase 1] Copilot Studio で IT-Helpdesk-Sample を作成
    └─ Topic 構造を Python 設計のリファレンスとして抽出
        ↓
[Phase 2] pac copilot extract-template で YAML 取得
    (設計参考、Foundry に直接流し込まない)
        ↓
[Phase 3] Foundry 受け側を準備
    ├─ Foundry project (azd ai agent init 推奨)
    ├─ モデル デプロイ
    ├─ ACR (Basic SKU 以上、Public endpoint 必須)
    ├─ Log Analytics + App Insights (テレメトリ)
    └─ RBAC: Foundry Project Manager + Contributor + AcrPush
        ↓
[Phase 4] コンテナ作成
    ├─ src/agent.py を Microsoft Agent Framework で記述
    ├─ Dockerfile (linux/amd64 必須、port 8088)
    └─ agent.yaml (kind: hosted, protocol: responses)
        ↓
[Phase 5] ビルド & プッシュ
    ├─ azd deploy (推奨、RBAC 自動付与) または
    ├─ docker build --platform linux/amd64 → docker push、または
    └─ az acr build (ローカル Docker 不要)
        ↓
[Phase 6] Hosted agent 登録
    ├─ azure-ai-projects SDK で create_version
    ├─ Project Managed Identity に AcrPull (Container Registry Repository Reader) 付与
    └─ Endpoint routing 構成 (patch_agent_details)
        ↓
[Phase 7] 動作確認 & テレメトリ確認
```

---

## 1. このシナリオが適する Copilot Studio エージェント

| 条件 | 該当 |
|---|---|
| 既に LangGraph / Semantic Kernel / Microsoft Agent Framework 等で書いた **コード資産**を Foundry に載せたい | ✅ |
| 独自モデル / 独自推論ロジック / 独自ベクトル DB を使いたい | ✅ |
| CI/CD パイプラインで完全にコード化したい | ✅ |
| スケール特性 (CPU / メモリ) を細かく制御したい | ✅ |
| 既存の OSS / 社内コードに依存している | ✅ |
| 短期間で公開したい | ❌ シナリオ A 推奨 |
| ノーコード保守を維持したい | ❌ シナリオ A / B 推奨 |
| ACR を Private endpoint 化したい | ❌ 現状 Hosted agent では非対応 (§9 参照) |

---

## 2. 前提条件

### 2.1 Copilot Studio 側 (Phase 1〜2 用)

📖 詳細は **`..\00-create-cs-agent.md`** 参照。

### 2.2 Azure / Foundry 側

公式 (Hosted agent 概念): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents>
公式 (デプロイ手順): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent>

| 項目 | 値 / 公式リンク |
|---|---|
| Foundry project | 必須 (Microsoft Foundry portal `ai.azure.com`) |
| ACR (Azure Container Registry) | Basic SKU 以上、**Public endpoint 必須** (§9.3) |
| Log Analytics + App Insights | テレメトリ用 (azd で自動プロビジョン) |
| **Azure Developer CLI (azd)** | ≥ 1.24.0 — `azd ext install azure.ai.agents` で agent 拡張も必要 |
| Azure CLI (az) | ≥ 2.80 |
| Python | 3.10 以上 |
| Docker Desktop | (任意。`azd deploy` / `az acr build` 利用なら不要) |
| VS Code + Microsoft Foundry Toolkit 拡張 | (任意、推奨) |
| Python SDK | `pip install "azure-ai-projects>=2.1.0" agent-framework agent-framework-foundry-hosting` |

### 2.3 RBAC 要件

| Who | Role | Scope | 用途 |
|---|---|---|---|
| デプロイ ユーザー | **Foundry Project Manager** | Project | Agent version 作成 + agent identity への role 付与 |
| デプロイ ユーザー | **Contributor** | Subscription | `azd` でリソース provision |
| デプロイ ユーザー | **Owner / User Access Administrator** | Subscription | Agent identity に Foundry User を付与 |
| デプロイ ユーザー | **AcrPush** (Container Registry Repository Writer) | ACR | コンテナ イメージ push |
| **Project Managed Identity** (自動作成) | **Container Registry Repository Reader** | ACR | プラットフォームが image pull |
| **Agent Entra Identity** (自動作成) | **Foundry User** | Foundry project | ランタイム時のモデル / tool アクセス |

> 💡 **azd または VS Code Foundry Toolkit を使えば、上記 RBAC は自動付与**されます。手動デプロイの場合のみ §6.4〜6.5 を実施。

### 2.4 Hosted agent ランタイム特性 (公式)

| 項目 | 値 |
|---|---|
| 同時セッション上限 | サブスクリプション × リージョンあたり 50 (サポート申請で増加可) |
| セッション保持期間 | 最大 30 日 |
| アイドル タイムアウト | 15 分 (15 分非アクティブで compute 解放、state は保持) |
| サンドボックス | Micro VM 分離 (per-session) |
| Listen ポート | **8088** (固定) |
| ARM アーキテクチャ | **linux/amd64 必須** (Apple Silicon 上では `--platform linux/amd64` 必須) |
| Scale-to-zero | ✅ 初回リクエストでプロビジョン、idle で解放 |
| 状態保持 | `$HOME` / `/files` ディレクトリは idle 越しに保持 |

---

## 3. Phase 1〜2: Copilot Studio でエージェント作成 → pac で抽出

📖 **詳細は `..\00-create-cs-agent.md` の §2〜§8**

このシナリオでは抽出した YAML を Foundry に直接流し込まず、**Python で再実装するための設計参考**として使います。具体的には:
- Topic ノード ツリー → Python の関数 + ステート マシン
- Power Fx 条件 → Python の `if` 文
- Question + Entity → LLM 呼出時の Function Calling パラメータ
- HTTP Request → `httpx` / `requests` での直接呼出 or OpenAPI tool 経由

---

## 4. Phase 3: Foundry 受け側の準備

### 4.1 azd でフル スタック プロビジョン (推奨)

```powershell
# azd インストール (未インストールなら)
winget install Microsoft.Azd

# agent 拡張
azd ext install azure.ai.agents

# 対話式スカフォールド (Foundry project + ACR + Log Analytics + App Insights を作成)
azd ai agent init

# プロビジョン
azd provision
```

`azd ai agent init` の対話プロンプトで:
- Subscription / Region 選択
- プロジェクト名 (= ディレクトリ名でも可)
- テンプレート: **Hosted agent (Python / Agent Framework)** を選択

### 4.2 手動プロビジョン (azd を使わない場合)

```powershell
$RG     = "rg-foundry-helpdesk-sample"
$REGION = "eastus"
$ACR    = "acrhelpdesk$((Get-Random -Max 9999))"

# Resource group
az group create -n $RG -l $REGION

# ACR (Basic SKU)
az acr create -g $RG -n $ACR --sku Basic

# Foundry resource + project は Bicep または portal で別途プロビジョン
# Bicep autodeploy: https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure
```

---

## 5. Phase 4: コンテナを書く

### 5.1 src/agent.py — Microsoft Agent Framework 版 (推奨)

📄 同梱: `src\agent.py`

公式サンプル: <https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents>

最小実装 (Responses protocol):

```python
import os
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential


def main():
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=DefaultAzureCredential(),
    )

    agent = Agent(
        client=client,
        instructions="""
        あなたは Contoso 社内 IT ヘルプデスク アシスタントです。
        ...(Copilot Studio Instructions を流用)
        """,
        default_options={"store": False},  # Foundry 側で履歴管理
    )

    server = ResponsesHostServer(agent)
    server.run()  # localhost:8088 で listen


if __name__ == "__main__":
    main()
```

カスタム tool 追加 (CreateTicket 相当):

```python
from agent_framework import Agent, tool
from pydantic import Field
from typing_extensions import Annotated

@tool(approval_mode="never_require")
def create_ticket(
    summary: Annotated[str, Field(description="問題の要約 (80 字以内)")],
    priority: Annotated[str, Field(description="low / medium / high / critical")],
    category: Annotated[str, Field(description="account / network / device / software / security / other")],
) -> str:
    """ユーザーが報告した IT 問題のチケットを起票する"""
    # 実装: httpx で社内 API 呼出
    import httpx
    r = httpx.post("https://httpbin.org/post", json={
        "summary": summary, "priority": priority,
        "category": category, "user_consent": True,
    })
    return f"Ticket {r.json().get('json', {})} created."

agent = Agent(
    client=client,
    instructions="...",
    tools=[create_ticket],
    default_options={"store": False},
)
```

### 5.2 requirements.txt

```
agent-framework>=1.2.2
agent-framework-foundry-hosting
azure-ai-projects>=2.1.0
azure-identity>=1.19.0
httpx>=0.27.0
```

### 5.3 Dockerfile

📄 同梱: `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY . user_agent/
WORKDIR /app/user_agent

RUN if [ -f requirements.txt ]; then \
        pip install -r requirements.txt; \
    else \
        echo "No requirements.txt found"; \
    fi

EXPOSE 8088

CMD ["python", "src/agent.py"]
```

> ⚠️ Apple Silicon / ARM 環境では必ず `--platform linux/amd64` で build (§6.2)

### 5.4 agent.yaml — azd デプロイ マニフェスト

> 📄 本シナリオは **SDK 経由 (`scripts\register_hosted_agent.py`) を正式手順**としており、`agent.yaml` は **同梱していません**。`azd ai agent init` / `azd deploy` ベースで運用する場合のみ、下記サンプルを `scenario-c-hosted-agent\agent.yaml` として配置してください。

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/microsoft/AgentSchema/refs/heads/main/schemas/v1.0/ContainerAgent.yaml
kind: hosted
name: helpdesk-hosted
protocols:
  - protocol: responses
    version: 1.0.0
resources:
  cpu: "0.25"
  memory: "0.5Gi"
environment_variables:
  - name: AZURE_AI_MODEL_DEPLOYMENT_NAME
    value: ${AZURE_AI_MODEL_DEPLOYMENT_NAME}
```

CPU / メモリ範囲: 0.25 vCPU / 0.5 GiB 〜 2 vCPU / 4 GiB

### 5.5 Responses Protocol の概要

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent#container-requirements>

| Protocol | Path | 用途 |
|---|---|---|
| Responses | `POST /responses` | OpenAI Responses 互換 (推奨) |
| Invocations | `POST /invocations` | 任意 JSON ペイロード (Webhook 等) |
| Healthcheck | `GET /readiness` | プロトコル ライブラリが自動公開 |

リクエスト例 (Responses):
```json
{
  "input": "パスワードを忘れた",
  "stream": false,
  "previous_response_id": "OPTIONAL",
  "agent_session_id": "OPTIONAL"
}
```

プラットフォームが自動注入する環境変数:

| 変数 | 内容 |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Project endpoint |
| `FOUNDRY_PROJECT_ARM_ID` | ARM ID |
| `FOUNDRY_AGENT_NAME` | Agent 名 |
| `FOUNDRY_AGENT_VERSION` | Version |
| `FOUNDRY_AGENT_SESSION_ID` | セッション ID |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | テレメトリ送信先 |

⚠️ これらを `agent.yaml` に再宣言しないこと (重複でエラー)。

---

## 6. Phase 5: ビルド & プッシュ

### 6.1 Option A: azd deploy (推奨、RBAC 自動)

```powershell
# プロビジョン済みなら:
azd deploy
# → リモートで build (Apple Silicon でも問題なし)
# → AcrPull / Foundry User の role assignment まで自動実行
# → Hosted agent の register / endpoint routing まで自動
```

### 6.2 Option B: 手動 Docker + az CLI

```powershell
# repo root から実行
cd .\demo-assets\scenario-c-hosted-agent

$ACR    = "acrhelpdesk1234"
$IMAGE  = "$ACR.azurecr.io/helpdesk-hosted:v1"

# linux/amd64 で build (Windows / Mac いずれも明示推奨)
docker build --platform linux/amd64 -t $IMAGE .

az acr login -n $ACR
docker push $IMAGE
```

### 6.3 Option C: az acr build (ローカル Docker 不要)

```powershell
az acr build `
  --registry $ACR `
  --image helpdesk-hosted:v1 `
  --platform linux/amd64 `
  .
```

### 6.4 Project Managed Identity に AcrPull 付与 (Option B / C のみ)

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent>

```powershell
# Project の System-assigned MI の Object ID を取得 (Azure portal → Foundry project → Identity)
$MI_OID  = "<project-managed-identity-object-id>"
$SUB     = "<subscription-id>"
$ACR_ID  = "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.ContainerRegistry/registries/$ACR"

az role assignment create `
  --assignee-object-id $MI_OID `
  --assignee-principal-type ServicePrincipal `
  --role "Container Registry Repository Reader" `
  --scope $ACR_ID
```

### 6.5 (登録後) Agent Identity に Foundry User 付与 (Option B / C のみ)

```powershell
# Agent Identity の Principal ID を取得
$AGENT_OID = az rest --method GET `
  --url "$($env:FOUNDRY_PROJECT_ENDPOINT)/agents/helpdesk-hosted?api-version=v1" `
  --resource "https://ai.azure.com" `
  --query "instance_identity.principal_id" --output tsv

# Foundry User を割り当て
az role assignment create `
  --assignee-object-id $AGENT_OID `
  --assignee-principal-type ServicePrincipal `
  --role "Foundry User" `
  --scope "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCT/projects/$PROJ"
```

---

## 7. Phase 6: Hosted agent を登録

### 7.1 SDK でレジスター

📄 同梱: `scripts\register_hosted_agent.py`

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent>

```powershell
pip install "azure-ai-projects>=2.1.0"

$env:FOUNDRY_PROJECT_ENDPOINT  = "https://<resource>.services.ai.azure.com/api/projects/<project>"
$env:AGENT_IMAGE               = "$ACR.azurecr.io/helpdesk-hosted:v1"
$env:FOUNDRY_MODEL_NAME        = "gpt-4.1-mini"

python scripts\register_hosted_agent.py
```

スクリプト内部:
```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, ProtocolVersionRecord, AgentProtocol
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    allow_preview=True,   # Hosted agent は preview 機能
)

agent = project.agents.create_version(
    agent_name="helpdesk-hosted",
    definition=HostedAgentDefinition(
        container_protocol_versions=[
            ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1.0.0")
        ],
        cpu="1",
        memory="2Gi",
        image=os.environ["AGENT_IMAGE"],
        environment_variables={
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": os.environ["FOUNDRY_MODEL_NAME"],
        },
    ),
)
print(f"Agent registered: {agent.name}, version: {agent.version}")
```

### 7.2 プロビジョン完了を polling

```python
import time
while True:
    info = project.agents.get_version(agent_name="helpdesk-hosted", agent_version=agent.version)
    status = info["status"]
    print(f"Status: {status}")
    if status == "active":
        break
    elif status == "failed":
        print(f"Failed: {info['error']}")
        break
    time.sleep(5)
```

通常 1 分以内に `active`。

### 7.3 Endpoint routing 構成

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/manage-hosted-agent>

```python
from azure.ai.projects.models import (
    AgentEndpoint, AgentEndpointProtocol,
    FixedRatioVersionSelectionRule, VersionSelector,
)

project.beta.agents.patch_agent_details(
    agent_name="helpdesk-hosted",
    agent_endpoint=AgentEndpoint(
        version_selector=VersionSelector(
            version_selection_rules=[
                FixedRatioVersionSelectionRule(agent_version=agent.version, traffic_percentage=100),
            ]
        ),
        protocols=[AgentEndpointProtocol.RESPONSES],
    ),
)
```

これで endpoint がアクティブになります:
```
{project_endpoint}/agents/helpdesk-hosted/endpoint/protocols/openai/v1/responses
```

---

## 8. Phase 7: 動作確認 & テレメトリ

### 8.1 SDK 経由で呼出

```python
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://ai.azure.com/.default"
)
client = AzureOpenAI(
    base_url=f"{os.environ['FOUNDRY_PROJECT_ENDPOINT']}/agents/helpdesk-hosted/endpoint/protocols/openai/v1",
    azure_ad_token_provider=token_provider,
    api_version="preview",
)
r = client.responses.create(input="パスワードを忘れた。社内 PC です。")
print(r.output_text)
```

### 8.2 ポータルで動作確認

- <https://ai.azure.com> → project → Agents → `helpdesk-hosted`
- **Playground** (Hosted agent も Playground で実行可能)
- **Logs** タブで App Insights のトレース確認

### 8.3 アプリ ログ確認

```powershell
# App Insights のログ
az monitor app-insights query `
  --apps <app-insights-name> -g $RG `
  --analytics-query "traces | where cloud_RoleName == 'helpdesk-hosted' | top 50 by timestamp desc"
```

---

## 9. 既知の制約 (公式確認済み)

| 領域 | 制約 |
|---|---|
| SLA | Public Preview、本番非推奨 |
| **ACR Public Endpoint 必須** | Private endpoint + public access disabled の構成は image pull 不可 |
| ARM アーキ | linux/amd64 のみ。ARM 上ビルドは `--platform linux/amd64` 必須 |
| 同時セッション | 50 / サブスク / リージョン (申請で増加可) |
| セッション保持 | 最大 30 日、15 分 idle で compute 解放 |
| Listen ポート | 8088 固定 |
| **Workflow デザイナーに直接配置不可** | A2A / OpenAPI / MCP 経由で間接統合 |
| Application Insights 接続文字列 | プラットフォームから自動注入 (再宣言しないこと) |
| SDK | `azure-ai-projects>=2.1.0` で `allow_preview=True` 必須 |

---

## 10. マッピング表: Copilot Studio → Hosted agent

| Copilot Studio 要素 | Hosted agent 側 |
|---|---|
| Topic | Python 関数 + ステート マシン / LangGraph の Node / Agent Framework の Agent |
| Trigger phrases | LLM の意図判定 (Instructions に列挙) |
| Condition (Power Fx) | Python の `if` 文 |
| Question + Entity | LLM Function Calling の `parameters` JSON Schema |
| Variables (Topic/Global) | Python 変数 / Cosmos DB / Redis 等 |
| Knowledge | File Search SDK / Foundry tool / 独自 RAG (Azure AI Search 等) |
| Action (HTTP) | `httpx` / `requests` / OpenAPI tool |
| Action (Power Automate Flow) | Logic Apps に移植 or Python 再実装 |
| HITL | カスタム実装 (Cosmos DB 承認待ち書込 → 別チャネル承認 → 続行) |
| Adaptive Card | クライアント (Teams / Web) 側で再実装 |
| Channel | Foundry Responses API を叩くフロントエンドを別途用意 (Teams なら Azure Bot Service 経由) |

---

## 11. 利点と欠点

| | 内容 |
|---|---|
| ✅ **利点** | **最大の自由度** / 既存コード資産再利用 / LangGraph / SK / 任意フレームワーク選択可 / コンテナでスケール制御 / Micro VM 分離で sandbox / Application Insights 自動接続 |
| ❌ **欠点** | **Public Preview** / Workflow デザイナー内に置けない / ACR / Docker / Bicep / RBAC の総合スキル必要 / 工数最大 / ACR は Public Endpoint 必須 / linux/amd64 限定 / 同時セッション 50 上限 |

---

## 12. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `Dockerfile` | コンテナ イメージ ビルド (linux/amd64 想定) |
| `requirements.txt` | Python 依存関係 |
| `src\agent.py` | Hosted Agent 本体 (Responses Protocol を expose) |
| `scripts\register_hosted_agent.py` | ACR の イメージを Foundry に Hosted Agent として登録 |
| `tools\create-ticket.openapi.yaml` | `..\common\tools\` のコピー (Docker ビルド コンテキスト用) |

実行コマンドは §5〜§7 を順に実行。

---

## 13. 関連公式ドキュメント

| トピック | URL |
|---|---|
| Hosted agent 概念 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents> |
| Hosted agent デプロイ手順 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent> |
| Hosted agent 管理 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/manage-hosted-agent> |
| Hosted agent Quickstart | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstarts/quickstart-hosted-agent> |
| Virtual Networks (制約) | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/virtual-networks> |
| 環境セットアップ | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/environment-setup> |
| Python Hosted agent サンプル | <https://github.com/microsoft-foundry/foundry-samples/tree/main/samples/python/hosted-agents> |
| Azure SDK サンプル | <https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/hosted_agents> |
| Microsoft Agent Framework | <https://github.com/microsoft/agent-framework> |
| Bicep infrastructure samples | <https://github.com/azure-ai-foundry/foundry-samples/tree/main/infrastructure> |
| RBAC | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry> |
