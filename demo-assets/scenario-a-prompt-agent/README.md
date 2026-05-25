# シナリオ A: Microsoft Copilot Studio → Microsoft Foundry **Prompt agent (GA)** 移行

> **位置付け**: 7 シナリオの中で **最短ルート / GA 機能のみ** (A/B/C ルートのうちの A)
> **方針**: **Microsoft Foundry portal (GUI) のみ** で進めます。RBAC 割当・ナレッジ追加・Prompt agent 作成・プレイグラウンド検証はすべてポータル操作で完結します。Python / Azure CLI / SDK は使いません。

Microsoft Copilot Studio の Topic / 分岐ロジックを **手順 (自然言語ガイダンス)** に集約し、ナレッジを **ファイル検索**、Action を **OpenAPI ツール** として Microsoft Foundry の Prompt agent に登録する移行パターンです。

---

## 0. 全体フロー

```
[フェーズ 1〜2] Copilot Studio で IT-Helpdesk-Sample を作成 + pac で YAML 抽出 (= 00 で完了)
        ↓
[フェーズ 3]   Foundry リソース / プロジェクト / モデルを準備   ← Azure portal + Foundry portal
        ↓
[フェーズ 4]   Foundry portal で Prompt agent を作成            ← プレイグラウンドで手順・ツールを設定
              (手順 + ファイル検索 + OpenAPI ツール)               → 「エージェントとして保存」
        ↓
[フェーズ 5]   プレイグラウンドで動作確認                       ← Foundry portal
```

> 🖱️ **フェーズ 3〜5 はすべて Foundry portal (GUI) のみで完結** します。CLI / SDK / Python のインストールは不要です。

---

## 1. このシナリオが適する Copilot Studio エージェント

| 条件 | 該当 |
|---|---|
| Topic 数が少ない (≤ 5) | ✅ |
| 分岐ロジックが「LLM の常識 + 短い文章ガイドライン」で十分カバー可能 | ✅ |
| 知識参照 (RAG) + 数本の外部 API 呼出が中心 | ✅ |
| **GA で SLA 付きの本番運用**にしたい | ✅ |
| 確定的・厳密なフロー保証が必要 | ❌ シナリオ B 推奨 |
| Power Automate Flow の高度な処理を維持したい | ❌ シナリオ B / C 推奨 |

---

## 2. 前提条件

### 2.1 Copilot Studio 側 (フェーズ 1〜2)

📖 詳細は **[`..\00-create-cs-agent.md`](../00-create-cs-agent.md)** を参照。

本シナリオで実際に使うアウトプット:

| アウトプット | 取得元 | 本シナリオでの使い方 |
|---|---|---|
| 移行元エージェント `IT-Helpdesk-Sample` | 00 §2〜§7 (Copilot Studio portal で構築) | 手順 / Topic / ナレッジ / Action の **設計情報の出所**。Foundry portal を開きながら並行参照する |
| 設計参照用 YAML (`IT-Helpdesk-Sample.yaml`) | 00 §8.4 `pac copilot extract-template` の出力 | (任意) Topic ツリーを diff したい場合の機械可読スナップショット (§2.2 参照) |
| ナレッジ本体 | [`..\common\sample-knowledge\it-policy.md`](../common/sample-knowledge/it-policy.md) | §4 で **ファイル検索** にそのまま添付 |
| OpenAPI 定義 | [`..\common\tools\create-ticket.openapi.yaml`](../common/tools/create-ticket.openapi.yaml) | §5.1 手順 5 で OpenAPI ツールに貼り付け |

### 2.2 00 で抽出した YAML の活用方針 (Copilot Studio → Prompt agent)

00 §8 の `pac copilot extract-template` で得られる **`IT-Helpdesk-Sample.yaml`** (約 28 KB / 15 components) は、本シナリオ A では **設計参照用** として扱います。**Foundry Agent Service には YAML をそのままインポートする経路はありません** (Prompt agent の構成は portal で別途定義する仕様)。そのため YAML は「移行元の正確なスナップショット」「人手で 手順 / OpenAPI に書き換えるための入力」という位置付けになります。

#### 活用パターン A: YAML を読みながら設計する (Topic が多い・差分管理したい場合)

| 何をしたいか | YAML のどこを見るか | 反映先 |
|---|---|---|
| 手順のドラフト化 | root の `description:` + Custom topic 配下の `triggerQueries:` / `actions:` ツリー | §5.2 手順テンプレート |
| ナレッジの棚卸し | `kind: SearchAndSummarizeContent` ノード / `entity:` ブロック | §4 (ファイル検索) |
| Action (HTTP) の差分確認 | `kind: HttpRequestAction` の `url` / `method` / `headers` / `body` / `responseSchema` | §5.1 手順 5 (OpenAPI ツール) と OpenAPI 定義を突合 |
| エージェント本体メタデータ | root の `displayName` / `description` / `parentBotId` / `schemaName` | §5.1 手順 2 の名前 / 説明 |
| 移行漏れチェック | `kind:` 行を全件抽出 (`Select-String 'kind:' IT-Helpdesk-Sample.yaml`) し、§7 の左列と突合 | §7 マッピング表 |

#### 活用パターン B: YAML を使わず Copilot Studio portal を直接参照する (★ 本シナリオの推奨パス ★)

本シナリオは Topic 数が少ない (≤ 5) ため、**Microsoft Copilot Studio portal を開いたまま並行参照するのが最短** です。設計情報の出所はどちらでも同じ (= 00 で構築したエージェント) なので、結果は一致します。

| 必要な情報 | Copilot Studio portal での参照場所 | 00 の該当節 |
|---|---|---|
| エージェントの説明 / 基本情報 | 上部 `IT-Helpdesk-Sample` → **概要** タブ → **詳細** | 00 §2.3 |
| 手順 (= 旧 `指示` / Instructions) | **概要** タブ → **指示** | 00 §2.4 |
| **Primary AI Model** (エージェント単位のモデル選択) | 上部の **AI モデル** ドロップダウン (または **設定** → **AI モデル**)。既定は `GPT-4.1`。**抽出 YAML には含まれない** ため portal 必須 | (00 §2.5 はオーケストレーション モードのみ。Primary AI Model 選択は未収録 → portal で直接確認) |
| 生成 AI オーケストレーション モード | **設定** → **生成 AI** (`classic` / `generative`) | 00 §2.5 |
| Topic 一覧 / Trigger phrases / ノード ツリー | 左メニュー **トピック** → 各 Topic を開く | 00 §4 (Trigger §4.2 / Question §4.3 / Message §4.4) |
| ナレッジ ソース | 左メニュー **ナレッジ** | 00 §3.2 |
| Action (HTTP 要求の送信) の設定値 | 各 Topic 内の **HTTP 要求の送信** ノード | 00 §5.1 |
| エラー ハンドリング / Power Automate フロー版 | 各 Topic 内の **設定** / 分岐ノード | 00 §5.2 / §5.3 (補足) |
| 発行 (Publish) / チャネル設定 | 上部 **発行** ボタン / 左メニュー **チャネル** | 00 §7 |

> ℹ️ **推奨**: 「Copilot Studio portal を見て設定を確認 → Foundry portal に転記」の往復で進めると、YAML を読まずに完了できます。YAML grep は CI で構成差分を取りたいときや、移行漏れチェック (パターン A の最終行) に使ってください。

### 2.3 Foundry 側 (フェーズ 3〜5)

MS Learn 該当箇所: [Microsoft Foundry Agent Service の概要](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/overview)

| 項目 | 値 |
|---|---|
| Foundry portal | <https://ai.azure.com> (**新しい Foundry** スイッチ ON) |
| アーキテクチャ | **Foundry リソース → Foundry プロジェクト** (旧 Hub-based は非対応) |
| モデル | `gpt-4.1-mini` / `gpt-5-mini` 等 (Responses API 対応モデル) |
| RBAC | **Foundry User** (プロジェクト スコープ) + **Storage Blob Data Contributor** |
| リージョン | Responses API 対応 (ファイル検索は Italy North / Brazil South 不可) |
| ローカル ツール | **不要 (GUI 完結)**。Python / Azure CLI / Foundry SDK のインストールは行いません |

> ⚠️ `Cognitive Services User` / `Azure AI Developer` などの旧ロール名は **Foundry プロジェクトには適用されません**。新名称 **Foundry User** を使ってください。詳細は [Microsoft Foundry の RBAC](https://learn.microsoft.com/ja-jp/azure/ai-foundry/concepts/rbac-foundry)。

---

## 3. フェーズ 3: Foundry プロジェクトの準備

### 3.1 Foundry リソース + プロジェクトを作成

MS Learn 該当箇所 (Quickstart): [コードを使って最初の AI Foundry プロジェクトを作成する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/quickstarts/get-started-code)

1. <https://ai.azure.com> にサインイン → ヘッダー右上の **新しい Foundry** スイッチを ON
2. ホームの **新規作成** ボタン → 名前 / リージョン / Basic を入力して作成
3. 作成完了後、プロジェクトのホーム画面が開きます (以降の手順はこの画面の上部ナビ「**検出**」「**ビルド**」「**操作**」「**ドキュメント**」を使い分けます)

### 3.2 モデルをデプロイ

1. 上部ナビ **検出** → 左メニュー **モデル**
2. 一覧から `gpt-4.1-mini` を選択 (右上の検索ボックスでもフィルタ可能)
3. ヘッダーの **デプロイ** ボタンを押し、メニューから **既定の設定** (グローバル標準 / 既定のクォータ) を選択
4. デプロイ完了後、自動で **ビルド → モデル → プレイグラウンド** 画面に遷移します (このプレイグラウンドが §5 / §6 の作業場所になります)

> 💡 用途に応じて配置先 / SKU / クォータ / PTU / スピルオーバー / ガードレールを細かく決めたい場合は、ステップ 3 で **カスタム設定** を選択してください。

#### Copilot Studio との比較 — モデル選択で気をつける点

MS Learn 該当箇所: [Select a primary AI model for your agent](https://learn.microsoft.com/ja-jp/microsoft-copilot-studio/authoring-select-agent-model)

| 観点 | Copilot Studio (移行元) | Microsoft Foundry (移行先 / 本シナリオ) |
|---|---|---|
| モデル選択の自由度 | **エージェント単位で選択可** (既定 `GPT-4.1`)。GA: GPT-4.1 / GPT-5 Chat / Claude Sonnet 4.5・4.6 等 / Preview: GPT-5 Reasoning・Auto / Claude Opus 4.6 / Experimental: GPT-5.3〜5.5 / Claude Opus 4.7 / Grok 4.1 Fast | **必須選択** (1,900+ モデルから明示的にデプロイ。本シナリオは `gpt-4.1-mini`) |
| 00 (移行元) での該当節 | 00 §2.5 は **オーケストレーション モード** (= LLM ルーティング ON/OFF) の確認のみで、Primary AI Model の選択には触れていません。Copilot Studio portal を直接開いて選択中のモデルを確認してください | (該当なし — Foundry 固有の新規ステップ) |
| 抽出 YAML (`IT-Helpdesk-Sample.yaml`) での表現 | **モデル名は含まれない** (実機 YAML 全体を `model` / `gpt` / `primary` / `aiCapabilit` で grep しても 0 件。`configuration.settings.GenerativeActionsEnabled: true` のフラグだけが書き出される)。Primary AI Model はエージェント ランタイム属性扱いで template YAML には serialize されない仕様 | (該当なし — デプロイ後のエンドポイント設定で別管理) |
| 料金体系 | **メッセージ単価** (Microsoft Copilot Studio Messages の従量課金。モデル変更で消費メッセージ数が変わるケースあり) | **トークン課金** (input / output ごと。モデルにより単価差) — `../../docs/cost-finops.md` 参照 |
| リージョン制約 | モデルごとに利用可リージョンが異なる ([Select a primary AI model for your agent](https://learn.microsoft.com/ja-jp/microsoft-copilot-studio/authoring-select-agent-model) の Model availability by region 表参照)。`cross-geo` 表記のモデルはリージョン外でデータ処理される可能性あり | モデルごとに利用可リージョンが異なる。ファイル検索利用時は **Italy North / Brazil South 不可** |



### 3.3 RBAC を割り当てる

Azure portal で以下 3 つのロールを自分 (人間ユーザー) に割り当てます。CLI / スクリプトは使わず、Azure portal の **アクセス制御 (IAM)** で実施します。

| ロール | スコープ | 用途 |
|---|---|---|
| **Foundry User** | Foundry リソース | 人間ユーザー (プレイグラウンド / エージェント操作) |
| **Foundry Owner** | Foundry リソース | ファイル / ナレッジの管理 |
| **Storage Blob Data Contributor** | Storage Account | ファイル検索のバックエンド |

**Azure portal での割当手順** (各ロール共通):

1. <https://portal.azure.com> → 対象リソース (Foundry リソース、または Storage Account) を開く
2. 左メニュー **アクセス制御 (IAM)** → **+ 追加** → **ロールの割り当ての追加**
3. **ロール** タブ → 検索ボックスにロール名 (例: `Foundry User`) を入力 → 選択
4. **メンバー** タブ → **ユーザー、グループ、またはサービス プリンシパル** → **+ メンバーを選択する** → 自分を選択
5. **レビューと割り当て** → **割り当て**

Foundry User と Foundry Owner は Foundry リソース側で、Storage Blob Data Contributor は Foundry が自動作成した Storage Account 側で、同じ手順を 3 回繰り返してください。

> ℹ️ ホストされたエージェントから外部 API を呼び出す場合はプロジェクト マネージド ID にも同等のロールが必要ですが、本シナリオの動作確認 (プレイグラウンド) だけなら不要です。


---

## 4. フェーズ 3b: ナレッジ (`it-policy.md`) を準備する

MS Learn 該当箇所 (ファイル検索): [ファイル検索ツールを使用する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/file-search)

| 項目 | 上限 |
|---|---|
| 最大ファイル サイズ | 512 MB |
| 1 ファイルあたり最大トークン | 2,000,000 |
| 1 ナレッジあたり最大ファイル数 | 10,000 |
| 1 エージェントに紐づけ可能なナレッジ数 | **1** |

このフェーズでは特別な準備は不要です。Foundry portal のプレイグラウンドで Prompt agent を作る際 (§5.1 手順 4) に、左ペインの **ツール → 追加 → ファイル検索 → ファイルの参照 → アタッチ** で `it-policy.md` を直接添付すれば、内部的にファイル ストアが自動作成されます。

📁 アップロード対象ファイル (ローカルから選択): [`..\common\sample-knowledge\it-policy.md`](../common/sample-knowledge/it-policy.md)

> 💡 大量のファイルや SharePoint / Azure AI Search など複数ソースを束ねたい場合は、左ナビ **ビルド → ナレッジ** (Foundry IQ) で **ナレッジ ベース** / **インデックス** を作成し、Azure AI Search リソースを **接続する** ことで永続的に管理できます (本シナリオでは省略)。


---

## 5. フェーズ 4: Prompt agent を作成

### 5.1 Foundry portal のプレイグラウンドから作成

§3.2 でモデルをデプロイすると、自動的に **ビルド → モデル → プレイグラウンド** 画面 (URL: `.../build/models/deployments/<model>/playground`) が開きます。この画面で手順とツールを設定し、最後に「**エージェントとして保存**」することで Prompt agent になります。

> 💡 まっさらな状態から始めたい場合は、上部ナビ **ビルド** → 左メニュー **エージェント** → 右上の **エージェントの作成** ボタンでも作成できます (この場合は名前を入力して空のエージェントが作られた後、同じプレイグラウンド画面で手順 / ツールを設定します)。

**手順**:

1. プレイグラウンド画面左ペインの **モデル** が `gpt-4.1-mini` (= §3.2 でデプロイしたモデル) になっていることを確認
2. **手順** セクションに §5.2 のテンプレートをそのまま貼り付け
3. **ツール** セクション → **追加** ボタン → メニューから **ファイル検索** を選択
   - 開いた **ファイルの添付** パネルで **ファイルの参照** → §2.1 で確認した [`..\common\sample-knowledge\it-policy.md`](../common/sample-knowledge/it-policy.md) を選択 → **アタッチ**
4. OpenAPI ツールを登録します。OpenAPI ツールはプレイグラウンドの **ツール → 追加** メニューには直接出ないため、いったん上部ナビ **ビルド** で先に登録してから紐付けます:
   - 上部ナビ **ビルド** → 左メニュー **ツール** → **ツール** タブ → **ツールを接続** → **カスタム** タブ → **OpenAPI ツール** を選択 → **作成**
   - 開いた **OpenAPI ツールの作成** ダイアログで以下を入力:

     | 項目 | 値 |
     |---|---|
     | **名前** | `create_ticket` |
     | **説明** | `社内 IT ヘルプデスクのチケットを起票します` |
     | **認証方法** | **接続** (本シナリオの公開エンドポイントは認証不要のため、§5.3 の注記を参照) |
     | **接続** | **新しい接続の追加** (匿名アクセスでよい場合は接続を「なし」相当で作成) |
     | **OpenAPI 3.0+ スキーマ** | [`..\common\tools\create-ticket.openapi.yaml`](../common/tools/create-ticket.openapi.yaml) の中身を全選択コピーして貼付 |

   - **ツールの作成** を押す → 一覧に `create_ticket` が表示される
5. プレイグラウンド画面に戻り、左ペイン **ツール → 追加** から先ほど作成した `create_ticket` を選択してエージェントに紐付ける
6. 画面上部の **エージェントとして保存** をクリック → 名前 `helpdesk-prompt` を入力して保存
7. 保存後、自動で **ビルド → エージェント → `helpdesk-prompt`** 画面に遷移します。以降の動作確認は §6 へ

> 💡 設定はすべて自動保存されます。明示的な保存ボタンは「**エージェントとして保存**」のときだけ押します。

### 5.2 手順テンプレート (Copilot Studio Topic の言語化)

00 §2.4 で Copilot Studio に書いた手順 (= 旧 `指示` / Instructions) と同等の内容です。**portal の 手順 欄にこのまま貼り付けてください**。

> 💡 **YAML との対応**: §2.2 パターン A で抽出 YAML を使う場合、root の `description:` フィールド + 各 Custom topic の `triggerQueries:` (= 「ユーザーが〜と言ったとき」の節) と `dialog.beginDialog.actions:` ツリー (= 番号付き手順) を段落化したものが、おおむね下記テンプレートに対応します。Topic を追加したらこの順序で言語化を追記してください。

```
あなたは Contoso 株式会社の社内 IT ヘルプデスク アシスタントです。

# 基本ルール
- 添付されたナレッジ (社内 IT 利用規定) から根拠を [filename] 付きで引用する
- パスワード / MFA コード / PIN など秘密情報をユーザーに尋ねない
- 緊急インシデント (情報漏えい・進行中の攻撃) は CSIRT ホットライン (内線 119) を案内する

# Topic: パスワード忘れ / ロックアウト
ユーザーが「パスワードを忘れた」「ロックアウト」と言ったとき:
  1. 「社内 PC からのご利用ですか、社外 PC ですか?」と確認する
  2. 「社内」→ セルフサービス ポータル https://passwordreset.contoso.local を案内
  3. 「社外」→ IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) を案内
  4. ロックアウトは 5 回失敗で発生、30 分後に自動解除と補足

# チケット起票ルール
- ナレッジでセルフサービス手順が見つからない、または手順実行後も解決しなかった場合のみ
- 起票前に必ずユーザーの同意を得る
- summary (80 字以内) / priority / category を判断して埋める
```

### 5.3 OpenAPI ツールの認証

新しい Foundry portal (新しい Foundry スイッチ ON) では、OpenAPI ツールの認証は **接続オブジェクト経由に統一** されています。**OpenAPI ツールの作成** ダイアログでは「認証方法」が **接続** 固定になり、以下を組み合わせて設定します。

| 用途 | 接続の作り方 | ダイアログでの選び方 |
|---|---|---|
| **公開エンドポイント (匿名)** — 本デモはこれ | 接続を作らず、ダイアログの **接続** で **新しい接続の追加** から最小限の匿名扱いで登録 | **認証方法**: 接続 / **接続**: 新規 / **資格情報**: 空のままでも可 |
| **API キー** | 上部ナビ **ビルド** → プロジェクト設定や接続管理画面で API キー接続を事前作成 | **接続**: 作成した API キー接続を選択 / **資格情報**: キー名と値を入力 |
| **マネージド ID** | プロジェクトに紐付くマネージド ID を持つリソースとして接続を作成 | **接続**: マネージド ID 接続を選択 |

MS Learn 該当箇所: [OpenAPI で指定されたツールを使用する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/openapi-spec)

> 💡 旧 portal にあった「Anonymous / API Key / Managed Identity」のドロップダウンは新エクスペリエンスでは廃止され、すべて「接続」オブジェクトで管理する設計になりました。本デモのサンプル OpenAPI は架空エンドポイントなので、接続を作成しても実際にネットワーク呼出は成功しません (会話ログでツール呼出の挙動だけ確認できます)。


---

## 6. フェーズ 5: プレイグラウンドで動作確認

1. <https://ai.azure.com> → 対象プロジェクト → 上部ナビ **ビルド** → 左メニュー **エージェント** → `helpdesk-prompt` を選択 → 画面右側の **プレイグラウンド** タブをクリック (§5.1 から続いて開いていれば既に表示されています)
2. 画面下部のチャット ボックスに下記テスト メッセージを順に投げ、応答と右ペインの **スレッド ログ** / **トレース** タブを確認

| # | テスト メッセージ | 期待動作 |
|---|---|---|
| 1 | `MFA の登録方法を教えて` | ファイル検索で `it-policy.md` §2.2 を引用 ([filename] 付き) |
| 2 | `パスワードを忘れた、社内 PC です` | セルフサービス URL `https://passwordreset.contoso.local` を案内、チケット起票しない |
| 3 | `パスワードを忘れた、社外 PC です` | IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) を案内 |
| 4 | `VPN がつながらない、再起動しても直らない` | 同意を取って CreateTicket を提案 (OpenAPI ツール呼出) |
| 5 | `私の PIN を教えて` | 拒否 + CSIRT 案内 |

3. 右ペインのトレース表示で:
   - 1 / 2 / 3 → **file_search** の引用が `it-policy.md` を指す
   - 4 → **openapi tool** (`create_ticket`) の呼出が出ている
   - 5 → ツール呼出なし (手順の安全ルールで拒否)

> 💡 プレイグラウンドのチャット履歴は自動保存されます。会話をリセットしたいときは、チャット上部の **新しいスレッド** (またはゴミ箱アイコン) で初期化してください。


---

## 7. マッピング表: Copilot Studio → Prompt agent

各行の **「Copilot Studio 側の参照箇所」列** は §2.2 のパターン A (YAML) / パターン B (portal) のどちらでも辿れるよう、両方の場所を併記しています。

| Copilot Studio 要素 | Copilot Studio 側の参照箇所 (portal / YAML) | Prompt agent 側 (Foundry portal の操作) |
|---|---|---|
| Description | portal: **概要** タブ → **詳細** / YAML: root の `description:` | ビルド > エージェント > 対象エージェント > **概要** に説明を記入 |
| 指示 (Instructions) | portal: **概要** タブ → **指示** / YAML: root の `instructions:` | プレイグラウンド左ペイン > **手順** に貼付 (8,000 文字 → 制限なし) |
| Topic (Trigger phrases + ノード) | portal: 左メニュー **トピック** → 各 Topic / YAML: `kind: AdaptiveDialog` 配下の `triggerQueries:` + `actions:` | **すべて 手順 に言語化**。Trigger 句は「ユーザーが〜と言ったとき」、ノードは番号付き手順 |
| Question ノード | portal: Topic 内の **質問** ノード / YAML: `kind: Question` | LLM が自然言語で逆質問 (**確定的ではない**) |
| Power Fx 条件 | portal: Topic 内の **条件** ノード / YAML: `kind: ConditionGroup` (`condition:` に Power Fx 式) | 手順 内の条件文 (`もし X なら…` 等) |
| Knowledge (ファイル アップロード) | portal: 左メニュー **ナレッジ** / YAML: `kind: SearchAndSummarizeContent` ノード + `entity:` (`accessControlPolicy`) | プレイグラウンドの **ツール → 追加 → ファイル検索 → ファイルの添付** (= §5.1 手順 3) |
| Knowledge (SharePoint) | portal: 左メニュー **ナレッジ** → SharePoint ソース / YAML: 同上 (`entity:` に SharePoint 設定) | プレイグラウンドの **ツール → 追加 → SharePoint** で接続 (= ビルド > ナレッジ の Foundry IQ でも管理可) |
| Action (HTTP 要求) | portal: Topic 内の **HTTP 要求の送信** ノード / YAML: `kind: HttpRequestAction` (`url` / `method` / `headers` / `body` / `responseSchema`) | **ビルド > ツール > ツールを接続 > カスタム > OpenAPI ツール** で OpenAPI 3.0+ スキーマを登録 → プレイグラウンドのツールに紐付け (= §5.1 手順 4) |
| Action (Power Automate フロー) | portal: Topic 内の **フローを実行** ノード / YAML: Solution エクスポート側で取得 (00 §8.5 注記参照) | Flow を独立 API 化 → OpenAPI ツールで接続、または シナリオ C で再実装 |
| Adaptive Card | portal: 各メッセージ ノードの **カード** / YAML: `kind: SendActivity` の `card:` ブロック | Prompt agent では非対応 → クライアント側で再実装 |

---

## 8. 利点と欠点

| | 内容 |
|---|---|
| ✅ **利点** | GA で SLA 対象 / 最速本番化 / 1,900+ モデル選択可 / **Foundry portal だけで完結 (RBAC + ナレッジ + エージェント + プレイグラウンド)** / コード記述ゼロ / Responses API による履歴自動管理 |
| ❌ **欠点** | 確定的フロー (必ず質問→分岐) は LLM 任せで保証されない / Topic 多いと 手順 が肥大化 / Adaptive Card 非対応 |

---

## 9. トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| Foundry portal で `Permission denied` でエージェント作成不可 | Foundry User 未割り当て | §3.3 を実施 |
| プレイグラウンドの ファイル検索 で参照が出ない | ファイル ingestion 未完了 | プレイグラウンドの **ツール → ファイル検索** で添付ファイルのステータスが完了になっているか確認 (数十秒〜数分待つ) |
| プレイグラウンドで OpenAPI ツールが呼ばれない | 手順 のチケット起票ルールが弱い / 接続設定の誤り | §5.2 と §5.3 を見直し、ビルド > ツール 側の OpenAPI ツールが正しく作成され、プレイグラウンドで紐付け済みか確認 |
| Italy North / Brazil South で ファイル検索 エラー | 地域制限 | 別リージョンにプロジェクトを作成 |

---

## 10. セキュリティ (Content Filter / Prompt Shields / XPIA / PII)

> 📄 詳細は **[`docs/security.md`](./docs/security.md)** を参照してください。Microsoft Learn からの verbatim 引用とともに、portal の操作手順を載せています。

本シナリオは社内 IT 規定 Markdown を ファイル検索 経由で読み込むため、**間接プロンプト インジェクション (XPIA: cross-prompt injection attack)** の現実リスクがあります。Microsoft Foundry の Content Filter は次の 4 種類の保護を提供しており、本番運用前に最低でも (1)(2)(3) を有効化することを推奨します。

| # | 保護 | 何を防ぐか | 公式 verbatim | 推奨 |
|---|---|---|---|---|
| 1 | **User prompt attacks (jailbreak)** | ユーザーが安全ガイドラインを迂回しようとする攻撃 | "Classifies user prompts as either safe or as attempting to manipulate the model's behavior" | 入力フィルタで有効化 |
| 2 | **Indirect attacks (XPIA)** | ナレッジ・OpenAPI レスポンス・MCP 等、**第三者コンテンツ経由の注入** | "Detects prompt injection attacks where third-party content (such as documents or web pages) attempts to manipulate the model" | 入力フィルタで有効化 (本シナリオで必須) |
| 3 | **PII Detection** | 出力に個人情報が含まれていないか | "Detects personal information in model output" | 出力フィルタで有効化 |
| 4 | **Task Adherence** | エージェントが付与されたタスクから逸脱していないか | "Evaluates whether the agent's response adheres to the task assigned to it" | 任意 (エージェント モード) |

設定手順 (要旨):

1. Foundry portal → 上部ナビ **ビルド** → 左メニュー **ガードレール** → **+ コンテンツ フィルターの作成**
2. 入力フィルタ: User prompt attacks / Indirect attacks を有効
3. 出力フィルタ: PII Detection を有効
4. モデル デプロイの **コンテンツ フィルター** プルダウンで作成したフィルタを選択

詳細は `docs/security.md` を参照。

---

## 11. 同梱ファイル

| ファイル | 用途 |
|---|---|
| `README.md` | 本ファイル |
| `docs\security.md` | Content Filter / Prompt Shields / XPIA / PII の設定手順 (§10 から参照) |
| `requirements.txt` / `create_prompt_agent.py` | (本シナリオでは未使用) GUI 完結方針のため Foundry portal だけで完結します。CI 化やコード再現用のリファレンス実装として残置 |

> ℹ️ **本シナリオは Foundry portal だけで完結する GUI 方針です。** Python ファイルや CLI コマンドの実行は一切不要です。RBAC は Azure portal、ナレッジ・エージェント・ツールはすべて Foundry portal で設定します。

---

## 12. 関連公式ドキュメント

| トピック | URL |
|---|---|
| Foundry Agent Service 概要 | [Microsoft Foundry Agent Service の概要](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/overview) |
| Prompt agent Quickstart | [コードを使って最初の AI Foundry プロジェクトを作成する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/quickstarts/get-started-code) |
| ファイル検索ツール | [ファイル検索ツールを使用する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/file-search) |
| OpenAPI ツール | [OpenAPI で指定されたツールを使用する](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/how-to/tools/openapi-spec) |
| Responses + Conversations API | [Microsoft Foundry Agent Service のランタイム コンポーネント](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/concepts/runtime-components) |
| RBAC (Foundry) | [Microsoft Foundry の RBAC](https://learn.microsoft.com/ja-jp/azure/ai-foundry/concepts/rbac-foundry) |
| 環境セットアップ | [Foundry Agent Service の環境セットアップ](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/environment-setup) |
| Limits / Quotas / Regions | [Foundry Agent Service の制限・クォータ・リージョン](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/concepts/limits-quotas-regions) |

---

## 13. 関連シナリオ・補助ドキュメント

| ドキュメント | 何が補強されるか |
|---|---|
| [`../scenario-d-cs-plus-foundry/README.md`](../scenario-d-cs-plus-foundry/README.md) | Copilot Studio を温存して本シナリオ A の Prompt agent を **Add an agent** で接続する (Preview) |
| [`../scenario-h-apim-ai-gateway/README.md`](../scenario-h-apim-ai-gateway/README.md) | Foundry endpoint を **Azure API Management** 経由化し、tokens-per-minute / semantic cache / `<llm-emit-token-metric>` を一元適用 |
| [`../../docs/governance.md`](../../docs/governance.md) | RBAC (GUID 指定) / Content Filter (Prompt Shields / XPIA / PII) / Preview terms の横断チェックリスト |
| [`../../docs/cost-finops.md`](../../docs/cost-finops.md) | gpt-4.1-mini / gpt-5-mini 月額試算 + Vector Store ($0.10/GB/日) + 削減アクション |