# シナリオ B: Copilot Studio → Foundry **Workflow agent (Preview)** 移行 完全手順書

> **位置付け**: 6 シナリオの中で **Microsoft Copilot Studio との互換度が最も高い** (Topic / 分岐 / HITL / Power Fx を温存)
> **状態**: ⚠️ **Public Preview** (SLA 対象外、本番運用は非推奨)
> **想定工数**: 1〜3 人日 (Topic 数による)

Copilot Studio の Topic ダイアログ ツリーを **Workflow agent のビジュアル ビルダー / Workflow YAML** に変換する移行パターン。Power Fx の文法とノード構造を多くそのまま流用できますが、いくつかの **重要な互換差分** (`Topic.*` スコープ非対応、Choice 型非対応、Azure Functions tool 廃止) があります。

---

## 0. 全体フロー

```
[Phase 1] Copilot Studio で IT-Helpdesk-Sample を作成
    └─ PasswordReset Topic (Question + Power Fx 分岐)
        ↓
[Phase 2] pac copilot extract-template で YAML 取得
    (Topic 構造を読み解く設計インプット)
        ↓
[Phase 3] Foundry 受け側を準備
    ├─ Foundry project + モデル
    ├─ RBAC: Contributor 以上 (Workflow 編集には Contributor が必要)
    ├─ Vector Store
    └─ 子 Prompt agent (子エージェント) を 2 体作成
        ├─ InternalGuideAgent  (社内 PC 向け案内)
        └─ ExternalGuideAgent (社外 PC 向け案内)
        ↓
[Phase 4] Workflow agent を作成
    ├─ ai.azure.com → Build → Create new workflow → Sequential
    ├─ Trigger → Send a message
    ├─ Ask a question (Local.PCType)
    ├─ if/else (Power Fx: Local.PCType = "社内PC")
    ├─ Invoke agent (InternalGuideAgent / ExternalGuideAgent)
    └─ Save (⚠️ 自動保存なし)
        ↓
[Phase 5] Run Workflow で動作確認 → YAML 出力 (バックアップ)
```

---

## 1. このシナリオが適する Copilot Studio エージェント

| 条件 | 該当 |
|---|---|
| Topic が 10〜数十本、分岐 / スロットフィリング / HITL が多い | ✅ |
| **確定的フローを保証したい** (LLM の気分で省略されたくない) | ✅ |
| Power Fx 式 / 条件分岐をできる限り維持したい | ✅ |
| マルチエージェントで承認フロー / 順次処理を組みたい | ✅ |
| Public Preview を許容できる (PoC や検証目的) | ✅ |
| GA で SLA 必須 | ❌ シナリオ A 推奨 |
| `Topic.*` / `Global.*` スコープを多用している | ⚠️ すべて `Local.*` に書き換え必要 |
| Choice 型 (Power Fx) を多用している | ⚠️ String に書き換え必要 |
| Azure Functions tool に依存している | ⚠️ MCP / OpenAPI tool に置き換え必要 |

---

## 2. 前提条件

### 2.1 Copilot Studio 側 (Phase 1〜2 用)

📖 詳細は **`..\00-create-cs-agent.md`** 参照。

### 2.2 Foundry 側 (Phase 3〜5 用)

公式 (Workflow 概念): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow>

| 項目 | 値 / 公式リンク |
|---|---|
| Foundry portal | <https://ai.azure.com>(**"New Foundry"** トグルを ON) |
| RBAC (Workflow 作成/編集) | **Contributor 以上** が project scope に必要 (公式トラブルシューティング表より) |
| RBAC (一般 agent 作成) | **Foundry User** (旧 Azure AI User) |
| モデル デプロイ | `gpt-4.1` (既定 autodeploy) / `gpt-4.1-mini` |
| Workflow 専用の preview opt-in | **不要** (`New Foundry` トグルが ON ならビルダーが表示される) |
| リージョン | Responses API 対応リージョン |

公式 RBAC: <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry>

### 2.3 重要な互換差分 (Phase 4 で必ず確認)

公式 (Workflow concept): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow>

| Copilot Studio 要素 | Foundry Workflow agent | 対応方針 |
|---|---|---|
| `Topic.*` 変数スコープ | **非対応** (`System.*` / `Local.*` のみ) | すべて `Local.*` に書き換え |
| `Global.*` 変数スコープ | **非対応** | Workflow 内で `Local.*` に置き換え、または外部ストアに保存 |
| Power Fx `Choice` 型 | **非対応** | String に変換し、`If(Local.X = "値1", ..., ...)` で分岐 |
| Azure Functions tool | 新 Agent Service では **廃止** | MCP tool または OpenAPI tool に置き換え |
| Hosted agent をデザイナー内に直接配置 | **不可** (公式明記) | A2A / OpenAPI / MCP 経由で間接呼出 |
| 自動保存 | **なし** | 編集後は必ず手動 **Save** クリック |
| Agent 名変更 | **不可** (作成後イミュータブル) | 命名は事前確定 |
| HITL (Human-in-the-Loop) | **テンプレート パターン**として提供 (専用ノードではない) | Ask a Question で代替するか、HITL テンプレから開始 |

---

## 3. Phase 1〜2: Copilot Studio でエージェント作成 → pac で抽出

📖 **詳細は `..\00-create-cs-agent.md` の §2〜§8**

このシナリオで特に重要な抽出内容:
- `PasswordReset` Topic の **ノードツリー全体** (Question / Condition / Message / HTTP Request)
- 各 Condition の **Power Fx 式**
- 各 Question ノードの **Identify 設定** (Multiple choice / Number / Date 等)
- `Topic.*` 変数とその参照箇所 (書き換え対象の特定)

> 💡 抽出した `IT-Helpdesk-Sample.yaml` を VS Code で開き、`kind: AdaptiveDialog` または `topics:` セクションを設計参照として手元に置いておくと、Workflow 構築時に役立ちます。

---

## 4. Phase 3: Foundry 受け側の準備

### 4.1 Project + モデル

シナリオ A の §4.1〜4.3 と同じ手順で:
- Foundry project 作成
- `gpt-4.1-mini` デプロイ
- RBAC 割り当て (**Contributor 以上** に注意)

### 4.2 Knowledge (Vector Store) アップロード

シナリオ A の §5 と同じ:
```powershell
python ..\common\scripts\upload_knowledge.py ..\common\sample-knowledge\it-policy.md
$env:KNOWLEDGE_VECTOR_STORE_ID = "vs_xxxxxxxx"
```

### 4.3 子 Prompt agent を 2 体作成

Workflow agent は **ノードの中で他の agent を呼ぶ** 構造です。
PasswordReset の 2 分岐用に、以下の 2 つの **Prompt agent** を予め作成します。

```powershell
# repo root から実行
cd .\demo-assets\scenario-a-prompt-agent
pip install -r requirements.txt

# 1 体目
$env:AGENT_NAME = "InternalGuideAgent"
$env:AGENT_INSTRUCTIONS = "社内 PC ユーザーへのパスワード リセット案内。セルフサービス ポータル https://passwordreset.contoso.local を必ず提示する。"
python create_prompt_agent.py   # 必要なら agent_name を引数で渡せるよう改修

# 2 体目
$env:AGENT_NAME = "ExternalGuideAgent"
$env:AGENT_INSTRUCTIONS = "社外 PC ユーザーへのパスワード リセット案内。IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) を必ず案内する。"
python create_prompt_agent.py
```

> 💡 同梱の `create_prompt_agent.py` は 1 体目 (`helpdesk-prompt`) 用にハードコードされています。
> 環境変数 `AGENT_NAME` / `AGENT_INSTRUCTIONS` を読むよう小修正してから 2 回実行するか、ポータルから 2 体作成してください。

---

## 5. Phase 4: Workflow agent をビジュアル ビルダーで作成

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow>

### 5.1 Workflow を新規作成

1. <https://ai.azure.com> → project → 右上 **Build** タブ
2. **Create new workflow** → パターンを選択:
   - **Sequential** (← PasswordReset はこれ)
   - **Group chat** (複数 agent が同時参加)
   - **Human in the loop** (承認ステップ標準装備)
   - Blank
3. Workflow 名を入力 (⚠️ 一度命名すると変更不可)

> ⚠️ **公式 UI ラベルは `Build → Create new workflow`** です。「Agents → + Create → Workflow agent」ではありません。

### 5.2 利用できるノード (公式確認済み)

| カテゴリ | ノード | 用途 |
|---|---|---|
| **Basic chat** | Send a message | テキスト返却 |
| Basic chat | Ask a question | 入力受付 (Choice 型は非対応) |
| **Logic** | if/else | Power Fx 条件で分岐 |
| Logic | go to | 別ノードへジャンプ |
| Logic | for each | ループ |
| **Data transformation** | Set a variable | `Local.*` 変数代入 |
| Data transformation | Parse a value | JSON / 文字列パース |
| **Agent** | Invoke agent | 既存 Prompt agent を呼ぶ (or 新規作成可) |

> ⚠️ **公式に存在しないラベル** (社内資料で見かけても誤り):
> - "Tool call" 単体ノード → 存在しない。tool は agent に attach し、その agent ノードを呼ぶ
> - "Human in the Loop" 単体ノード → ない。**HITL は workflow テンプレート パターン**として提供される
> - "A2A" 単体ノード → A2A tool 経由は別パターン (§5.5 参照)

### 5.3 PasswordReset Workflow の構築手順

```
[Trigger]
  ↓
[Send a message] "パスワード関連でお困りですね。お手伝いします。"
  ↓
[Ask a question]
  - Message: "お使いの PC は社内 PC ですか、社外 PC ですか? (社内PC / 社外PC)"
  - Variable: Local.PCType (型: String)
  ↓
[if/else] Power Fx: Local.PCType = "社内PC"
  ├─ true:  [Invoke agent] InternalGuideAgent (input: ユーザーの最初の質問)
  └─ false: [Invoke agent] ExternalGuideAgent
```

#### 5.3.1 Trigger ノード
- 既定で先頭に配置済み。triggering 条件は workflow が呼ばれた瞬間。

#### 5.3.2 Send a message ノード
- ノードを追加 → Basic chat → **Send a message**
- 内容: "パスワード関連でお困りですね。お手伝いします。"

#### 5.3.3 Ask a question ノード
- 追加 → Basic chat → **Ask a question**
- Message: 上記参照
- **Identify**: String (Choice は非対応のため)
- Save user response as: `Local.PCType` (`Local.` プレフィックス必須)

#### 5.3.4 if/else ノード + Power Fx
- 追加 → Logic → **if/else**
- Condition: `Local.PCType = "社内PC"`
- Copilot Studio の `Topic.PCType = "社内PC"` を `Local.` に書き換えただけ

公式 Power Fx 対応関数表 (Foundry Workflow agent 用):

| 型 | 利用可能関数 |
|---|---|
| String | `Text`, `Concat`, `Len`, `Lower`/`Upper`, `IsMatch`, `Find`, `Replace`/`Substitute` |
| Boolean | `Boolean`, `And`/`Or`/`Not`, `If`/`Switch` |
| Number | `Decimal`/`Float`/`Value`, `Int`/`Round` |
| Record/Table | `Filter`/`LookUp`, `JSON`/`ParseJSON`, `Count`/`ForAll` |
| Date/Time | `Date`/`DateTime`, `Now`/`Today`, `DateAdd`/`DateDiff` |
| Blank | `IsBlank`/`Coalesce`, `IfError`/`IsError` |

#### 5.3.5 Invoke agent ノード
- 追加 → Agent → **Invoke agent**
- **Existing** を選び、`InternalGuideAgent` または `ExternalGuideAgent` を選択
- 入力には Local 変数や System.LastMessage.Text を渡せる

### 5.4 変数スコープ

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow>

| Prefix | 意味 |
|---|---|
| `System.*` | システム変数 (`System.LastMessage.Text`, `System.Conversation.Id`, `System.User.Language`, `System.Conversation.InTestMode` 等) |
| `Local.*` | Workflow 内で作成した変数 |

> ⚠️ **`Topic.*` / `Global.*` は非対応**。Copilot Studio から持ち込む式はすべて書き換え。

### 5.5 Tool 呼出 (OpenAPI / MCP / A2A)

公式 (Tool catalog): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog>
公式 (OpenAPI tool): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi>
公式 (A2A tool): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/agent-to-agent>

**重要:** Workflow デザイナーには tool を直接ノードとして配置しません。Tool は **agent に attach** し、その agent を Invoke agent ノードで呼びます。

CreateTicket を呼ぶ場合:
1. **新しい子 Prompt agent** (`TicketAgent`) を作成し、OpenAPI tool として CreateTicket を attach
2. Workflow から **Invoke agent → TicketAgent** で呼出

または、A2A tool (Preview):
- Portal → Tools → Connect tool → Custom → **Agent2Agent (A2A)**
- 呼出元 agent が Agent A、被呼出 agent が Agent B のとき:
  - **Workflow Invoke パターン**: A→B、B が応答全権 (A は loop 外)
  - **A2A tool パターン**: A→B、B の応答が A に戻り、A が要約して応答 (A が制御維持)

### 5.6 Save と Version 管理

- 編集後は必ず **右上の Save** をクリック (⚠️ 自動保存なし)
- **Save するたびに新しい version (immutable)** が作成される
- Version 履歴: Save ボタン左の **Version dropdown** で参照 / 削除

### 5.7 YAML view (任意)

- 編集画面で **YAML Visualizer View トグル** を ON にすると YAML 表示
- YAML 編集も可能。Save で同期。
- VS Code 経由編集: **YAML** ボタン → "Open in VS Code for Web"
- **Generate Code** で Python / C# (Agent Framework) コードに変換可能
- ⚠️ **公式 YAML スキーマ仕様書はまだ公開されていない** (本書執筆時点)。Preview の制約。

### 5.8 同梱の参考 YAML

📄 `workflows\password-reset.workflow.yaml` — 本シナリオが想定する **概念サンプル**。
スキーマは Preview のため変動するため、実デプロイ時は portal で構築 → YAML を export するのが確実です。

---

## 6. Phase 5: 動作確認

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow>

### 6.1 ポータルから **Run Workflow**

1. ビルダー画面右上 **Run Workflow**
2. 右のチャット ウィンドウで以下を試す:
   - `パスワード忘れた` → Send → Ask a question で社内/社外 PC を確認
   - `社内PC` → if/else → InternalGuideAgent 応答
   - 別セッションで `社外PC` → ExternalGuideAgent 応答
3. 検証:
   - ✅ 各ノードがビジュアライザで完了 (チェックマーク)
   - ✅ チャット応答が期待通り
   - ✅ `Local.*` 変数が期待値を保持

### 6.2 VS Code Remote Playground

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/vs-code-agents-workflow-low-code>

- VS Code に **Microsoft Foundry Toolkit** 拡張をインストール (Pre-release)
- **My Resources** → project → **Declarative Agents** → version 選択
- **Remote Agent Playground** ペインでテスト

### 6.3 トレース (AgentOps)

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/observability/concepts/trace-agent-concept>

- Run 後、project の **Observability → Tracing** で実行ログを確認
- どのノードでどの agent が呼ばれたかタイムライン表示

---

## 7. マッピング表: Copilot Studio → Workflow agent

| Copilot Studio 要素 | Workflow agent 側 |
|---|---|
| Topic 全体 | 1 Workflow YAML (Sequential / HITL テンプレ等) |
| Trigger phrases | Workflow をどの場面で呼び出すかは **呼出元 agent の Instructions / Description** で制御 |
| Description | Workflow メタデータ |
| Message ノード | **Send a message** |
| Question (Choice) | **Ask a question** (Choice 非対応のため String + 案内文で代替) |
| Question (Text/Number/Date) | **Ask a question** + Identify 設定 |
| Condition (Power Fx) | **if/else** + Power Fx 式 (`Local.*` 必須) |
| GoTo | **go to** |
| For loop | **for each** |
| Variable assign | **Set a variable** (`Local.*`) |
| JSON parse | **Parse a value** |
| Action (HTTP) | OpenAPI tool を attach した子 Prompt agent + **Invoke agent** |
| Action (Power Automate Flow) | Flow を HTTP API 化して OpenAPI に or MCP tool 化 |
| Action (Azure Functions) | **廃止**。MCP / OpenAPI に置き換え |
| Escalate to live agent | **Human-in-the-Loop テンプレ** で workflow 構築、または Ask a question + 外部通知 |
| Topic redirect | Sequential Workflow で次ノード、または **Invoke agent** で別 workflow agent ネスト |
| `Topic.X` / `Global.X` | `Local.X` に書き換え必須 |

---

## 8. 利点と欠点

| | 内容 |
|---|---|
| ✅ **利点** | **Copilot Studio Topic 構造を最も忠実に保持** / Power Fx 流用可 / 確定的フロー / HITL テンプレ / マルチエージェント / ビジュアル ビルダー / YAML 編集 / Code 生成 |
| ❌ **欠点** | **Public Preview** SLA 外 / Hosted agent をデザイナー内に置けない / 自動保存なし / Choice 型非対応 / `Topic.*` / `Global.*` 非対応 / Azure Functions tool 廃止 / YAML スキーマ仕様書未公開 |

---

## 9. 既知の制約 (公式確認済み)

| 領域 | 制約 | 出典 |
|---|---|---|
| SLA | Public Preview、本番非推奨 | agents/how-to/tools/agent-to-agent (preview banner) |
| Hosted agent をデザイナーに | **配置不可** | agents/concepts/workflow |
| Choice 型 (Power Fx) | **非対応** | agents/concepts/workflow (literal values table) |
| 変数スコープ | `System.*` / `Local.*` のみ | agents/concepts/workflow |
| 自動保存 | **なし** (手動 Save 必須) | agents/concepts/workflow |
| Agent 名 | 作成後変更不可 | agents/concepts/development-lifecycle |
| Tool 登録上限 | 128 / agent | agents/concepts/limits-quotas-regions |
| OpenAPI body 形式 | `application/json`, `application/json-patch+json` のみ | agents/how-to/tools/openapi |
| Azure Functions tool | 新 Agent Service では廃止 (移行: MCP / OpenAPI) | agents/how-to/migrate |
| Version | 保存後イミュータブル | agents/concepts/workflow |
| YAML スキーマ仕様 | **未公開** | (検索結果なし) |
| HITL 専用ノード | **なし** (テンプレ パターンとして提供) | agents/concepts/workflow |

---

## 10. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `workflows\password-reset.workflow.yaml` | PasswordReset Topic を Workflow YAML に翻訳した **概念サンプル** (Preview のため実 schema と差異あり) |

---

## 11. 関連公式ドキュメント

| トピック | URL |
|---|---|
| Workflow agent 概念 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow> |
| Agent Service 概要 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> |
| VS Code 低コード ワークフロー | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/vs-code-agents-workflow-low-code> |
| 開発ライフサイクル | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/development-lifecycle> |
| Tool catalog | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog> |
| OpenAPI tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi> |
| Agent-to-Agent (A2A) tool | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/agent-to-agent> |
| A2A authentication | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-to-agent-authentication> |
| Power Fx (formula reference) | <https://learn.microsoft.com/en-us/power-platform/power-fx/formula-reference-copilot-studio> |
| Limits / Quotas / Regions | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/limits-quotas-regions> |
| Migration table (classic → new) | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/migrate> |
| Tracing (AgentOps) | <https://learn.microsoft.com/en-us/azure/ai-foundry/observability/concepts/trace-agent-concept> |
| Agent Framework orchestrations | <https://learn.microsoft.com/en-us/agent-framework/user-guide/workflows/orchestrations/overview> |
