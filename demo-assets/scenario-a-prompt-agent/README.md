# シナリオ A: Copilot Studio → Foundry **Prompt agent (GA)** 移行

> **位置付け**: 4 シナリオの中で **最短ルート / GA 機能のみ**  
> **想定工数**: 0.5〜1 人日  
> **本リポジトリでローカル検証済み (2026-05-22)** — `run-log.md` に実行ログ、`screenshots/scenario-a/` に成果スクリーンショット

Copilot Studio の Topic / 分岐ロジックを **Instructions (自然言語ガイダンス)** に集約し、Knowledge を **File Search**、Action を **OpenAPI tool** として Foundry Prompt agent に登録する移行パターンです。

![Phase 3〜5 ローカル実行ログ](../screenshots/scenario-a/A-LOG-01-phase-summary.png)

---

## 0. 全体フロー

```
[Phase 1] Copilot Studio で IT-Helpdesk-Sample を作成
    ├─ Knowledge: it-policy.md
    ├─ Topic: PasswordReset (Question + Power Fx)
    └─ Action: CreateTicket (HTTP)
        ↓
[Phase 2] pac copilot extract-template で YAML 取得 (設計参照用)
        ↓
[Phase 3] Foundry 受け側を準備 (Project / Model / RBAC / Vector Store)
        ↓
[Phase 4] Prompt agent を登録 (Instructions + FileSearchTool + OpenApiTool)
        ↓
[Phase 5] Playground / Responses API で動作確認 (回帰テスト 5/5)
```

---

## 1. このシナリオが適する Copilot Studio エージェント

| 条件 | 該当 |
|---|---|
| Topic 数が少ない (≤ 5) | ✅ |
| 分岐ロジックが「LLM の常識 + 短い文章ガイドライン」で十分カバー可能 | ✅ |
| 知識参照 (RAG) + 数本の外部 API 呼出が中心 | ✅ |
| **GA で SLA 付きの本番運用**にしたい | ✅ |
| 確定的・厳密なフロー保証が必要 | ❌ シナリオ B 推奨 |
| Power Automate Flow の高度な処理を維持したい | ❌ シナリオ B / C 推奨 |

---

## 2. 前提条件

### 2.1 Copilot Studio 側 (Phase 1〜2)

📖 詳細は **[`..\00-create-cs-agent.md`](../00-create-cs-agent.md)** を参照。

| 項目 | 値 |
|---|---|
| ライセンス | Copilot Studio Standalone / Trial / M365 Copilot |
| 環境 | Production 環境推奨。Dataverse search 有効 |
| Maker 権限 | agent author + System Customizer |
| pac CLI | `dotnet tool install --global Microsoft.PowerApps.CLI.Tool` |

### 2.2 Foundry 側 (Phase 3〜5)

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview>

| 項目 | 値 |
|---|---|
| Foundry portal | <https://ai.azure.com>(**New Foundry** トグル ON) |
| アーキテクチャ | **Foundry resource → Foundry project** (旧 Hub-based は非対応) |
| Endpoint 形式 | `https://<resource>.services.ai.azure.com/api/projects/<project>` |
| モデル | `gpt-4.1-mini` / `gpt-5-mini` 等 (Responses API 対応モデル) |
| RBAC | **Foundry User** (project scope) + **Storage Blob Data Contributor** |
| リージョン | Responses API 対応 (File Search は Italy North / Brazil South 不可) |
| Python SDK | `pip install -r requirements.txt` |

![Microsoft Foundry Agent Service 概要 (公式)](../screenshots/scenario-a/reference-docs/ref-01-agents-overview.png)

> ⚠️ `Cognitive Services User` / `Azure AI Developer` などの旧ロール名は **Foundry project には適用されません**。新名称 **Foundry User** を使ってください。詳細は [RBAC リファレンス](https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry)。

![RBAC for Foundry (公式)](../screenshots/scenario-a/reference-docs/ref-06-rbac-foundry.png)

---

## 3. Phase 1〜2: Copilot Studio でエージェント作成 → pac で抽出

📖 **詳細手順は [`..\00-create-cs-agent.md`](../00-create-cs-agent.md) の §2〜§8** を参照。

本シナリオに必要なアウトプット:
- `IT-Helpdesk-Sample.yaml` (設計参照用)
- Knowledge ファイル本体 [`..\common\sample-knowledge\it-policy.md`](../common/sample-knowledge/it-policy.md)
- OpenAPI 定義 [`..\common\tools\create-ticket.openapi.yaml`](../common/tools/create-ticket.openapi.yaml)

サンプル `it-policy.md` (パスワード忘れ・ロックアウト時の対応 §2.3):

![it-policy.md 抜粋](../screenshots/scenario-a/A-CODE-03-it-policy-md.png)

サンプル OpenAPI 定義(`CreateTicket` の全体):

![create-ticket.openapi.yaml](../screenshots/scenario-a/A-CODE-01-openapi-yaml.png)

---

## 4. Phase 3: Foundry プロジェクトの準備

### 4.1 Foundry resource + project を作成

公式 Quickstart: <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code>

![Quickstart: get-started-code (公式)](../screenshots/scenario-a/reference-docs/ref-02-quickstart.png)

1. <https://ai.azure.com> にサインイン → **New Foundry** トグル ON
2. **+ Create a project** → 名前 / リージョン / Basic を入力
3. 作成後、**Project endpoint** をコピー (形式: `https://<resource>.services.ai.azure.com/api/projects/<project>`)

### 4.2 モデルをデプロイ

1. 左メニュー **Models + Endpoints** → **+ Deploy model**
2. `gpt-4.1-mini` を選択 (`gpt-5-mini` でも本シナリオは動作確認済み)
3. Deployment name = モデル名と同一、SKU = GlobalStandard
4. **Deploy**

### 4.3 RBAC を割り当てる

```powershell
$RG    = "<resource group>"
$ACCT  = "<Foundry account name>"
$PROJ  = "<Foundry project name>"
$SUB   = "<subscription id>"

az role assignment create `
  --assignee <your-email-or-objectId> `
  --role "Foundry User" `
  --scope "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCT/projects/$PROJ"

# (ファイル アップロード用) Storage Blob Data Contributor も必要
az role assignment create `
  --assignee <your-email-or-objectId> `
  --role "Storage Blob Data Contributor" `
  --scope "/subscriptions/$SUB/resourceGroups/$RG"
```

### 4.4 ログインと環境変数

```powershell
az login
$env:FOUNDRY_PROJECT_ENDPOINT = "https://<resource>.services.ai.azure.com/api/projects/<project>"
$env:FOUNDRY_MODEL_NAME       = "gpt-5-mini"        # または gpt-4.1-mini
```

---

## 5. Phase 3b: Vector Store に `it-policy.md` をアップロード

公式 (File Search): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search>

![File Search 公式ドキュメント](../screenshots/scenario-a/reference-docs/ref-03-file-search.png)

| 項目 | 上限 |
|---|---|
| 最大ファイル サイズ | 512 MB |
| 1 ファイルあたり最大トークン | 2,000,000 |
| 1 vector store の最大ファイル数 | 10,000 |
| Agent に紐づけ可能な vector store 数 | **1** |

### 実行

```powershell
cd .\demo-assets
pip install -r scenario-a-prompt-agent\requirements.txt
python common\scripts\upload_knowledge.py common\sample-knowledge\it-policy.md
```

出力例:

```
file_id           = assistant-VjL1LGUgkPDaora2UZ36o6
vector_store_id   = vs_LFFXzBenUR1e5bjU5fxRXfiH
vector_store_name = it-policy-vs
```

```powershell
$env:KNOWLEDGE_VECTOR_STORE_ID = "vs_LFFXzBenUR1e5bjU5fxRXfiH"
```

> 💡 本スクリプトは Responses API (`openai.vector_stores.create`) で作成します。旧 `client.agents.upload_file_and_poll` は `azure-ai-projects>=2.0` で削除済みです。

---

## 6. Phase 4: Prompt agent を作成

### 6.1 ポータルで作成する場合

1. <https://ai.azure.com> → project → **Agents** → **+ Create** → **Prompt agent**
2. 各フィールド:

| Field | 値 |
|---|---|
| **Name** | `helpdesk-prompt` |
| **Model** | `gpt-4.1-mini` または `gpt-5-mini` |
| **Instructions** | §6.3 を貼り付け |
| **Tools → + Add → File search** | 上で作成した vector store を選択 |
| **Tools → + Add → OpenAPI** | `..\common\tools\create-ticket.openapi.yaml` を貼り付け、Auth = Anonymous |

3. **Save** → Agent playground が自動で開く

### 6.2 Python SDK で作成する場合 (再現性 / CI 向け)

📄 本シナリオ同梱: [`create_prompt_agent.py`](create_prompt_agent.py)

![create_prompt_agent.py 抜粋](../screenshots/scenario-a/A-CODE-02-prompt-agent-script.png)

```powershell
cd .\demo-assets\scenario-a-prompt-agent
python create_prompt_agent.py
```

出力例:

```
agent_name        = helpdesk-prompt
agent_version_id  = helpdesk-prompt:1
```

> 💡 GA SDK では agent は `(agent_name, agent_version)` で識別します (旧 `agent_id` GUID は廃止)。
> 公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components>

![Runtime components (公式)](../screenshots/scenario-a/reference-docs/ref-05-runtime-components.png)

### 6.3 Instructions テンプレート (Copilot Studio Topic の言語化)

`create_prompt_agent.py` の `INSTRUCTIONS` 定数に既に含まれている内容です。

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

| Auth type | SDK クラス | 用途 |
|---|---|---|
| **Anonymous** | `OpenApiAnonymousAuthDetails()` | 公開エンドポイント (本デモはこれ) |
| **Connection (API key)** | `OpenApiProjectConnectionAuthDetails(security_scheme=OpenApiProjectConnectionSecurityScheme(connection_id=...))` | Foundry の Project connection 経由 |
| **Managed Identity** | `OpenApiManagedAuthDetails(security_scheme=OpenApiManagedSecurityScheme(audience="..."))` | Entra 保護 API |

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec>

![OpenAPI tool (公式)](../screenshots/scenario-a/reference-docs/ref-04-openapi-tool.png)

> ⚠️ `auth=` には **dict ではなく SDK のクラス インスタンス** を渡してください (`azure-ai-projects>=2.1` 時点)。
> 同様に `spec=` には YAML 文字列ではなく **dict** が必要です(`yaml.safe_load()` で変換)。`create_prompt_agent.py` ではこの変換を行っています。

---

## 7. Phase 5: 動作確認

### 7.1 Playground (ポータル UI)

1. <https://ai.azure.com> → project → **Agents** → `helpdesk-prompt` → **Playground**
2. テストメッセージ:
   - `MFA の登録方法を教えて`
   - `パスワード忘れた`
   - `VPN がつながらない`
3. 右ペインの **Trace** で File Search / OpenAPI 呼び出しを可視化

### 7.2 SDK 経由でプログラマティックに呼ぶ (回帰テスト用)

📄 本シナリオ同梱: [`test_agent.py`](test_agent.py)

```powershell
cd .\demo-assets\scenario-a-prompt-agent
python test_agent.py
```

実行結果(抜粋、`gpt-5-mini` で平均 25 秒):

![Responses API 回帰テスト ログ](../screenshots/scenario-a/A-LOG-02-test-session.png)

### 7.3 回帰テスト一覧

| 検証項目 | 期待動作 | ローカル検証結果 |
|---|---|---|
| パスワード忘れ + 社内 PC | セルフサービス URL を案内、チケットは起票しない | ✅ |
| パスワード忘れ + 社外 PC | IT ヘルプデスク連絡先を案内 | ✅ |
| 解決しなかった旨を続報 (VPN) | 同意を取って CreateTicket を提案 | ✅ |
| MFA 登録質問 | it-policy.md §2.2 から引用 | ✅ |
| 機密情報の要求 (PIN を教えろ) | 拒否、CSIRT 案内 | ✅ |

intent 一致率 100% (5/5)。詳細は [`run-log.md`](run-log.md) を参照。

---

## 8. マッピング表: Copilot Studio → Prompt agent

| Copilot Studio 要素 | Prompt agent 側 |
|---|---|
| Description | `PromptAgentDefinition.description` |
| Instructions | `PromptAgentDefinition.instructions` (8,000 文字 → 制限なし) |
| Topic (Trigger phrases + ノード) | **すべて Instructions に言語化**。Trigger 句は「ユーザーが〜と言ったとき」、ノードは番号付き手順 |
| Question ノード | LLM が自然言語で逆質問 (**確定的ではない**) |
| Power Fx 条件 | Instructions の条件文 (`もし X なら…` 等) |
| Knowledge (File upload) | `FileSearchTool(vector_store_ids=[vs_id])` |
| Knowledge (SharePoint) | Project connection で SharePoint 接続を作成 → `SharepointTool` |
| Action (HTTP Request) | `OpenApiTool(openapi=OpenApiFunctionDefinition(spec=...))` |
| Action (Power Automate Flow) | Flow を独立 API 化 → OpenAPI 接続、または シナリオ C で Python 再実装 |
| Adaptive Card | Prompt agent では非対応 → クライアント側で再実装 |

---

## 9. 利点と欠点

| | 内容 |
|---|---|
| ✅ **利点** | GA で SLA 対象 / 最速本番化 / 1,900+ モデル選択可 / コード量最小 / Playground 即試行 / Responses API による履歴自動管理 |
| ❌ **欠点** | 確定的フロー (必ず質問→分岐) は LLM 任せで保証されない / Topic 多いと Instructions 肥大化 / Adaptive Card 非対応 |

---

## 10. トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `DefaultAzureCredential` で 401 | `az login` 未実行 | `az login` → 再実行 |
| `Azure CLI not found on path` (Python のサブプロセス) | Windows で `cmd.exe` 起動時に **PATH が長すぎて切り捨て** (環境変数 PATH が約 8KB を超える) | PowerShell セッションで PATH を必要最小限に絞ってから Python を起動 (本リポジトリの検証で遭遇) |
| `(invalid_payload) type: Value is "string" but should be "object"` | `OpenApiTool` の `auth=` に dict を渡している | `OpenApiAnonymousAuthDetails()` などの SDK クラスを渡す |
| `OpenApiFunctionDefinition` で同様のエラー | `spec=` に YAML 文字列を渡している | `yaml.safe_load(...)` で dict に変換 |
| `AttributeError: 'AgentsOperations' object has no attribute 'upload_file_and_poll'` | 旧 API は `azure-ai-projects>=2.0` で削除 | `openai.files.create` + `openai.vector_stores.create` (新 API) を使用 |
| `Permission denied` で agent 作成不可 | Foundry User 未割り当て | §4.3 を実施 |
| File Search が結果を返さない | Vector store ingestion 未完了 | 数十秒〜数分待ち、ingestion 完了を確認 |
| Italy North / Brazil South で File Search エラー | 地域制限 | 別リージョンに project 作成 |

PATH 切り捨て問題のワークアラウンド例(本リポジトリ検証時):

```powershell
$env:PATH = "C:\Program Files\PowerShell\7;" +
            "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin;" +
            "C:\Windows\System32;C:\Windows;" +
            (Split-Path (Get-Command python).Source)
python create_prompt_agent.py
```

---

## 11. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `requirements.txt` | Python 依存関係 (azure-ai-projects, azure-identity, pyyaml) |
| `create_prompt_agent.py` | Prompt agent を 1 体作成するスクリプト (Phase 4) |
| `test_agent.py` | Responses API 経由の回帰テスト (Phase 5、5 ケース) |
| `run-log.md` | 本リポジトリでローカル実行した際のログ (2026-05-22) |
| `capture_learn_docs.py` | Microsoft Learn 参照画像を Playwright で取得 (認証不要) |
| `generate_log_screenshots.py` | 実行ログをターミナル風画像に化(README 用、認証不要) |
| `generate_code_screenshots.py` | 同梱コードをシンタックス ハイライト画像に化(README 用、認証不要) |
| `capture_foundry_screenshots.py` | Foundry Portal の各ページをスクショ取得 (**初回サインインが必要**、persistent profile を `.pw-profile/` に保存) |

---

## 12. 関連公式ドキュメント

| トピック | URL |
|---|---|
| Foundry Agent Service 概要 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> |
| Prompt agent Quickstart | <https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code> |
| File Search tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search> |
| Vector Stores | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/vector-stores> |
| OpenAPI tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec> |
| Responses + Conversations API | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components> |
| RBAC (Foundry) | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry> |
| 環境セットアップ | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/environment-setup> |
| Limits / Quotas / Regions | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/limits-quotas-regions> |
| Python SDK | <https://pypi.org/project/azure-ai-projects/> |
