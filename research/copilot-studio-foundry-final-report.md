# Copilot Studio と Microsoft Foundry の違い・移行/併用観点 最終調査レポート

## Executive Summary

結論として、Copilot Studio と Microsoft Foundry（旧称: Azure AI Studio / Azure AI Foundry）は「片方から片方へ置き換える前提の同種製品」ではなく、対象者・実装モデル・運用境界が異なるエージェント構築基盤です。Copilot Studio は Power Platform/Microsoft 365 に近いローコードのエージェント作成・公開基盤であり、Microsoft Foundry は Azure 上でモデル、ツール、エージェント、評価、監視、ガバナンスを扱う統合 AI プラットフォームです。[^foundry-name][^cs-what][^foundry-what]

Copilot Studio から Foundry へエージェントを丸ごと自動移行する公式ツールや公式マイグレーション手順は確認できませんでした。公式に確認できるのは、Copilot Studio のエージェントから Foundry Agent を外部エージェントとして呼び出す、Foundry Agent を Microsoft 365 Copilot/Teams に公開する、Azure OpenAI in Microsoft Foundry から Copilot Studio エージェントを作る、などの「接続・併用」パターンです。[^cs-add-foundry][^foundry-publish][^cs-azure-openai]

したがって、移行は多くの場合「インポート」ではなく「再設計・再実装」です。特に Topics、Power Automate/Power Platform connectors、チャネル、認証、DLP、Dataverse、分析/評価データはそのまま Foundry へ移せる前提にしない方が安全です。Copilot Studio の solution export/import は Copilot Studio 環境間の ALM であり、Foundry への取り込み経路ではありません。[^cs-export][^cs-solutions][^foundry-migrate]

併用は公式に機能として提供されていますが、主要な接続機能の一部は Public Preview または Early Access Preview です。特に「Copilot Studio から Foundry agent を追加」は Public Preview、「Foundry agent を Microsoft 365 Copilot/Teams に公開」は Early Access Preview であり、本番適用ではプレビュー条件、SLA、データ境界、管理責任を明示的に確認する必要があります。[^cs-add-other-agents][^foundry-publish][^feature-status]

## 1. Copilot Studio と Microsoft Foundry の違い

| 観点 | Copilot Studio | Microsoft Foundry |
|---|---|---|
| 主な位置づけ | グラフィカルなローコードのエージェント/agent flow 作成ツール。Microsoft 365 Copilot への公開や複数チャネル展開を重視。 | Azure PaaS として、モデル、エージェント、ツール、評価、監視、ガバナンスを統合する AI 開発/運用基盤。 |
| 主な利用者 | 業務部門、情報ワーカー、市民開発者、Power Platform 利用者、IT 管理者。 | アプリ開発者、ML エンジニア/データサイエンティスト、IT/プラットフォーム管理者。 |
| 開発モデル | ローコード UI、Topics、Knowledge、Actions/flows、Power Platform connectors。 | Prompt agents、Workflow agents、Hosted agents、SDK/API、モデルカタログ、Tool catalog、MCP/OpenAPI/A2A。 |
| モデル選択 | Copilot Studio 管理モデルや BYO model。BYO Foundry model は別途 Azure 側課金。 | Foundry Models/モデルカタログ、カスタム/OSS/商用モデル、Agent Service。 |
| チャネル | Teams/Microsoft 365 Copilot、SharePoint、Web、Mobile、Facebook、WhatsApp、Azure Bot Service channels、音声/IVR など。 | API/カスタム統合が基本。Microsoft 365 Copilot/Teams 公開は Early Access Preview。その他チャネルはカスタム実装や Copilot Studio 等との橋渡しが必要。 |
| ガバナンス | Power Platform environment、Dataverse、DLP、solution ALM、Power Platform 管理センター、Purview/Sentinel 連携。 | Azure RBAC、Foundry roles、Private Link/VNet、Azure Monitor/Application Insights、Foundry Control Plane、Azure Policy/APIM など。 |
| 評価/監視 | Copilot Studio analytics、評価用 test set、CSAT/会話分析などの組み込み運用画面。 | OpenTelemetry/Application Insights、SDK ベース評価、Red Teaming、token/latency/tool call などの詳細トレース。 |
| 得意領域 | 早期構築、多チャネル公開、Power Platform/Dataverse/Power Automate 統合、M365 Copilot 拡張、部門向け運用。 | pro-code、カスタムモデル、RAG/検索、ネットワーク分離、CI/CD、詳細評価/監視、複雑なエージェント/ツール統合。 |

Copilot Studio は公式に "graphical, low-code tool for building agents and agent flows" と説明されています。[^cs-what] 一方、Microsoft Foundry は "unified Azure platform-as-a-service offering for enterprise AI operations, model builders, and application development" と説明されています。[^foundry-what] このため、両者の差は単なる UI の違いではなく、保存先、実行基盤、課金、権限、運用監視、ALM、公開チャネルまで含むプラットフォーム差です。

## 2. 移行の観点で難しい点

### 2.1 公式の「Copilot Studio -> Foundry 自動移行」は確認できない

Microsoft 公式資料で確認できる移行手順は、主に Assistants API/classic agents から Foundry Agent Service v2 への移行、hub-based/classic Foundry project から新 Foundry project への移行、Azure OpenAI resource から Foundry resource へのアップグレードです。Copilot Studio agent を Foundry agent に変換する公式ツールや、Foundry agent を Copilot Studio にインポートする公式手順は確認できませんでした。[^foundry-migrate][^foundry-project-migrate][^foundry-openai-upgrade]

Copilot Studio 側の export/import は Power Platform solution を使う Copilot Studio 環境間の ALM です。認証設定、チャネル詳細、会話 ID、環境 ID などは移行時に再構成が必要であり、これは Foundry 取り込み用フォーマットではありません。[^cs-export][^cs-solutions]

### 2.2 Topics / YAML / フローはそのまま移せない

Copilot Studio の Topics は、会話の進行をノードやトピックで表現する Copilot Studio/Power Platform 側のモデルです。Foundry の Prompt/Workflow/Hosted agents は、instructions、workflow definition、containerized code など別の実行モデルで構成されます。[^cs-topics][^foundry-agents]

Foundry Workflow agents では YAML や Power Fx が登場しますが、それは Copilot Studio topic YAML を直接インポートできるという意味ではありません。安全な表現は「一部の設計意図や Power Fx 的な式は手作業で再利用/翻訳できる可能性があるが、スキーマ互換や自動変換は公式に確認できない」です。[^foundry-workflow][^cs-export]

### 2.3 Power Platform 依存の再設計が必要

Copilot Studio で Power Automate flows、agent flows、Power Platform connectors、Dataverse、DLP、Power Platform environment を利用している場合、それらは Foundry の Azure RBAC、Azure Functions/OpenAPI/MCP、Azure Monitor/Application Insights、Azure networking へ単純対応しません。Foundry に寄せる場合、ツール呼び出し、認証、シークレット管理、監査、ネットワーク、CI/CD を Azure 側で再設計します。[^cs-connectors][^cs-security][^foundry-tools][^foundry-rbac]

### 2.4 チャネル差が大きい

Copilot Studio は Teams/Microsoft 365 Copilot、SharePoint、Web、Mobile、Facebook、WhatsApp、Azure Bot Service channels、音声/IVR など、多数の公開チャネルを持ちます。Foundry は API/カスタム統合や Microsoft 365 Copilot/Teams 公開を提供しますが、Foundry agent の Microsoft 365 Copilot/Teams 公開は Early Access Preview であり、ファイルアップロード、画像生成、Private Link、ストリーミング、引用などに制約があります。[^cs-channels][^foundry-publish]

### 2.5 運用/評価/分析の移行は別物

Copilot Studio の analytics、評価 test sets、CSAT、会話分析は、Foundry の Application Insights/OpenTelemetry/SDK 評価とは異なる運用面です。既存の評価観点は再利用できますが、データやダッシュボードをそのまま Foundry 側へ持ち込む公式移行手順は確認できませんでした。[^cs-analytics][^cs-evaluation][^foundry-observe]

### 2.6 課金モデルが変わる

Copilot Studio は Copilot Credits/メッセージ/機能別課金を軸にし、BYO model を含む Azure Foundry model 呼び出しは別途 Azure 側課金です。Foundry は agent hosting 自体、model token、tool、storage、compute、Application Insights 等が組み合わさります。移行すると、会話単価だけではなくトークン、ツール呼び出し、評価、ログ、検索、コンピュートの費用設計が必要です。[^cs-billing][^foundry-pricing]

## 3. では移行はできるのか

実務上は、Copilot Studio agent を Foundry に移す場合、「設計資産を参照しながら、実行基盤に合わせて再実装する」と考えるのが正確です。会話設計、FAQ、プロンプト、業務ルール、API 仕様、テストケース、評価観点は再利用できますが、Topics、Power Automate flows、connectors、channels、Dataverse、DLP、analytics は Foundry の同一オブジェクトにはなりません。[^cs-export][^foundry-agents][^foundry-tools]

移行対象を分解すると、次の判断になります。

| 資産 | そのまま移せるか | 現実的な対応 |
|---|---:|---|
| 目的、ペルソナ、業務シナリオ | ほぼ可 | 要件/設計書として再利用。 |
| Instructions / prompts | 部分可 | Foundry agent instructions へ手動移植し、評価で調整。 |
| FAQ/ナレッジ文書 | 部分可 | Foundry File Search/Azure AI Search/SharePoint tool などへ再構成。 |
| Topics / conversation flows | 不可に近い | Workflow agent、Hosted agent、またはコード/状態機械として再設計。 |
| Power Automate flows | 直接不可 | API、Azure Functions、Logic Apps、MCP/OpenAPI tool などへ置換。 |
| Power Platform connectors | 直接不可 | OpenAPI/MCP/APIM/custom code で再接続。 |
| Teams/Web/WhatsApp/Voice 等チャネル | 直接不可 | Copilot Studio を front door に残すか、Bot/Teams/custom channel を別設計。 |
| DLP/Power Platform ALM | 直接不可 | Azure RBAC、Policy、APIM、CI/CD、networking に置換。 |
| Analytics/evaluation results | 直接不可 | 評価データセット/指標を再作成。 |

つまり、Copilot Studio の強みを多く使っている agent ほど「移行」ではなく「再構築」になります。逆に、Copilot Studio を薄い UI/front door として使い、実ロジックが既に API/検索/外部サービスに分離されている場合は、Foundry 側への再実装範囲は小さくできます。

## 4. 併用は推奨されているのか

「Microsoft が一文で『移行より併用を推奨』と明記している」資料は確認できませんでした。

一方で、Microsoft は両者の接続機能を公式に提供し、Copilot Studio が Microsoft Foundry agent を外部エージェントとして呼び出す手順、Foundry agent を Microsoft 365 Copilot/Teams に公開する手順、Azure OpenAI in Microsoft Foundry のデータ接続から Copilot Studio agent を作成する手順を公開しています。[^cs-add-foundry][^foundry-publish][^cs-azure-openai] そのため、正確には「併用は公式にサポート/文書化されている。ただし一部は Preview であり、本番利用は制約確認が必要」です。

### 4.1 推奨しやすい併用パターン

| パターン | 使いどころ | 注意点 |
|---|---|---|
| Copilot Studio を front door、Foundry を specialist agent/API とする | Teams/Web/SharePoint/WhatsApp/Voice など多チャネルや Power Platform 統合を残しつつ、難しい推論/RAG/モデル選択/評価だけ Foundry に寄せる。 | Copilot Studio -> Foundry agent 接続は Public Preview。新 Microsoft Foundry portal で作成した agent のみ接続可。 |
| Copilot Studio から A2A agent を呼ぶ | Foundry 以外も含む外部 agent と標準プロトコルで接続したい場合。 | Copilot Studio A2A 接続自体は GA と確認。ただし Foundry 側 A2A tool/inbound は Preview/一部手順未公開。 |
| Copilot Studio から REST API / custom connector / Power Automate 経由で Foundry 周辺機能を呼ぶ | 既存 Power Platform governance を使いながら、Azure API/Foundry endpoint/Functions/APIM を接続したい場合。 | OpenAPI/認証/コネクター DLP/資格情報管理を設計する。 |
| MCP をツール接続の共通面にする | ツール/データアクセスを agent から分離し、複数 agent で再利用したい場合。 | Foundry tool catalog は GA だが個別 tool は Preview がある。Copilot Studio MCP は DLP の影響を受ける。 |
| Foundry agent を Microsoft 365 Copilot/Teams に公開 | pro-code/custom model agent を M365/Teams に直接出したい場合。 | Early Access Preview。M365 では streaming/citations/file upload 等に制約。 |
| APIM を AI Gateway として置く | 複数 Foundry endpoint、MCP、A2A、REST tool を統制したい場合。 | AI Gateway in Foundry など一部 Preview。 |

### 4.2 ベストプラクティス案

短期的には、Copilot Studio を利用者接点と業務オーケストレーションの中心に残し、Foundry は高度な AI 部品として後ろに置く構成が最もリスクが低いです。Copilot Studio は多チャネル公開、Power Platform connectors、Power Automate、DLP、Microsoft 365/Power Platform 運用に強く、Foundry はカスタムモデル、RAG、SDK/CI/CD、評価、トレース、Azure ネットワーク/セキュリティに強いためです。[^cs-channels][^cs-security][^foundry-tools][^foundry-observe]

本番化では、Preview 機能に依存する経路を避けるか、Preview 条件を受け入れたうえで段階導入します。とくに Copilot Studio -> Foundry agent の direct connection と Foundry -> Microsoft 365 Copilot/Teams publish は、現時点で本番 SLA を前提にしない設計が必要です。[^feature-status][^cs-add-other-agents][^foundry-publish]

## 5. 公式事例・周辺事例

公式 Microsoft 資料で、Copilot Studio と Azure AI Foundry/Microsoft Foundry を同じソリューションで使っている明確な事例として Rabobank のケースが確認できました。Rabobank は Copilot Studio agent を customer self-service に使い、規制/データ主権上の理由から Azure AI Foundry で自社 Azure subscription 内に AI models をデプロイし、Azure AI Search と組み合わせて fallback generative AI を構成しています。[^rabobank]

一方、Copilot Studio から Foundry へ、または Foundry から Copilot Studio へ移行したという公式 customer case は確認できませんでした。確認できたのは、ABN AMRO Bank のような「既存チャットボット基盤から Copilot Studio への移行」、Power Virtual Agents から Copilot Studio への製品進化、Azure OpenAI resource から Foundry resource へのアップグレード、Foundry agent の Microsoft 365 Copilot/Teams 公開などの隣接事例です。[^abn-amro][^pva-cs][^foundry-openai-upgrade][^foundry-publish]

したがって、事例の章で安全に書ける結論は次です。

1. Copilot Studio + Foundry の併用事例はある。
2. Copilot Studio と Foundry 間の直接移行事例は確認できない。
3. 既存 chatbot から Copilot Studio への移行事例や、Azure OpenAI/Foundry classic 周辺の移行/アップグレード事例はあるが、Copilot Studio -> Foundry 移行とは別物である。

## 6. 判断基準

| 要件 | 推奨 |
|---|---|
| Teams/M365/Web/SharePoint/WhatsApp/音声など多チャネル公開が主目的 | Copilot Studio を主にする。 |
| Power Automate、Dataverse、Power Platform connectors、DLP を活用する | Copilot Studio を主にする。 |
| 業務部門が継続改善するローコード agent | Copilot Studio を主にする。 |
| カスタムモデル、複数モデル、詳細 RAG、MCP/OpenAPI tool、SDK、CI/CD が重要 | Foundry を主にする。 |
| VNet/Private Link/BYO Azure resources/詳細 RBAC が必須 | Foundry を主にする。 |
| Microsoft 365/Teams 上に pro-code agent を出したい | Foundry publish を検討。ただし Early Access Preview。 |
| 既存 Copilot Studio agent を活かしつつ一部だけ高度化したい | Copilot Studio front door + Foundry specialist agent/API の併用。 |
| Copilot Studio を完全廃止して Foundry に寄せたい | 公式移行ではなく再構築計画として扱う。 |

## 7. 推奨ロードマップ

### Phase 0: 棚卸し

既存 Copilot Studio agent の Topics、knowledge sources、flows、connectors、channels、auth、DLP、analytics、評価 test sets、利用量、所有者を棚卸しします。Foundry へ移す対象ではなく、「残すもの」「Foundry 後段化するもの」「再構築するもの」に分類します。[^cs-export][^cs-solutions]

### Phase 1: 併用 PoC

1 つの高価値シナリオだけを Foundry agent/API として作り、Copilot Studio から呼び出します。direct Foundry connection が Preview でリスクがある場合は、REST API/custom connector/APIM/Power Automate 経由も比較します。[^cs-add-foundry][^cs-rest][^apim-ai-gateway]

### Phase 2: 評価・監視・コスト比較

同じシナリオで、Copilot Studio の analytics/evaluation と Foundry の Application Insights/evaluation を並べて、回答品質、遅延、トークン/クレジット/ログ費用、tool call 成功率、セキュリティ境界を比較します。[^cs-evaluation][^foundry-observe][^cs-billing][^foundry-pricing]

### Phase 3: 本番境界の確定

利用者接点を Copilot Studio に残すか、Foundry agent を Microsoft 365 Copilot/Teams に公開するか、またはカスタムアプリ/API 統合にするかを決めます。Preview 機能を本番経路に入れる場合は、Preview terms、SLA、データ境界、管理者承認、ロール/監査設計を明記します。[^foundry-publish][^feature-status]

## 8. Confidence Assessment

**高確度**: Copilot Studio と Microsoft Foundry の製品定義、対象者、主な運用面の差、Copilot Studio -> Foundry agent 接続が Public Preview であること、Foundry agent -> Microsoft 365 Copilot/Teams publish が Early Access Preview であること、Copilot Studio/Foudry 間の直接自動移行ツールが公式資料では確認できないこと。[^cs-what][^foundry-what][^cs-add-other-agents][^foundry-publish][^foundry-migrate]

**中確度**: 「併用がベストプラクティス」という表現。公式に併用機能と判断材料はありますが、「移行より併用を推奨」と明文化した単独資料は確認できません。最終表現は「併用は公式に文書化されており、現実的な段階移行パターンとして妥当」に留めるのが安全です。[^cs-add-foundry][^m365-decision][^custom-engine]

**低確度/未確認**: 非公開 Preview の移行ツール、将来 GA 化された機能、Microsoft blog/customers.microsoft.com 側の未取得ページ。今回確認した範囲では、Copilot Studio <-> Foundry の直接移行事例は見つかっていません。[^rabobank][^abn-amro]

## Footnotes

[^foundry-name]: Microsoft Learn, "What is Microsoft Foundry", Evolution of Foundry. `https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry` / mirror: `https://learn.microsoft.com/en-us/azure/ai-foundry/what-is-azure-ai-foundry`
[^cs-what]: Microsoft Learn, "What is Microsoft Copilot Studio", "Copilot Studio is a graphical, low-code tool for building agents and agent flows." `https://learn.microsoft.com/en-us/microsoft-copilot-studio/fundamentals-what-is-copilot-studio`
[^foundry-what]: Microsoft Learn, "What is Microsoft Foundry", "Microsoft Foundry is a unified Azure platform-as-a-service..." `https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry`
[^cs-add-foundry]: Microsoft Learn, "Add a Microsoft Foundry agent to your agent", includes setup steps and the new Foundry portal limitation. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/add-agent-foundry-agent`
[^cs-add-other-agents]: Microsoft Learn, "Add other agents to your agent", states connecting to agents built with Microsoft Foundry is currently available in public preview. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-add-other-agents`
[^foundry-publish]: Microsoft Learn, "Publish Foundry agents to Microsoft 365 Copilot and Teams", states the feature is Early Access Preview and documents limitations. `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/publish-copilot`
[^cs-azure-openai]: Microsoft Learn, "Create generative answers with Azure OpenAI Service in Microsoft Foundry", documents connecting a Copilot Studio agent to data by selecting Deploy to a new Microsoft Copilot Studio bot. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/nlu-generative-answers-azure-openai`
[^cs-export]: Microsoft Learn, "Export and import agents using solutions", documents Copilot Studio solution-based export/import and items requiring reconfiguration. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-export-import-bots`
[^cs-solutions]: Microsoft Learn, "Manage agents with solutions", Power Platform solution ALM for Copilot Studio. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-solutions-overview`
[^foundry-migrate]: Microsoft Learn, "Migrate to Foundry Agent Service", covers Assistants API/classic migration, not Copilot Studio agent migration. `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/migrate`
[^foundry-project-migrate]: Microsoft Learn, "Migrate from hub-based to Foundry project". `https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/migrate-project`
[^foundry-openai-upgrade]: Microsoft Learn, "Upgrade an Azure OpenAI resource to a Microsoft Foundry resource". `https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/upgrade-azure-openai`
[^comparison-404]: Confirmed during this research: `https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/copilot-studio-vs-foundry` returned HTTP 404; no standalone Microsoft Learn page titled "Copilot Studio vs Foundry" was found.
[^m365-decision]: Microsoft Learn, "Agents for Microsoft 365 Copilot - decision guide", declarative vs custom engine agent guidance. `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/decision-guide`
[^custom-engine]: Microsoft Learn, "Custom engine agents overview", includes comparison table with Copilot Studio, Teams AI, Agents SDK, and Foundry. `https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-custom-engine-agent`
[^cs-security]: Microsoft Learn, "Security and governance in Copilot Studio". `https://learn.microsoft.com/en-us/microsoft-copilot-studio/security-and-governance`
[^foundry-rbac]: Microsoft Learn, "Role-based access control in Microsoft Foundry". `https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry`
[^cs-topics]: Microsoft Learn, "Create and edit topics", "In Copilot Studio, a topic defines how an agent conversation progresses." `https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-create-edit-topics`
[^foundry-agents]: Microsoft Learn, "Foundry Agent Service overview", describes Prompt agents, Workflow agents, and Hosted agents. `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview`
[^foundry-workflow]: Microsoft Learn, "Workflow agents", describes visual/YAML workflow definitions and Power Fx usage. `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/workflow`
[^cs-connectors]: Microsoft Learn, "Use Power Platform connectors in Copilot Studio". `https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-connectors`
[^foundry-tools]: Microsoft Learn, "Tool catalog for Foundry Agent Service". `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog`
[^cs-channels]: Microsoft Learn, "Publish and deploy your agent", Copilot Studio channels. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/publication-fundamentals-publish-channels`
[^cs-analytics]: Microsoft Learn, "Analytics in Copilot Studio". `https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-overview`
[^cs-evaluation]: Microsoft Learn, "Evaluate your agent", Copilot Studio evaluation/test sets. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/analytics-agent-evaluation-overview`
[^foundry-observe]: Microsoft Learn, "Trace agents" and "Evaluate agents" in Azure AI Foundry observability/evaluation docs. `https://learn.microsoft.com/en-us/azure/ai-foundry/observability/concepts/trace-agent-concept` and `https://learn.microsoft.com/en-us/azure/ai-foundry/observability/how-to/evaluate-agent`
[^cs-billing]: Microsoft Learn, "Copilot Studio message management / Copilot Credits", including BYO Azure Foundry model billing note. `https://learn.microsoft.com/en-us/microsoft-copilot-studio/requirements-messages-management`
[^foundry-pricing]: Azure pricing page for AI Foundry / Agent Service. `https://azure.microsoft.com/en-us/pricing/details/ai-foundry/`
[^feature-status]: Current status verified from Microsoft Learn during this research: Copilot Studio A2A GA via What's New April 2026; Copilot Studio -> Foundry external agent Public Preview; Foundry A2A tool Public Preview; Foundry Workflow/Hosted agents Preview; Foundry MCP core framework/tool catalog GA with individual tools varying. Key URLs: `https://learn.microsoft.com/en-us/microsoft-copilot-studio/whats-new`, `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/agent-to-agent`, `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/hosted-agents`, `https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog`
[^cs-rest]: Microsoft Learn, "Use REST APIs as tools in Copilot Studio". `https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api`
[^apim-ai-gateway]: Microsoft Learn, "Azure API Management AI gateway capabilities". `https://learn.microsoft.com/en-us/azure/api-management/genai-gateway-capabilities`
[^rabobank]: Microsoft Learn Power Platform guidance case study, "Rabobank conversational banking", documents Copilot Studio agents and "Azure AI Foundry as a compliant generative AI enabler". `https://learn.microsoft.com/en-us/power-platform/guidance/case-studies/rabobank-conversational-banking`
[^abn-amro]: Microsoft Learn Power Platform guidance case study, "ABN AMRO enhances AI", documents migration to Copilot Studio from previous chatbot platform. `https://learn.microsoft.com/en-us/power-platform/guidance/case-studies/abn-amro-enhances-ai`
[^pva-cs]: Microsoft Copilot Studio product FAQ, states Power Virtual Agents is now included in Microsoft Copilot Studio. `https://www.microsoft.com/en-us/microsoft-copilot/microsoft-copilot-studio`
