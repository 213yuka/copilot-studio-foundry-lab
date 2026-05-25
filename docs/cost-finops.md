# 横断 FinOps: Microsoft Foundry token / Microsoft Copilot Studio Credits / APIM token metric

> ⚠️ **作業中・検証中のドラフトです (確定版ではありません)。本番採用前に公式ドキュメントで最終確認してください。**

> **目的**: シナリオ A〜F + H で発生する **AI 関連コストを 1 ファイルで俯瞰** し、見積・予算アラート・最適化アクションをまとめる。
>
> **対象読者**: アーキテクト / 営業エンジニア / FinOps 担当 / プロジェクト マネージャー。
>
> **更新方針**: 価格は 2026 年 5 月時点の **list price ベース** (一次資料は Microsoft 公式の価格ページ)。商用契約では EA / MCA / CSP 等の割引が別途適用されるため、社内見積では契約済単価で再計算すること。

---

## 0. 目次

1. [課金体系のレイヤー整理](#1-課金体系のレイヤー整理)
2. [Microsoft Foundry の課金 (Token + 補助リソース)](#2-microsoft-foundry-の課金-token--補助リソース)
3. [Microsoft Copilot Studio Credits](#3-microsoft-copilot-studio-credits)
4. [シナリオ別コスト試算](#4-シナリオ別コスト試算)
5. [APIM `<llm-emit-token-metric>` による可視化](#5-apim-llm-emit-token-metric-による可視化)
6. [Foundry Observability の token metric](#6-foundry-observability-の-token-metric)
7. [予算アラート / 削減アクション](#7-予算アラート--削減アクション)
8. [ライセンス比較表 (Standalone / Teams plan / D365 Customer Service)](#8-ライセンス比較表)

---

## 1. 課金体系のレイヤー整理

```
┌─────────────────────────────────────────────────────────────────┐
│ レイヤー 1: ユーザー向けライセンス                                  │
│   ・Microsoft 365 Copilot ($30/user/month)                       │
│   ・Microsoft Copilot Studio Standalone ($200/tenant/month +     │
│     Credits パック)                                               │
│   ・Dynamics 365 Customer Service                                │
├─────────────────────────────────────────────────────────────────┤
│ レイヤー 2: メッセージ / アクション課金 (Copilot Credits)          │
│   ・Generative answer: 1〜2 Credits / 質問                       │
│   ・Agent action (tool 呼出): 5 Credits / 起動                   │
│   ・Autonomous trigger: 25〜50 Credits / イベント                │
├─────────────────────────────────────────────────────────────────┤
│ レイヤー 3: Foundry トークン課金 (input / output 別)              │
│   ・gpt-4.1-mini: ~$0.40 / 1M input, ~$1.60 / 1M output         │
│   ・gpt-5-mini:   ~$1.25 / 1M input, ~$5.00 / 1M output         │
│   ・gpt-4o:       ~$2.50 / 1M input, ~$10.00 / 1M output        │
├─────────────────────────────────────────────────────────────────┤
│ レイヤー 4: 補助リソース                                          │
│   ・Vector Store (File Search): $0.10 / GB / 日                  │
│   ・Hosted Compute: 0.25 vCPU / 0.5 GiB ~ 2 vCPU / 4 GiB         │
│   ・Application Insights: ingestion 単価                          │
│   ・Azure AI Search (semantic cache): SKU 別                     │
│   ・Azure AI Content Safety: API call 単価                       │
│   ・APIM (Standard v2 ~ Premium): インスタンス時間 + リクエスト   │
└─────────────────────────────────────────────────────────────────┘
```

> ⚠️ シナリオ **D / E / F** ではレイヤー 1〜4 が **すべて並走して課金** されます (Copilot Studio + Foundry の二重課金)。

---

## 2. Microsoft Foundry の課金 (Token + 補助リソース)

### 2.1 主要モデル価格 (list, 2026-05 時点)

公式: <https://azure.microsoft.com/pricing/details/ai-foundry/>

| モデル | input ($/1M) | output ($/1M) | 用途 |
|---|---|---|---|
| `gpt-4.1-mini` | ~$0.40 | ~$1.60 | デフォルトの低コスト オプション。シナリオ A の推奨 |
| `gpt-4.1` | ~$2.00 | ~$8.00 | 中堅。Judge model (評価用) に推奨 |
| `gpt-5-mini` | ~$1.25 | ~$5.00 | **要事前登録** (`https://aka.ms/openai/gpt-5/2025-08-07`)。シナリオ A のサンプル実行で利用 |
| `gpt-5` | ~$10.00 | ~$30.00 | 要事前登録 |
| `gpt-4o` | ~$2.50 | ~$10.00 | マルチモーダル必要時 |
| `o3-mini` | ~$1.10 | ~$4.40 | 推論強化 |

> 💡 **見積式**: `月額 = (平均 input tokens × DAU × 質問数/日 × 営業日) × input単価 + 同様の output 計算`
>
> 例 (シナリオ A: 1 質問 ≒ 2,000 input + 500 output, DAU 100, 質問 5/日, 営業日 20):
> - input: 100 × 5 × 20 × 2,000 = 20M tokens → 20 × $0.40 = **$8.00**
> - output: 100 × 5 × 20 × 500 = 5M tokens → 5 × $1.60 = **$8.00**
> - **合計: $16/月** (gpt-4.1-mini)
> - 同条件で gpt-5-mini: $25 + $25 = **$50/月**

### 2.2 補助リソース

| リソース | 単価目安 | 課金トリガー |
|---|---|---|
| **Vector Store (File Search)** | $0.10 / GB / 日 | アップロード後の保管期間中、常時課金 |
| **Hosted Compute (Hosted agent)** | sandbox 0.25 vCPU / 0.5 GiB ≒ $0.00X/hour 〜 2 vCPU / 4 GiB | per-session VM の実行時間 (sandbox はアイドル時も従量) |
| **Application Insights** | ingestion $2.30/GB + retention $0.12/GB/月 (basic Logs) | trace / metric / log 送出量 |
| **Azure AI Content Safety** | $1〜3 / 1,000 リクエスト (Text Shield) | Content Filter / Prompt Shields / Safety evaluator |
| **Azure AI Search (semantic cache)** | Basic ~ $75/月、Standard S1 ~ $250/月 | APIM `<llm-semantic-cache-*>` の embeddings store |

> ⚠️ Vector Store は **削除しない限り課金継続**。シナリオ A の `common/scripts/cleanup_resources.py` 等で定期的に古い vector store を削除する運用を推奨。

---

## 3. Microsoft Copilot Studio Credits

公式: <https://microsoft.github.io/copilot-studio-estimator/> (Copilot Credits 推定ツール)

| アクション | 推定 Credits |
|---|---|
| Generative answer (Knowledge 参照のみ) | 1 |
| Generative answer (複雑な orchestration) | 2 |
| **Agent action (tool / connector 呼出)** | **5** / 起動 |
| **Foundry agent 呼出 (シナリオ D)** | **5** / 起動 (Copilot Credit 側) **+ Foundry token 別途** |
| BYOM Prompt (シナリオ E) | 通常 generative answer と同等 + Foundry token |
| MCP server tool 呼出 (シナリオ F) | Agent action と同等 (5) |
| Autonomous trigger (event-driven) | 25〜50 / イベント |

### 3.1 メッセージ管理ポリシー

公式 (`requirements-messages-management`) verbatim:

> _"Copilot Studio enforces tenant-level message capacity with a 125% execution policy."_

- 月次容量の 125% まで一時的に超過可能 (それ以降は throttle)
- 詳細条件は Licensing Guide PDF (`https://go.microsoft.com/fwlink/?linkid=2320995`) 参照

### 3.2 Credits パック価格 (list)

| パック | Credits | 月額目安 |
|---|---|---|
| 25,000 Credits pack | 25,000 | ~$200 |
| 個別購入 (Power Platform 計算) | 1 Credit = $0.01 換算 | — |

> 💡 シナリオ D (Foundry agent 呼出 5 Credits / 起動) は **CS 側で $0.05 / 呼出 + Foundry token 別途**。1 ユーザー / 日 10 回の業務で月額 ~$10/ユーザー (CS 側) + Foundry token 課金。

---

## 4. シナリオ別コスト試算

前提: **DAU 100 名 / 1 ユーザー 5 質問/日 / 営業日 20**

| シナリオ | 月額目安 (list) | 主要内訳 |
|---|---|---|
| **A (Prompt agent, gpt-4.1-mini)** | **$20〜30** | Foundry token $16 + Vector store $4 (50 MB) + App Insights $1 |
| **A (gpt-5-mini)** | **$55〜70** | Foundry token $50 + 他 |
| **B (Workflow agent)** | **$25〜40** | A と同程度 + Workflow Tracing |
| **C (Hosted agent, sandbox 0.25 vCPU)** | **$50〜100** | A の token + Hosted Compute (常時稼働の場合) + ACR ストレージ |
| **D (CS + Foundry, 1,000 委譲/月)** | **$50〜80** | CS Credits 5,000 ≒ $50 + Foundry token (A と同等) |
| **E (BYOM)** | **$30〜50** | CS Credits (Generative answer) + Foundry モデル token |
| **F (MCP, 既製 server)** | **$20〜40** | CS Credits (Agent action) + MCP server ホスト (Container Apps ~$10/月) |
| **H (APIM AI Gateway, Standard v2)** | **+$700/月** (固定) | APIM Standard v2 ~$700 + ポリシー実行リクエスト課金 |

> ⚠️ 上記は **PoC ベースの参考値**。本番では DAU・1 ユーザー質問数・モデル選択・キャッシュ率 (シナリオ H で 30〜70% 削減効果あり) によって 2〜10 倍の振れ幅があります。

---

## 5. APIM `<llm-emit-token-metric>` による可視化

シナリオ H で APIM AI Gateway を経由する場合、**全 LLM 呼出を一元的に計測** できます。

### 5.1 推奨 dimension 設計

| Dimension | 値 | 用途 |
|---|---|---|
| `Tenant` | テナント ID (header から取得) | テナント別月次按分 |
| `Model` | デプロイ名 | モデル別予算管理 |
| `Workload` | シナリオ A〜F + H の識別子 | シナリオ別レポート |
| `Environment` | dev / staging / prod | 環境別コスト管理 |
| `User` | (匿名化された) ユーザー ID | 異常利用検出 (任意) |

```xml
<llm-emit-token-metric namespace="genai">
  <dimension name="Tenant" value="@(context.Request.Headers.GetValueOrDefault(&quot;x-tenant-id&quot;, &quot;unknown&quot;))" />
  <dimension name="Model" value="@(context.Variables.GetValueOrDefault&lt;string&gt;(&quot;model&quot;, &quot;unknown&quot;))" />
  <dimension name="Workload" value="@(context.Request.Headers.GetValueOrDefault(&quot;x-workload&quot;, &quot;unknown&quot;))" />
  <dimension name="Environment" value="@(context.Deployment.Region)" />
</llm-emit-token-metric>
```

### 5.2 KQL レポート例 (Application Insights)

```kusto
// テナント別 / モデル別の月次 token 消費とコスト試算
customMetrics
| where name in ("PromptTokens", "CompletionTokens", "TotalTokens")
| extend Tenant = tostring(customDimensions.Tenant),
         Model = tostring(customDimensions.Model)
| summarize TotalTokens = sum(value) by Tenant, Model, name, bin(timestamp, 30d)
| extend EstimatedCost = case(
    Model == "gpt-4.1-mini" and name == "PromptTokens",     TotalTokens / 1000000.0 * 0.40,
    Model == "gpt-4.1-mini" and name == "CompletionTokens", TotalTokens / 1000000.0 * 1.60,
    Model == "gpt-5-mini"   and name == "PromptTokens",     TotalTokens / 1000000.0 * 1.25,
    Model == "gpt-5-mini"   and name == "CompletionTokens", TotalTokens / 1000000.0 * 5.00,
    0.0)
| order by EstimatedCost desc
```

---

## 6. Foundry Observability の token metric

公式: `observability/concepts/trace-agent-concept`

| 観点 | 内容 |
|---|---|
| 出力先 | Application Insights (Foundry project に連結された接続文字列) |
| 取得粒度 | `responseId` / `contextId` / `agentId` ベースで token 消費を取得可 |
| 状態 | Prompt agent は **GA**、Workflow / Hosted agent は **Preview** |
| 制約 | Hosted agent のセッション内コード実行は trace されない (コンテナ内のロジックは別途 OpenTelemetry が必要) |

### 6.1 Python セットアップ例

```python
from azure.monitor.opentelemetry import configure_azure_monitor
import os

configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    enable_live_metrics=True,
)
# 以降の Foundry SDK 呼出が自動で trace 化
```

---

## 7. 予算アラート / 削減アクション

### 7.1 予算アラート設定

| 設定場所 | 推奨閾値 |
|---|---|
| **Azure Cost Management → Budgets** | 月次予算の 50% / 80% / 100% |
| **APIM `<llm-token-limit>`** | テナント毎の TPM (例: 10,000) |
| **Application Insights アラート** | 1 時間あたりの token 消費 (急増検知) |
| **Foundry portal → Quotas** | TPM / RPM の上限を Azure サポートと調整 |

### 7.2 コスト削減チェックリスト

| 観点 | アクション | 期待効果 |
|---|---|---|
| **モデル選択** | gpt-4o → gpt-4.1-mini に切替 (シナリオ A / D) | 5〜10x 削減 |
| **Semantic cache (シナリオ H)** | APIM `<llm-semantic-cache-*>` を有効化 | 30〜70% 削減 (FAQ 系) |
| **Prompt 短縮** | システム instructions / few-shot 例を精査 | 20〜40% 削減 |
| **`store=false` 運用** | Responses API の履歴保持を停止 | リテンション ストレージ削減 |
| **Vector Store クリーンアップ** | 古い vector store の自動削除スクリプト | $0.10/GB/日 × 不要分を削減 |
| **PTU 検討** | 月次 token 消費が一定以上 (~$10K/月) なら PTU 切替検討 | PayGo の 1/2 〜 1/3 |
| **DLP で外部 connector 制限** | Microsoft Copilot Studio の非業務 connector ブロック | 想定外利用の抑止 |

---

## 8. ライセンス比較表

公式: <https://www.microsoft.com/microsoft-copilot/microsoft-copilot-studio/pricing>

| プラン | 月額 (list) | 含まれるもの | 主な制約 |
|---|---|---|---|
| **Microsoft 365 Copilot** | $30 / ユーザー | M365 Copilot + Copilot Studio (制限付き) + Copilot agents 利用 | エージェント作成は Maker に Copilot Studio Standalone が別途必要 |
| **Microsoft Copilot Studio (Standalone)** | $200 / テナント (Base) + 25,000 Credits | Authoring + Credits パック | Credits 消費は別途課金 |
| **Microsoft Copilot Studio in Teams** | M365 Copilot ライセンスに包含 | Teams 内エージェント作成 | 公開チャネルが Teams 限定 |
| **Dynamics 365 Customer Service** (D365 CC) | $X (D365 ライセンス内) | Customer Service Workspace 内 Copilot | D365 環境内に限定 |

### 8.1 シナリオ別の推奨ライセンス

| シナリオ | 推奨 ライセンス | 理由 |
|---|---|---|
| **A〜C (Foundry agent 本体)** | Microsoft 365 Copilot (公開先で必要) + Foundry resource (Azure 従量) | Copilot Studio ライセンスは不要 (Foundry agent は CS 外で動作) |
| **D (CS → Foundry)** | Copilot Studio Standalone + Foundry resource | CS Maker + Foundry agent 呼出 |
| **E (BYOM)** | Copilot Studio Standalone (Generative answers 利用) + Foundry resource | BYOM 機能利用 |
| **F (MCP)** | Copilot Studio Standalone + MCP server ホスト | MCP tool 接続 |
| **H (APIM)** | 上記 + APIM Standard v2 以上 | 集中ゲートウェイ |

---

## 9. 参考: 関連ドキュメント

| ドキュメント | 内容 |
|---|---|
| [`./governance.md`](./governance.md) | DLP / RBAC / Content Safety / Preview terms (Preview ステータスの取扱い等) |
| [`../demo-assets/scenario-h-apim-ai-gateway/README.md`](../demo-assets/scenario-h-apim-ai-gateway/README.md) | シナリオ H (`<llm-emit-token-metric>` の実装詳細) |
| Copilot Credits 推定ツール | <https://microsoft.github.io/copilot-studio-estimator/> |
| Foundry 価格表 | <https://azure.microsoft.com/pricing/details/ai-foundry/> |
| Copilot Studio Licensing Guide | <https://go.microsoft.com/fwlink/?linkid=2320995> |
