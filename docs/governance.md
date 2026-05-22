# 横断ガバナンス: DLP / RBAC / Content Safety / Preview terms

> ⚠️ **作業中・検証中のドラフトです (確定版ではありません)。本番採用前に公式ドキュメントで最終確認してください。**

> **目的**: シナリオ A〜I で共通する **ガバナンス (Governance) 観点** を一箇所に集約し、デモ・PoC・本番計画のすべての段階で参照できる "1 ファイル チェックリスト" を提供する。
>
> **対象読者**: アーキテクト / セキュリティ レビュアー / コンプライアンス担当 / プラットフォーム エンジニア。
>
> **更新方針**: Microsoft 公式の更新頻度が高いため、本ドキュメントは **2026 年 5 月時点の情報**を反映。商用デプロイ前には必ず一次資料 (各セクション冒頭の `公式` リンク) を再確認すること。

---

## 0. 目次

1. [Responsible AI (RAI) 全体像](#1-responsible-ai-rai-全体像)
2. [RBAC: Microsoft Foundry / Microsoft Copilot Studio / Power Platform](#2-rbac-microsoft-foundry--microsoft-copilot-studio--power-platform)
3. [Entra Agent Identity (Agent Application)](#3-entra-agent-identity-agent-application)
4. [Content Safety / Prompt Shields / XPIA](#4-content-safety--prompt-shields--xpia)
5. [Microsoft Copilot Studio の DLP](#5-microsoft-copilot-studio-の-dlp)
6. [データ滞留 / リテンション](#6-データ滞留--リテンション)
7. [Preview supplemental terms (SLA / サポート対象外の取扱い)](#7-preview-supplemental-terms-sla--サポート対象外の取扱い)
8. [シナリオ別チェックリスト](#8-シナリオ別チェックリスト)

---

## 1. Responsible AI (RAI) 全体像

公式 (`responsible-use-of-ai-overview`): Microsoft Foundry の RAI は **Discover / Protect / Govern** の 3 層で整理されている。

| 層 | 機能 | 公式リンク |
|---|---|---|
| **Discover** | モデル/エージェントのリスク評価 (Built-in evaluator / Red Teaming Agent) | `concepts/built-in-evaluators` |
| **Protect** | Content Filter / Prompt Shields / XPIA / PII Detection | `concepts/content-filtering` |
| **Govern** | RBAC / Audit logs / Tracing / Preview terms | `concepts/rbac-foundry` / `observability/concepts/trace-agent-concept` |

> 💡 **Microsoft Copilot Studio 側** は別系統の RAI として `nlu-generative-answers` の moderation / jailbreak / prompt injection ガード、および Power Platform DLP が中核。**Foundry の RAI 設定が Microsoft Copilot Studio に自動継承されない点に注意** (各レイヤーで個別設計が必要)。

---

## 2. RBAC: Microsoft Foundry / Microsoft Copilot Studio / Power Platform

### 2.1 Microsoft Foundry のロール GUID (公式 verbatim)

公式: `concepts/rbac-foundry`

| ロール | GUID | スコープ | 主な用途 |
|---|---|---|---|
| **Foundry User** | `53ca6127-db72-4b80-b1b0-d745d6d5456d` | **Foundry account (resource) scope** | agent / model / tool への読み書き |
| **Foundry Owner** | (公式参照) | account scope | File Search 利用、Vector store 管理、Agent Application 公開 |
| **Foundry Project Manager** | (公式参照) | project scope | Hosted agent のデプロイ / 管理 |
| **Foundry Contributor** | (公式参照) | account / project | Hosted agent 編集、Workflow 編集 |

> ⚠️ **誤りやすいパターン**:
> - Project scope に Foundry User を割り当てる (正: **account / resource scope** に Foundry User)
> - Storage への RBAC を Resource Group scope に割り当てる (正: **Storage Account scope** に必要最小限)
> - Project Managed Identity / Agent Application の Entra Object ID への割当を忘れる (RBAC が継承されない — §3 参照)

### 2.2 シナリオ別 最小権限セット

| シナリオ | 必要ロール |
|---|---|
| **A (Prompt agent)** | Foundry User (account scope) + Storage Blob Data Contributor (storage account scope) + File Search 利用時は Foundry Owner |
| **B (Workflow agent)** | Foundry User + Contributor (Workflow 編集) + Workflow Tracing 有効化時は Application Insights Contributor |
| **C (Hosted agent)** | Foundry Project Manager + Contributor + **AcrPull** (Project Managed Identity に対し) |
| **D (CS → Foundry)** | Foundry User + Microsoft Copilot Studio Maker 権限 (Power Platform 環境) |
| **E (BYOM)** | Power Platform 環境 Maker + Foundry **Reader** (Foundry endpoint への接続のみ) |
| **F (MCP)** | MCP server 側で個別設計 (OAuth 推奨) + Microsoft Copilot Studio Maker |
| **G (Foundry → M365)** | Foundry Owner + Microsoft 365 管理者 (`People in your organization` 公開時) |
| **H (APIM AI Gateway)** | APIM Contributor + Cognitive Services User (APIM → Foundry 呼出時) |
| **I (Evaluation)** | Foundry Owner (Red Teaming Agent 作成) |

### 2.3 CLI コマンド (GUID 指定)

```powershell
$SUB = "<subscription-id>"
$RG = "<resource-group>"
$ACCT = "<foundry-account-name>"
$USER_OBJ = "<user-or-sp-object-id>"
$ACCT_SCOPE = "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCT"

# Foundry User (account scope)
az role assignment create `
  --assignee-object-id $USER_OBJ --assignee-principal-type User `
  --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" `
  --scope $ACCT_SCOPE
```

> 💡 ロール名 (`Foundry User` / 旧 `Azure AI User`) は遷移期にあるため、**GUID 指定**が最も安全。

---

## 3. Entra Agent Identity (Agent Application)

公式: `concepts/agent-identity` / `concepts/development-lifecycle`

### 3.1 Agent Application は **独立した Entra Identity**

公式 verbatim (`concepts/development-lifecycle`):

> _"Permissions assigned to the project identity don't automatically transfer to the published agent. When you publish an agent as an Agent Application, the application receives its own Entra agent identity, and you must explicitly re-grant any RBAC roles."_

| 観点 | 内容 |
|---|---|
| 状態 | Entra Agent Identity 本体は **GA** / Entra Agent Registry は **将来統合予定** (Preview ですらない) |
| 影響範囲 | シナリオ B (Workflow Publish) / C (Hosted) / G (Foundry → M365) すべてで **手動再割当が必須** |
| 再割当対象 | Foundry account、子 agent、OpenAPI tool、Storage、Vector Store、関連 Cognitive Services |

### 3.2 OBO (On-Behalf-Of) フロー

公式: `concepts/agent-identity` (シナリオ D 強化として重要)

| 観点 | 内容 |
|---|---|
| 状態 | **GA** |
| 用途 | Microsoft Copilot Studio → Foundry agent の連携で、ユーザー トークンを Foundry agent が継承し SharePoint / Microsoft Graph を呼ぶ (ゼロトラスト) |
| 注意 | OBO 利用には Entra アプリ登録の `delegated permissions` 設定が必要 |

---

## 4. Content Safety / Prompt Shields / XPIA

公式: `concepts/content-filtering` / Azure AI Content Safety `jailbreak-detection`

### 4.1 Foundry の Content Filter (シナリオ A〜C 共通)

| 機能 | 状態 | 用途 |
|---|---|---|
| **Hate / Self-harm / Violence / Sexual** カテゴリ filter | GA | 入出力の有害コンテンツ filter (4 段階 Severity) |
| **Prompt Shields (Direct Attack / User Prompt Attack)** | GA | jailbreak / role-play による guardrails 突破試行を検出 |
| **Indirect Attacks (XPIA)** | GA | 外部 document (RAG / Vector Store / MCP resource) 経由のプロンプト インジェクション検出 |
| **PII Detection** | GA | 個人情報 (mail / 電話 / 社員番号 等) の検出 + マスキング |
| **Task Adherence** | Preview | agent が instructions に従っているかリアルタイム検出 |
| **Protected Material** | GA | 著作権保護されたテキスト / コードの出力検出 |
| **Groundedness** | GA | RAG 応答の根拠検出 (ハルシネーション抑制) |

### 4.2 設定手順 (Portal 操作 verbatim)

公式 (`concepts/content-filtering`) verbatim:

> _"To configure content filters, go to Guardrails + controls → + Create content filter → set Input and Output filters → assign to model deployment."_

```text
1. Foundry portal → 対象 project → Guardrails + controls
2. + Create content filter
3. Input tab: Hate / Self-harm / Violence / Sexual (各 Severity 閾値)
                + Prompt Shields (Detect direct attacks / Detect indirect attacks)
                + PII Detection
4. Output tab: 同上 + Groundedness + Protected Material
5. モデル デプロイに紐付け (Apply to deployment)
```

### 4.3 シナリオ別の最小設定

| シナリオ | 入力 filter | 出力 filter | 備考 |
|---|---|---|---|
| **A (IT helpdesk)** | Hate / Violence / **Prompt Shields (Direct + Indirect)** / PII | 同左 + **Groundedness** + Protected Material | 外部 IT 質問の中に攻撃 prompt が混在する想定 |
| **B (Workflow)** | A と同じ | A と同じ | Workflow ノードの LLM 呼出ごとに継承 |
| **C (Hosted)** | A と同じ | A と同じ + **Task Adherence** (Preview) | コード生成あれば Code Vulnerability も推奨 |
| **D (CS + Foundry)** | Foundry 側 = A と同じ / CS 側 = Generative answers moderation | 同左 | DLP / Content filter は二重に評価される |
| **E (BYOM)** | Foundry モデル endpoint 側で Content Filter 必須 | 同左 | CS 側 Prompt の jailbreak 攻撃対策で重要 |
| **F (MCP)** | MCP server 側で別途 input validation | LLM 出力は CS / Foundry 側で filter | XPIA は **MCP resource 経由が最重要** |
| **G (Foundry → M365)** | Agent Application の入力 | Activity Protocol 出力 | Teams 公開のため Hate / Protected Material 厳格化 |
| **H (APIM)** | APIM の `send-request` で Content Safety 集中強制 | 同左 | 全 LLM 呼出に一元適用可能 (推奨) |

---

## 5. Microsoft Copilot Studio の DLP

公式: `power-platform/admin/wp-data-loss-prevention` / `admin-data-loss-prevention`

| 観点 | 内容 |
|---|---|
| 状態 | **GA** (Power Platform DLP の枠組み内) |
| 適用範囲 | Microsoft Copilot Studio が呼ぶすべての connector / Power Automate / カスタム コネクタ / MCP server |
| ポリシー カテゴリ | **Business** / **Non-Business** / **Blocked** の 3 分類 |
| MCP 連携時の注意 | MCP server を呼ぶ connector は **Non-Business** にデフォルト分類される。Business と Non-Business の同一エージェント内併用はブロックされるため設計時に統一が必要 |

### 5.1 シナリオ F (MCP) における DLP 連鎖ブロック

公式 (`agent-extend-action-mcp`) verbatim:

> _"When you connect to a non-Microsoft product, including an external MCP server, you're responsible for the tools and resources you access from within Copilot Studio."_

| シナリオ | DLP 設計のポイント |
|---|---|
| F (MCP, 自社 IT) | MCP server を Business connector として登録、SharePoint / 社内 API と同じ DLP グループに配置 |
| F (MCP, OSS / 3rd party) | Non-Business に配置 → Business connector とは同一エージェントで併用不可。本番では別エージェントに分離 |
| D (CS + Foundry) | Foundry agent connector は Business / Non-Business のどちらに分類するかを **テナント全体で統一** |

---

## 6. データ滞留 / リテンション

### 6.1 Responses API (シナリオ A / C)

公式: `azure/ai-services/openai/how-to/responses`

| 設定 | 動作 |
|---|---|
| `store=true` (デフォルト) | 会話履歴を **30 日**保持 |
| `store=false` | 履歴を保持しない (Multi-turn 会話は SDK 側で履歴管理が必要) |
| `client.responses.delete(response_id)` | 個別 response の即時削除 |

> ⚠️ **GDPR / 個人情報保護法対応**: PII を含む会話を保持する場合は `store=false` または明示的な `delete` 運用が必須。

### 6.2 Foundry agent / Hosted agent のデータ

| データ | 保存場所 | 保持期間 |
|---|---|---|
| Vector Store (File Search) | Foundry account 内の独自ストア | 明示削除まで永続 (`$0.10/GB/day` 課金) |
| Hosted agent コンテナの `$HOME` | per-session VM 永続化 (Preview) | session 終了で破棄 |
| Tracing (Application Insights) | Application Insights のデフォルト | 既定 90 日 (調整可) |

---

## 7. Preview supplemental terms (SLA / サポート対象外の取扱い)

公式: <https://azure.microsoft.com/support/legal/preview-supplemental-terms/>

| シナリオ | Preview 部分 | 商用利用可否 |
|---|---|---|
| **B (Workflow agent)** | Workflow agent 自体 Preview | SLA 対象外。本番運用は推奨されない |
| **C (Hosted agent)** | Hosted agent 自体 Preview | SLA 対象外 |
| **D (CS → Foundry 接続機能)** | 接続機能 Preview | SLA 対象外 |
| **F (MCP)** | MCP 機能 GA。**MCP Prompts のみ未対応** | GA。Prompts 未対応に注意 |
| **G (Foundry → M365)** | **Early Access Preview** | SLA 対象外 |
| **H (APIM AI Gateway)** | コア機能 GA。Foundry portal からの自動連携 / MCP server expose は Preview | GA 部分は商用利用可 |
| **I (Evaluation)** | Agent evaluator / Red Teaming Agent / Continuous monitoring は Preview | Built-in (GA) は商用利用可 |

### 7.1 Preview 機能の運用ガイドライン

1. **本番依存禁止**: Preview API のシグネチャは変更されうる前提でコード設計 (薄いラッパー / Feature flag 推奨)
2. **SLA 対象外を関係者に周知**: 営業 / カスタマー サクセス / SRE と事前共有
3. **代替プラン**: GA 機能でのフォールバック パスを用意 (例: Workflow Preview → Prompt agent への自動切替)
4. **terms 受諾の記録**: テナント管理者が Preview 機能を有効化した日付と承認者を記録

---

## 8. シナリオ別チェックリスト

各シナリオ実施前に確認すべき最低項目 (Yes/No チェック推奨):

### 8.1 共通 (全シナリオ)

- [ ] Preview supplemental terms を関係者に共有済み
- [ ] テナント管理者が必要な機能を有効化済み
- [ ] DLP 分類 (Business / Non-Business / Blocked) を確認済み
- [ ] PII / 機密情報の入力可否を ユーザー向けメッセージで明示

### 8.2 シナリオ A〜C (Foundry agent 本体)

- [ ] RBAC を account scope + GUID 指定で割当済
- [ ] Project Managed Identity への割当を漏れなく実施
- [ ] Content Filter を Hate / Self-harm / Violence / Sexual + Prompt Shields (Direct + Indirect) + PII で設定
- [ ] File Search / Vector Store の保持期間と削除運用を定義
- [ ] (C のみ) Hosted Compute の SKU と $/hour を把握

### 8.3 シナリオ D / E / F (Microsoft Copilot Studio 連携)

- [ ] Copilot Studio DLP ポリシーで対象 connector を分類済
- [ ] Generative orchestration の有効化 (F は必須)
- [ ] BYOM (E) / MCP (F) のキー管理を Key Vault または APIM に集約
- [ ] Copilot Credits 課金の予算アラートを設定

### 8.4 シナリオ G (Foundry → M365)

- [ ] Agent Application の Entra Object ID への RBAC 再割当を完了
- [ ] Microsoft 365 管理者承認フロー (`People in your organization` 公開時) の事前合意
- [ ] Activity Protocol / Responses Protocol の選択を確定 (1 Agent Application に 1 つのみ)

### 8.5 シナリオ H (APIM)

- [ ] APIM SKU (Standard v2 以上) と policy 限界を確認
- [ ] `<llm-token-limit>` の counter-key 設計 (テナント単位 / ユーザー単位)
- [ ] Semantic cache の vary-by 設計 (キャッシュ汚染防止)
- [ ] `<llm-emit-token-metric>` の dimensions を FinOps 要件に合わせる

### 8.6 シナリオ I (Evaluation)

- [ ] Playground 評価のデフォルト ON / 課金を把握
- [ ] Judge model を評価対象モデルと別に設定
- [ ] Safety evaluator の Content Safety 課金を予算に組込
- [ ] AI Red Teaming Agent の scan 結果を Issue tracker と連携

---

## 9. 参考: 関連ドキュメント

| ドキュメント | 内容 |
|---|---|
| [`./cost-finops.md`](./cost-finops.md) | 横断コスト管理 (Foundry token / Copilot Credits / APIM token metric) |
| [`./evaluation-playbook.md`](./evaluation-playbook.md) | Evaluator の推奨組合せ / Red Teaming / CI/CD ゲート |
| [`../demo-assets/README.md`](../demo-assets/README.md) | シナリオ A〜F の比較表 + 共通 Responsible AI / DLP 観点 |
| [`../demo-assets/scenario-g-foundry-to-m365/README.md`](../demo-assets/scenario-g-foundry-to-m365/README.md) | シナリオ G (Agent Application + Entra Agent Identity) |
| [`../demo-assets/scenario-h-apim-ai-gateway/README.md`](../demo-assets/scenario-h-apim-ai-gateway/README.md) | シナリオ H (APIM ポリシーによる集中ガバナンス) |
| [`../demo-assets/scenario-i-evaluation-redteam/README.md`](../demo-assets/scenario-i-evaluation-redteam/README.md) | シナリオ I (Evaluation + Red Teaming) |
