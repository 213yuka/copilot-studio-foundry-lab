# Microsoft Copilot Studio — 過去1年（2025年5月〜2026年5月）のアップデート調査レポート

> **調査期間：** 2025年5月 〜 2026年5月
> **最終更新の出典基準日：** Microsoft Learn の What's new ページが `2026-05-15` 更新時点[^1]
> **主要出典：** Microsoft Learn 公式ドキュメント、Microsoft 365 Copilot 公式ブログ、Power Platform Release Plan、Microsoft Build 2025 セッションブログ

---

## 1. エグゼクティブサマリー

過去1年間（2025年5月〜2026年5月）、Microsoft Copilot Studio は **ローコードチャットボット作成基盤** から **エンタープライズ向けマルチエージェントオーケストレーション基盤** へと大きく進化しました。主な転換点は次の5点です。

1. **モデルの多様化と進化**：GPT-4o の退役と GPT-4.1 のデフォルト化（2025年10月）、GPT-5 Chat の段階的 GA（2025年11月→2026年3月）、Anthropic Claude（Sonnet 4.5 / 4.6 / Opus）の GA（2026年3月）、GPT-5.5 Reasoning (Deep) の実験提供（2026年4月）など、単一ベンダー依存から脱却[^2][^3]。
2. **オープン標準採用**：**Model Context Protocol (MCP) が 2025年5月の Build 2025 で GA**[^4]、**Agent-to-Agent (A2A) Protocol が 2026年4月に GA**[^1] となり、外部フレームワーク（LangChain、AutoGen など）や Microsoft Foundry / Fabric / M365 Agents SDK のエージェントとの相互運用が本番利用可能に。
3. **Computer Use の実用化**：2025年4月の限定リサーチプレビューから、2025年9月の一般プレビュー、2026年1月の Cloud PC プール／セッションリプレイ／拡張監査ログの追加を経て、エンタープライズ運用に耐える機能へ拡張[^1][^5]。
4. **課金体系のリブランディング**：2025年9月1日に課金単位が「Messages」から「**Copilot Credits**」へ名称変更（数量・PAYG レートは変更なし）[^6]。Microsoft 365 Copilot ライセンス保有者向けにはクラシック回答・生成型回答・テナント Graph グラウンディングがゼロレート[^6]。
5. **開発者ツールチェーンの GA 化**：**Microsoft 365 Agents Toolkit & SDK が 2025年5月に GA**[^7]、**Copilot Studio extension for Visual Studio Code が 2026年1月に GA**[^8] し、YAML ベース定義・Git 連携・CI/CD パイプラインを使ったエージェント開発が標準化。

---

## 2. 月別ハイライト（主要リリースの抜粋）

| 時期 | 主要リリース | ステータス |
|---|---|---|
| 2025年4月 | Computer Use（限定リサーチプレビュー、米国）、Customer Managed Keys、ROI Analysis (Viva Insights) | Preview |
| **2025年5月（Build 2025）** | **MCP GA**、Multi-Agent Orchestration プレビュー、**Custom Engine Agents → M365 Copilot Chat GA**、**Microsoft 365 Agents Toolkit & SDK GA**、Code Interpreter プレビュー、SharePoint チャンネル GA、Agent Store、BYOM (Azure AI Foundry 11,000+ モデル) | 複数 GA |
| 2025年6月 | Microsoft 365 Copilot Tuning（Preview）、File Groups（Preview）、Multilingual Generative Orchestration（Preview）、GPT-4.1 mini（米国 Preview）、Power Fx 正規表現サポート | Preview |
| 2025年7月 | WhatsApp チャンネル公開、ROI Analytics（自律エージェント）、Microsoft Purview MIP 感度ラベル（Preview）、SSO 同意カード（Preview） | Preview/GA |
| 2025年8月 | **Code Interpreter GA**、**File Groups GA**、MCP オンボーディングウィザード、ユーザーファイル・画像アップロード | GA |
| 2025年9月 | **Computer-Using Agents (CUA) 一般プレビュー**、Client SDK（Android/iOS/Windows）プレビュー、Code Interpreter in Chat（Preview）、**課金単位を Copilot Credits へ変更（9/1）** | Preview |
| 2025年10月 | **GPT-4o 退役 → GPT-4.1 が新デフォルト**、GPT-5 プレビュー、MCP サーバー（動的コンテンツ）、Customizable Test Sets（Preview）、Express Mode for Agent Flows | GA/Preview |
| 2025年11月 | **GPT-5 Chat GA（米・EU）**、Microsoft Entra Agent Identities（Preview）、SharePoint メタデータフィルター、Work IQ for SharePoint、Multi-Agent Orchestration 強化、Copy Agents from M365 Copilot to Copilot Studio | GA/Preview |
| 2025年12月 | Multi-Version Agent Comparison | Preview |
| 2026年1月 | **Copilot Studio VS Code Extension GA**、Computer Use 拡張（Cloud PC pool / セッションリプレイ / 監査ログ）、Agent Evaluation 強化 | GA |
| 2026年2月 | Claude Sonnet 4.5 for Computer Use（ベータ）、Prompt Builder 強化（コンテンツモデレーション設定）、Graph コネクタ応答精度向上 | Preview |
| 2026年3月 | **GPT-5 Chat グローバル GA**、**Claude Sonnet 4.5/4.6 & Opus GA**、**Agent Evaluations GA**、Multi-Turn Conversation Tests、Bing Custom Search 知識ソース、Work IQ Tools Integration、Prompt Assistant | GA |
| 2026年4月 | **A2A Protocol GA**、Real-Time Voice Agents（Preview）、Voice Hold and Resume、Agent Usage Estimator、Custom Metrics（Preview）、GPT-5.5 Reasoning (Deep)（Experimental）、Analytics Viewer ロール | GA/Preview |

---

## 3. AI / エージェント機能

### 3.1 Autonomous Agents（自律エージェント）

- 2025年5月の Build 2025 を契機に実用展開が加速[^7]。Generative Orchestration をベースに、イベントトリガー（スケジュール／外部システムイベント等）で動作し、ユーザー介在なしにマルチステップタスクを完了する設計。
- **Custom engine agents → Microsoft 365 Copilot Chat への公開が 2025年5月に GA**[^7]。Topics・Autonomous Triggers・Analytics・Azure AI 連携など Copilot Studio の全機能をそのまま M365 体験（Teams / Word / Excel / PowerPoint / Office）から呼び出し可能。
- 2025年7月：**自律エージェント向け ROI Analytics** で成功実行・アクションから時間・コスト削減を推定[^1]。
- 2025年10月：**Express Mode for Agent Flows**（Preview）でフロー実行の高速化とタイムアウト削減[^1]。

### 3.2 Generative Orchestration（生成型オーケストレーション）

- 新規エージェントのデフォルト動作モード。AI がリアルタイムにトピック・ツール・ナレッジ・他エージェントの最適な組み合わせを選択し、複数ステップを自動連鎖[^9]。
- 2025年6月：**多言語サポート**（Preview）で全サポート言語に拡張[^1]。
- 2025年10月：**GPT-4o 退役（10/27〜31）、GPT-4.1 が新デフォルトモデル**へ昇格[^1]（GCC 顧客は継続利用可、`Continue using retired models` オプションで11/26まで GPT-4o を継続利用可能）。
- **2026年6月以降：従来型 Classic Chatbots（Teams アプリ版）の新規作成は終了予定**[^9]。

### 3.3 Deep Reasoning / Chain of Thought

- **Deep Reasoning（Preview, EU・米国限定）**：Azure OpenAI o3 モデルを使用し、特定ステップの指示文に `reason` キーワードを含めることで部分適用が可能[^10]。
- Activity Map に Deep Reasoning ノードが表示され、推論ステップと使用データをトレース可能。Copilot Credits を消費するため複数ステップ使用時はレイテンシ／コストに注意[^10]。
- 2026年3月：**GPT-5 Reasoning** が EU・米国で Preview[^1]。
- 2026年4月：**GPT-5.5 Reasoning (Deep)** が Experimental モデル（Early Access Environment 限定）で追加[^1]。

### 3.4 モデル選択 / BYOM

| モデル | 提供時期 | ステータス（2026年5月時点） |
|---|---|---|
| GPT-4o | 〜2025年10月 | **退役**（GCC は継続） |
| **GPT-4.1** | 2025年10月 | **デフォルト・GA** |
| GPT-5 Chat | 2025年11月（US/EU）→ 2026年3月（グローバル） | **GA** |
| GPT-5 Reasoning | 2026年3月 | Preview（EU・US） |
| GPT-5 Auto | 2026年3月 | Preview（EU・US） |
| GPT-5.5 Reasoning (Deep) | 2026年4月 | Experimental（Early Access） |
| Claude Sonnet 4.5 / 4.6 | 2026年3月 | **GA（cross-geo）** |
| Claude Opus 4.6 | 2026年3月 | **GA（cross-geo）** |
| Claude Opus 4.7 | 最新 | Experimental |
| Grok 4.1 Fast | 最新 | Experimental（本番非推奨）[^11] |

モデルカテゴリは **General / Deep / Auto** の3タグに分類され、速度／推論深度／コストのトレードオフを明示[^11]。

**Bring Your Own Model (BYOM)**：2025年5月の Build 2025 で Azure AI Foundry 経由の **11,000以上のモデル**（GPT-4.1・Llama・DeepSeek・カスタムモデル含む）へのアクセスとファインチューニング機能を発表[^7]。Anthropic Claude は Microsoft のサブプロセッサーとして組み込まれ、xAI Grok は xAI 利用規約への同意が必要[^11]。

### 3.5 Microsoft Copilot Tuning

- 2025年5月 Build で発表 → 2025年6月から Preview。組織独自データで LLM をファインチューニングし、ドメイン特化タスク（文書作成・要約・Q&A・バリデーション・スタイル編集）に最適化されたエージェントを作成可能[^12]。
- Microsoft 365 テナント境界内で動作し、Copilot in Teams / Word / Chat に統合できる[^12]。

---

## 4. Computer Use（Computer-Using Agents, CUA）

| 時期 | 進化 |
|---|---|
| 2025年4月 | 限定リサーチプレビュー（米国、500K messages 以上テナント）[^13] |
| 2025年5月（Build 2025） | Frontier Program 経由で拡大プレビュー[^7] |
| 2025年9月 | **CUA 一般プレビュー昇格**、Windows デスクトップアプリ自動化対応[^1] |
| 2026年1月 | **Cloud PC プーリング**、**セッションリプレイ付き拡張監査ログ**、組み込みクレデンシャル[^1] |
| 2026年2月 | Computer Use 用に **Claude Sonnet 4.5（ベータ）** 選択可能[^1] |
| 2026年5月（現在） | OpenAI CUA モデル、Claude Sonnet 4.5 が GA、Claude Sonnet 4.6 / Opus 4.6 が Experimental[^14] |

**主要機能**：

- Vision（画面認識）と高度な推論を組み合わせ、API のないシステムでも仮想マウス／キーボードで操作[^14]。
- 自然言語でタスク指示を記述（コード不要）、入力値のダイナミック設定、Power Automate Machine 連携、Azure Key Vault または Power Platform 内部ストレージでの認証情報保管[^14]。
- 許可リスト形式の **アクセス制御**、有害指示検知時に Outlook 経由でレビュアーに通知する **Human Supervision**[^14]。

---

## 5. マルチエージェントオーケストレーション / A2A

### 5.1 種類

Copilot Studio は次の3種類のサブエージェント接続をサポート[^15]：

- **Child agents（子エージェント）**：メインエージェント内の軽量サブエージェント。ツール・知識・指示の論理的グループ化。
- **Connected agents**：同一環境内の他 Copilot Studio エージェント。
- **External agents**：A2A、Microsoft 365 Agents SDK、Microsoft Foundry、Microsoft Fabric 経由の外部エージェント。

### 5.2 タイムライン

| 機能 | 発表 | GA |
|---|---|---|
| Multi-agent orchestration（基本） | 2025年5月 Build 2025 | 2025年11月（Connected agents） |
| Child agents | 2025年5月以前 | GA |
| **A2A (Agent-to-Agent) Protocol** | 2025年5月 Build 2025（発表）[^7] | **2026年4月 GA**[^1] |
| Microsoft Fabric Data Agents 連携 | 2025年11月 Preview | Preview 継続 |
| Microsoft 365 Agents SDK 連携 | Preview | Preview 継続 |
| Microsoft Foundry Agents 連携 | Preview | Preview 継続 |
| Component Collections（子エージェント・MCP 含むエクスポート/インポート） | 2025年11月 | GA |
| Agent Node in Agent Flow | 2026年3月 | GA |

**A2A Protocol** はオープン標準で、外部フレームワーク（LangChain、AutoGen 等）で構築されたエージェントへのタスク委譲を可能にする。通常の HTTP コネクタと異なり、マルチターン対話・コンテキストメタデータ（contextId、メッセージ ID、ロケール、チャット履歴等）・フレームワーク非依存の連携を実現する[^16]。

---

## 6. Model Context Protocol (MCP) サポート

| 時期 | 内容 |
|---|---|
| 2025年3月 | パブリックプレビュー開始 |
| **2025年5月（Build 2025）** | **MCP GA**（ツール一覧表示・Streamable トランスポート・拡張トレーシング／分析）[^4] |
| 2025年8月 | MCP オンボーディングウィザード（既存 MCP サーバーへの直接接続）、**SSE トランスポート廃止**[^1] |
| 2025年10月 | MCP サーバーによる動的コンテンツアクセス[^1] |
| 2025年11月 | Component Collections に MCP サポート追加[^1] |

**サポート仕様**[^17]：

- トランスポート：Streamable（SSE は2025年8月以降非サポート）
- 認証：None / API Key（Header or Query）/ OAuth 2.0（Dynamic Discovery, Dynamic, Manual の3種）
- 接続方法：(1) MCP オンボーディングウィザード（推奨）、(2) Power Apps カスタムコネクタ経由（OpenAPI YAML スキーマ）
- DLP 対応：Power Platform のデータポリシーが MCP サーバーへのアクセスにも適用
- Microsoft 製プレビルド MCP コネクタがカタログで提供[^17]

---

## 7. ナレッジソース

### 7.1 新規追加・拡張

| 時期 | ナレッジソース |
|---|---|
| 2025年5月 Build | OneDrive ファイル、SharePoint リスト、Teams チャット／チャンネル、Salesforce / ServiceNow / Zendesk（非構造化）、Snowflake / Databricks / SAP（構造化）、**Azure AI Search GA**[^7] |
| 2025年6月 → 2025年8月 | **File Groups**（Preview → GA）：複数ファイルをグループ化し単一ナレッジソースとして扱う[^1] |
| 2025年11月 | **SharePoint メタデータフィルター**（ファイル名・所有者・更新日でフィルタ）、**Work IQ for SharePoint**（取得精度向上、新アーキテクチャ）[^1][^18] |
| 2026年3月 | **Bing Custom Search**（カスタム構成 ID 経由のスコープ Web インデックス）[^1] |
| 2026年3月 | **Work IQ Tools Integration**（M365 ファイル・メール・会議・チャットへのリアルタイムアクセス、Preview）[^19] |

### 7.2 Microsoft Graph Connectors（"Copilot connectors" に改名）

- 2025年5月：Microsoft Graph connectors を **"Copilot connectors"** に改名、40以上のコネクタが GA または Public Preview[^7]。
- 2026年2月：ServiceNow チケット、Azure DevOps 作業項目の応答精度を大幅改善[^1]。

### 7.3 Dataverse

- Dataverse をリアルタイム知識ソースとして使用可能（Preview）。メタデータのみインデックス化し、ランタイムでユーザートークンを使ったアクセス制御[^20]。
- 2025年7月：Dataverse での Purview MIP 感度ラベル対応（Preview）[^21]。

---

## 8. 統合機能

### 8.1 Microsoft 365 Copilot

- **Custom Engine Agents → Microsoft 365 Copilot Chat 公開が2025年5月に GA**[^7]。`@エージェント名` で M365 Copilot Chat から呼び出し可能。Teams App Store の「Built with Power Platform」または「Built for your org」セクションに掲載[^22]。
- **Declarative Agent（Microsoft 365 Copilot 専用エージェント）** を Copilot Studio から作成可能。SharePoint・Graph コネクタ・Bing Web 検索を知識ソースに、Power Platform コネクタを介した REST API ツールも追加可能[^23]。
- 2025年11月：**M365 Copilot から Copilot Studio へエージェントをコピー**できるようになり、マルチステップワークフローや複数チャネル公開へのアップグレードパスが提供[^1]。
- **Agent Store**：2025年5月発表。Microsoft / パートナー / 顧客作成の70以上のエージェントを一元配信するマーケットプレイス[^7]。

### 8.2 Microsoft Foundry（旧 Azure AI Foundry）

- 2025年11月：**Microsoft Foundry agents との接続（Preview）**。Foundry プロジェクトエンドポイント URL と Agent ID を指定すれば、Copilot Studio から呼び出し可能[^24]。
- 2025年5月 Build：Azure AI Foundry 経由で **11,000以上のモデル** にアクセス、ファインチューニング対応[^7]。
- 2026年4月：A2A Protocol の GA により、Foundry と Copilot Studio 間の本番連携が可能に[^1]。

### 8.3 Microsoft Teams

- Teams 1:1 チャット、チームチャンネル、Teams App Store への公開をサポート（チャンネル／グループチャットでのメンション応答は段階的に拡張中）[^22]。
- 2025年7月：Teams 上でエージェント回答に使用したデータの **Purview MIP 感度ラベル**を表示（Preview）[^21]。
- 2026年3月：**Work IQ Teams MCP** で Teams チャット・会議データをリアルタイム参照可能（Preview）[^19]。

### 8.4 SharePoint

- 2025年5月：**SharePoint チャンネル GA**（ワンクリック公開）[^7]。
- 2025年11月：**SharePoint メタデータフィルター**、**Work IQ for SharePoint**[^18]。

### 8.5 Microsoft Fabric

- 2025年11月：Microsoft Fabric Data Agents を Copilot Studio エージェントのサブエージェントとして接続可能（Preview）[^25]。

### 8.6 Power Automate / Power Apps

- **Agent Flows**：Copilot Studio 内ネイティブの自動化フロー。`When an agent calls the flow` トリガー、自然言語フロー作成[^26]。
- **Workflows（新オーサリングキャンバス）**：2026年3〜5月 Preview。ネイティブ AI アクション、エージェントハンドオフ、ノードレベルテスト[^26]。
- 既存 Power Automate クラウドフローを Agent Flow に変換し、Copilot Studio のキャパシティ課金体系に移行可能（不可逆）[^26]。
- 2025年11月：Agent Flow の **Request Information アクション**（Outlook 経由のヒューマンインザループ）[^1]。

### 8.7 その他チャネル

- **WhatsApp チャンネル**（2025年7月公開）：エージェントを WhatsApp 電話番号に直接公開[^1]。
- **音声エージェント**（2026年4月 Preview）：リアルタイム音声、Voice Hold and Resume、Dynamics 365 Contact Center 連携、電話チャンネル公開[^1]。
- **Client SDK**（2025年9月）：Android / iOS / Windows ネイティブアプリへの埋め込み[^27]。

---

## 9. ライセンス / 価格

### 9.1 課金単位の変更

- **2025年9月1日：**「Messages」→「**Copilot Credits**」へ単位名称変更（数量・PAYG レートは変更なし）[^6]。
- 2026年4月：**Agent Usage Estimator**（[microsoft.github.io/copilot-studio-estimator](https://microsoft.github.io/copilot-studio-estimator/)）で大規模デプロイ前にクレジット消費量を試算可能[^28]。

### 9.2 Copilot Credits レート（抜粋）

| 機能 | レート | M365 Copilot ライセンス保有者 |
|---|---|---|
| クラシック回答 | 1 クレジット | **無料（ゼロレート）** |
| ジェネレーティブ回答 | 2 クレジット | **無料** |
| エージェントアクション | 5 クレジット | **無料** |
| テナント Graph グラウンディング | 10 クレジット | **無料** |
| Agent Flows アクション（100アクションあたり） | 13 クレジット | **無料** |
| AI ツール（標準）/ 10 レスポンス | 15 クレジット | 無料 |
| AI ツール（プレミアム）/ 10 レスポンス | 100 クレジット | 無料 |
| 音声（プレミアム・リアルタイム） | 75 クレジット/分 | — |

出典：[Copilot Studio messages management][^29]

### 9.3 ライセンス種別

| 種別 | 概要 |
|---|---|
| Copilot Studio テナントライセンス | M365 管理センターで購入するテナント単位のクレジットプール |
| Copilot Studio ユーザーライセンス | エージェント作成者向け |
| **Pay-as-you-go (PAYG)** | Azure サブスクリプションを Power Platform Admin Center の Billing Policy に紐付け、超過分を Azure メーターで課金 |
| **Copilot Credits 前払い (CCCU)** | Azure ポータルで購入する1年前払いオプション。Copilot Credit Commit Units で複数 Microsoft 製品横断利用可 |

出典：[Copilot Studio billing and licensing][^6]

### 9.4 超過エンフォースメント

- テナントが **125% 容量に達した時点でカスタムエージェントを無効化**（PAYG 環境は対象外）[^29]。
- Agent Flows は **100% 容量到達でフロー実行のみブロック**（エージェント本体は継続稼働）[^29]。
- Power Platform Admin Center の `Licensing > Copilot Studio > Manage Agents` で個別エージェントの月次消費上限設定が可能[^29]。

---

## 10. ガバナンス / セキュリティ

### 10.1 DLP（Data Loss Prevention）

- 2025年初頭：**全テナントで DLP エンフォースメントが本格施行**（MC973179）、エグゼンプション廃止[^30]。
- DLP 対象に追加された新コネクター：`Knowledge source with SharePoint/OneDrive`、`Knowledge source with public websites`、`Knowledge source with documents`、`Event triggers / Microsoft Copilot Studio` ほか[^30]。
- **MCP サーバーも DLP 対象**：Power Platform コネクター経由の MCP サーバーツールを `Block` 設定で制御可能[^30]。
- エンドポイントフィルタリング：SharePoint・公開 Web サイト・HTTP リクエストで特定 URL の許可／拒否設定が可能[^30]。

### 10.2 Microsoft Entra Agent Identities（Preview）

- 2025年11月（Preview）：エージェントに **個別の Entra Agent ID を自動付与**[^31]。
- Entra admin center で監査ログ、コネクター権限の可視化、**Conditional Access ポリシー**（ネットワーク場所・デバイスコンプライアンス・リスク条件）の適用、Entra ID Governance 統合をサポート[^31]。

### 10.3 Microsoft Purview MIP 感度ラベル

- 2025年7月（Preview）：コネクター・テストチャット・Teams・M365 Copilot 全体で MIP 感度ラベルを表示[^21]。
- SharePoint / OneDrive / SQL / Dataverse / Cosmos / Azure Blob Storage / Word / Excel / Outlook 等のソースのラベルを自動表示し、過剰共有防止と機密データ保護を実現[^21]。

### 10.4 暗号化・データ常駐性

- **Customer Managed Keys (CMK)**：Power Platform の CMK 実装をサポート（Managed Environments 限定）[^32]。
- **2025年4月7日以前** に CMK を有効化した環境は、引き続き Microsoft 管理キーで暗号化。再適用するには CMK をオフ → オンする必要[^32]。
- **EU Data Boundary (EUDB) 準拠**：EU/EFTA 課金テナントが全環境を EU リージョン内に作成した場合に対象[^33]。

### 10.5 Copilot Studio Kit（Power CAT 製）

2025年10月に正式紹介された Power Customer Advisory Team (Power CAT) 製ガバナンス・テストツールスイート[^34]：

- **Compliance Hub**：ガバナンスポリシーの自動評価、SLA ドリブンのレビューライフサイクル管理
- **Agent Inventory**：テナント全体エージェントのダッシュボード表示
- **Agent Review Tool**：アンチパターン検出
- **Power Platform Pipelines 連携**：CI/CD テスト自動化・品質ゲート
- **Rubrics refinement / Prompt Advisor / Conversation Analyzer**

---

## 11. 開発者ツール

### 11.1 Microsoft 365 Agents SDK

Microsoft は **Bot Framework SDK の後継** として Microsoft 365 Agents SDK を提供[^35]：

| パッケージ名（npm） | 旧 botbuilder 対応 |
|---|---|
| `@microsoft/agents-activity` | `botframework-schema` |
| `@microsoft/agents-hosting` | `botbuilder` |
| `@microsoft/agents-hosting-extensions-teams` | `botbuilder`（Teams 拡張） |
| `@microsoft/agents-hosting-dialogs` | `botbuilder-dialogs` |
| `@microsoft/agents-hosting-storage-blob` / `-cosmos` | `botbuilder-azure` |
| **`@microsoft/agents-copilotstudio-client`** | Copilot Studio エージェントへの Direct-to-Engine クライアント |

対応言語：JavaScript/TypeScript（[microsoft/Agents-for-js][^36]）・C#（microsoft/Agents-for-net）・Python（microsoft/Agents-for-python）。

**2025年5月 Build 2025 で Microsoft 365 Agents Toolkit & SDK が GA**[^7]。

### 11.2 Copilot Studio extension for Visual Studio Code

- **2026年1月：GA**[^8]。
- 主な機能：
  - Copilot Studio エージェントのローカルクローン
  - **YAML 編集 + IntelliSense**（カラーフォーマット、参照検索）
  - Component Management（ナレッジソース、ツール、トピック、トリガー、スキル）
  - Sync 操作（ローカル ↔ クラウド差分管理）
  - Git 統合（Pull Request ワークフロー）
  - GitHub Copilot / Claude Code 等の AI コーディングアシスタントとの併用想定
- VS Code Marketplace で月次リリース、Issue は GitHub [`microsoft/vscode-copilotstudio`][^8] で公開管理。

### 11.3 Code Mode / Power Fx

- 2025年6月：**Power Fx 正規表現サポート**（`IsMatch`、`Match`、`MatchAll`）、**Prompt Builder への Power Fx インライン挿入**[^1]。
- **YAML エージェント定義言語** で VS Code 拡張からエージェント全体を編集・バージョン管理可能[^8]。

### 11.4 Agents Client SDK（モバイル・Windows）

2025年9月（プレビュー）：Android / iOS / Windows ネイティブアプリ向け SDK。テキスト・音声・画像・スクリーンキャプチャによるマルチモーダル会話に対応[^27]。

### 11.5 ALM（Solutions / Pipelines / Source Control）

- Solutions 単位でのエージェント・Topics・Flows・環境変数・カスタムコネクターのエクスポート/インポート[^37]。
- 2025年11月：**Component Collections 強化**（サイドバーアクセス、子エージェント・MCP コネクタ含むエクスポート/インポート、Power Platform API の新 `copilotstudio` 名前空間）[^1]。
- 2026年4月：**REST API による評価自動化（Preview）**（Power Platform API 経由、CI/CD パイプライン統合）、Power Automate Copilot Studio コネクターによる評価スケジュール[^1]。

---

## 12. 分析・モニタリング

### 12.1 Analytics ダッシュボード

| 機能 | 時期 |
|---|---|
| 自律エージェント専用分析（実行ごとパフォーマンス追跡） | 〜2025年 |
| ハイブリッドビュー（会話型 + 自律型併列表示） | 〜2025年 |
| AI サマリー機能 | 〜2025年 |
| **回答率・品質分析 GA** | 2025年8月 |
| **テーマ分析（Preview）** | 2025年10月 |
| ROI 分析（時間・コスト節約） | 2025年7月（自律）・2025年10月（会話） |
| **マルチバージョンエージェント比較** | 2025年12月 |
| ユーザー質問・リアクションリスト | 2026年3月 |
| **Analytics Viewer ロール**（限定共有） | 2026年4月 |
| **カスタムメトリクス（Preview）** | 2026年4月 |
| Agent Usage Estimator | 2026年4月 |

出典：[Copilot Studio analytics overview][^38]

### 12.2 Application Insights 連携

- エージェント `Settings > Advanced > Application Insights` に接続文字列を入力で有効化[^39]。
- **Copilot Studio Dashboard ワークブック**（Preview）：会話数・レイテンシ・例外・ツール使用状況・トピック分析を単一ビューで表示[^39]。
- Analytics データは最大 **180日間** 保存、セッション詳細・トランスクリプトは最新 **28日間**[^38]。

### 12.3 Agent Evaluation

| 機能 | 時期 |
|---|---|
| カスタマイズ可能テストセット | 2025年10月（Preview） |
| Activity Map（入力→判断→出力可視化） | 2026年1月 |
| **Agent Evaluations GA** | **2026年3月** |
| マルチターン会話テスト | 2026年3月 |
| REST API による自動評価（Preview） | 2026年4月 |
| サムズアップ／ダウンフィードバック | 2026年1月 |

出典：[Copilot Studio What's new][^1]

---

## 13. 主要イベント別サマリー

### Microsoft Build 2025（2025年5月）

| 発表内容 | ステータス |
|---|---|
| Multi-agent orchestration（A2A プロトコル対応含む） | Preview → 段階展開 |
| Computer Use（米国先行） | Preview |
| **MCP (Model Context Protocol) GA** | **GA** |
| BYOM（Azure AI Foundry 11,000+モデル / Fine-tuning） | 発表 |
| Code Interpreter | Preview → 8月 GA |
| **Custom Engine Agents → M365 Copilot Chat GA** | **GA** |
| **Microsoft 365 Agents Toolkit & SDK GA** | **GA** |
| Agent Store | 発表・リリース |
| SharePoint チャンネル GA | **GA** |
| VS Code 拡張機能 | Preview |
| Managed Security Enhancements（Entra Agent ID 等） | 発表 |

出典：[Microsoft Copilot Studio announcements at Microsoft Build 2025][^7]

### Microsoft Ignite 2025（2025年11月）相当の更新

| 発表内容 | ステータス |
|---|---|
| GPT-5 Chat GA（US・EU） | **GA** |
| Microsoft Entra Agent Identities | Preview |
| Multi-Agent Orchestration（Fabric / Foundry 連携） | Preview |
| SharePoint メタデータフィルター | GA |
| Work IQ for SharePoint | GA |
| Copy Agents from M365 Copilot to Copilot Studio | GA |
| Component Collections（MCP・子エージェント対応） | GA |

出典：[Copilot Studio What's new][^1]（November 2025 セクション）

### 2026年上半期（〜Build 2026 前後）

| 発表内容 | ステータス |
|---|---|
| **VS Code Extension GA** | **2026年1月 GA** |
| Computer Use 拡張（Cloud PC pool / セッションリプレイ） | 2026年1月 |
| **Agent Evaluations GA** | **2026年3月 GA** |
| **Claude Sonnet 4.5 / 4.6 & Opus GA** | **2026年3月 GA** |
| **GPT-5 Chat グローバル GA** | **2026年3月 GA** |
| **A2A Protocol GA** | **2026年4月 GA** |
| GPT-5.5 Reasoning (Deep) | 2026年4月 Experimental |
| Real-Time Voice Agents | 2026年4月 Preview |

---

## 14. 確信度評価（Confidence Assessment）

**高確度（公式 Microsoft Learn / 公式ブログで明示）**：

- 月別 What's new に記載された機能・時期・ステータス（GA / Preview / Experimental）[^1]
- Build 2025 の発表内容（MCP GA、Custom Engine Agents GA、M365 Agents Toolkit & SDK GA など）[^7]
- 課金単位の Copilot Credits への変更（2025年9月1日）[^6]
- VS Code 拡張機能 GA（2026年1月）[^8]
- A2A Protocol GA（2026年4月）[^1]
- Computer Use の段階的提供[^14]

**中確度（公式ドキュメントから推測 / 一次情報が分散）**：

- Microsoft Ignite 2025 の発表内容：公式 Tech Community ブログが認証ウォールにより直接取得できず、What's new ページの2025年11月セクションから間接的に整理しています。
- Autonomous Agents 機能全体の「GA 日付」：トピック単位の GA は明示されているが、機能全体としての包括的 GA 宣言日は確認できていません。

**未確認・ギャップ事項**：

1. **Copilot Pages / Copilot Notebooks との直接統合**：今回の調査範囲では Copilot Studio 側から明示的な API 統合は確認できませんでした。間接的な連携の可能性はありますが、専用ドキュメントは未確認です。
2. **Microsoft Build 2026（2026年5月）の詳細発表内容**：本調査時点（2026年5月22日）で What's new ページの最終更新は2026年5月15日であり、5月分のセクションはまだ掲載されていません。Build 2026 の独立した発表ブログも未取得です。
3. **CoE Toolkit との連携詳細**：Power Platform CoE Starter Kit と Copilot Studio Kit の連携詳細は公式 Learn ドキュメントに明示記載が見つかりませんでした。
4. **Autonomous Agent の Tenant Pack 課金詳細**：最新の Microsoft Copilot Studio Licensing Guide PDF（[aka.ms/licensing/MicrosoftCopilotStudio](https://aka.ms/licensing/MicrosoftCopilotStudio)）の参照を推奨します。
5. **GCC（Government Community Cloud）環境**：GPT-5 等の機能適用差異は個別確認が必要です。
6. **「Power Virtual Agents」ブログ**：現在は Copilot Studio ブログにリダイレクトされており、実質同一情報です。

---

## Footnotes（出典）

[^1]: [Microsoft Learn — What's new in Microsoft Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new)（最終更新：2026-05-15）

[^2]: [Microsoft Learn — Select a primary AI model for your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model)

[^3]: [Microsoft Learn — Choose an external response model](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-external-response-model)

[^4]: [Model Context Protocol (MCP) is now generally available in Microsoft Copilot Studio — Microsoft Copilot blog](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/model-context-protocol-mcp-is-now-generally-available-in-microsoft-copilot-studio/)

[^5]: [Announcing Computer Use in Microsoft Copilot Studio — UI Automation](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/announcing-computer-use-microsoft-copilot-studio-ui-automation/)

[^6]: [Microsoft Learn — Microsoft Copilot Studio billing and licensing](https://learn.microsoft.com/en-us/microsoft-copilot-studio/billing-licensing)

[^7]: [Multi-agent orchestration, maker controls, and more — Microsoft Copilot Studio announcements at Microsoft Build 2025](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/multi-agent-orchestration-maker-controls-and-more-microsoft-copilot-studio-announcements-at-microsoft-build-2025/)

[^8]: [Microsoft Learn — Copilot Studio extension for Visual Studio Code overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/visual-studio-code-extension-overview)（GitHub: [microsoft/vscode-copilotstudio](https://github.com/microsoft/vscode-copilotstudio)）

[^9]: [Microsoft Learn — Orchestrate agent behavior with generative AI](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-generative-actions)

[^10]: [Microsoft Learn — Deep reasoning models (Preview)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-reasoning-models)

[^11]: [Microsoft Learn — Select a primary AI model for your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-select-agent-model)（モデルカテゴリ / Anthropic Claude / xAI Grok の運用条件）

[^12]: [Microsoft Learn — Microsoft 365 Copilot Tuning（fine-tune a model）](https://learn.microsoft.com/en-us/microsoft-copilot-studio/microsoft-copilot-fine-tune-model)

[^13]: [What's new in Copilot Studio — April 2025（公式ブログ）](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/whats-new-in-copilot-studio-april-2025/)

[^14]: [Microsoft Learn — Computer Use in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/computer-use)

[^15]: [Microsoft Learn — Add other agents to your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents)

[^16]: [Microsoft Learn — Connect to an agent over the A2A protocol](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-agent-to-agent)（および [a2a-protocol.org](https://a2a-protocol.org/)）

[^17]: [Microsoft Learn — Add an MCP server to your agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-components-to-agent) ／ [Connect to an existing MCP server](https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent)

[^18]: [Microsoft Learn — Add a SharePoint knowledge source](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-sharepoint)

[^19]: [Microsoft Learn — Use Work IQ in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/use-work-iq)

[^20]: [Microsoft Learn — Real-time connector knowledge sources](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-real-time-connectors)

[^21]: [Microsoft Learn — Display sensitivity labels in Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/sensitivity-label-copilot-studio)

[^22]: [Microsoft Learn — Publish your agent to Microsoft Teams and Microsoft 365 Copilot](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-add-bot-to-microsoft-teams)

[^23]: [Microsoft Learn — Extend Microsoft 365 Copilot from Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/microsoft-copilot-extend-copilot-extensions)

[^24]: [Microsoft Learn — Connect to a Microsoft Foundry agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent)

[^25]: [Microsoft Learn — Add a Microsoft Fabric Data Agent](https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-fabric-data-agent)

[^26]: [Microsoft Learn — Agent flows / Workflows overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/flows-overview)

[^27]: [Microsoft Learn — Communicate with an agent from a native app (Client SDK)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-communicate-with-agent-from-native-app)

[^28]: [Microsoft Copilot Studio agent usage estimator](https://microsoft.github.io/copilot-studio-estimator/) ／ [Microsoft Learn — Agent usage estimator](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-usage-estimator)

[^29]: [Microsoft Learn — Copilot Studio messages management (Copilot Credits)](https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management)

[^30]: [Microsoft Learn — Data Loss Prevention for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-data-loss-prevention)

[^31]: [Microsoft Learn — Use Microsoft Entra agent identities](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-use-entra-agent-identities)

[^32]: [Microsoft Learn — Customer Managed Keys for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/admin-customer-managed-keys)

[^33]: [Microsoft Learn — Geographic data residency for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/geo-data-residency)

[^34]: [Microsoft Learn — Copilot Studio Kit overview](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/kit-overview)

[^35]: [Microsoft Learn — Microsoft 365 Agents SDK overview](https://learn.microsoft.com/en-us/microsoft-365/agents-sdk/agents-sdk-overview)

[^36]: [GitHub — microsoft/Agents-for-js](https://github.com/microsoft/Agents-for-js)（C# 版：microsoft/Agents-for-net、Python 版：microsoft/Agents-for-python）

[^37]: [Microsoft Learn — Export and import agents with solutions](https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-bots)

[^38]: [Microsoft Learn — Analytics overview for Copilot Studio](https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview)

[^39]: [Microsoft Learn — Capture telemetry with Application Insights](https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-bot-framework-composer-capture-telemetry)

**Release plan 参考：**

- [Power Platform Release Plan — 2025 Wave 1 / Microsoft Copilot Studio](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave1/microsoft-copilot-studio/)
- [Power Platform Release Plan — 2025 Wave 2 / Microsoft Copilot Studio](https://learn.microsoft.com/en-us/power-platform/release-plan/2025wave2/microsoft-copilot-studio/)
- [Power Platform Release Plan — 2026 Wave 1 / Microsoft Copilot Studio](https://learn.microsoft.com/en-us/power-platform/release-plan/2026wave1/microsoft-copilot-studio/)
