# demo-assets — 内部デモ用素材一式 (7 シナリオ構成)

> ⚠️ **作業中・検証中のドラフトです (確定版ではありません)。本番採用前に公式ドキュメントで最終確認してください。**

Microsoft Copilot Studio ↔ Microsoft Foundry の **移行 / 連携 / ガバナンス** を網羅する 7 つのシナリオを格納しています。

> シナリオは **3 つのレイヤー** で整理しています。
>
> | レイヤー | シナリオ | 何を Microsoft Foundry 側に持っていくか / 被せるか |
> |---|---|---|
> | エージェント本体 (移行) | **A / B / C** | Microsoft Copilot Studio の agent を Microsoft Foundry agent (Prompt / Workflow / Hosted) に置き換える |
> | エージェント間 / モデル / ツール連携 | **D / E / F** | Microsoft Copilot Studio を温存し、Microsoft Foundry の **agent (D)** / **モデル (E)** / **MCP ツール (F)** を呼び出す |
> | 横断ガバナンス / FinOps | **H** | **APIM AI Gateway (H)** を被せて token 制御・semantic cache・MCP expose を一元化 |

## 📘 まず読むべきもの

1. **[`00-create-cs-agent.md`](00-create-cs-agent.md)** — **共通の出発点**: Microsoft Copilot Studio で IT ヘルプデスク エージェントを作成し、pac CLI で YAML 抽出、**Agent Evaluation で品質採点**するまでの完全な手順書 (シナリオ A〜D 共通。E / F も同じエージェントを起点とする)。実 UI スクショ 35 枚 + 評価実行記録付きで検証済
2. 各シナリオの README — Microsoft Foundry 側の受け皿 (A〜F) / 横断ガバナンス (H) ごとの完全手順書
3. シナリオ A〜F + H の概要・比較は本 README の「シナリオ概要」表 (11 列) を参照
4. (本番化を見据える場合) [`../docs/`](../docs/) — Governance / FinOps の横断ドキュメント

## ディレクトリ構成

```
demo-assets/
├── README.md                                  ← このファイル
├── 00-create-cs-agent.md                      ← ★ 共通: Microsoft Copilot Studio でエージェント作成 → pac 抽出
│
├── screenshots/
│   └── copilot-studio-agent/                  ← 00 検証で取得済の Microsoft Copilot Studio 実 UI スクショ (`01-26.png` 26 枚)
│
├── common/                                    ← シナリオ A〜C 共通素材 (Microsoft Foundry agent 本体を作る系)
│   ├── README.md
│   ├── sample-knowledge/
│   │   └── it-policy.md                       ← Contoso 架空 IT 規定 (ファイル検索にそのままアップロード可)
│   ├── tools/
│   │   └── create-ticket.openapi.yaml         ← OpenAPI tool 定義 (チケット起票)
│   └── scripts/
│       └── upload_knowledge.py                ← (任意) Vector Store 作成スクリプト (シナリオ B / C 向け、A は GUI で完結)
│
├── scenario-a-prompt-agent/                   ← 🟢 シナリオ A: Prompt agent (GA / 最短ルート / GUI 完結)
│   ├── README.md
│   ├── requirements.txt                       ← (本シナリオでは未使用) CI 化・コード再現用リファレンス
│   ├── create_prompt_agent.py                 ← (本シナリオでは未使用) Foundry portal の代替として SDK で agent を作る参考実装
│   └── docs/
│       └── security.md                        ← Content Filter / Prompt Shields / XPIA / PII 設定手順
│
├── scenario-b-workflow-agent/                 ← 🟡 シナリオ B: Workflow agent (Preview / Microsoft Copilot Studio にいちばん近い)
│   ├── README.md
│   └── workflows/
│       └── password-reset.workflow.yaml       ← Topic を Workflow YAML に翻訳した例
│
├── scenario-c-hosted-agent/                   ← 🔴 シナリオ C: Hosted agent (Preview / 最大の自由度)
│   ├── README.md
│   ├── Dockerfile
│   ├── agent.yaml                             ← azd deploy 用 Hosted agent マニフェスト
│   ├── azure.yaml                             ← Azure Developer CLI (azd) サービス定義
│   ├── requirements.txt                       ← 本番ランタイム用 (最小化)
│   ├── src/agent.py
│   ├── scripts/
│   │   ├── register_hosted_agent.py           ← ACR イメージを Microsoft Foundry に Hosted agent として登録
│   │   └── requirements-scripts.txt           ← 管理スクリプト専用の依存関係
│   └── tools/create-ticket.openapi.yaml
│
├── scenario-d-cs-plus-foundry/                ← 🟣 シナリオ D: Microsoft Copilot Studio + Microsoft Foundry 併用 (Preview)
│   ├── README.md
│   ├── cs-connection-notes.md
│   └── topic-route-to-foundry.md
│
├── scenario-e-byom-foundry-model/             ← 🔵 シナリオ E: BYOM (GA / モデルだけ差し替え)
│   ├── README.md
│   ├── foundry-model-connection-notes.md
│   └── byom-prompt-instructions.md
│
├── scenario-f-mcp-connection/                 ← 🟠 シナリオ F: MCP server 接続 (GA / 汎用ツール連携)
│   ├── README.md
│   ├── mcp-server-candidates.md
│   └── mcp-onboarding-checklist.md
│
└── scenario-h-apim-ai-gateway/                ← ⚫ シナリオ H: APIM AI Gateway (横断ガバナンス・FinOps)
    └── README.md
```

## シナリオ概要

> 11 列で **SLA / コスト / RBAC / 公開チャネル / Region** まで網羅した比較表。詳細は各シナリオ README を参照。

| シナリオ | ターゲット | レイヤー | 状態 | Microsoft Copilot Studio 互換度 | SLA | コスト概算 | RBAC 最小権限 | 公開チャネル | Region 制約 | 本リポジトリ検証状況 |
|---|---|---|---|---|---|---|---|---|---|---|
| **A** | Microsoft Foundry Prompt agent | エージェント本体 (移行) | ✅ GA | 中 (instructions 集約) | あり (GA) | Token 課金のみ | Foundry User + Storage Blob Data Contributor | Foundry SDK/API | File Search が Italy North / Brazil South で不可 等あり | GUI 完結方針で README リライト済 (Foundry portal 検証はこれから) |
| **B** | Microsoft Foundry Workflow agent | エージェント本体 (移行) | ⚠️ Preview | **高** (Power Fx 互換 + ノード継承) | なし (Preview) | Token 課金 + Workflow Tracing は Preview の課金体系 | Foundry User + Contributor (Workflow 編集に必要) | Foundry SDK/API + Agent Application 経由 (Publish 後) | Workflow Tracing 対応リージョン限定 (`concepts/limits-quotas-regions` 要確認) | (未実施) |
| **C** | Microsoft Foundry Hosted agent | エージェント本体 (移行) | ⚠️ Preview | 低 (コードで再現) | なし (Preview) | Token + Hosted Compute (sandbox 0.25 vCPU / 0.5 GiB 〜 2 vCPU / 4 GiB) + ACR ストレージ | Foundry Project Manager + Contributor + AcrPull (Project Managed Identity) | Responses / Activity / A2A / Invocations の 4 プロトコル、Bot Service 経由で Teams も可 | 18 リージョン限定 (`concepts/hosted-agents`) | (未実施) |
| **D** | Microsoft Copilot Studio + Microsoft Foundry agent 接続 | エージェント間連携 | ⚠️ Preview (接続機能) | **最高** (Microsoft Copilot Studio そのまま) | なし (接続機能は Preview) | Copilot Credits 5 / Agent action + Foundry 側 Token 課金 (二重) | Foundry User + Copilot Studio Maker 権限 | Copilot Studio の全チャネル (Teams / M365 / Web 等) | Copilot Studio リージョン + Foundry リージョン両方の制約 | (未実施) |
| **E** | Microsoft Copilot Studio + Microsoft Foundry モデル (BYOM) | モデル / ツール単位 | ✅ GA (2025-09-15) | **最高** (Microsoft Copilot Studio そのまま) | あり (BYOM 機能は GA) | Foundry 従量課金 + Copilot Credits | Power Platform 環境 Maker + Foundry Reader | Copilot Studio の全チャネル | Fine-tuning は Classic Foundry portal 必須 / Image generation は UI 非対応 | (未実施) |
| **F** | Microsoft Copilot Studio + MCP server (Microsoft Foundry 含む) | モデル / ツール単位 | ✅ GA | **最高** (Microsoft Copilot Studio そのまま) | あり (Copilot Studio の MCP 接続は GA) | MCP server ホスト コスト + Copilot Credits | MCP server 側で個別設計 (OAuth 推奨) + Maker 権限 | Copilot Studio の全チャネル | Streamable HTTP 必須 / MCP Prompts は未対応 / DLP 設定で連鎖ブロック可 | (未実施) |
| **H** | Azure API Management を AI Gateway として被せる | 横断ガバナンス / FinOps | APIM コア ✅ GA / Foundry 統合 ⚠️ Preview | — (上位レイヤー) | あり (APIM GA 部分) | **+$700/月** (Standard v2) + リクエスト課金 | APIM Contributor + Cognitive Services User | A〜F すべての backend を統合 | Streamable HTTP 必須 (MCP) / Standard v2 以上推奨 | (未実施) |

> 📝 **共通の出発点 (`00-create-cs-agent.md`) の検証状況**: Microsoft Copilot Studio で `IT-Helpdesk-Sample` を作成し、pac CLI で YAML 抽出、**Agent Evaluation で品質採点** (10 件 / 全般的な品質 / スコア **70%**) まで **Web UI で全工程を検証済 (実 UI スクショ 35 枚 [`screenshots/copilot-studio-agent/`](screenshots/copilot-studio-agent/) を添付)**。シナリオ A〜D / F はここを起点に進めます。

各シナリオの README には以下が完備されています:
- 前提条件 (Microsoft Copilot Studio / Microsoft Foundry / Azure / Microsoft 365 各側のライセンス・RBAC・SDK バージョン)
- (A〜F) Phase 1〜2: Microsoft Copilot Studio でエージェント作成 → pac 抽出 (→ `00-create-cs-agent.md` 参照)
- Phase 3 以降: Microsoft Foundry / Azure / 評価環境の準備・登録・動作確認
- Microsoft Copilot Studio → Microsoft Foundry のマッピング表 (A〜D)
- 既知の制約 / 公式ドキュメント リファレンス
- **関連シナリオ H・補助ドキュメント** への相互リンク (各 README 末尾)

## 共通の前提

シナリオ A〜D / F はいずれも、まず **`00-create-cs-agent.md`** に従って Microsoft Copilot Studio に `IT-Helpdesk-Sample` エージェントを構築します (シナリオ E は Microsoft Copilot Studio 側のエージェントがある前提で開始)。

その上で、Microsoft Foundry agent を作る系 (シナリオ A〜C) では `it-policy.md` を **ファイル検索 (File Search)** で利用できる状態にします。アップロード手段はシナリオごとに推奨パスが異なります:

- **シナリオ A (GUI 完結)**: Foundry portal のプレイグラウンドで **ツール → 追加 → ファイル検索 → ファイルの参照 → アタッチ** するだけで完結 (Python 不要、`vector_store_id` の手動管理も不要)。詳細は [`scenario-a-prompt-agent/README.md`](scenario-a-prompt-agent/README.md) §4 を参照。
- **シナリオ B / C (SDK 主体)**: `common/scripts/upload_knowledge.py` で Vector Store を作成し、`vector_store_id` を環境変数に設定して進めます。

```powershell
# (シナリオ B / C 向け) repo root から実行
cd .\demo-assets
pip install azure-ai-projects azure-identity
$env:FOUNDRY_PROJECT_ENDPOINT = "<Microsoft Foundry プロジェクト endpoint>"
python common\scripts\upload_knowledge.py common\sample-knowledge\it-policy.md
# 出力された vector_store_id を控える
$env:KNOWLEDGE_VECTOR_STORE_ID = "<vs_xxxxxxxx>"
```

> シナリオ E / F は Microsoft Foundry 側に agent を作る必要が無い (E はモデルだけ、F は MCP server だけ) ため、上記 Vector Store 作成手順は不要です。シナリオ **H** (APIM) は A〜D を「被せる対象」として参照します。

## サンプル PDF を使いたい場合

`common/sample-knowledge/it-policy.md` を PDF 化したいときは:

```powershell
# Word で開いて「名前を付けて保存 → PDF」、または:
pandoc demo-assets\common\sample-knowledge\it-policy.md -o demo-assets\common\sample-knowledge\it-policy.pdf
```

Microsoft Foundry の File Search は `.md` を直接サポートするため、デモでは PDF 化せずそのままアップロードで問題ありません。

## 共通: Responsible AI / Content Safety / DLP / Preview terms

シナリオ A〜F + H すべてで以下の Responsible AI / セキュリティ / コンプライアンス観点を共通で考慮してください。デモ実施前に各 README §動作確認 の前に必ず一読することを推奨します。**横断的なチェックリスト** は [`../docs/governance.md`](../docs/governance.md) に集約しています。

### Microsoft Foundry 側 (シナリオ A〜D の Foundry agent / Hosted agent、シナリオ E のモデル、シナリオ F の MCP server)

| 観点 | 公式リファレンス |
|---|---|
| RAI 全体像 (Discover / Protect / Govern) | [Microsoft Foundry における責任ある AI の概要](https://learn.microsoft.com/ja-jp/azure/ai-foundry/responsible-use-of-ai-overview) |
| Content filters (Azure AI Content Safety 連携) | [Microsoft Foundry のコンテンツ フィルタリング](https://learn.microsoft.com/ja-jp/azure/ai-foundry/concepts/content-filtering) |
| Guardrails & Controls | [Azure OpenAI の責任ある AI](https://learn.microsoft.com/ja-jp/azure/ai-foundry/responsible-ai/openai/overview) |
| Tracing / Monitoring (AgentOps) | [エージェント トレーシングの概念](https://learn.microsoft.com/ja-jp/azure/ai-foundry/observability/concepts/trace-agent-concept) |
| Preview supplemental terms | [Microsoft Azure Preview の追加使用条件](https://azure.microsoft.com/support/legal/preview-supplemental-terms/) |

### Microsoft Copilot Studio 側 (シナリオ D / E / F、および既存 Microsoft Copilot Studio エージェント)

| 観点 | 公式リファレンス |
|---|---|
| Security and governance 全体 | [Microsoft Copilot Studio のセキュリティとガバナンス](https://learn.microsoft.com/ja-jp/microsoft-copilot-studio/security-and-governance) |
| DLP (Data Loss Prevention) ポリシー | [Power Platform のデータ損失防止 (DLP) ポリシー](https://learn.microsoft.com/ja-jp/power-platform/admin/wp-data-loss-prevention) |
| Generative answers の moderation / jailbreak / prompt injection 対策 | [生成型回答 (Generative answers) の概要](https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers) |
| BYOM (シナリオ E) | [Prompts で独自モデル (BYOM) を使う](https://learn.microsoft.com/ja-jp/microsoft-copilot-studio/bring-your-own-model-prompts) |
| MCP 連携 (シナリオ F) | [MCP でアクションを拡張する](https://learn.microsoft.com/ja-jp/microsoft-copilot-studio/agent-extend-action-mcp) |

### Azure API Management 側 (シナリオ H)

| 観点 | 公式リファレンス |
|---|---|
| AI Gateway 機能一覧 | [API Management の AI Gateway 機能](https://learn.microsoft.com/ja-jp/azure/api-management/genai-gateway-capabilities) |
| Foundry portal からの APIM 連携 | [Foundry portal から API Management AI Gateway を有効化する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/configuration/enable-ai-api-management-gateway-portal) |
| MCP server を APIM 経由で公開 | [既存の MCP server を API Management 経由で公開する](https://learn.microsoft.com/ja-jp/azure/api-management/expose-existing-mcp-server) |

### 共通の運用ガイドライン (デモ時の最低ライン)

- ユーザー入力にパスワード / MFA コード / PIN / 個人特定情報 (PII) を要求しない (各 Instructions / Topic で禁止文を明記)
- 緊急インシデント (情報漏えい・進行中の攻撃) は agent では対応せず、CSIRT 等の人手プロセスへエスカレーション
- Microsoft Foundry agent と Microsoft Copilot Studio agent の **両方を使うシナリオ D / E / F** では、Microsoft Copilot Studio DLP と Microsoft Foundry RBAC / VNet を別々に設計・運用 (1 箇所に統合する公式機能は現時点なし。**シナリオ H で APIM に集約する** 設計が現時点の標準)
- 会話履歴の保存有無 (Responses API の `store` 等) は法令・社内規程に合わせて明示的に設定
- Preview / Early Access Preview 機能 (シナリオ B / C / D の一部) は SLA 対象外。本番運用前に Preview supplemental terms を必ず確認
- MCP server (シナリオ F) を社外サービスに繋ぐ場合、公式注記 (verbatim) 「When you connect to a non-Microsoft product, including an external MCP server, you're responsible for the tools and resources you access from within Copilot Studio.」 を関係者に周知

## シナリオ選定ガイド (フローチャート)

```
Q1. Microsoft Copilot Studio を残したいか、Microsoft Foundry に移行したいか?
   ├─ 移行したい                       → Q2
   └─ Microsoft Copilot Studio は残したい → Q3

Q2 (移行ルート). 必要なフローの確定性は?
   ├─ LLM の判断に任せて良い (簡易)         → シナリオ A (Prompt agent, GA)
   ├─ Topic / 分岐をできるだけそのまま残したい → シナリオ B (Workflow agent, Preview)
   └─ コードでフルカスタム / 既存資産活用     → シナリオ C (Hosted agent, Preview)

Q3 (温存ルート). Microsoft Foundry の何を呼びたいか?
   ├─ エージェント全体 (Prompt/Workflow/Hosted agent) → シナリオ D (Microsoft Copilot Studio + Microsoft Foundry agent, Preview)
   ├─ LLM モデルだけ (BYOM)                          → シナリオ E (BYOM, GA)
   └─ 任意の tool / 外部サービス (MCP)                → シナリオ F (MCP, GA)

Q4 (上位レイヤー / 本番化). A〜F で構築した後、本番ローンチ前に被せるか?
   └─ Token 制御 / Semantic cache / MCP expose を一元化したい         → シナリオ H (APIM AI Gateway)
```

> 💡 **段階的移行 + 本番化の推奨パス**: いきなり A〜C で全面移行するのではなく、まず **E (モデル品質を 1 Prompt で検証)** → **D (1 機能だけ agent 委譲で検証)** → 必要に応じ **A/B/C で全面移行** → 公開規模に応じて **H (ガバナンス・FinOps)** を被せる、という順で進めると低リスクです。F は D / E と並行して進められます。

## 横断補助ドキュメント (`../docs/`)

シナリオを跨いで参照するガバナンス / FinOps の補助ドキュメントを集約しています。

| ドキュメント | 内容 | 主に参照するシナリオ |
|---|---|---|
| [`../docs/governance.md`](../docs/governance.md) | DLP / RBAC (GUID 指定) / Entra Agent Identity / Content Safety / Preview terms の横断チェックリスト | A〜F + H すべて |
| [`../docs/cost-finops.md`](../docs/cost-finops.md) | Foundry token / Copilot Credits / 補助リソース / APIM token metric / シナリオ別月額試算 / KQL レポート | A〜F + H すべて (特に H) |

## スクリーンショット運用ルール

- 配置先: [`screenshots/copilot-studio-agent/`](screenshots/copilot-studio-agent/) — `00-create-cs-agent.md` 検証時に取得した Microsoft Copilot Studio の実 UI スクショ (`01-home-screen.png` 〜 `35-evaluation-failure-detail.png` の 35 枚。01〜26 = エージェント作成 / 27〜35 = §6.4 評価機能)
- ファイル名: `{連番}-{内容}.png` (例: `07-add-knowledge-modal.png`)。00 と同じ規則で追加してください
- 解像度: 1300〜1600 px 横幅推奨
- マスキング: テナント名 / ユーザー名 / サブスクリプション ID / 個人特定情報は必ずマスキング
- シナリオ A〜F + H の実 UI を新たに撮影する場合は、シナリオ別サブディレクトリ (例: `screenshots/scenario-a/`) を作成して同じ規則で配置してください
