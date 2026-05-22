# Screenshots — 撮影チェックリスト

デモ進行中に取得すべきスクリーンショット一覧。すべて取得すれば資料として完結します。

> ⚠️ 取得時はテナント名・ユーザー名・サブスクリプション ID 等の機密情報をマスキングすること。

## Phase A: Copilot Studio

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| A-01 | `A-01-studio-home.png` | Copilot Studio ホーム | 環境セレクタが見える状態 |
| A-02 | `A-02-create-agent.png` | 「+ 新しいエージェント」ダイアログ | 「スキップして構成」が見える |
| A-03 | `A-03-agent-overview.png` | エージェント作成完了直後の概要画面 | エージェント名・説明 |
| A-04 | `A-04-knowledge-add.png` | ナレッジ タブで PDF/MD を追加した直後 | ファイル名と「処理中/利用可能」状態 |
| A-05 | `A-05-action-config.png` | アクション (CreateTicket) 設定画面 | エンドポイント / 入力スキーマ |
| A-06 | `A-06-topic-yaml.png` | トピックのコード ビュー (YAML) | YAML が見えている状態 |
| A-07 | `A-07-test-pane.png` | テスト ペインで質問→回答 | 引用と Action 呼出が見える |

## Phase B: Foundry リソース基盤

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| B-01 | `B-01-bicep-deploy.png` | `az deployment group create` 完了画面 | リソース ID / Endpoint URL |
| B-02 | `B-02-foundry-portal.png` | ai.azure.com で proj-helpdesk を開いた直後 | リソース ツリー |
| B-03 | `B-03-model-deploy.png` | gpt-4.1-mini デプロイ完了 | デプロイ ステータス |
| B-04 | `B-04-playground-baseline.png` | Playground でモデルにテキスト送信 | レスポンス確認 |
| B-05 | `B-05-rbac.png` | Foundry User ロール付与画面 | ロール名 / GUID |

## Phase C: Knowledge & Action

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| C-01 | `C-01-vector-store.png` | `upload_knowledge.py` 実行完了 | vector_store_id 出力 |
| C-02 | `C-02-openapi-yaml.png` | OpenAPI YAML を VS Code で開いた状態 | 構造が見える |

## Phase D: Hosted Agent 構築

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| D-01 | `D-01-azd-init.png` | `azd init` 直後のフォルダ構成 | tree 表示 |
| D-02 | `D-02-docker-build.png` | `docker build` 完了 | image ID / size |
| D-03 | `D-03-acr-push.png` | `docker push` 完了 | リポジトリにイメージが見える |
| D-04 | `D-04-register-output.png` | `register_hosted_agent.py` 実行結果 | agent_version_id |
| D-05 | `D-05-foundry-agent-list.png` | Foundry ポータルで helpdesk-hosted が表示 | エージェント一覧 |
| D-06 | `D-06-acrpull-rbac.png` | Hosted agent MI に AcrPull 付与 | ロール割り当て |

## Phase E: テスト & 評価

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| E-01 | `E-01-playground-foundry.png` | Foundry Playground で「VPN がつながりません」 | ナレッジ引用 + Tool 呼出 |
| E-02 | `E-02-trace.png` | Agent Tracing 画面 | ツール呼び出しチェーン |
| E-03 | `E-03-evaluation.png` | Evaluation Hub のメトリクス | groundedness / relevance |

## Phase F: ハイブリッド (任意)

| # | ファイル名 | 撮影タイミング | ポイント |
|---|---|---|---|
| F-01 | `F-01-add-foundry-agent.png` | Copilot Studio 「+ エージェントの追加 → Microsoft Foundry のエージェント」 | Preview バッジ |
| F-02 | `F-02-hybrid-test.png` | Copilot Studio テスト ペインから Foundry agent 呼出 | 応答が返る |

## 比較スライド用 (デモ後に追加)

| # | ファイル名 | 用途 |
|---|---|---|
| X-01 | `X-01-side-by-side.png` | Copilot Studio Topic YAML と Foundry Workflow YAML の並列表示 |
| X-02 | `X-02-feature-matrix.png` | 機能マッピング表のスクショ (移行レポートから) |
