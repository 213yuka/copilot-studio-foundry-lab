# シナリオ E: Microsoft Copilot Studio → Microsoft Foundry **モデル持ち込み (BYOM, GA)** 連携

> **位置付け**: Microsoft Copilot Studio エージェント本体は **そのまま温存**し、**プロンプト ノードで利用する LLM だけ** Microsoft Foundry のモデルカタログから差し替える、最小工数・最小リスクの連携パターン。
> **状態**: ✅ **GA** (Power Platform の "Azure AI Foundry" コネクタ経由)
> **想定工数**: 0.5 人日 (Foundry リソース・モデルが既に存在する場合)
> **公式ガイド (一次資料)**: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/bring-your-own-model-prompts>

シナリオ A〜D は **エージェント (agent)** レイヤーの選択肢でしたが、本シナリオ E は **モデル (model)** レイヤーの選択肢です。Microsoft Copilot Studio の Topic / Action / Knowledge 構造は何も変えず、**Prompt ツール (= Power Platform AI Builder Prompt)** が呼び出す LLM だけを Microsoft Foundry 側に切り替えます。

---

## 0. 全体構成図

```
[エンド ユーザー]
   │  (Teams / M365 Copilot / 公開 Web)
   ▼
[Microsoft Copilot Studio エージェント] ── 既存資産そのまま
   ├─ Topic: PasswordReset      (Question + Power Fx 分岐)
   ├─ Topic: PolicyQA           (Knowledge: it-policy.md)
   ├─ Action: CreateTicket      (HTTP Request)
   └─ Prompt (New tool)         ← ★ ここの Model だけ差し替え
                                  │
        "+ Connect a model from Azure AI Foundry"
        で Foundry モデルカタログから選択
                                  │
   ┌──────────────────────────────┴──────────────────────────────┐
   │ Microsoft Foundry 側 (モデル デプロイのみ、agent は作らない) │
   │   ・GPT-4o / GPT-4o-mini / GPT-4.5-preview / o1            │
   │   ・Llama 3.x / DeepSeek R1                                 │
   │   ・Phi-3.5/Phi-4 (image 対応)                              │
   │   ・任意のファインチューン モデル                            │
   └─────────────────────────────────────────────────────────────┘
```

---

## 1. このシナリオが適する状況

| 条件 | 該当 |
|---|---|
| 既存の Microsoft Copilot Studio エージェントを **そのまま継続使用**したい | ✅ |
| 1〜数本の Prompt ノードだけ、別モデルで処理させたい (例: 日本語要約は Llama 3.x、画像入力は GPT-4o) | ✅ |
| ファインチューニング済みモデルを使いたい | ✅ |
| マルチモーダル (画像・ドキュメント入力) を Foundry の対応モデルで実現したい | ✅ |
| **GA で SLA 付きの本番運用** にしたい | ✅ (BYOM 機能自体は GA) |
| エージェント全体を Foundry に移行したい | ❌ シナリオ A〜C 推奨 |
| Topic / Action のレベルで Foundry 機能を呼びたい | ❌ シナリオ D (agent 接続) または F (MCP) 推奨 |

> 💡 **シナリオ D との違い**: D は「Foundry **agent** を呼ぶ」(エージェント単位の委譲)。E は「Foundry **model** を呼ぶ」(プロンプト単位の差し替え)。両者は併用可能。

---

## 2. 前提条件

### 2.1 Microsoft Copilot Studio 側

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions>

| 項目 | 値 |
|---|---|
| ライセンス | Microsoft Copilot Studio Standalone / Trial / M365 Copilot |
| 環境 | Production 環境推奨 |
| Maker 権限 | agent author + Power Platform Connection 作成権限 |
| ポータル | <https://copilotstudio.microsoft.com> |

📖 まだ Microsoft Copilot Studio エージェントが無い場合は `..\00-create-cs-agent.md` を先に実施。

### 2.2 Microsoft Foundry 側

| 項目 | 値 |
|---|---|
| Foundry portal | <https://ai.azure.com> (**New Foundry** トグル ON) |
| アーキテクチャ | Foundry resource → Foundry project |
| 対応モデル | Azure AI Foundry / Model catalog の **chat completion** タイプ (1,800+ モデル) |
| エンドポイント | モデル デプロイ後の **deployment name** と **base model name** が必要 (両方とも portal の表記に **完全一致**で入力) |
| RBAC | Foundry project に **Foundry User** ロール |

公式モデルカタログ: <https://ai.azure.com/explore/models>

### 2.3 Power Platform 管理側

| 項目 | 値 |
|---|---|
| コネクタ名 | **`Azure AI Foundry`** (Power Platform admin center のデータ ポリシー ページ上の表記) |
| 必要操作 | DLP ポリシーで `Azure AI Foundry` コネクタを許可リスト (Business / Non-business) に配置 |
| 管理 portal | <https://admin.powerplatform.microsoft.com> |

> ⚠️ Power Platform DLP で `Azure AI Foundry` コネクタを Blocked にすると、Microsoft Copilot Studio 側でモデル選択時にエラーになります。

---

## 3. Phase 1: Microsoft Foundry 側でモデルをデプロイ

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/deploy-models-openai>

1. <https://ai.azure.com> にサインイン → **New Foundry** トグル ON
2. 既存 project を開く (無ければ `+ Create a project`)
3. 左メニュー **Models + Endpoints** → **+ Deploy model**
4. モデルカタログから選択 (例):
   - `gpt-4o` (マルチモーダル / image 対応)
   - `gpt-4o-mini` (高速・低コスト)
   - `Meta-Llama-3.3-70B-Instruct`
   - `DeepSeek-R1`
   - `Phi-3.5-vision-instruct` (image 対応)
5. **Deployment name** を控える (例: `gpt-4o-japaneast-prod`)
6. **Base model name** を控える (例: `gpt-4o`)

> ⚠️ Deployment name と Base model name は **Microsoft Copilot Studio 側で別フィールドに入力**します。誤入力するとモデルが見つからずエラー。

### 3.1 (任意) ファインチューン モデルの場合

公式: <https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/fine-tune-managed-compute>

1. Foundry portal → **Fine-tuning** で base model にファインチューンを実行
2. 完了後、上記同様 **Models + Endpoints** にデプロイ
3. Deployment name はファインチューン後のもの、Base model name は元の base model 名

---

## 4. Phase 2: Microsoft Copilot Studio で Prompt ツールを作成

公式 (Prompt ツール全体): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompts-overview>

### 4.1 Prompt ツール (= Action) を新規追加

1. <https://copilotstudio.microsoft.com> → 対象エージェント (例: `IT-Helpdesk-Sample`) を開く
2. 左メニュー **Tools** タブ → **+ Add a tool**
3. **New tool** → **Prompt** を選択
4. プロンプト名を入力 (例: `JapaneseSummarizeWithLlama`)
5. **Instructions** に処理内容を記述 (例: 「以下のチケット内容を 100 文字以内で日本語要約せよ」)

または Topic 内に直接追加することも可能:
- **Topics** タブ → 既存 Topic → **+** → **Add a topic** → **New prompt**

### 4.2 Foundry モデルを接続

1. Prompt 編集画面の右側 **Model** ドロップダウンを開く
2. **+ (プラス)** ボタンをクリック → **Connect a model from Azure AI Foundry**
3. 以下を入力:
   - **Model deployment name**: Phase 1 で控えた deployment name (例: `gpt-4o-japaneast-prod`)
   - **Base model name**: Phase 1 で控えた base model name (例: `gpt-4o`)
4. **Connect**
5. 接続が完了すると **Model** ドロップダウンに追加され、選択可能になる
6. Prompt の **Model** にこの新しいモデルを選択 → 保存

> ⚠️ 公式注記 (verbatim 引用):
> 「Make sure to add the **Model deployment name** and **Base model name** exactly as they appear in Azure AI Foundry.」

### 4.3 画像・ドキュメント入力を扱う場合

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/bring-your-own-model-prompts>

Prompt に **画像入力**を追加すると、ドロップダウンには **画像対応モデルのみ**が表示されます。

現時点で画像対応とされているモデル (公式リスト):

- `Phi-3.5-vision-instruct`
- `Phi-4-multimodal-instruct`
- `Phi-3-vision-128k-instruct`
- `o1`
- `GPT-4o`
- `GPT-4o-mini`
- `GPT-4`
- `GPT-4.5-preview`

> ⚠️ 公式 Note (verbatim 引用):
> 「Copilot Studio doesn't natively support image generation or expose Azure AI Foundry models directly in the user interface. The **Add an AI model** catalog currently includes AI Builder models and selected Azure AI Services, but no text-to-image models.」
>
> 画像 **生成** (DALL·E 3 等) は本 BYOM 機能では UI から直接呼べないため、プラグイン / カスタム アクション (REST API 呼び出し) で実装します。

---

## 5. Phase 3: Topic / Action から Prompt を呼び出す

### 5.1 Topic ノードから呼び出し

1. 対象 Topic を開く
2. 適切な位置で **+** → **Call an action** → 作成した Prompt を選択
3. 入力変数 (例: ユーザー発話・チケット本文) を Prompt のパラメータにマップ
4. 出力 (= Prompt 実行結果) を Topic 変数に保存 (例: `Topic.SummarizedText`)
5. 後続の Message / HTTP Request 等で利用

### 5.2 Generative orchestration から自動呼び出し

Generative orchestration が ON の場合、Prompt の **Description** をオーケストレーターが評価し、ユーザー入力に応じて自動的に呼び出します。Description のベスト プラクティスは [`..\scenario-d-cs-plus-foundry\README.md` §4.2](../scenario-d-cs-plus-foundry/README.md) を参照。

---

## 6. Phase 4: 動作確認

### 6.1 Test pane

1. Microsoft Copilot Studio portal → 対象エージェント → 右上 **Test** をオン
2. 対象 Prompt を呼ぶシナリオを入力 (例: チケット要約を呼び出す Topic の trigger)
3. **Track between topics** をオンにすると、どの Prompt / モデルが選ばれたかを可視化できる

### 6.2 Foundry 側で利用状況を確認

1. <https://ai.azure.com> → project → **Models + Endpoints** → 対象 deployment
2. **Monitoring** タブで Tokens / RPM / Latency を確認
3. Microsoft Copilot Studio の Prompt 実行が **Foundry 側のメトリクスに計上**されることを確認

> ⚠️ 課金は Foundry 側 (Azure サブスクリプション) の従量課金にも乗ります。Microsoft Copilot Studio Message Capacity とは **別計算** なのでコスト管理を分けて設計してください。

---

## 7. Microsoft Copilot Studio ↔ Microsoft Foundry マッピング表

| Microsoft Copilot Studio | Microsoft Foundry | 備考 |
|---|---|---|
| Prompt (New tool → Prompt) | Foundry Model deployment | chat completion タイプのみ対応 |
| Prompt の Model フィールド | Foundry portal → Models + Endpoints の deployment | deployment name + base model name を入力 |
| Prompt の Instructions | (送信時に system prompt 相当として渡る) | Foundry 側は生のモデル呼び出しのみ |
| Connection (Azure AI Foundry コネクタ) | Foundry project | Power Platform Connection で 1:1 紐付け |
| Power Platform DLP | (該当なし) | コネクタ単位で許可/拒否 |
| ❌ Foundry agent (Prompt agent 等) | ❌ 本シナリオでは使わない | agent 側の File Search / OpenAPI 等は **動かない** (シナリオ A 等で使用) |
| ❌ Foundry Vector Store / File Search | ❌ 本シナリオでは使わない | Knowledge は Microsoft Copilot Studio 側 Knowledge を継続利用 |
| ❌ Foundry tool (OpenAPI / Function) | ❌ 本シナリオでは使わない | Microsoft Copilot Studio 側 Action / Tool を継続利用 |

---

## 8. 既知の制約・注意点

| 観点 | 内容 | 公式リファレンス |
|---|---|---|
| **対応モデル種別** | **chat completion** タイプのみ。embedding / text-to-image / speech 等は本機能では非対応 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/bring-your-own-model-prompts> |
| **画像生成** | DALL·E 3 等の text-to-image は UI から直接選べない (プラグイン / REST API 呼び出しで代替) | 同上 |
| **deployment name / base model name** | Foundry portal の表記と **完全一致**必須 | 同上 |
| **データ越境** | Microsoft Copilot Studio 環境のデータ (= プロンプト入力 + 履歴) が Foundry テナント / リージョンへ流れる。データ レジデンシー要件があるなら **同一リージョン構成**を必須化 | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/encryption-keys-portal> |
| **DLP** | Power Platform admin center で `Azure AI Foundry` コネクタが Blocked になっていると接続不可 | <https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention> |
| **課金** | Microsoft Copilot Studio Message Capacity と Foundry モデル従量課金の **二重計上** が発生 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages> |
| **Responsible AI** | Foundry モデル側の Content Filter / Guardrails は **Foundry 側責任**で別途設定する必要あり | <https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-use-of-ai-overview> |
| **オーケストレーション** | Topic / Action の選択ロジック (Generative orchestration) は Microsoft Copilot Studio 側で従来通り。Foundry 側は呼ばれた瞬間に LLM 推論するだけで、ルーティング判断はしない | — |

---

## 9. クイック リファレンス: 公式ドキュメント

| トピック | URL |
|---|---|
| Bring your own model (本機能の本家ドキュメント) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/bring-your-own-model-prompts> |
| Prompts overview (Prompt ツール全般) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/prompts-overview> |
| Power Platform Release Plan: BYOM in prompt builder | <https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave1/ai-builder/use-own-generative-ai-model-azure-ai-foundry-prompt-builder> |
| Azure AI Foundry Model catalog | <https://ai.azure.com/explore/models> |
| Featured models (Meta / DeepSeek 等) | <https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/models-featured> |
| Foundry: Fine-tuning | <https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/fine-tune-managed-compute> |
| Power Platform admin center | <https://admin.powerplatform.microsoft.com> |
| Power Platform DLP 概要 | <https://learn.microsoft.com/en-us/power-platform/admin/wp-data-loss-prevention> |
| Responsible AI for Azure AI Foundry | <https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-use-of-ai-overview> |

---

## 10. 他シナリオとの併用パターン

| 併用 | 動作 |
|---|---|
| **E + D** | Microsoft Copilot Studio 内で、Topic A の Prompt は Foundry モデル (E)・Topic B では Foundry agent 全体を呼ぶ (D) → きめ細かい使い分けが可能 |
| **E + F** | Prompt のモデルは Foundry (E)、Action は MCP server 経由で外部ツールを呼ぶ (F) → ノーコードのまま機能拡張 |
| **E + A/B/C** | Microsoft Copilot Studio を残しつつ、別に Foundry agent (A/B/C) を作って D の方式で接続。Prompt 単位の差し替え (E) も併用 → 段階的移行戦略 |

> 💡 **おすすめの最初の一歩**: いきなりエージェント全体を移行 (A〜C) せず、まず E で **「Foundry のモデル品質が業務シナリオに合うか」**を Prompt 1 本で検証 → OK なら D で agent 接続 → 全面移行が必要になったら A〜C へ、という段階移行が低リスクです。
