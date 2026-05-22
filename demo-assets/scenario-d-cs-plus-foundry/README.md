# シナリオ D: Copilot Studio + Microsoft Foundry **併用 (Connect to a Foundry agent)** 完全手順書

> **位置付け**: 既存 Copilot Studio エージェントを **そのまま温存**し、Foundry agent を **司令塔 (Copilot Studio) から呼ばれる外部エージェント**として接続するパターン
> **状態**: ⚠️ **Public Preview** (接続機能側、SLA 対象外)
> **想定工数**: 0.5 人日〜 (Foundry 側 agent が既に存在する前提)
> **公式ガイド (一次資料)**: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent>

Copilot Studio 側を完全に残したまま、特定 Topic (例: 「高度な調査」) を Foundry agent (シナリオ A / B / C のいずれか) に **委譲** する構成。お客様の M365 / Teams / Power Platform 投資を維持しつつ、Foundry の最新モデル / Deep Research / カスタム コードのメリットを活用できます。

---

## 0. 全体構成図

```
[エンド ユーザー]
   │  (Teams / M365 Copilot / 公開 Web)
   ▼
[Copilot Studio エージェント] ── 既存資産そのまま
   ├─ Topic: FAQ          → Copilot Studio Knowledge
   ├─ Topic: 申請処理      → Power Automate
   └─ Topic: 高度な調査     → [Foundry agent]
                              ▲
              "Add an agent → Microsoft Foundry"
              で接続 (Public Preview)
                              │
   ┌──────────────────────────┴──────────────────────────┐
   │ Foundry agent (どれか) :                              │
   │   ・シナリオ A: Prompt agent (GA)                     │
   │   ・シナリオ B: Workflow agent (Preview)              │
   │   ・シナリオ C: Hosted agent (Preview)                │
   └─────────────────────────────────────────────────────┘
```

Copilot Studio 側のオーケストレーター (Generative orchestration) が、各 Topic / 接続 agent の **Description** を読んで呼出先を選びます。

---

## 1. このシナリオが適する状況

| 条件 | 該当 |
|---|---|
| 既存の Copilot Studio エージェントを **そのまま継続使用**したい | ✅ |
| Teams / M365 Copilot / Power Platform 連携を維持したい | ✅ |
| 一部の問い合わせだけ Foundry の最新モデル / Deep Research / カスタム ロジックで処理したい | ✅ |
| 段階的に Copilot Studio → Foundry へ移行したい (一度に切り替えない) | ✅ |
| Copilot Studio と Foundry の **両方** で課金発生して構わない | ✅ |
| 単一プロダクトで完結させたい (Copilot Studio 廃止予定) | ❌ シナリオ A〜C 推奨 |

---

## 2. 前提条件

### 2.1 Copilot Studio 側

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing>

| 項目 | 値 |
|---|---|
| Copilot Studio ライセンス | Copilot Studio Standalone / Trial / M365 Copilot |
| Maker 権限 | 対象エージェントへの **Edit 権限** + Power Platform Connection 作成権限 |
| エージェント側設定 | **Generative orchestration が ON** であること (推奨) |
| ポータル | <https://copilotstudio.microsoft.com> |

📖 まだ Copilot Studio エージェントが無い場合は `..\00-create-cs-agent.md` を先に実施。

### 2.2 Foundry 側

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent>

| 項目 | 値 |
|---|---|
| Foundry portal | <https://ai.azure.com> ⚠️ **新ポータル必須** |
| 対象 agent | 既に **作成・公開**済みであること (シナリオ A / B / C いずれか) |
| 必要情報 | **Agent Id** (or Agent name) + **Project endpoint URL** |
| ユーザー権限 | Foundry project に **Foundry User** ロール |

> ⚠️ **最重要 — 公式 Note 引用 (verbatim)**:
> 「When connecting to Microsoft Foundry agents from Copilot Studio, you can only connect to agents created in the **new Microsoft Foundry portal**. Connecting to an agent created in the previous portal leads to an error indicating **'404 - Version not found'**」
>
> 旧 (classic) Azure AI Studio で作った agent は接続不可。`ai.azure.com` で **"New Foundry"** トグルを ON にした状態で作った agent のみ対応します。

---

## 3. Phase 1: 接続先となる Foundry agent を準備

3 つの選択肢があります。デモ目的なら **シナリオ A (Prompt agent)** が最速です。

| 接続先候補 | 手順 README | 工数 | 状態 |
|---|---|---|---|
| **Prompt agent** | [`..\scenario-a-prompt-agent\README.md`](../scenario-a-prompt-agent/README.md) | 0.5〜1 人日 | GA |
| Workflow agent | [`..\scenario-b-workflow-agent\README.md`](../scenario-b-workflow-agent/README.md) | 1〜3 人日 | Preview |
| Hosted agent | [`..\scenario-c-hosted-agent\README.md`](../scenario-c-hosted-agent/README.md) | 3〜10 人日 | Preview |

完了後、以下 2 つの値を控えておきます (Phase 3 で必要):

1. **Project endpoint URL**
   - 取得場所: Foundry portal → project → **Overview** → **Libraries → Foundry**
   - 形式: `https://<resource>.services.ai.azure.com/api/projects/<project>`
2. **Agent Id** (or Agent name)
   - 取得場所: portal → Agents → 対象 agent → 詳細画面

📄 同梱ファイル `cs-connection-notes.md` に控えるテンプレを用意してあります。

---

## 4. Phase 2: Copilot Studio 側のオーケストレーション設計

公式 (Generative orchestration): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions>

### 4.1 Generative orchestration の動作

Copilot Studio の Generative orchestration がオンの場合、ユーザー入力に対し以下の候補をすべて評価し、**Description** が最も適合するものを選びます:

- 自前の Topic
- Knowledge ソース
- 自前の Tool / Action
- **接続された外部 agent (Foundry agent / Fabric / SDK)** ← **新規追加**

公式引用:
> 「The most important factor is the description of the topics, tools, agents, and knowledge sources.」
> 「Child and connected agents: The agent selects child and connected agents based on their description.」

### 4.2 Description の書き方 (= 呼ばれる/呼ばれないが決まる)

公式 Best practices: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions#best-practices>

| ルール | 例 |
|---|---|
| 1〜2 文で **目的** を簡潔に | ✅ "社内 IT 利用規定とチケット起票に特化した IT ヘルプデスク アシスタント。MFA / VPN / パスワード関連の問い合わせに対応する。" |
| 単純・直接・現在形・能動態 | |
| 機能に関連する **キーワード** を含める | "MFA / VPN / パスワード" |
| 似た tool / agent との **曖昧さを排除**する具体語 | |
| 漠然とした記述は ❌ | ❌ "This tool can answer questions." |

### 4.3 ルーティング設計サンプル

📄 同梱: `topic-route-to-foundry.md`

```
[Copilot Studio エージェント: ContosoHelpDeskOrchestrator]
  ├─ Topic: WelcomeGreeting
  │     Description: "ユーザーが最初に挨拶 / 自己紹介したときに使う"
  │
  ├─ Topic: SimpleHRFAQ
  │     Description: "勤怠 / 休暇 / 給与関連の FAQ。社内 HR Knowledge を引いて回答"
  │
  ├─ Connected agent: ITHelpdeskFoundryAgent (Foundry, シナリオ A)
  │     Description: "社内 IT 利用規定とチケット起票に特化した IT ヘルプデスク アシスタント。
  │                  MFA / VPN / パスワード / アカウント関連の問い合わせに対応"
  │
  └─ Connected agent: ResearchFoundryAgent (Foundry, シナリオ C)
        Description: "競合分析や市場動向など、Web を横断した深い調査が必要な質問に対応"
```

---

## 5. Phase 3: Copilot Studio に Foundry agent を接続

公式手順 (verbatim): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent>

公式の 8 ステップを順に実行します。

### Step 1
1. Copilot Studio portal にサインイン → 対象エージェントを開く
2. 左メニュー **Agents** ページに移動 → **Add an agent** をクリック

### Step 2
- **Connect to an external agent** セクションで **Microsoft Foundry** を選択

### Step 3
- **接続 (Connection)** を選択 or 新規作成
- 新規作成時は **Foundry project endpoint URL** (Phase 1 で控えた値) を入力

> ⚠️ ここで再掲: 旧 portal の agent は接続不可。新 Foundry portal の endpoint URL のみサポート。

### Step 4
- 接続作成完了後、**Next** をクリック

### Step 5
- **Name** と **Description** を入力
- ⚠️ Description は **Copilot Studio オーケストレーターが「いつこの Foundry agent を呼ぶか」を判断する根拠**
  - 上記 §4.2 の Best practices を必ず守る

### Step 6
- **Agent Id** (Phase 1 で控えた値) を入力

### Step 7
- Description を見直し / 調整 (他の tool / topic と曖昧にならないように)
- 公式引用:「make the description more specific if you have other tools or agents where the descriptions might overlap」

### Step 8
- **Add Agent** をクリック

接続後の修正 (Agent Id 変更等) は Agents 一覧 → 対象 agent → 詳細画面から可能。

---

## 6. Phase 4: 動作確認

### 6.1 Copilot Studio の Test pane

1. Copilot Studio portal → 対象エージェント → 右上 **Test** をオン
2. テスト メッセージ例:
   - `MFA を再登録したい` → ITHelpdeskFoundryAgent が選ばれて呼ばれるはず
   - `競合 X 社の最新動向を調べて` → ResearchFoundryAgent が選ばれて呼ばれるはず
3. **Track between topics** をオンにして、orchestration がどの agent / topic を選んだかを確認

### 6.2 明示的に Topic から呼出 (任意)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents>

Generative orchestration の自動ルーティングではなく、特定 Topic から **明示的に Foundry agent を呼ぶ** ことも可能 (公式引用):

> 「You can explicitly redirect to a child or connected agent from within a topic. Once the agent is done, the originating topic where you redirected from resumes.」

手順:
1. Topic 内で **Add node** → **Redirect to agent** → Foundry agent を選択
2. (一部 agent では) input / output 変数のマッピングが可能

> ⚠️ 公式 Note: 「Redirecting to Fabric Data agents isn't currently supported.」(Fabric は不可、Foundry agent は OK)

### 6.3 公開 (Teams / M365 Copilot / Web)

Copilot Studio 側を **Publish** すれば、Foundry 接続もそのまま公開チャネルで動作します。

1. Copilot Studio portal → **Publish** → **Publish**
2. **Channels** → Teams / M365 Copilot / Demo Website を追加
3. Teams で実機テスト

---

## 7. 認証・データ フロー

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent>
公式 (Foundry overview): <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview>

### 7.1 認証フロー

- Copilot Studio → Foundry の呼出は **Power Platform Connection** が仲介
- Connection は Copilot Studio の Maker / 環境スコープで作成
- 公式ドキュメントは認証主体 (Service Principal / User-delegated) を明示していないが、Power Platform OAuth2 Service Connection のパターンと整合
- Foundry 側では Microsoft Entra identity / RBAC / Content filter が **Foundry agent 側の責任**で適用される

### 7.2 データ フロー上の注意

| 観点 | 注意点 |
|---|---|
| **データ越境** | Copilot Studio 環境のデータが Foundry テナント / リージョンへ流れる。データ レジデンシー要件があるなら同一リージョン構成を必須化 |
| **DLP ポリシー** | Copilot Studio DLP と Foundry RBAC / VNet を **別々に**設計・運用する必要あり (1 箇所に統合できない) |
| **会話履歴** | Foundry 側で会話履歴が保存される場合がある (Responses API の `store: true` 等)。法令対応・削除ポリシーを Foundry 側でも別途整備 |
| **PII / 機密情報** | Copilot Studio で受け取ったデータが Foundry のモデル プロバイダー (Azure OpenAI 等) を経由する。Content filter / Privacy 設定を確認 |

### 7.3 監査ログ

- Copilot Studio 側: Power Platform admin center → 環境 → アクティビティ ログ
- Foundry 側: project → **Observability → Tracing** (AgentOps)
- ⚠️ **両方を別々にレビューする必要あり**。1 つの監査ダッシュボードに集約する公式機能は現時点で無い

---

## 8. 課金モデル

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management>

> 公式引用: 「These rates apply to all language models that Copilot Studio provides. They **exclude bring-your-own-model configurations, including Azure Foundry models, which are billed separately**.」

つまり:

| プロダクト | 課金対象 |
|---|---|
| **Copilot Studio** | Copilot Studio Copilot Credits (メッセージ単価 / 機能利用に応じて) |
| **Microsoft Foundry** | Azure サブスクリプションでの モデル トークン / Tool 呼出 / Hosted agent コンピュート |

**Foundry agent が呼ばれるたびに、Copilot Studio と Foundry の両方で課金が発生**します。月額シミュレーションは両方の単価で個別に試算が必要です。

---

## 9. 既知の制約 (公式確認済み)

| 観点 | 制約 |
|---|---|
| 機能ステータス | **Public Preview** (SLA 外) |
| Foundry portal バージョン | **新ポータル必須**。旧 portal の agent は `404 - Version not found` |
| 課金 | Copilot Studio + Foundry **両方** に発生 |
| 認証 | Foundry 側の認証は別途設計が必要 |
| DLP / データ越境 | Copilot Studio DLP と Foundry RBAC / VNet を別個に設計 |
| Channel | Copilot Studio の標準チャネル (Teams / M365 / Web) で問題なく動作するが、Streaming の挙動はチャネルにより差あり |
| Agent Id 変更 | 接続後も詳細画面から変更可能 |
| Fabric Data agent への redirect | **非サポート** (Foundry agent は OK) |
| 接続上限 | 公式に明示なし |
| 将来の置き換え | Copilot Studio 完全置き換えする際は、シナリオ A / B / C に切り替え可能 (Copilot Studio Topic を削除して Foundry agent を直接公開) |

---

## 10. 段階的移行のロードマップ例

シナリオ D は **段階移行戦略の中間点**として最も価値が出ます。

```
[現在]          [Phase 1: 試験]      [Phase 2: 並走]      [Phase 3: 完全移行]
                                                            (オプション)
Copilot Studio のみ    →    Copilot Studio が司令塔         Copilot Studio が司令塔          Foundry agent を
              + Foundry に試験       + 半数の Topic を     公開して Copilot Studio を廃止
              用 1 topic 委譲        Foundry に委譲       (= シナリオ A/B/C)

         シナリオ D 採用     →    シナリオ D 採用     →    シナリオ A/B/C
                                                          (の最終形)
```

---

## 11. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `cs-connection-notes.md` | Copilot Studio 接続時に必要な Foundry 側情報を控えるテンプレ |
| `topic-route-to-foundry.md` | Copilot Studio の Trigger Phrase / Description 設計サンプル |

> ℹ️ Foundry agent 本体 (A / B / C) は `..\scenario-a-prompt-agent\` 等のものを流用してください。本フォルダは **接続レイヤ・運用設計**のみを扱います。

---

## 12. 関連公式ドキュメント

| トピック | URL |
|---|---|
| **Connect to a Microsoft Foundry agent (一次資料)** | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent> |
| 外部 agent 接続 全般 (Foundry / Fabric / SDK) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents> |
| Generative orchestration / Best practices | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions> |
| Copilot Studio ライセンス | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing> |
| メッセージ課金 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management> |
| Foundry Agent Service 概要 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> |
| Foundry project endpoint 取得 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/quickstart?pivots=ai-foundry-portal> |
| Foundry RBAC | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry> |
| Foundry agent FAQ | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/faq> |
| Preview 利用規約 | <https://azure.microsoft.com/support/legal/preview-supplemental-terms/> |
