# シナリオ G: Microsoft Foundry → Microsoft 365 Copilot / Microsoft Teams **逆方向公開** (Early Access Preview)

> **位置付け**: シナリオ D の **逆方向**。Microsoft Foundry で作成した Prompt agent / Workflow agent / Hosted agent を、Microsoft Copilot Studio を経由せずに **Azure Bot Service 経由で Microsoft 365 Copilot / Microsoft Teams へ直接公開** するシナリオ。
>
> **状態**: **Early Access Preview** (2026 年時点)。本番運用にあたっては Microsoft Learn の最新情報を必ず確認してください。SLA 対象外。
>
> **想定工数**: 0.5〜2 人日 (既存 Foundry agent がある場合)
>
> **公式ガイド (一次資料)**:
> - <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> (Publishing 概要)
> - <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-copilot> (M365 / Teams 発行)
> - <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-agent> (Agent Application 全般)
> - <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity> (Entra Agent Identity)

> ℹ️ 本シナリオは、`scenario-d-cs-plus-foundry/reverse-publish-foundry-to-m365.md` を独立化したものです。シナリオ D が「Microsoft Copilot Studio から Foundry agent を呼ぶ」のに対し、本シナリオは「Foundry agent を Microsoft 365 Copilot / Teams で直接使う」点が逆向きです。

---

## 0. シナリオ D との比較

| 観点 | シナリオ D (Copilot Studio → Foundry) | **シナリオ G (Foundry → M365/Teams)** |
|---|---|---|
| 親オーケストレータ | Microsoft Copilot Studio | **なし** (Agent Application が直接フロント) |
| 公開チャネル | Microsoft Copilot Studio が対応するすべて (Teams / Web / Power Platform / Dynamics 365 等) | **Microsoft 365 Copilot / Microsoft Teams** (Azure Bot Service 経由で自動構成) |
| 課金 | Copilot Credits (5 / Agent action) + Foundry token | Foundry token + Azure Bot Service Channels (Standard チャネルは通常無料) |
| RBAC モデル | Copilot Studio 環境 + Foundry resource scope | **Entra Agent Identity** (将来は Entra Agent Registry 統合予定) |
| デプロイ単位 | Microsoft Copilot Studio エージェント (公開フロー内蔵) | **Agent Application** (ARM リソース、Activity Protocol 経由) |
| 状態 | Preview | **Early Access Preview** |

> 公式 verbatim (`agents/overview`):
>
> _"Version agents, create stable endpoints, and share through Microsoft Teams, Microsoft 365 Copilot, and the Entra Agent Registry."_

---

## 1. このシナリオが適する状況

| 条件 | 該当 |
|---|---|
| Microsoft Foundry 側で開発した agent を Microsoft 365 Copilot / Microsoft Teams で**直接**使いたい | ✅ |
| Microsoft Copilot Studio をフロントに持たず、エンタープライズ Bot を Microsoft Foundry のみで完結したい | ✅ |
| Activity Protocol 経由で Bot Framework / Teams 固有体験 (Adaptive Cards / Mention 等) を活かしたい | ✅ |
| Copilot Studio 既存資産があり、それを温存しつつ拡張したい | ❌ シナリオ D 推奨 |
| 本番 SLA 必須 | ❌ (Early Access Preview のため) |
| Power Platform 環境ライセンスがない / Microsoft 365 管理者の承認フローが通せない | ❌ |

---

## 2. 前提条件

### 2.1 Microsoft Foundry 側

| 項目 | 値 |
|---|---|
| Foundry resource + project | 既存 (シナリオ A〜C で作成したもの可) |
| 対象 agent | Prompt / Workflow / Hosted のいずれか (本シナリオでは A の `helpdesk-prompt` 想定) |
| Foundry portal | <https://ai.azure.com> (**New Foundry** トグル ON) |
| RBAC | Foundry Owner (Agent Application を作成する権限) |

### 2.2 Microsoft 365 テナント側

| 項目 | 値 |
|---|---|
| Microsoft 365 管理者権限 | `People in your organization` スコープ公開時に必要 |
| Microsoft 365 Copilot ライセンス | 公開先で利用するユーザーに付与 |
| Microsoft Teams 管理センター | App permission policy で許可 (必要に応じ) |

### 2.3 Azure サブスクリプション側

| 項目 | 値 |
|---|---|
| `Microsoft.BotService` プロバイダー | Public Preview 中は自動登録だが、未登録の場合は `az provider register --namespace Microsoft.BotService` |
| Entra Agent Identity | Agent Application 作成時に自動付与 (Object ID を控える) |

---

## 3. 公開フロー (要旨)

> ⚠️ 詳細手順は Microsoft Learn `how-to/publish-copilot` を参照 (Early Access Preview のためコマンド形式は変動)。

### 3.1 Foundry portal から公開

1. Foundry portal → 対象 Project → 対象 Agent (Prompt / Workflow / Hosted) を選択
2. 右上 **Publish** → **Microsoft 365 Copilot / Teams**
3. **Scope** を選択:
   - **Just you**: 自分のみ即時利用可 (検証用)
   - **People in your organization**: Microsoft 365 管理センター承認フロー
4. **Agent Application 名** と **アイコン / 説明** を入力
5. **Microsoft.BotService** リソースが裏側で自動作成される
6. 必要に応じて Teams Admin Center で **App permission policy** を更新
7. 公開完了後、Microsoft 365 Copilot / Teams のアプリ ストアに表示

### 3.2 RBAC の再割当 (重要)

公式 (`concepts/development-lifecycle`) verbatim:

> _"Permissions assigned to the project identity don't automatically transfer to the published agent. When you publish an agent as an Agent Application, the application receives its own Entra agent identity, and you must explicitly re-grant any RBAC roles."_

Agent Application は **独立した Entra Agent Identity** を持つため、Project に付与した RBAC は継承されません。下記を Agent Application Object ID に再割当てしてください:

```powershell
$APP_OBJ_ID = "<Agent Application の Entra Object ID>"
$ACCT_SCOPE = "/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCT"

# Foundry User (53ca6127-db72-4b80-b1b0-d745d6d5456d)
az role assignment create --assignee-object-id $APP_OBJ_ID --assignee-principal-type ServicePrincipal `
  --role "53ca6127-db72-4b80-b1b0-d745d6d5456d" --scope $ACCT_SCOPE

# 子 agent / OpenAPI tool / Storage / Vector Store が参照するリソースにも同様に再割当て
```

---

## 4. プロトコル選択

公式 (`how-to/publish-copilot`) verbatim:

> _"Currently, only one protocol — either Responses or Activity Protocol — can be enabled for an Agent Application at a time."_

| プロトコル | 用途 | 主な制約 |
|---|---|---|
| **Responses** | プログラマティック呼出 (SDK / REST) | Teams の Adaptive Card / Mention / Typing indicator 等を直接扱えない |
| **Activity Protocol** | **Microsoft Teams / Microsoft 365 Copilot 公開** (本シナリオで必要) | OpenAI Responses 互換クライアントから呼べない |

両方を同時に有効化したい場合は、**Agent Application を 2 つ** (Activity 用と Responses 用) 作成する設計を検討してください。

---

## 5. 動作確認のテレメトリ

| 確認場所 | 何を見るか |
|---|---|
| **Foundry Tracing** (Observability) | `contextId` / `responseId` でエンドツーエンドのトレース |
| **Application Insights** | `traces` / `dependencies` テーブル (`session-id` で会話ごとに集約) |
| **Azure Bot Service** | `Microsoft.BotService` リソース → Channels → Test in Web Chat (デバッグ向け) |
| **Microsoft 365 Admin Center** | 公開承認フローの状態、利用テナント数 |
| **Teams Admin Center** | アプリの分布状況、App permission policy への影響 |

---

## 6. 重要な制約 (verbatim)

| # | 制約 | verbatim 引用 |
|---|---|---|
| 1 | Entra Agent Registry 未登録 | _"Agent Applications are not registered in the Microsoft Entra agent registry"_ (`publish-agent`) |
| 2 | 1 Agent Application は **片方のプロトコルのみ** | _"Currently, only one protocol — either Responses or Activity Protocol — can be enabled for an Agent Application at a time"_ (`publish-copilot`) |
| 3 | SLA 対象外 | Early Access Preview のため、Production SLA は対象外 |
| 4 | Publish 後の RBAC は手動再割当 | (`concepts/development-lifecycle`) — シナリオ B/G 共通 |
| 5 | Workflow Tracing は Preview | (`observability/concepts/trace-agent-concept`) — Tracing GA は Prompt agent のみ |

---

## 7. シナリオ D との併用パターン

| 要件 | 推奨 |
|---|---|
| **既存 Copilot Studio エージェントを Foundry に拡張したい** | シナリオ D |
| **既存 Foundry エージェントを Microsoft 365 Copilot で使いたい** | **シナリオ G (本シナリオ)** |
| **両方の入口が欲しい (Copilot Studio フロント + M365 Copilot フロント)** | D + G を併用 (ただし課金・トレーシングを別管理) |
| **Bot Framework / カスタム チャネル (Web / IVR)** | Activity Protocol を有効化し、Azure Bot Service の他チャネル設定 |

---

## 8. 既知の Open Question (継続調査)

- **Entra Agent Registry の独立 URL**: 公式記述では将来統合予定とあるが、独立した管理 UI のリリース時期は未公表
- **シナリオ D との同時公開**: Activity Protocol と Responses Protocol を併用する Agent Application のサポート時期は未公表
- **EU Data Boundary 対応**: 2026-05 時点では Real-time Voice 等の機能が北米限定。本シナリオ全体での EU 対応ロードマップは別途確認が必要
- **Microsoft Agent 365 との関係**: Microsoft Ignite 2025 で発表された Microsoft Agent 365 と本シナリオ G の Agent Application の関係性は今後継続観察が必要

---

## 9. 関連シナリオ・補助ドキュメント

| ドキュメント | 内容 |
|---|---|
| [`../scenario-d-cs-plus-foundry/README.md`](../scenario-d-cs-plus-foundry/README.md) | 逆向き (CS → Foundry) のシナリオ D |
| [`../scenario-d-cs-plus-foundry/reverse-publish-foundry-to-m365.md`](../scenario-d-cs-plus-foundry/reverse-publish-foundry-to-m365.md) | 本シナリオの簡易メモ (シナリオ D の参考資料として) |
| [`../../docs/publishing-channels.md`](../../docs/publishing-channels.md) | Foundry Agent Application の発行経路一覧 |
| [`../../docs/governance.md`](../../docs/governance.md) | DLP / RBAC / Content Safety / Preview terms |
