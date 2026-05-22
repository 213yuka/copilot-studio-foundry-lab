# シナリオ H: Azure API Management を **AI Gateway** として使う Microsoft Foundry / Microsoft Copilot Studio 統合

> **位置付け**: Microsoft Foundry endpoint / MCP server / A2A agent API / Microsoft Copilot Studio が呼び出すツールを **単一の Azure API Management (APIM) インスタンス** で集約し、トークン レート制御・セマンティック キャッシュ・ロード バランス・コンテンツ セーフティ・コスト可視化を一元的に提供する **ガバナンス & FinOps シナリオ**。
>
> **状態**: APIM 本体は **GA** / **AI Gateway policies (LLM token limit / semantic cache / llm-emit-token-metric / MCP expose / MCP export)** は **GA + Preview の混在** (機能ごとに差あり)。Microsoft Foundry portal からの **APIM 自動連携 (Connect API Management)** は **Public Preview**。
>
> **想定工数**: 0.5 人日 (既存 APIM がある場合) 〜 3 人日 (APIM + Foundry + MCP を新規構築する場合)
>
> **公式ガイド (一次資料)**:
> - <https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities> (AI Gateway 機能一覧)
> - <https://learn.microsoft.com/en-us/azure/ai-foundry/configuration/enable-ai-api-management-gateway-portal> (Foundry portal からの APIM 連携)
> - <https://learn.microsoft.com/en-us/azure/api-management/expose-existing-mcp-server> (既存 MCP server を APIM 経由で公開)
> - <https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server> (REST API を MCP server としてエクスポート)

> ℹ️ 本シナリオは **既存 6 シナリオ (A〜F) の上位レイヤー**として配置します。シナリオ A〜F のいずれを採用していても、APIM AI Gateway を被せることで「トークン課金の月次予算超過」「Foundry endpoint の障害時フェイルオーバー」「MCP server の認証統一」を後付けで実現できます。

---

## 0. 全体構成図

```
[エンド ユーザー / Microsoft Copilot Studio / 他システム]
   │
   │  (1 つの APIM endpoint で集約)
   ▼
┌─────────────────────────────────────────────────────────────────┐
│  Azure API Management (AI Gateway)                              │
│                                                                  │
│   Inbound policies:                                              │
│     ・<llm-token-limit>          (テナント / API key 単位の TPM)  │
│     ・<llm-semantic-cache-lookup> (Azure AI Search ベース)       │
│     ・<content-safety>           (Azure AI Content Safety 連携)  │
│     ・<validate-jwt>             (Entra ID 認証)                 │
│   Backend:                                                       │
│     ・<llm-load-balancer> + circuit breaker                      │
│     ・優先度別 backend pool (PTU → PayGo フォールバック)          │
│   Outbound policies:                                             │
│     ・<llm-emit-token-metric>    (App Insights / Azure Monitor)  │
│     ・<llm-semantic-cache-store>                                 │
└─────────────────────────────────────────────────────────────────┘
        │              │                │                  │
        ▼              ▼                ▼                  ▼
 [Foundry agent]  [Foundry model]  [MCP server]    [Foundry A2A endpoint]
 (シナリオ A〜D)    (シナリオ E)     (シナリオ F)    (シナリオ C / D)
```

---

## 1. このシナリオが適する状況

| 条件 | 該当 |
|---|---|
| 複数の Foundry endpoint / モデル / MCP server を **横断的に統制**したい | ✅ |
| **テナント / 利用者単位の token 制限・課金按分** が必要 (社内マルチテナント運用) | ✅ |
| **Semantic caching** で頻出クエリのコストとレイテンシを削減したい | ✅ |
| **PTU + PayGo の混成構成**で、PTU 枯渇時に自動フェイルオーバーしたい | ✅ |
| 既存 REST API を **MCP server として APIM 経由で公開**したい (シナリオ F の拡張) | ✅ |
| **Content Safety / Prompt Shields** を全 LLM 呼出に強制したい | ✅ |
| 単一プロジェクト・単一モデル・単一テナントで完結する小規模 PoC | ❌ (オーバースペック) |
| Foundry portal の Built-in evaluator だけで十分 / 観測性は Application Insights 単体で十分 | ❌ |

---

## 2. 前提条件

### 2.1 Azure サブスクリプション側

| 項目 | 値 |
|---|---|
| APIM SKU | **Standard v2 / Premium / Developer** (AI Gateway policies は Standard v2 以上推奨) |
| `Microsoft.ApiManagement` プロバイダー | 登録済 (`az provider register --namespace Microsoft.ApiManagement`) |
| RBAC | APIM Contributor + Cognitive Services User (Foundry endpoint へ送信時に必要) |
| 関連サービス | Azure AI Search (semantic cache 用 / 任意) / Application Insights (token metric 用) / Azure AI Content Safety (任意) |

### 2.2 Microsoft Foundry 側

| 項目 | 値 |
|---|---|
| Foundry resource + project | 既存 (シナリオ A〜C で作成したもの可) |
| Foundry portal | <https://ai.azure.com> (**New Foundry** トグル ON) |
| 接続方式 | (a) Foundry portal の **Connect API Management** ウィザード (Preview) / (b) APIM portal から **Add API → Azure OpenAI / Azure AI Foundry** で手動追加 |

### 2.3 MCP server 側 (シナリオ F と併用する場合)

| 項目 | 値 |
|---|---|
| 既存 MCP server を APIM 経由で公開 | `expose-existing-mcp-server` の手順 (APIM `import` → MCP-compliant URL に変換) |
| REST API を MCP server 化 | `export-rest-mcp-server` の手順 (APIM 上の既存 REST API を `Export → MCP` で MCP として公開) |

---

## 3. AI Gateway の主要ポリシー

### 3.1 トークン制限 (`<llm-token-limit>`)

公式 (`genai-gateway-capabilities`) verbatim:

> _"The LLM token limit policy lets you set a token-per-minute (TPM) quota for a subscription, IP address, or any custom key."_

```xml
<inbound>
  <base />
  <llm-token-limit
    counter-key="@(context.Subscription.Id)"
    tokens-per-minute="10000"
    estimate-prompt-tokens="true"
    tokens-consumed-header-name="x-tokens-consumed"
    remaining-tokens-header-name="x-tokens-remaining" />
</inbound>
```

| 設定キー | 用途 |
|---|---|
| `counter-key` | テナント / API key / ユーザー識別子。社内マルチテナント運用ではテナント ID を渡す |
| `estimate-prompt-tokens="true"` | リクエスト送信前に prompt tokens を推定し超過時は即 429 |
| `tokens-consumed-header-name` | 呼出元クライアントに消費トークン数を返却 (FinOps 可視化用) |

### 3.2 Semantic caching (`<llm-semantic-cache-*>`)

公式 (`genai-gateway-capabilities`) verbatim:

> _"Semantic caching reduces backend load and improves response times by storing and reusing responses based on semantic similarity of prompts."_

```xml
<inbound>
  <base />
  <llm-semantic-cache-lookup
    score-threshold="0.05"
    embeddings-backend-id="azure-ai-search-embeddings"
    embeddings-backend-auth="system-assigned-managed-identity" />
</inbound>
<outbound>
  <base />
  <llm-semantic-cache-store duration="3600" />
</outbound>
```

| 注意点 | 説明 |
|---|---|
| `score-threshold` | 0.05 (公式推奨) より大きくすると誤ヒット増加。慎重に調整 |
| `embeddings-backend-id` | Azure AI Search またはエンベディング モデル backend が事前登録必要 |
| キャッシュ汚染リスク | テナント / ユーザー単位のキー分離を必須 (`vary-by` で `subscription-id` 等を指定) |

### 3.3 ロード バランス + Circuit breaker (`<llm-load-balancer>`)

公式 (`genai-gateway-capabilities`) verbatim:

> _"Load balancer policy distributes traffic across multiple Azure OpenAI Service or Azure AI Foundry deployments with priority and weight."_

```xml
<backend>
  <llm-load-balancer
    backends-pool-id="foundry-pool"
    strategy="priority-then-weight" />
</backend>
```

| パターン | 設定 |
|---|---|
| **PTU 優先 + PayGo フォールバック** | PTU backend は priority=1, PayGo backend は priority=2 |
| **A/B テスト** | 2 つのモデル backend を weight 50/50 に |
| **リージョン フェイルオーバー** | プライマリ リージョンを priority=1, セカンダリ リージョンを priority=2、circuit breaker で 5xx 連続時に切替 |

### 3.4 トークン メトリック (`<llm-emit-token-metric>`)

公式 (`genai-gateway-capabilities`) verbatim:

> _"Emit token metrics to Application Insights for cost tracking and analytics, broken down by dimensions like subscription, model, and custom dimensions."_

```xml
<outbound>
  <base />
  <llm-emit-token-metric
    namespace="genai">
    <dimension name="Subscription ID" value="@(context.Subscription.Id)" />
    <dimension name="Tenant" value="@(context.Request.Headers.GetValueOrDefault(&quot;x-tenant-id&quot;, &quot;unknown&quot;))" />
    <dimension name="Model" value="@(context.Variables.GetValueOrDefault&lt;string&gt;(&quot;model&quot;, &quot;unknown&quot;))" />
  </llm-emit-token-metric>
</outbound>
```

| 出力先 | 用途 |
|---|---|
| Application Insights カスタム メトリック | テナント別月次レポート、Power BI 連携 |
| Azure Monitor metrics | アラート (例: 月次予算の 80% で通知) |
| Log Analytics (任意) | KQL でドリルダウン解析 (`customMetrics | summarize sum(value) by tostring(customDimensions.Tenant)`) |

### 3.5 Content Safety / Prompt Shields 強制

公式 (`genai-gateway-capabilities`) verbatim (要約):

> APIM から Azure AI Content Safety を呼び出すパターン (`set-backend-service` または `send-request` ポリシー経由) で、全 LLM 呼出に対しモデレーション / Prompt Shields / Indirect attacks を **集中強制** できる。

```xml
<inbound>
  <base />
  <send-request mode="new" response-variable-name="shieldResp" timeout="5" ignore-error="false">
    <set-url>@($"https://{context.Variables[&quot;contentSafetyEndpoint&quot;]}/contentsafety/text:shieldPrompt?api-version=2024-09-01")</set-url>
    <set-method>POST</set-method>
    <set-header name="Ocp-Apim-Subscription-Key" exists-action="override">
      <value>{{content-safety-key}}</value>
    </set-header>
    <set-body>@{ return JsonConvert.SerializeObject(new { userPrompt = context.Request.Body.As<string>(true) }); }</set-body>
  </send-request>
  <choose>
    <when condition="@(((IResponse)context.Variables[&quot;shieldResp&quot;]).Body.As<JObject>()[&quot;userPromptAnalysis&quot;][&quot;attackDetected&quot;].Value<bool>())">
      <return-response>
        <set-status code="400" reason="Prompt injection detected" />
      </return-response>
    </when>
  </choose>
</inbound>
```

> ⚠️ Content Safety の Prompt Shields は **Indirect attacks (XPIA)** にも対応。File Search / MCP resource を介した間接的なプロンプト インジェクション対策として有効。

---

## 4. MCP server を APIM 経由で公開する

### 4.1 既存 MCP server を APIM の Backend として登録

公式: `expose-existing-mcp-server`

| 手順 | 内容 |
|---|---|
| 1 | APIM portal → **APIs** → **+ Add API** → **OpenAPI** または **HTTP** で MCP server URL を登録 |
| 2 | `Streamable HTTP` transport を選択 (旧 SSE transport は 2025-08 以降サポート終了 — シナリオ F 参照) |
| 3 | OAuth 2.0 (Entra ID / その他 IdP) または `Ocp-Apim-Subscription-Key` で認証 |
| 4 | Foundry / Microsoft Copilot Studio 側からは APIM の MCP endpoint を「外部 MCP server」として登録 |

### 4.2 既存 REST API を MCP server としてエクスポート

公式: `export-rest-mcp-server`

| 手順 | 内容 |
|---|---|
| 1 | APIM portal → 対象 API → **Export → MCP** |
| 2 | `tools` / `resources` セクションが自動生成される (OpenAPI から MCP tool 定義に変換) |
| 3 | Microsoft Copilot Studio エージェント → **Tools → Model Context Protocol** で APIM の MCP endpoint を追加 (シナリオ F の手順) |

> 💡 既存 IT システム (Service Now / Salesforce / 社内 REST API) を **APIM 上の REST API として一度ラップ** → **MCP として export** することで、新規 MCP server を実装することなく Microsoft Copilot Studio / Foundry agent から利用可能にできます。

---

## 5. Microsoft Foundry portal からの APIM 連携 (Public Preview)

公式: `enable-ai-api-management-gateway-portal`

| 手順 | 内容 |
|---|---|
| 1 | Foundry portal → 対象 Project → **Settings → Connected resources → Connect API Management** |
| 2 | 既存 APIM インスタンスを選択 (RBAC: APIM Contributor + Foundry Project Manager) |
| 3 | Foundry が APIM 上に **専用 API** (`/openai`, `/foundry/agents` 等) を自動作成 |
| 4 | プロジェクト endpoint が APIM 経由の URL に切替わる (既存 SDK コードは変更不要) |
| 5 | デフォルト ポリシーとして `<llm-token-limit>` + `<llm-emit-token-metric>` が適用 (ベース テンプレート提供) |

> ⚠️ **Preview 注意**: 接続後の APIM 側ポリシー (テンプレート以外) は **APIM portal 側で手動編集**する必要があります。Foundry portal からの追加ポリシー編集 UI は本記事執筆時点では未提供。

---

## 6. シナリオ A〜F との組合せパターン

| 既存シナリオ | APIM AI Gateway を被せる効果 |
|---|---|
| **A (Prompt agent)** | tokens-per-minute 制御 + semantic cache でデモ時のレート制限 / コスト削減。Foundry endpoint の URL を APIM endpoint に差替えるだけで適用 |
| **B (Workflow agent)** | Workflow 内の LLM 呼出を APIM 経由に。Workflow ノードの `Model` 設定で APIM endpoint を指定 |
| **C (Hosted agent)** | Hosted agent コンテナ内の `OPENAI_BASE_URL` を APIM endpoint に差替え。コンテナ単位ではなく **コール単位**で metric を取得可能 |
| **D (CS → Foundry agent)** | Microsoft Copilot Studio → Foundry の通信を APIM 経由化 → DLP の補強 + テナント単位 token quota |
| **E (BYOM)** | Microsoft Copilot Studio が呼ぶモデル endpoint を APIM 経由化 → 複数モデルのフェイルオーバー / A/B テスト |
| **F (MCP)** | MCP server を APIM 上で公開 → OAuth 認証集約 + tools/resources の export ↔ 既存 REST API のラップ |
| **G (Foundry → M365)** | Agent Application が呼び出す全 backend (Foundry endpoint / external API) を APIM 経由化 → エンタープライズ統制 |

---

## 7. 動作確認

| 確認場所 | 何を見るか |
|---|---|
| **APIM portal → Analytics → Metrics** | リクエスト数 / レイテンシ / 4xx・5xx 比率 |
| **Application Insights → Metrics (`genai`)** | テナント別 / モデル別の token 消費量・コスト集計 |
| **Application Insights → Logs** | KQL で `customMetrics` をテナント別に集計 (`sum(value) by tostring(customDimensions.Tenant)`) |
| **Foundry Tracing (Observability)** | Foundry 側の trace と APIM 側の `request-id` 突合 (相関 ID 設計が重要) |
| **Azure Monitor アラート** | 月次予算の閾値 (80% / 100%) で通知。スロットリング (429) 多発時の通知 |

---

## 8. 重要な制約・注意点 (verbatim)

| # | 制約 | verbatim 引用 |
|---|---|---|
| 1 | LLM token limit の対応モデル | _"The policy supports Azure OpenAI Service, Azure AI Foundry model inference, and OpenAI-compatible endpoints."_ (`genai-gateway-capabilities`) |
| 2 | Semantic cache の embeddings backend は事前登録 | _"The semantic cache lookup policy requires an embeddings backend to be configured."_ (`genai-gateway-capabilities`) |
| 3 | Foundry portal からの APIM 連携は **Preview** | _"This feature is in preview."_ (`enable-ai-api-management-gateway-portal`) |
| 4 | MCP server APIM 公開は **Preview** | _"MCP server in API Management is in preview."_ (`expose-existing-mcp-server`) |
| 5 | Streamable HTTP 限定 | SSE transport は 2025-08 以降サポート終了 (シナリオ F の MCP 注記と同じ) |

---

## 9. 既知の Open Question (継続調査)

- **Foundry portal の APIM 連携 GA タイミング**: 公式未発表。Preview 期間中の SLA は対象外
- **MCP server APIM 公開の認証**: OAuth 2.0 の動的クライアント登録 (DCR) サポート状況は要追加検証
- **Semantic cache の精度**: `score-threshold` の最適値は業務ドメインに依存。日本語の場合は閾値の追加チューニングが推奨される
- **Microsoft Copilot Studio との連携**: Microsoft Copilot Studio が直接呼ぶ Foundry endpoint (シナリオ D) を APIM 経由化した場合、Copilot Studio Analytics で観測できる粒度の差は要検証
- **Cost attribution の正確性**: `<llm-emit-token-metric>` で送出される dimension は **APIM 側で観測可能な情報のみ**。エンド ユーザー単位の課金按分には別途相関 ID 設計が必要

---

## 10. 関連シナリオ・補助ドキュメント

| ドキュメント | 内容 |
|---|---|
| [`../scenario-a-prompt-agent/README.md`](../scenario-a-prompt-agent/README.md) | シナリオ A (APIM を被せる対象) |
| [`../scenario-d-cs-plus-foundry/README.md`](../scenario-d-cs-plus-foundry/README.md) | シナリオ D (APIM 経由で CS ↔ Foundry を統制) |
| [`../scenario-e-byom-foundry-model/README.md`](../scenario-e-byom-foundry-model/README.md) | シナリオ E (BYOM モデル endpoint を APIM 経由化) |
| [`../scenario-f-mcp-connection/README.md`](../scenario-f-mcp-connection/README.md) | シナリオ F (MCP server を APIM 経由で公開) |
| [`../scenario-g-foundry-to-m365/README.md`](../scenario-g-foundry-to-m365/README.md) | シナリオ G (Agent Application の外部呼出を APIM 経由化) |
| [`../scenario-i-evaluation-redteam/README.md`](../scenario-i-evaluation-redteam/README.md) | シナリオ I (APIM 経由のトレース ↔ Evaluation データ収集) |
| [`../../docs/governance.md`](../../docs/governance.md) | DLP / RBAC / Content Safety / Preview terms 横断ガバナンス |
| [`../../docs/cost-finops.md`](../../docs/cost-finops.md) | Foundry token / Copilot Credits / APIM token metric の横断 FinOps |
