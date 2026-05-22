# シナリオ G (Foundry → M365 Copilot / Teams 逆方向公開) — Early Access Preview

> **位置付け**: シナリオ D の **逆方向**。Microsoft Foundry で作成した Prompt agent / Workflow agent / Hosted agent を、Microsoft Copilot Studio を経由せずに **Azure Bot Service / Microsoft 365 Copilot / Microsoft Teams へ直接公開** するシナリオ。
>
> **状態**: **Early Access Preview** (2026 年時点)。本番運用にあたっては Microsoft Learn の最新情報を必ず確認してください。

公式リファレンス:

| トピック | URL |
|---|---|
| Microsoft Foundry Agents — Publishing 概要 | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview> |
| Foundry → M365 / Teams 発行 (Publish Copilot) | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-copilot> |
| Agent Application 全般 (Publish Agent) | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-agent> |
| Agent Identity (Entra Agent Identity) | <https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/agent-identity> |

---

## 1. シナリオ D との比較

| 観点 | シナリオ D (Copilot Studio → Foundry) | **シナリオ G (Foundry → M365/Teams)** |
|---|---|---|
| 親オーケストレータ | Copilot Studio | **なし** (Agent Application が直接フロント) |
| 公開チャネル | Copilot Studio が対応するすべて (Teams / Web / Power Platform / D365 等) | **M365 Copilot / Teams** (Azure Bot Service 経由で自動構成) |
| 課金 | Copilot Credits (5 / Agent action) | Foundry のトークン課金 + Azure Bot Service Channels (通常無料) |
| RBAC モデル | Copilot Studio 環境 + Foundry resource scope | **Entra Agent Identity** (将来は Entra Agent Registry 統合予定) |
| デプロイ単位 | Copilot Studio エージェント (公開フロー内蔵) | **Agent Application** (ARM リソース、Activity Protocol 経由) |

> 公式 verbatim (`agents/overview`): _"Version agents, create stable endpoints, and share through Microsoft Teams, Microsoft 365 Copilot, and the Entra Agent Registry."_

---

## 2. 公開フロー (要旨)

> ⚠️ 詳細手順は Microsoft Learn `how-to/publish-copilot` を参照 (Early Access Preview のためコマンド形式は変動)。

1. Foundry portal → 対象 Project → 対象 Agent (Prompt / Workflow / Hosted) を選択
2. 右上 **Publish** → **Microsoft 365 Copilot / Teams**
3. **Scope** を選択:
   - **Just you**: 自分のみ即時利用可
   - **People in your organization**: Microsoft 365 管理センター承認フロー
4. **Microsoft.BotService** リソースが裏側で自動作成される
5. 必要に応じて Teams Admin Center で **App permission policy** を更新
6. 公開完了後、Microsoft 365 Copilot / Teams のアプリ ストアに表示

---

## 3. 重要な制約 (verbatim)

| # | 制約 | verbatim 引用 |
|---|---|---|
| 1 | Entra Agent Registry 未登録 | _"Agent Applications are not registered in the Microsoft Entra agent registry"_ |
| 2 | 1 Agent Application は **片方のプロトコルのみ** | _"Currently, only one protocol — either Responses or Activity Protocol — can be enabled for an Agent Application at a time"_ |
| 3 | SLA 対象外 | Early Access Preview のため、Production SLA は対象外 |

---

## 4. シナリオ D と併用する場合の判断指針

| 要件 | 推奨 |
|---|---|
| **既存 Copilot Studio エージェントを Foundry に拡張したい** | シナリオ D |
| **既存 Foundry エージェントを M365 Copilot で使いたい** | **シナリオ G (本シナリオ)** |
| **両方の入口が欲しい (Copilot Studio フロント + M365 Copilot フロント)** | D + G を併用 (ただし課金・トレーシングを別管理) |
| **Bot Framework / カスタム チャネル (Web / IVR)** | Activity Protocol を有効化し、Azure Bot Service の他チャネル設定 |

---

## 5. 動作確認のテレメトリ

- **Foundry Tracing**: シナリオ D と同じ Application Insights で `contextId` / `responseId` を確認
- **Azure Bot Service**: `Microsoft.BotService` リソース → Channels → Test in Web Chat
- **Microsoft 365 Admin Center**: 公開承認フローの状態確認

---

## 6. 既知の Open Question (継続調査)

- **Entra Agent Registry の独立 URL**: 公式記述では将来統合予定とあるが、独立した管理 UI のリリース時期は未公表
- **シナリオ D との同時公開**: Activity Protocol と Responses Protocol を併用する Agent Application のサポート時期は未公表
- **EU Data Boundary 対応**: 2026-05 時点では Real-time Voice 等の機能が北米限定。本シナリオ全体での EU 対応ロードマップは別途確認が必要
