# Screenshots — 撮影 / 取得チェックリスト

このフォルダにはデモ進行中・検証中に取得したスクリーンショット (`.png`) を格納します。

> ⚠️ 取得時はテナント名・ユーザー名・サブスクリプション ID 等の機密情報をマスキングすること。

## 命名規則

- ファイル名: `{Phase}-{連番}-{内容}.png` (例: `A-02-create-agent.png`)
- 解像度: 横 1300〜1600 px 推奨
- Foundry Portal は `wsid` クエリにサブスクリプション ID が入るためマスキング必須

## ディレクトリ構成

```
screenshots/
├── README.md                      ← 本ファイル
└── scenario-a/                    ← シナリオ A 関連のスクリーンショット (`generate_*.py` で生成)
    ├── A-LOG-01-phase-summary.png        ← Phase 3〜5 ローカル実行ログ サマリ
    ├── A-LOG-02-test-session.png         ← Responses API 回帰テスト セッション
    ├── A-CODE-01-openapi-yaml.png        ← create-ticket.openapi.yaml の全体
    ├── A-CODE-02-prompt-agent-script.png ← create_prompt_agent.py の main 関数抜粋
    └── A-CODE-03-it-policy-md.png        ← it-policy.md §2.3 抜粋
```

各シナリオ (B / C / D / E / F / **G / H / I**) のスクリーンショットを追加する場合は、同様に `scenario-b/`, `scenario-c/`, `scenario-d/`, `scenario-e/`, `scenario-f/`, `scenario-g/`, `scenario-h/`, `scenario-i/` を切ってください。

> 💡 シナリオ E (BYOM) は Microsoft Copilot Studio 側の Prompt ツール画面と Microsoft Foundry の Models + Endpoints 画面が、シナリオ F (MCP) は Microsoft Copilot Studio 側の Tools タブの MCP onboarding wizard と接続後の Tools / Resources 一覧が主要な撮影ポイントになります。
>
> シナリオ G は Foundry portal の **Publish → Microsoft 365 Copilot / Teams** ダイアログと、Azure portal で自動生成された **`Microsoft.BotService`** リソース、シナリオ H は **APIM portal の AI Gateway ポリシー編集画面 + Application Insights の `genai` メトリック**、シナリオ I は **Foundry portal の Evaluations / Red teaming タブ + GitHub Actions のゲート ログ** が主要な撮影ポイントになります。

## 再生成スクリプト (シナリオ A)

[`scenario-a-prompt-agent`](../scenario-a-prompt-agent/) には README 用のスクリーンショットを再生成するスクリプトが含まれています。

| スクリプト | 取得内容 | 認証 |
|---|---|---|
| `generate_log_screenshots.py` | Phase 3〜5 実行ログのターミナル風画像 | 不要 |
| `generate_code_screenshots.py` | 同梱コード ファイルのシンタックス ハイライト画像 | 不要 |

実行方法:

```powershell
cd .\demo-assets\scenario-a-prompt-agent

# Playwright Chromium バイナリ (初回のみ)
python -m playwright install chromium

# 2 種類を順に実行
python generate_log_screenshots.py
python generate_code_screenshots.py
```

## ポータル スクリーンショット撮影チェックリスト (任意、手動で取得)

`ai.azure.com` / `copilotstudio.microsoft.com` は MFA サインインが必須のため、自動取得スクリプトの対象外です。以下は手動撮影時の推奨カットです。

### Microsoft Copilot Studio 側 (シナリオ A〜D / F 共通。E は既存エージェントを前提のためスキップ可)

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| CS-01 | `cs-01-studio-home.png` | Microsoft Copilot Studio ホーム | 環境セレクタが見える状態 |
| CS-02 | `cs-02-create-agent.png` | 「+ 新しいエージェント」ダイアログ | 「スキップして構成」が見える |
| CS-03 | `cs-03-agent-overview.png` | エージェント作成完了直後 | エージェント名・説明 |
| CS-04 | `cs-04-knowledge-add.png` | ナレッジ追加直後 | ファイル名と「Ready」状態 |
| CS-05 | `cs-05-topic-yaml.png` | トピックのコード ビュー | YAML 表示 |
| CS-06 | `cs-06-test-pane.png` | テスト ペインで質問→回答 | 引用 + Action 呼出 |
| CS-07 | `cs-07-pac-extract.png` | `pac copilot extract-template` 実行結果 | YAML ファイル生成 (シナリオ A〜D で必要、E / F は任意) |

### Microsoft Foundry 側 (シナリオ A 対応)

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| F-A-01 | `f-a-01-project-overview.png` | Foundry project の Overview | endpoint URL |
| F-A-02 | `f-a-02-model-deploy.png` | Models + Endpoints | gpt-4.1-mini / gpt-5-mini |
| F-A-03 | `f-a-03-rbac.png` | RBAC 画面 | Foundry User ロール |
| F-A-04 | `f-a-04-vector-store.png` | Data → Vector stores | `it-policy-vs` (file_counts=1) |
| F-A-05 | `f-a-05-agent-list.png` | Agents 一覧 | `helpdesk-prompt:1` が見える |
| F-A-06 | `f-a-06-agent-detail.png` | Agent 詳細 | Instructions + Tools (FileSearch + OpenAPI) |
| F-A-07 | `f-a-07-playground.png` | Playground でテスト送信 | 引用 + Tool 呼出のトレース |
| F-A-08 | `f-a-08-trace.png` | Trace ペイン | OpenAPI 呼び出しチェーン |
