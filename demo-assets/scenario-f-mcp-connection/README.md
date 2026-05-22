# シナリオ F: Microsoft Copilot Studio × Microsoft Foundry **MCP (Model Context Protocol) 連携**

> **位置付け**: Microsoft Copilot Studio エージェントに **MCP server を tool として接続**し、Microsoft Foundry agent や任意の外部システムを **標準プロトコル (MCP)** 経由で呼び出す連携パターン。
> **状態**: ✅ **GA (一般提供開始済み)** (Microsoft Copilot Studio の MCP 接続機能)
> **想定工数**: 0.5 人日 (既存 MCP server を繋ぐ場合) 〜 3 人日 (MCP server を自作する場合)
> **公式ガイド (一次資料)**:
>  - <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp>
>  - <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent>
>  - <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent>

シナリオ D が **エージェント単位 (agent-to-agent)** の委譲、E が **モデル単位 (BYOM)** の差し替えだったのに対し、本シナリオ F は **ツール単位 (tool-level)** の汎用接続です。MCP は Anthropic 発のオープン プロトコルで、Microsoft Copilot Studio・Microsoft Foundry・任意の OSS / SaaS が同じ規格で相互接続できます。

---

## 0. 全体構成図

```
[エンド ユーザー]
   │  (Teams / M365 Copilot / 公開 Web)
   ▼
[Microsoft Copilot Studio エージェント]
   ├─ Topic: FAQ
   ├─ Action: CreateTicket
   └─ Tool: <MCP server> ← ★ ここで MCP 接続を追加
              │
              │  Streamable HTTP transport (旧 SSE は 2025-08 以降サポート終了)
              │  認証: None / API Key (Header or Query) / OAuth 2.0 (Dynamic Discovery / Dynamic / Manual)
              ▼
   ┌──────────────────────────────────────────────────────────────┐
   │  MCP server の選択肢:                                          │
   │   ・自作: Microsoft Foundry agent を MCP server として公開     │
   │   ・自作: Hosted agent (シナリオ C) コンテナに MCP endpoint    │
   │   ・既製: Microsoft Learn Docs MCP                            │
   │   ・既製: Azure AI Search MCP / 任意の MCP-compliant server   │
   │   ・他社 SaaS が公開する MCP server                            │
   └──────────────────────────────────────────────────────────────┘
```

---

## 1. このシナリオが適する状況

| 条件 | 該当 |
|---|---|
| 既存の Microsoft Copilot Studio エージェントを **そのまま継続使用**したい | ✅ |
| 複数の外部システム / Microsoft Foundry agent / OSS ツールを **統一プロトコル**で接続したい | ✅ |
| MCP 仕様で公開された **3rd party / OSS ツール** を活用したい (Learn Docs / GitHub / DB ツール等) | ✅ |
| 各 tool の追加・更新を **MCP server 側で完結**させ、Microsoft Copilot Studio の再ビルドを避けたい | ✅ |
| 認証は API key / OAuth 2.0 のいずれかで運用したい | ✅ |
| 1 体の特定 Microsoft Foundry agent に直接委譲したい (オーケストレーション含む) | ❌ シナリオ D 推奨 |
| LLM モデルだけ Microsoft Foundry のものを使いたい | ❌ シナリオ E 推奨 |

> 💡 **MCP の最大の魅力**: tool 定義が **MCP server 側で動的に更新される** ため、Microsoft Copilot Studio 側はサーバーを 1 度繋ぐだけで、サーバーが提供する全ツールに追従できる。

---

## 2. 前提条件

### 2.1 Microsoft Copilot Studio 側

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp>

| 項目 | 値 |
|---|---|
| ライセンス | Microsoft Copilot Studio Standalone / Trial / M365 Copilot |
| 環境 | Production 環境推奨 |
| Maker 権限 | agent author + Power Platform Connection 作成権限 |
| ポータル | <https://copilotstudio.microsoft.com> |
| **Generative orchestration** | **ON 必須** (MCP tool は orchestration が選ぶため) |
| 対応 transport | **Streamable HTTP のみ**。公式 (`mcp-add-existing-server-to-agent`) verbatim: _"SSE transport is deprecated, Copilot Studio no longer supports SSE for MCP after August 2025."_ ※これは旧 HTTP+SSE transport (`modelcontextprotocol.io/specification/2024-11-05/...`) の廃止であり、Streamable HTTP 内での SSE ストリーミング自体は引き続き利用可能 |
| **MCP 機能対応範囲** | ✅ **Tools** ・ ✅ **Resources** ・ ❌ **Prompts (未対応)**。公式 (`agent-extend-action-mcp`) verbatim: _"Copilot Studio currently supports MCP tools and resources."_ ← Prompts は明示的に列挙されていない |

📖 まだ Microsoft Copilot Studio エージェントが無い場合は `..\00-create-cs-agent.md` を先に実施。

### 2.2 MCP server 側

| パターン | 詳細 |
|---|---|
| **自作 (Microsoft Foundry / Hosted agent)** | シナリオ C の Hosted agent コンテナに MCP server (FastMCP / TypeScript SDK / .NET SDK 等) を実装して公開する |
| **自作 (Azure Container Apps / Functions)** | 任意の言語で MCP server を実装し、Azure Container Apps / Azure Functions / App Service / AKS にホストする |
| **既製 (Microsoft 公式)** | Microsoft Learn Docs MCP / Azure AI Foundry MCP / Sentinel MCP / Azure AI Search MCP 等 |
| **既製 (3rd party)** | GitHub MCP / Slack MCP / 各種 DB MCP server 等 (MCP 仕様準拠なら接続可) |

### 2.3 認証要件 (公式 verbatim)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent>

| 認証タイプ | 用途 |
|---|---|
| **None** | 公開 endpoint・社内検証のみ |
| **API key (Header)** | リクエストヘッダーに API key を載せる |
| **API key (Query)** | URL クエリパラメータに API key を載せる |
| **OAuth 2.0 — Dynamic Discovery** | MCP server が DCR (Dynamic Client Registration) + discovery に対応している場合の **最も簡単な方法** |
| **OAuth 2.0 — Dynamic** | DCR は対応するが discovery 非対応の場合。Authorization URL / Token URL template を手動入力 |
| **OAuth 2.0 — Manual** | Client ID / Client Secret / Authorization URL / Token URL / Refresh URL / Scopes を全て手動入力 |

---

## 3. Phase 1: MCP server を準備 (or 既存サーバーを選定)

### 3.1 パターン A: 既存の MCP server を使う (推奨スタート)

最速で試すなら **Microsoft Learn Docs MCP** が便利:

| 項目 | 値 |
|---|---|
| Server name | `Microsoft Learn Docs` |
| Server URL | (Microsoft 公開のエンドポイントを利用) |
| 認証 | OAuth 2.0 (Dynamic Discovery) または None (公開検索のみ) |
| 提供 tool | Microsoft Learn 検索 / ドキュメント取得 |
| 公式 Lab | <https://aka.ms/mcsmcp/lab/blog> |

### 3.2 パターン B: Microsoft Foundry の Hosted agent を MCP server 化する

> ⚠️ **免責**: 本節 (パターン B) は **Microsoft 公式ドキュメントに記載された手順ではなく、カスタム実装例** です。Foundry Hosted agent コンテナ内に MCP server を同梱する公式パターンは 2026-05 時点では確認できていません。FastMCP の API シグネチャ (`run_streamable_http(...)`) も SDK バージョンによって変動するため、必ず PyPI の最新版で再確認してください。
>
> 公式の MCP server 実装サンプルは Microsoft 公式リポジトリを参照することを推奨します:
>
> - <https://github.com/microsoft/CopilotStudioSamples/tree/main/extensibility/mcp>
> - サンプル一覧: `search-species-resources-typescript` / `pass-resources-as-inputs` / `dynamic-mcp-routing-typescript` / `order-management-enhanced-tc`
>
> シナリオ C と本パターンを併用する場合は、それぞれ別コンテナ (Hosted agent / MCP server) に分けて Azure Container Apps 等にデプロイし、Copilot Studio から MCP server に直接接続する構成を推奨します。

シナリオ C の Hosted agent コンテナに MCP server endpoint を追加する例 (Python / FastMCP):

```python
# src/mcp_server.py (FastMCP を Hosted agent コンテナに同梱)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("contoso-helpdesk-mcp")

@mcp.tool()
def search_it_policy(query: str) -> str:
    """Contoso 社内 IT 利用規定を検索して該当パッセージを返す。"""
    # ... シナリオ A で作った Vector Store を呼ぶ等の実装 ...
    return "..."

@mcp.tool()
def create_ticket(summary: str, priority: str, category: str) -> dict:
    """IT ヘルプデスク チケットを起票する。"""
    # ... CreateTicket OpenAPI 相当の処理 ...
    return {"ticket_id": "TK-XXXX", "status": "created"}

if __name__ == "__main__":
    # Streamable HTTP transport で起動 (port 8088 / path /mcp)
    mcp.run_streamable_http(host="0.0.0.0", port=8088, path="/mcp")
```

- Dockerfile に MCP 起動コマンドを追加し、Foundry Hosted agent (シナリオ C) と並行ホスト
- 公開 endpoint 例: `https://<aca-or-aci-host>.azurecontainerapps.io/mcp`
- 認証は OAuth 2.0 (Entra ID) を推奨

### 3.3 パターン C: 任意の MCP server を自作

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server>

- Python (FastMCP) / TypeScript (`@modelcontextprotocol/sdk`) / .NET / Go 等の MCP SDK を利用
- Streamable HTTP transport 必須 (SSE は非サポート)
- Azure Container Apps / Functions / App Service / AKS いずれにもホスト可能

### 3.4 共通の前提

| 観点 | 内容 |
|---|---|
| Transport | Streamable HTTP **必須**。SSE は 2025-08 以降サポート対象外 |
| URL | HTTPS 必須 (Microsoft Copilot Studio から公開されている必要あり) |
| Description | MCP server / 各 tool の Description は orchestration の判断材料 — 簡潔・直接・具体的に書く |
| Resource | Microsoft Copilot Studio agent が MCP resource を利用するには、MCP server 側で resource を **tool の output として公開**する必要がある (公式注記) |

---

## 4. Phase 2: Microsoft Copilot Studio に MCP server を接続

公式 (verbatim): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent>

### 4.1 MCP onboarding wizard で接続 (推奨)

1. <https://copilotstudio.microsoft.com> → 対象エージェント → **Tools** タブ
2. **+ Add a tool** → **New tool** → **Model Context Protocol**
3. MCP onboarding wizard で以下を入力:

   | フィールド | 値 |
   |---|---|
   | **Server name** | MCP server の識別名 (例: `Contoso Helpdesk MCP`) |
   | **Server description** | server が提供する機能を簡潔に。**orchestration の選択根拠**になる |
   | **Server URL** | 公開された HTTPS endpoint (例: `https://contoso-helpdesk.azurecontainerapps.io/mcp`) |
   | **Authentication** | None / API key / OAuth 2.0 のいずれか |

4. 認証種別に応じて追加情報を入力:
   - **API key**: Type = Header または Query、param 名を入力
   - **OAuth 2.0 (Dynamic discovery)**: Create を押すだけで自動構成
   - **OAuth 2.0 (Dynamic)**: Authorization URL / Token URL template を入力
   - **OAuth 2.0 (Manual)**: Client ID / Client Secret / Authorization URL / Token URL / Refresh URL / Scopes
5. **Create** を押すと callback URL が表示されるので、必要に応じて Identity Provider 側に登録
6. **Next** → **Create a new connection** → **Add to agent**

### 4.2 既存のプリビルト MCP コネクタを使う

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent>

1. **Tools** タブ → **+ Add a tool**
2. **Model Context Protocol** を選択 → 利用可能な MCP コネクタ一覧から選択
3. **Authorize the connection** で認証情報を入力
4. **Add and configure**

### 4.3 接続後の確認

1. **Tools** タブに MCP server がツールとして表示される
2. クリックして詳細ページを開くと以下が見られる:
   - **Tools** タブ: MCP server が公開する tool の一覧 (name / description)
   - **Resources** タブ: MCP server が公開する resource の一覧
3. **Allow all** トグルで全 tool 有効/無効を一括切り替え可能
4. **Allow all** を OFF にすると、tool ごとに個別 ON/OFF 可能

> ⚠️ 公式注記 (verbatim): 「When you turn off Allow all, any new tools added to the MCP server are turned off by default.」(`Allow all` を OFF にした後、MCP server に新規追加された tool は **デフォルトで OFF**)

### 4.4 (代替) Power Apps でカスタム MCP コネクタを作成

OpenAPI 仕様 YAML を持っている場合は、Power Apps でカスタム コネクタ化して接続することも可能 (公式 Option 2)。

---

## 5. Phase 3: 動作確認

### 5.1 Test pane

1. Microsoft Copilot Studio portal → 対象エージェント → 右上 **Test** をオン
2. MCP server の tool が呼ばれるシナリオを試す
   - 例: 「社内 IT 利用規定で MFA の章を教えて」→ `search_it_policy` ツールが呼ばれる
3. **Track between topics** をオンにして、orchestration がどの tool / resource を選んだかを確認

### 5.2 MCP server 側で呼び出しログ確認

- Azure Container Apps Console / App Service Log Stream / Foundry の Tracing / Application Insights 等で、Microsoft Copilot Studio からの MCP リクエストが届いていることを確認
- リクエストヘッダーに認証トークン (API key / OAuth Bearer) が想定通り含まれているか確認

---

## 6. Microsoft Copilot Studio ↔ MCP server ↔ Microsoft Foundry マッピング

| Microsoft Copilot Studio 概念 | MCP 概念 | Microsoft Foundry での実装例 |
|---|---|---|
| Tool (Tools タブ) | MCP server | Hosted agent コンテナに同梱した FastMCP server |
| Tool の機能 (= 個別 action) | MCP tool | `@mcp.tool()` で定義した Python 関数 |
| Tool の参照データ | MCP resource | tool の output として返す JSON / Markdown 等 |
| Generative orchestration | tool 選択ロジック | (Microsoft Copilot Studio 側で実施。Foundry 側は呼ばれた瞬間に処理) |
| Power Platform Connection | MCP 認証 (None / API key / OAuth 2.0) | Foundry agent の Entra ID + RBAC で OAuth 2.0 を推奨 |
| Power Platform DLP | コネクタ単位の許可/拒否 | (該当なし。MCP server は OAuth scope / API key で粒度制御) |

---

## 7. 既知の制約・注意点

| 観点 | 内容 | 公式リファレンス |
|---|---|---|
| **Transport 制限** | Streamable HTTP のみ。SSE は **2025-08 以降サポート終了** | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent> |
| **Generative orchestration 必須** | MCP tool は orchestration が選ぶ。Classic (Trigger phrase) のみのエージェントでは MCP tool が呼ばれない | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp> |
| **Resource の前提条件** | Microsoft Copilot Studio agent が MCP resource を使うには、MCP server 側で resource を tool の output として公開する必要がある | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent> |
| **DLP** | MCP server への接続は Power Platform コネクタ経由。`Custom connector` 系の DLP ポリシーが適用される | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention> |
| **データ越境** | tool 呼出時のパラメータ (= ユーザー入力) が MCP server ホスト先に流れる。MCP server を Azure 外に置くなら明示同意・契約整備が必要 | — |
| **MCP server 側の責任** | 公式注記 (verbatim): 「When you connect to a non-Microsoft product, including an external MCP server, you're responsible for the tools and resources you access from within Copilot Studio.」 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp> |
| **トラブルシューティング** | 公式に専用ページあり | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-troubleshooting> |

---

## 8. クイック リファレンス: 公式ドキュメント

| トピック | URL |
|---|---|
| Extend agent with MCP (本機能の本家ドキュメント) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp> |
| Add existing MCP server to an agent | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent> |
| Add MCP server tools and resources to an agent | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent> |
| Create a new MCP server | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-create-new-server> |
| MCP troubleshooting | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-troubleshooting> |
| Microsoft Copilot Studio MCP Lab (公式 hands-on) | <https://aka.ms/mcsmcp/lab/blog> |
| MCP 仕様 (Anthropic) | <https://modelcontextprotocol.io> |
| MCP Streamable HTTP 仕様 | <https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http> |
| MCP server リファレンス実装 (Microsoft samples) | <https://github.com/microsoft/CopilotStudioSamples/tree/main/extensibility/mcp/search-species-resources-typescript> |
| Custom connector certification (テナント横断公開) | <https://learn.microsoft.com/en-us/connectors/custom-connectors/submit-certification> |

---

## 9. 他シナリオとの併用パターン

| 併用 | 動作 |
|---|---|
| **F + C** | Microsoft Foundry の Hosted agent コンテナに **MCP server を同梱**して公開し、Microsoft Copilot Studio から接続。1 つのコンテナで「Hosted agent」と「MCP tool 供給」の両方を提供 |
| **F + D** | エージェント本体は Microsoft Foundry agent に委譲 (D)、補助的な検索 / 情報取得は MCP server で接続 (F) |
| **F + E** | Microsoft Copilot Studio の Prompt はモデルだけ Microsoft Foundry の BYOM で差し替え (E)、Tool は MCP 経由で外部接続 (F) → 構成変更を最小化したまま機能拡張 |
| **F + A/B** | Microsoft Foundry 側を Prompt agent / Workflow agent で構成し、その配下の tool 群を MCP server として束ねる構成 |

> 💡 **MCP を活かす設計指針**: tool が増えるたびに Microsoft Copilot Studio 側の Action / Connection を追加するのではなく、**MCP server 側に tool を集約**して 1 接続で複数 tool を扱う形にすると、ガバナンスとメンテナンス性が大きく改善します。

---

## 10. 関連シナリオ G/H/I・補助ドキュメント

| ドキュメント | 何が補強されるか |
|---|---|
| [`../scenario-g-foundry-to-m365/README.md`](../scenario-g-foundry-to-m365/README.md) | Microsoft Foundry agent (シナリオ A〜C) を MCP server として公開し、それを **Microsoft 365 Copilot / Teams から直接呼ぶ** ためのフロント側公開ルート |
| [`../scenario-h-apim-ai-gateway/README.md`](../scenario-h-apim-ai-gateway/README.md) | 既存 MCP server を **APIM 経由で公開** (`expose-existing-mcp-server`) または **既存 REST API を MCP として export** (`export-rest-mcp-server`)。OAuth 認証 / Streamable HTTP の集中管理に最適 |
| [`../scenario-i-evaluation-redteam/README.md`](../scenario-i-evaluation-redteam/README.md) | MCP server を呼び出す Foundry agent 全体を **ToolCallAccuracy + Agent 評価器**で評価。**Indirect attack (XPIA)** が MCP resource 経由で発生しやすいため Safety 評価器が必須 |
| [`../../docs/governance.md`](../../docs/governance.md) | Microsoft Copilot Studio DLP の Business / Non-Business 分類 + MCP server を 3rd party に置く場合の連鎖ブロック対策 |
| [`../../docs/cost-finops.md`](../../docs/cost-finops.md) | MCP server ホスト コスト (Container Apps / Functions) + Copilot Credits (Agent action 5) の月額試算 |
| [`../../docs/evaluation-playbook.md`](../../docs/evaluation-playbook.md) | MCP tool 利用時の **ToolCallAccuracy / IntentResolution / IndirectAttack** の閾値設計 |
