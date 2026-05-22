# シナリオ F 用: MCP server 候補と選定指針

Microsoft Copilot Studio に MCP server を接続する際の代表的な候補と、`IT-Helpdesk-Sample` エージェントのデモ目的での選定指針です。

## 1. 既存 MCP server (調達不要・即繋ぎ可)

| MCP server | 提供元 | 主な用途 | 認証 | 備考 |
|---|---|---|---|---|
| Microsoft Learn Docs MCP | Microsoft 公式 | Microsoft Learn のドキュメント検索 / 取得 | OAuth 2.0 (Dynamic Discovery) | デモ向け推奨。公式 lab: <https://aka.ms/mcsmcp/lab/blog> |
| Azure AI Search MCP (コミュニティ) | OSS / Power Platform connector ギャラリー | Azure AI Search の index 検索 / 管理 | API key / OAuth 2.0 | 社内 Knowledge を index 化していれば最短 |
| GitHub MCP | GitHub | リポジトリ / Issue / PR 検索 | OAuth 2.0 (Manual) | GitHub App 連携 |
| 各社 DB MCP (Postgres / MySQL / Cosmos DB 等) | OSS / 各ベンダ | DB クエリ実行 | API key / mTLS | 機密データの場合は ReadOnly ロール推奨 |

## 2. 自作 MCP server (Microsoft Foundry / Azure 上にホスト)

| ホスト先 | 工数目安 | 認証推奨 | 備考 |
|---|---|---|---|
| Microsoft Foundry Hosted agent コンテナ (シナリオ C) | 1〜3 人日 | Entra ID (OAuth 2.0 Manual) | 既存 Hosted agent のサイドカー的に同梱可能 |
| Azure Container Apps | 0.5〜1 人日 | Entra ID | スケール 0 対応・最低コスト |
| Azure Functions (HTTP trigger) | 0.5〜1 人日 | Function key / Entra ID | コールドスタート許容なら最速 |
| Azure App Service / AKS | 1〜3 人日 | Entra ID | 既存ホスティングがある場合 |

## 3. `IT-Helpdesk-Sample` 向けの最小デモ構成

```
Microsoft Copilot Studio: IT-Helpdesk-Sample
  └─ Tool (MCP): contoso-helpdesk-mcp
        ├─ search_it_policy(query: str) → str    # Vector Store 検索 (シナリオ A の vs を流用)
        └─ create_ticket(summary, priority, category) → {ticket_id, status}
```

- ホスト先: Azure Container Apps (検証用) または Foundry Hosted agent コンテナ (シナリオ C と統合)
- 言語: Python (FastMCP) を推奨。Microsoft Foundry SDK (`azure-ai-projects`) と相性が良い
- Transport: Streamable HTTP (`POST /mcp`)
- 認証: 検証段階は API key (Header)、本番想定は OAuth 2.0 (Entra ID Manual)

## 4. 選定フロー

```
Q1. 接続したい機能が既に MCP server として公開されている?
   ├─ Yes → §1 の既存 MCP server を Microsoft Copilot Studio に接続するだけ (Phase 1 不要、Phase 2 から開始)
   └─ No  ↓
Q2. 既に Microsoft Foundry Hosted agent (シナリオ C) を運用しているか?
   ├─ Yes → そのコンテナに MCP server を同梱 (FastMCP 等) → Phase 1 §3.2
   └─ No  ↓
Q3. 既存の Azure リソース (Container Apps / Functions / App Service) があるか?
   ├─ Yes → そこに MCP server をホスト → Phase 1 §3.3
   └─ No  → Azure Container Apps を新規作成 (スケール 0 対応・最低コスト)
```

## 5. 接続情報の控え

各 MCP server について、以下を控えてから Microsoft Copilot Studio の MCP onboarding wizard に入力してください:

| 項目 | 値 |
|---|---|
| Server name | |
| Server description | (orchestration の選択根拠になる。簡潔・具体的に) |
| Server URL (HTTPS) | |
| Transport | Streamable HTTP (固定) |
| Authentication type | None / API key (Header/Query) / OAuth 2.0 (Dynamic Discovery / Dynamic / Manual) |
| API key (該当時) | param 名 + 値 |
| OAuth Client ID / Secret (Manual 時) | |
| Authorization URL (OAuth Dynamic/Manual 時) | |
| Token URL template (OAuth Dynamic/Manual 時) | |
| Refresh URL (OAuth Manual 時) | |
| Scopes (OAuth Manual 時) | |
| Callback URL (Wizard が表示) | Identity Provider 側に登録 |
| 公開 tool 一覧 | (orchestration が呼ぶ可能性のあるもの) |
| 公開 resource 一覧 | (tool の output として返るもののみが利用可能) |
