# demo-assets — 内部デモ用素材一式 (4 シナリオ構成)

Copilot Studio → Foundry 移行デモの 4 シナリオに対応した素材を格納しています。

## 📘 まず読むべきもの

1. **[`00-create-cs-agent.md`](00-create-cs-agent.md)** — **共通の出発点**: Copilot Studio で IT ヘルプデスク エージェントを作成し、pac CLI で YAML 抽出するまでの完全な手順書 (4 シナリオ共通)
2. 各シナリオの README — Foundry 側の受け皿 (A〜D) ごとの完全手順書
3. シナリオ A〜D の概要・比較は本 README の「シナリオ概要」表を参照

## ディレクトリ構成

```
demo-assets/
├── README.md                                  ← このファイル
├── 00-create-cs-agent.md                      ← ★ 共通: Copilot Studio でエージェント作成 → pac 抽出
│
├── screenshots/                               ← デモ進行中に取得するスクショ置き場
│   └── README.md                              ← 撮影チェックリスト
│
├── common/                                    ← 3 シナリオ共通素材
│   ├── sample-knowledge/
│   │   └── it-policy.md                       ← Contoso 架空 IT 規定 (File Search にそのままアップロード可)
│   ├── tools/
│   │   └── create-ticket.openapi.yaml         ← OpenAPI tool 定義 (チケット起票)
│   └── scripts/
│       └── upload_knowledge.py                ← Vector Store 作成 (3 シナリオ共通)
│
├── scenario-a-prompt-agent/                   ← 🟢 シナリオ A: Prompt agent (GA / 最短ルート)
│   ├── README.md
│   ├── requirements.txt
│   └── create_prompt_agent.py                 ← instructions + tools で 1 体作成
│
├── scenario-b-workflow-agent/                 ← 🟡 シナリオ B: Workflow agent (Preview / Copilot Studio にいちばん近い)
│   ├── README.md
│   └── workflows/
│       └── password-reset.workflow.yaml       ← Topic を Workflow YAML に翻訳した例
│
├── scenario-c-hosted-agent/                   ← 🔴 シナリオ C: Hosted agent (Preview / 最大の自由度)
│   ├── README.md
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── src/
│   │   └── agent.py                           ← Hosted Agent 本体 (Python + Agent Framework)
│   ├── scripts/
│   │   └── register_hosted_agent.py           ← Foundry に Hosted Agent 登録
│   └── tools/
│       └── create-ticket.openapi.yaml         ← common/ のコピー (Docker ビルド コンテキスト用)
│
└── scenario-d-cs-plus-foundry/                ← 🟣 シナリオ D: Copilot Studio + Foundry 併用 (Preview / 既存 Copilot Studio 温存)
    ├── README.md                              ← 接続手順 + 注意点
    ├── cs-connection-notes.md                 ← Foundry 側情報を控えるテンプレ
    └── topic-route-to-foundry.md              ← Copilot Studio ルーティング設計サンプル
```

## シナリオ概要

| シナリオ | ターゲット | 状態 | Copilot Studio 互換度 | 工数目安 | 本リポジトリ検証状況 |
|---|---|---|---|---|---|
| **A** | Prompt agent | ✅ GA | 中 (instructions 集約) | 0.5〜1 人日 | ✅ ローカル検証済み (2026-05-22): `scenario-a-prompt-agent/run-log.md` 参照 |
| **B** | Workflow agent | ⚠️ Preview | **高** (Power Fx 互換 + ノード継承) | 1〜3 人日 | (未実施) |
| **C** | Hosted agent | ⚠️ Preview | 低 (コードで再現) | 3〜10 人日 | (未実施) |
| **D** | Copilot Studio + Foundry 併用 | ⚠️ Preview (接続機能) | **最高** (Copilot Studio そのまま) | 0.5 人日〜 | (未実施) |

各シナリオの README には以下が完備されています:
- 前提条件 (Copilot Studio / Foundry 両側のライセンス・RBAC・SDK バージョン)
- Phase 1〜2: Copilot Studio でエージェント作成 → pac 抽出 (→ `00-create-cs-agent.md` 参照)
- Phase 3 以降: Foundry 受け側の準備・登録・動作確認
- Copilot Studio → Foundry のマッピング表
- 既知の制約 / 公式ドキュメント リファレンス

## 共通の前提

4 シナリオはいずれも、まず **`00-create-cs-agent.md`** に従って Copilot Studio に `IT-Helpdesk-Sample` エージェントを構築します。
その上で Foundry 側 (シナリオ A〜C) では **`common/scripts/upload_knowledge.py`** で `it-policy.md` を Vector Store に登録し、得られた `vector_store_id` を環境変数に設定する手順で進めます。

```powershell
# repo root から実行
cd .\demo-assets
pip install azure-ai-projects azure-identity
$env:FOUNDRY_PROJECT_ENDPOINT = "<Foundry プロジェクト endpoint>"
python common\scripts\upload_knowledge.py common\sample-knowledge\it-policy.md
# 出力された vector_store_id を控える
$env:KNOWLEDGE_VECTOR_STORE_ID = "<vs_xxxxxxxx>"
```

## サンプル PDF を使いたい場合

`common/sample-knowledge/it-policy.md` を PDF 化したいときは:

```powershell
# Word で開いて「名前を付けて保存 → PDF」、または:
pandoc demo-assets\common\sample-knowledge\it-policy.md -o demo-assets\common\sample-knowledge\it-policy.pdf
```

Foundry の File Search は `.md` を直接サポートするため、デモでは PDF 化せずそのままアップロードで問題ありません。

## 共通: Responsible AI / Content Safety / DLP / Preview terms

4 シナリオすべてで以下の Responsible AI / セキュリティ / コンプライアンス観点を共通で考慮してください。デモ実施前に各 README §動作確認 の前に必ず一読することを推奨します。

### Foundry 側 (シナリオ A〜D の Foundry agent / Hosted agent)

| 観点 | 公式リファレンス |
|---|---|
| RAI 全体像 (Discover / Protect / Govern) | <https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-use-of-ai-overview> |
| Content filters (Azure AI Content Safety 連携) | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/content-filtering> |
| Guardrails & Controls | <https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/overview> |
| Tracing / Monitoring (AgentOps) | <https://learn.microsoft.com/en-us/azure/ai-foundry/observability/concepts/trace-agent-concept> |
| Preview supplemental terms | <https://azure.microsoft.com/support/legal/preview-supplemental-terms/> |

### Copilot Studio 側 (シナリオ D / 既存 Copilot Studio エージェント)

| 観点 | 公式リファレンス |
|---|---|
| Security and governance 全体 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance> |
| DLP (Data Loss Prevention) ポリシー | <https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention> |
| Generative answers の moderation / jailbreak / prompt injection 対策 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers> |

### 共通の運用ガイドライン (デモ時の最低ライン)

- ユーザー入力にパスワード / MFA コード / PIN / 個人特定情報 (PII) を要求しない (各 Instructions / Topic で禁止文を明記)
- 緊急インシデント (情報漏えい・進行中の攻撃) は agent では対応せず、CSIRT 等の人手プロセスへエスカレーション
- Foundry agent と Copilot Studio agent の **両方を使うシナリオ D** では、Copilot Studio DLP と Foundry RBAC / VNet を別々に設計・運用 (1 箇所に統合する公式機能は現時点なし)
- 会話履歴の保存有無 (Responses API の `store` 等) は法令・社内規程に合わせて明示的に設定
- Preview 機能 (シナリオ B / C / D) は SLA 対象外。本番運用前に Preview supplemental terms を必ず確認

## スクショ運用ルール

- ファイル名: `{Phase}-{連番}-{内容}.png` (例: `A-02-create-agent.png`)
- 解像度: 1300〜1600 px 横幅推奨
- マスキング: テナント名 / ユーザー名 / サブスクリプション ID は必ずマスキング
- 詳細は `screenshots/README.md`

シナリオ A では Playwright を使って **認証不要なスクリーンショット (Microsoft Learn 参照、実行ログ、コード抜粋)** を自動生成するスクリプトを同梱しています。詳細は [`scenario-a-prompt-agent/README.md §7.2 / §11`](scenario-a-prompt-agent/README.md) と [`screenshots/README.md`](screenshots/README.md) を参照してください。
