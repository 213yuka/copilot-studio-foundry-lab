# 00. 共通: Copilot Studio で IT ヘルプデスク エージェントを作成する

> 本書はシナリオ A〜D の **共通の出発点** です。各シナリオ README から `..\00-create-cs-agent.md` として参照されます。
> 4 シナリオはいずれも、ここで作る同一の Copilot Studio エージェント (**IT-Helpdesk-Sample**) を出発点に、Foundry 側の受け皿を変えていく構成です。

---

## 0. このフェーズで作るもの

| 要素 | 内容 |
|---|---|
| エージェント名 | `IT-Helpdesk-Sample` |
| 説明 | Contoso 社内 IT ヘルプデスク。社内 IT 利用規定を引用し、必要時のみチケットを起票 |
| 言語 | 日本語 |
| Generative orchestration | **ON** (既定) |
| Knowledge | `it-policy.md` (本リポジトリ `common/sample-knowledge/`) を File upload で登録 |
| Topic | `PasswordReset` — Question + Power Fx 条件で社内 PC / 社外 PC 分岐 |
| Action | `CreateTicket` — HTTP Request ノードでチケット起票エンドポイントを呼び出し |

最後に **`pac copilot extract-template`** で YAML テンプレートをエクスポートし、シナリオ A〜D のいずれかの Foundry 受け皿に渡します。

---

## 1. 前提条件

### 1.1 ライセンス

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions>

主なライセンスの種類:

- **Copilot Studio (Standalone)** — 全機能利用可
- **Copilot Studio for Teams plan** (一部 Microsoft 365 サブスクリプションに同梱) — 機能制限あり
- **Trial** (30 日、サインアップ: <https://go.microsoft.com/fwlink/?LinkId=2107702>) — デモ・検証用

> 各ライセンスの適用範囲・価格・割り当て方法などの詳細は割愛します。導入検討時は **担当営業 / Microsoft パートナー** にご相談ください。デモ目的であれば Trial で十分です。

### 1.2 環境 (Power Platform Environment)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience>

- 初回サインインで既定環境が自動作成されますが、**本番想定のデモなら別途 Production 環境を作るのが推奨**
- 作成場所: <https://admin.powerplatform.com> → Environments → New
  - Region (データ存在地域)、Type = **Production**、Dataverse = **Yes** を必ず指定
- **注意:** Power Platform admin center に表示される「Microsoft 365 Copilot Chat」環境は M365 Copilot の課金管理用です。**Copilot Studio エージェントの構築には使わないこと**

### 1.3 Maker 権限

- 最低限: 環境内で **agent author** セキュリティロール
- 後段のソリューション エクスポートに **System Customizer** ロールも必要

---

## 2. Phase 1 — Copilot Studio ポータルでエージェントを新規作成

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot>

### 2.1 サインインと環境選択

1. **<https://copilotstudio.microsoft.com>** にサインイン
2. 画面上部の **環境セレクター** で対象環境を選択 (作成後に変更不可ではないが、別環境で作ったエージェントは別物として扱われる)

### 2.2 エージェント作成 (Blank パスを推奨)

デモ再現性確保のため、AI 自動生成 (Describe) ではなく **Blank** から始めます。

1. ホーム → **Create an agent** → "Start building from scratch"
2. もしくは Agents 一覧 → **Create blank agent**
3. 詳細を指定 (右の **Advanced create** 推奨):
   - **Primary language**: 日本語 (⚠️ **作成後に変更不可**)
   - **Solution**: 後で `pac` 抽出する場合は任意の Solution に入れておくと管理しやすい
   - **Schema name**: 例 `it_helpdesk_sample`
4. **Confirm and create**

### 2.3 基本情報の入力 (Overview ページ)

| フィールド | 値 |
|---|---|
| **Name** | `IT-Helpdesk-Sample` (最大 42 文字、`< >` 不可) |
| **Description** | `Contoso 社内 IT ヘルプデスク。社内 IT 利用規定から回答し、必要に応じてチケットを起票する` |
| **Instructions** | (次の §2.4) |
| **Suggested prompts** | (任意) `パスワードを忘れた` / `VPN がつながらない` / `MFA を再登録したい` |
| **Agent icon** | PNG 192×192 / 72 KB 未満 (任意) |

### 2.4 Instructions (動作ガイダンス、最大 8,000 文字)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot>

```
あなたは Contoso 株式会社の社内 IT ヘルプデスク アシスタントです。

# 基本ルール
- ナレッジ (社内 IT 利用規定) を根拠に [filename] 付きで回答する
- パスワード / MFA コード / PIN 等の秘密情報をユーザーに尋ねない
- 緊急インシデント (情報漏えい・進行中の攻撃) は CSIRT ホットライン (内線 119) を案内する
- 解決しない場合のみ CreateTicket を呼び出してチケットを起票する (ユーザー同意必須)
```

> 💡 Generative orchestration が ON のとき、Instructions は **agent 全体の動作指針**。Topic は「明示的に確定的なフローを残したいケース」に絞ります。

### 2.5 Generative orchestration の確認

- 新規作成エージェントは **既定で ON**
- 確認/変更: 上部メニュー **Settings** → **Generative AI** → **Orchestration**
- ON のとき、Topic は Trigger phrase ではなく **Description** で選ばれます (この区別が後段の Foundry 移行時に重要)

---

## 3. Phase 2 — Knowledge ソースを追加 (it-policy.md)

公式 (概要): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-existing-copilot>
公式 (file upload): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload>

### 3.1 サポート形式と上限

| 項目 | 値 |
|---|---|
| 最大ファイル サイズ | 512 MB / 1 ファイル |
| 最大ファイル数 | 500 / 1 エージェント |
| 主要対応形式 | `.md` / `.txt` / `.pdf` / `.docx` / `.pptx` / `.xlsx` / `.html` / `.csv` / `.json` / `.yaml` 他 |
| 非対応 | 暗号化/機密ラベル付きファイル、画像・動画・実行可能ファイル |
| **前提** | 環境で **Dataverse search 有効化** が必要 (admin に確認) |

### 3.2 it-policy.md を登録する手順

1. 左メニュー **Knowledge** → **Add knowledge**
2. **Files** タブを選択
3. `demo-assets\common\sample-knowledge\it-policy.md` をドラッグ&ドロップ
4. **Name**: `IT Security Policy 2026`
5. **Description**: `Contoso のアカウント / MFA / VPN / SaaS / インシデント対応 / リモートワークに関する社内 IT 利用規定`
   - ⚠️ **Generative orchestration が ON のときは Description が必須**。エージェントが「どの問い合わせでこのナレッジを引くか」を判断する根拠になります
6. **Add to agent**
7. ステータスが **Ready** になるまで待機 (md なら 30〜60 秒)

---

## 4. Phase 3 — Topic を作成 (PasswordReset)

公式 (作成): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics>
公式 (Question): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-ask-a-question>
公式 (Condition + Power Fx): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-using-conditions>
公式 (Trigger phrase): <https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/trigger-phrases-best-practices>

### 4.1 Topic 新規作成

1. 左メニュー **Topics** → **Add a topic** → **From blank**
2. キャンバスが開く (Trigger ノードのみ)
3. 上部 **Details** → **Name** = `PasswordReset` (⚠️ **名前にピリオド `.` を含めない** — solution export で破損)
4. Description (Generative orchestration 向け):
   `ユーザーが社内システムのパスワードを忘れた、またはアカウントがロックアウトされたときに使用する。社内 PC / 社外 PC で案内先が異なる手順を提供する。`

### 4.2 Trigger phrase

Trigger ノード → **Properties** → **Phrases** タブ:

```
パスワードを忘れた
パスワードがわからない
ロックアウト
ログインできない
パスワードリセット
アカウントがロックされた
パスワードを変更したい
```

ベスト プラクティス (公式より):
- **5〜10 件以上**、語順や用語のバリエーションを変える
- **10 単語以内**、単語 1 つだけの trigger は避ける
- 最大 200 phrase / Topic

### 4.3 Question ノード — 社内 PC か 社外 PC か

1. Trigger ノード下の **+** → **Ask a question**
2. **Enter a message**: `お使いの PC は社内 PC ですか、社外 PC ですか？`
3. **Identify**: **Multiple choice options** を選択
4. **Options for user** に追加:
   - `社内PC`
   - `社外PC`
5. **Save user response as** → 変数名を `PCType` にリネーム (型は自動的に **Choice**)

### 4.4 Condition ノード — Power Fx で分岐

1. Question ノード下の **+** → **Add a condition**
2. 既定で 2 分岐 (Condition / All Other Conditions)
3. **Condition 分岐**:
   - Select a variable → `Topic.PCType`
   - Operator → `is equal to`
   - Value → `社内PC`
4. Condition ノード上で **…** → **Change to formula** で Power Fx 直書きも可:
   ```
   Topic.PCType = "社内PC"
   ```

#### 各分岐に Message ノードを追加

**社内 PC 分岐:**
```
社内 PC をお使いの場合は、セルフサービス リセット ポータル
https://passwordreset.contoso.local
から再設定してください。アカウントは 5 回失敗で 30 分間ロックされます。
```

**社外 PC 分岐 (All Other Conditions):**
```
社外 PC の場合は IT ヘルプデスク (内線 8888 / helpdesk@contoso.com)
にご連絡ください。
```

### 4.5 Power Fx 変数スコープ参考

| Scope | Prefix | 例 |
|---|---|---|
| Topic local | `Topic.` | `Topic.PCType` |
| Global (全 Topic 共通) | `Global.` | `Global.UserName` |
| System | `System.` | `System.Conversation.Id` |
| Environment variable | `Environment.` | `Environment.ServiceURL` |

> ⚠️ **Foundry の Workflow agent は `Topic.*` / `Global.*` 非対応。** すべて `Local.*` に書き換える必要があります (シナリオ B の README で詳述)。

### 4.6 Save

右上 **Save** をクリック (Topic 単位で保存)。

---

## 5. Phase 4 — Action を追加 (CreateTicket HTTP Request)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-http-node>

`demo-assets\common\tools\create-ticket.openapi.yaml` の OpenAPI 仕様を参考に、Copilot Studio では **HTTP Request ノード** で同等処理を構築します。

### 5.1 HTTP Request ノードを追加

PasswordReset Topic 内の適切な位置 (チケット起票が必要な分岐) で:

1. **+** → **Advanced** → **Send HTTP request**
2. **URL**: `https://httpbin.org/post` (デモ用エンドポイント)
3. **Method**: `POST`
4. **Headers and body → Edit**
5. **Headers**:
   - `Content-Type: application/json`
6. **Body**: **JSON content** → **Formula** モード:
   ```
   {
     summary: "パスワードリセットの相談",
     priority: "medium",
     category: "account",
     user_consent: true
   }
   ```
7. **Response data type**: **From Sample Data** → サンプル貼り付け:
   ```json
   { "ticket_id": "TK-1234", "status": "created" }
   ```
   → **Confirm** (型付き変数が自動生成)
8. **Save user response as**: `Topic.TicketResponse`
9. レスポンスは後続ノードで `Topic.TicketResponse.ticket_id` のように参照

### 5.2 Error handling

- 既定: **Raise an error** → System の `On Error` Topic が発火
- 代替: **Continue on error** → Status code / error body 用変数を設定し、Topic 内で復旧処理

### 5.3 Power Automate Flow 版 (代替)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow-create>

- 既存の Logic Apps / Power Automate 資産がある場合はこちら
- Trigger: **"When an agent calls the flow"**
- Response: **"Respond to the agent"** (Async モードは **OFF** 必須、応答は 100 秒以内)
- 入出力パラメータを定義して Copilot Studio 側の Topic 変数とマップ

---

## 6. Phase 5 — Test pane で動作確認

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot>

1. 画面右上 **Test** トグルをオン
2. テスト用入力:
   - `パスワード忘れた` → PasswordReset Topic が発火することを確認
   - 選択肢 `社内PC` をクリック → 社内案内メッセージ
   - 別セッション (Reset アイコン) で `社外PC` を試す → 社外案内メッセージ
3. ナレッジ参照テスト: `MFA はどう設定する?` → it-policy.md からの引用 + `[filename]` 出典
4. **Track between topics** トグル ON で Topic 間の遷移可視化
5. 必要なら **三点リーダー → Save snapshot** で `botContent.zip` をダウンロード (障害時の調査用)

> ⚠️ **既知の制約**: タイマー / 非アクティブ トリガーは Test pane で発火しません。実チャネル経由でのみテスト可能。

---

## 7. Phase 6 — Publish (任意)

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels>

シナリオ D (Copilot Studio + Foundry 併用) を行う場合、Copilot Studio 側を Teams または M365 Copilot に Publish した状態にしておくことが推奨です。シナリオ A〜C のみであれば Publish 不要。

1. 上部 **Publish** → **Publish**
2. **Channels** ページで Teams / M365 Copilot / Demo Website 等を追加
3. Publish 後の変更は **新しい会話セッション**から反映 (約 30 分の inactivity でセッション切れ)

---

## 8. Phase 7 — pac CLI でエクスポート (移行の核心)

シナリオ A〜D のいずれでも、ここで取得した YAML が Foundry 側の設計インプットになります。

### 8.1 pac CLI のインストール

公式: <https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction>

```powershell
# .NET Tool 経由 (推奨、cross-platform)
dotnet tool install --global Microsoft.PowerApps.CLI.Tool

# 動作確認
pac
```

代替: Windows MSI / VS Code 拡張 **"Power Platform Tools"**

### 8.2 認証

公式: <https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/auth>

```powershell
# 対話 OAuth ログイン
pac auth create

# 環境を指定したい場合
pac auth create --environment "Contoso-Dev"

# 一覧確認
pac auth list
```

### 8.3 Bot ID の取得

公式: <https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot#pac-copilot-list>

```powershell
pac copilot list --environment <ENVIRONMENT-GUID>
```

出力例:
```
Name                  Bot ID                                Component State  Is Managed  Status Code
IT-Helpdesk-Sample    9ee3f7aa-ab79-4cf6-a726-d85c8c18cc3e  Published        Unmanaged   Active
```

### 8.4 テンプレート エクスポート

公式: <https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot#pac-copilot-extract-template>

```powershell
pac copilot extract-template `
   --environment <ENVIRONMENT-GUID> `
   --bot 9ee3f7aa-ab79-4cf6-a726-d85c8c18cc3e `
   --templateFileName IT-Helpdesk-Sample.yaml
```

> ⚠️ **重要 — 出力形式**:
> `pac copilot extract-template` の出力は **単一の YAML ファイル** です。`bot.yaml + topics/ + actions/ + knowledge/` のディレクトリ構造ではありません。Topics / Entities などすべての要素が 1 ファイルにシリアライズされます。
>
> 過去の社内資料で「ディレクトリ構造で抽出される」と書かれていたら、それは `pac solution export` + `pac solution unpack` の話です (こちらは Solution 全体を unzip + 分解する別コマンド)。

### 8.5 抽出に含まれる / 含まれない要素

公式: <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-bots>

| 区分 | 内容 |
|---|---|
| ✅ **含まれる** | Name / Description / Instructions / 全 Custom topic (nodes 含む) / Entities / Variables / Schema name |
| ⚠️ Solution export 限定 | Power Automate Flow (Add required objects 必須) / 環境変数の **定義のみ** (値は除外) |
| ❌ **含まれない** | **Knowledge ファイルの中身** / SharePoint / 公開 Web URL の再設定 / Connection の認証情報 / Adaptive Card の外部 URL 資産 / アイコン / Channel 設定 / Conversation ID 等の環境固有 ID / コメント |

つまり Foundry 側では、少なくとも以下を **手動で再構築** する必要があります:
- Knowledge (it-policy.md を Foundry の Vector Store に再アップロード)
- Connection / API キー / 認証情報
- Channel (Teams / Web / M365 等)
- Adaptive Card (使用していれば)

### 8.6 Solution 経由のフル エクスポート (代替)

Flow / 環境変数 / カスタム コネクタも含めて移行したい場合は **Solution エクスポート/インポート** を使用:

1. Copilot Studio ポータル → **Settings** → **Solutions** → Custom (Unmanaged) solution 作成
2. 既存エージェント追加 → **Advanced** → **Add required objects** で関連 Flow / Connector を取り込み
3. Export (Unmanaged のみ可能)
4. ターゲット環境で Import

---

## 9. 抽出した YAML を Foundry へ — シナリオ別に分岐

ここから先はシナリオによって受け皿が変わります。Microsoft Foundry agent を作るルート (A〜C / D)、Microsoft Copilot Studio を温存しつつモデル / MCP だけ Microsoft Foundry に頼るルート (E / F) の **6 通り** が用意されています:

| シナリオ | レイヤー | Foundry での受け皿 | YAML / 抽出物の使い方 | 状態 | 詳細 README |
|---|---|---|---|---|---|
| **A** | エージェント本体 (移行) | Prompt agent | Instructions / Knowledge 接続 / Action OpenAPI を Python SDK で 1 体登録 | ✅ GA | [`scenario-a-prompt-agent\README.md`](scenario-a-prompt-agent/README.md) |
| **B** | エージェント本体 (移行) | Workflow agent | Topic ダイアログ ツリーを Workflow YAML / ビジュアル ビルダーに変換 | ⚠️ Preview | [`scenario-b-workflow-agent\README.md`](scenario-b-workflow-agent/README.md) |
| **C** | エージェント本体 (移行) | Hosted agent | コードで再実装し、コンテナとして ACR → Foundry 登録 | ⚠️ Preview | [`scenario-c-hosted-agent\README.md`](scenario-c-hosted-agent/README.md) |
| **D** | エージェント間連携 | Foundry agent を `Add an agent` で接続 | Microsoft Copilot Studio をそのまま残し、Foundry agent (= A/B/C) を `Add an agent → Microsoft Foundry` で接続 | ⚠️ Preview | [`scenario-d-cs-plus-foundry\README.md`](scenario-d-cs-plus-foundry/README.md) |
| **E** | モデル / ツール単位 | Foundry モデル デプロイ (BYOM) | Microsoft Copilot Studio の Prompt ツールの **Model** に Foundry モデルを接続 (YAML は使わず、Prompt Instructions を新規作成) | ✅ GA | [`scenario-e-byom-foundry-model\README.md`](scenario-e-byom-foundry-model/README.md) |
| **F** | モデル / ツール単位 | MCP server (Foundry / 任意ホスト) | Microsoft Copilot Studio の Tools に `Model Context Protocol` で接続 (YAML は使わず、MCP server 側の tool 定義を利用) | ✅ GA | [`scenario-f-mcp-connection\README.md`](scenario-f-mcp-connection/README.md) |

> 💡 **シナリオ A〜D は `pac copilot extract-template` の YAML が設計インプット**になります。E / F は Microsoft Copilot Studio エージェント本体を変更しない (Prompt / Tool を追加するだけ) ため、YAML 抽出は必須ではありません (構成変更後の差分管理用に取得しておくのは推奨)。

---

## 10. クイック リファレンス: 公式ドキュメント

| トピック | URL |
|---|---|
| Copilot Studio ライセンス比較 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-licensing-subscriptions> |
| 環境の初期構成 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/environments-first-run-experience> |
| エージェント作成 (Quickstart) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-first-bot> |
| Knowledge 全般 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio> |
| Knowledge (File upload) | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-file-upload> |
| Topic 作成 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics> |
| Trigger phrase 設計指針 | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/trigger-phrases-best-practices> |
| Question ノード | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-ask-a-question> |
| Condition + Power Fx | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-using-conditions> |
| Power Fx in Copilot Studio | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-power-fx> |
| HTTP Request ノード | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-http-node> |
| Power Automate Flow Action | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-flow-create> |
| Test pane | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-test-bot> |
| Publish / Channels | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels> |
| Solution Export/Import | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-bots> |
| pac CLI インストール | <https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction> |
| pac auth | <https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/auth> |
| pac copilot | <https://learn.microsoft.com/en-us/power-platform/developer/cli/reference/copilot> |
| Quotas / Limits | <https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-quotas> |
