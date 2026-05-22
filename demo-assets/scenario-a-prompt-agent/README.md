# シナリオ A: Copilot Studio → Foundry **Prompt agent (GA)** 移行 完全手順書

> **位置付け**: 4 シナリオの中で **最短ルート / GA 機能のみ**
> **想定工数**: 0.5〜1 人日

CS の Topic / 分岐ロジックを **Instructions (自然言語ガイダンス) に集約**し、Knowledge を **File Search**、Action を **OpenAPI tool** として Foundry Prompt agent に登録する移行パターンです。

---

## 0. 全体フロー

```
[Phase 1] CS で IT-Helpdesk-Sample を作成
    ├─ Knowledge: it-policy.md
    ├─ Topic: PasswordReset (Question + Power Fx)
    └─ Action: CreateTicket (HTTP)
        ↓
[Phase 2] pac copilot extract-template で YAML 取得
        ↓
[Phase 3] Foundry 受け側を準備
    ├─ Foundry project (新ポータル)
    ├─ モデル (gpt-4.1-mini) デプロイ
    ├─ RBAC (Foundry User)
    └─ Vector Store (it-policy.md アップロード)
        ↓
[Phase 4] Prompt agent を登録
    ├─ Instructions (Topic ロジックを言語化)
    ├─ FileSearchTool
    └─ OpenApiTool (CreateTicket)
        ↓
[Phase 5] Playground で動作確認 → 回帰テスト
```

---

## 1. このシナリオが適する CS エージェント

| 条件 | 該当 |
|---|---|
| Topic 数が少ない (≤ 5) | ✅ |
| 分岐ロジックが「LLM の常識 + 短い文章ガイドライン」で十分カバー可能 | ✅ |
| 知識参照 (RAG) + 数本の外部 API 呼出が中心 | ✅ |
| **GA で SLA 付きの本番運用**にしたい | ✅ |
| 確定的・厳密なフロー保証が必要 (必ず質問→分岐) | ❌ シナリオ B 推奨 |
| Power Automate Flow の高度な処理を維持したい | ❌ シナリオ B / C 推奨 |

---

## 2. 前提条件

### 2.1 Copilot Studio 側 (Phase 1〜2 用)

📖 詳細は **`..\00-create-cs-agent.md`** を参照。

| 項目 | 値 |
|---|---|
| ライセンス | Copilot Studio Standalone / Trial / M365 Copilot のいずれか |
| 環境 | Production 環境推奨。Dataverse search 有効 |
| Maker 権限 | agent author (作成) + System Customizer (export) |
| pac CLI | `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` |

### 2.2 Foundry 側 (Phase 3〜5 用)

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview>

| 項目 | 値 / 公式リンク |
|---|---|
| Azure サブスクリプション | 必須 |
| Foundry portal | <https://ai.azure.com>(**"New Foundry"** トグルを ON) |
| アーキテクチャ | **Foundry resource → Foundry project** (旧 Hub-based projects は非サポート) |
| Endpoint 形式 | `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| モデル デプロイ | `gpt-4.1-mini` 推奨 (Models + Endpoints から確認) |
| RBAC (作成) | **Foundry Account Owner** (subscription scope) |
| RBAC (Agent 編集) | **Foundry User** (project scope、principal & MI 両方) — 旧称 Azure AI User |
| RBAC (ファイル アップロード) | + **Storage Blob Data Contributor** (project の storage account) |
| リージョン | Responses API 対応リージョン (File Search は **Italy North / Brazil South 不可**) |
| Python SDK | `pip install "azure-ai-projects>=2.0.0" azure-identity openai` |

公式 RBAC リファレンス: <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry>
公式 環境セットアップ: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/environment-setup>

> ⚠️ **`Cognitive Services User` / `Azure AI Developer` などの旧ロールは Foundry project には適用されません。** 新名称の **Foundry** ロールを使用してください (2024 後半に rename)。

---

## 3. Phase 1〜2: CS でエージェント作成 → pac で抽出

📖 **詳細は `..\00-create-cs-agent.md` の §2〜§8**

このシナリオで必要な情報:
- 抽出した `IT-Helpdesk-Sample.yaml` (本シナリオでは設計参照用。Foundry にそのまま流し込むことはしない)
- Knowledge ファイル本体 `it-policy.md` (CS export には含まれないため、リポジトリ同梱の `..\common\sample-knowledge\it-policy.md` を再利用)
- OpenAPI 定義 `..\common\tools\create-ticket.openapi.yaml`

---

## 4. Phase 3: Foundry プロジェクトの準備

### 4.1 Foundry resource + project を作成

公式 Quickstart: <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code>

1. <https://ai.azure.com> にサインイン
2. 右上 **New Foundry** トグル ON
3. ホーム → **+ Create a project** → 名前 / リージョン / セットアップ (Basic 推奨) を入力
4. プロジェクト作成完了後、左上の **Project endpoint** をコピー
   形式: `https://<resource>.services.ai.azure.com/api/projects/<project>`

### 4.2 モデルをデプロイ

1. 左メニュー **Models + Endpoints** → **+ Deploy model**
2. `gpt-4.1-mini` を選択 (region: East US 等、利用可能なリージョン)
3. Deployment name = `gpt-4.1-mini`、SKU = GlobalStandard
4. **Deploy**

### 4.3 RBAC を割り当てる

```powershell
# 自分自身に Foundry User を割り当て (Az CLI)
$RG       = "rg-foundry-demo"
$ACCT     = "<Foundry account name>"
$PROJ     = "<Foundry project name>"
$SUB      = "<subscription id>"

az role assignment create `
  --assignee <your-email-or-objectId> `
  --role "Foundry User" `
  --scope "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCT/projects/$PROJ"
```

### 4.4 環境変数を設定

```powershell
$env:FOUNDRY_PROJECT_ENDPOINT  = "https://<resource>.services.ai.azure.com/api/projects/<project>"
$env:FOUNDRY_MODEL_NAME        = "gpt-4.1-mini"
az login    # DefaultAzureCredential 用
```

---

## 5. Phase 3b: Vector Store に it-policy.md をアップロード

公式 (File Search): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search>
公式 (Vector Stores): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/vector-stores>

| 項目 | 上限 |
|---|---|
| 最大ファイル サイズ | 512 MB |
| 1 ファイルあたり最大トークン | 2,000,000 |
| 1 vector store の最大ファイル数 | 10,000 |
| Agent に紐づけ可能な vector store 数 | **1** |

### 実行

```powershell
# repo root から実行
cd .\demo-assets

pip install "azure-ai-projects>=2.0.0" azure-identity openai

python common\scripts\upload_knowledge.py common\sample-knowledge\it-policy.md
# 出力:
#   file_id           = file_xxxxxxxx
#   vector_store_id   = vs_xxxxxxxx

$env:KNOWLEDGE_VECTOR_STORE_ID = "vs_xxxxxxxx"
```

> ⚠️ 同梱の `upload_knowledge.py` は学習用に旧 API パターン (`client.agents.upload_file_and_poll`) を使用しています。
> **新しいプロジェクトでは下記の Responses API 経由が推奨**:
> ```python
> openai = project.get_openai_client()
> vs = openai.vector_stores.create(name="it-policy-vs")
> openai.vector_stores.files.upload_and_poll(vector_store_id=vs.id, file=open("it-policy.md","rb"))
> ```
> いずれの方式でも生成される vector_store_id は同形式 (`vs_*`)。

---

## 6. Phase 4: Prompt agent を作成

### 6.1 ポータルで作成する場合

公式 Quickstart: <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code>

1. <https://ai.azure.com> → 対象 project → 左メニュー **Agents**
2. **+ Create** → **Prompt agent** (GA タグ付き)
3. 各フィールドを入力:

| Field (UI ラベル) | 値 |
|---|---|
| **Name** | `helpdesk-prompt` |
| **Model** | `gpt-4.1-mini` |
| **Instructions** | 下の §6.3 を貼り付け |
| **Tools → + Add tool → File search** | 上で作成した vector store を選択 |
| **Tools → + Add tool → OpenAPI** | `..\common\tools\create-ticket.openapi.yaml` を貼り付け、Auth = Anonymous |

4. **Save** → **Agent playground** が自動で開く

### 6.2 Python SDK で作成する場合 (再現性 / CI 向け)

📄 本シナリオ同梱: `create_prompt_agent.py`

```powershell
# repo root から実行
cd .\demo-assets\scenario-a-prompt-agent
pip install -r requirements.txt

# 環境変数は §4.4 + §5 で設定済み
python create_prompt_agent.py
```

出力:
```
agent_name        = helpdesk-prompt
agent_version_id  = ver_xxxxxxxx
```

> 💡 **GA SDK では agent は `(agent_name, agent_version)` で識別** されます (旧 `agent_id` GUID は廃止)。
> 同梱スクリプトは `client.agents.create_version()` を呼んでおり、最新 SDK に準拠しています。
> 公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components>

### 6.3 Instructions テンプレート (CS Topic の言語化)

CS の **PasswordReset Topic + 分岐** を以下のように自然言語化します。同梱の `create_prompt_agent.py` の `INSTRUCTIONS` 定数に既に含まれています。

```
あなたは Contoso 株式会社の社内 IT ヘルプデスク アシスタントです。

# 基本ルール
- 添付されたナレッジ (社内 IT 利用規定) から根拠を [filename] 付きで引用する
- パスワード / MFA コード / PIN など秘密情報をユーザーに尋ねない
- 緊急インシデント (情報漏えい・進行中の攻撃) は CSIRT ホットライン (内線 119) を案内する

# Topic: パスワード忘れ / ロックアウト
ユーザーが「パスワードを忘れた」「ロックアウト」と言ったとき:
  1. 「社内 PC からのご利用ですか、社外 PC ですか?」と確認する
  2. 「社内」→ セルフサービス ポータル https://passwordreset.contoso.local を案内
  3. 「社外」→ IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) を案内
  4. ロックアウトは 5 回失敗で発生、30 分後に自動解除と補足

# チケット起票ルール
- ナレッジでセルフサービス手順が見つからない、または手順実行後も解決しなかった場合のみ
- 起票前に必ずユーザーの同意を得る
- summary (80 字以内) / priority / category を判断して埋める
```

### 6.4 OpenAPI tool の認証

| Auth type | Python class | 用途 |
|---|---|---|
| **Anonymous** | `OpenApiAnonymousAuthDetails()` | 公開エンドポイント (本デモはこれ) |
| **API Key (connection)** | `OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=...))` | API key の Connection を Foundry ポータルで作成し、ID を参照 |
| **Managed Identity** | `OpenApiManagedAuthDetails(security_scheme=OpenApiManagedSecurityScheme(audience="..."))` | Entra 保護 API |

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec>

> ⚠️ OpenAPI spec の各 operation は `operationId` 必須 (英字 + `-` + `_` のみ)。

---

## 7. Phase 5: Playground で動作確認

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/concept-playgrounds>

### 7.1 Playground

1. <https://ai.azure.com> → project → **Agents** → `helpdesk-prompt` → **Playground**
2. テストメッセージ:
   - `MFA の登録方法を教えて` → File Search 引用ありで返答 (`[it-policy.md]`)
   - `パスワード忘れた` → 社内 PC / 社外 PC を確認 → 適切な案内
   - `VPN がつながらない` → ナレッジで解決しなければ CreateTicket 呼出を提案
3. 右ペインの **Trace** で File Search / OpenAPI 呼び出しを可視化

### 7.2 SDK 経由でプログラマティックに呼ぶ (回帰テスト用)

新しい Foundry projects は **Responses + Conversations API** が標準:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import os

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
openai = project.get_openai_client()

response = openai.responses.create(
    input="パスワードを忘れた。社内PCです。",
    extra_body={"agent_reference": {"name": "helpdesk-prompt", "type": "agent_reference"}},
)
print(response.output_text)
```

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components>

### 7.3 回帰テスト推奨

CS → Foundry 移行では Topic ロジックの再現性検証が必須。最低でも以下のシナリオを 3〜5 回実行:

| 検証項目 | 期待動作 |
|---|---|
| パスワード忘れ + 社内 PC | セルフサービス URL を案内、チケットは起票しない |
| パスワード忘れ + 社外 PC | IT ヘルプデスク連絡先を案内 |
| 解決しなかった旨を続報 | 同意を取って CreateTicket を呼出 |
| MFA 登録質問 | it-policy.md §2.2 から引用 |
| 機密情報の要求 (PIN を教えろ) | 拒否、CSIRT 案内 |

intent 一致率 90% 以上を目標に。

---

## 8. マッピング表: CS → Prompt agent

| CS 要素 | Prompt agent 側 |
|---|---|
| Description (Generative orchestration 用) | `PromptAgentDefinition.description` |
| Instructions | `PromptAgentDefinition.instructions` (8,000 文字 → 制限なし) |
| Topic (Trigger phrases + ノード) | **すべて Instructions に言語化**。Trigger 句は「ユーザーが〜と言ったとき」、ノードは番号付き手順 |
| Question ノード | LLM が自然言語で逆質問 (**確定的ではない**) |
| Power Fx 条件 | Instructions の条件文 (`もし X なら…` 等) |
| Knowledge (File upload) | `FileSearchTool(vector_store_ids=[vs_id])` |
| Knowledge (SharePoint) | Foundry に **Project connection** で SharePoint 接続を作成 → `SharepointTool` (auth = connection) |
| Action (HTTP Request) | `OpenApiTool(openapi=OpenApiFunctionDefinition(spec=...))` |
| Action (Power Automate Flow) | Flow を独立 API 化して OpenAPI 接続するか、シナリオ C で Python 再実装 |
| Adaptive Card | Prompt agent の出力フォーマットでは表現困難 → クライアント側で再実装 |

---

## 9. 利点と欠点

| | 内容 |
|---|---|
| ✅ **利点** | GA で SLA 対象 / 最速本番化 / 1,900+ モデル選択可 / コード量最小 / Playground 即試行 / Responses API による履歴自動管理 |
| ❌ **欠点** | **確定的フロー (必ず質問→分岐) は LLM 任せで保証されない** / Topic 多いと Instructions 肥大化 / Adaptive Card 非対応 / 細かいルート制御は Generative orchestration の Description 頼み |

---

## 10. 既知の制約 / トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `DefaultAzureCredential` で 401 | ローカルで `az login` してない | `az login` → 再実行 |
| `Permission denied` で agent 作成不可 | Foundry User 未割り当て | §4.3 を実施 |
| File Search が結果を返さない | Vector store ingestion 未完了 | `vs.file_counts.completed` を polling、`completed` 待ち |
| OpenAPI tool が呼ばれない | operationId 不正 / Instructions に呼出条件が書かれていない | OpenAPI spec を `pip install jsonref` で確認、Instructions に呼出条件追記 |
| Italy North / Brazil South で File Search エラー | 地域制限 | 別リージョンに project 作成 |

---

## 11. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `requirements.txt` | Python 依存関係 (azure-ai-projects, azure-identity 他) |
| `create_prompt_agent.py` | Prompt agent を 1 体作成するスクリプト |

実行コマンドは §6.2 参照。

---

## 12. 関連公式ドキュメント (リファレンス)

| トピック | URL |
|---|---|
| Agent Service 概要 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> |
| Prompt agent Quickstart (Portal) | <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code> |
| SDK Quickstart | <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code> |
| Foundry project 作成 | <https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/create-projects> |
| 環境セットアップ | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/environment-setup> |
| RBAC (Foundry) | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry> |
| File Search tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search> |
| Vector Stores | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/vector-stores> |
| OpenAPI tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec> |
| Runtime: Responses + Conversations | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components> |
| Playground | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/concept-playgrounds> |
| Limits / Quotas / Regions | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/limits-quotas-regions> |
| Python SDK package | <https://pypi.org/project/azure-ai-projects/> |
| SDK サンプル | <https://aka.ms/azsdk/azure-ai-projects/python/samples> |
