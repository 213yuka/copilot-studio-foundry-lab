# copilot-studio-foundry-lab

Microsoft Copilot Studio と Microsoft Foundry の **違い・移行・併用パターン** を、調査レポートと実行可能なデモ素材の両面から学習するためのラボ リポジトリです。

> **位置付け**: 公式ドキュメントに基づく調査結果 (`research/`) と、6 つの移行/連携シナリオに対応する再現用素材 (`demo-assets/`) をセットで提供します。プロダクション用テンプレートではなく、**社内勉強会・PoC・お客様デモの出発点**として利用してください。

## ディレクトリ構成

```
.
├── README.md          ← このファイル
├── .gitignore
├── demo-assets/       ← 6 シナリオの再現素材一式 (手順書・サンプル コード・OpenAPI など)
└── research/          ← Microsoft Copilot Studio vs Microsoft Foundry の調査レポート (出典付き)
```

| ディレクトリ | 役割 | まず読むファイル |
|---|---|---|
| [`research/`](research/) | Microsoft Copilot Studio と Microsoft Foundry の機能差・移行可否・連携パターンの調査結果 | [`copilot-studio-foundry-final-report.md`](research/copilot-studio-foundry-final-report.md) |
| [`demo-assets/`](demo-assets/) | 6 シナリオ (A〜F) の手順書・コード・設定サンプル | [`README.md`](demo-assets/README.md) / [`00-create-cs-agent.md`](demo-assets/00-create-cs-agent.md) |

## 取り扱うシナリオ (demo-assets)

シナリオは **3 つのレイヤー** に整理しています。シナリオ A〜D / F は共通の出発点として **Microsoft Copilot Studio に同一の `IT-Helpdesk-Sample` エージェントを構築**します (シナリオ E は既存の Microsoft Copilot Studio エージェントを前提に開始)。

| シナリオ | レイヤー | Microsoft Foundry 側の受け皿 / 利用形態 | 状態 | Microsoft Copilot Studio 互換度 |
|---|---|---|---|---|
| **A** | エージェント本体 (移行) | Prompt agent | GA | 中 (instructions に集約) |
| **B** | エージェント本体 (移行) | Workflow agent | Preview | 高 (Power Fx / ノード継承) |
| **C** | エージェント本体 (移行) | Hosted agent | Preview | 低 (Python コードで再実装) |
| **D** | エージェント間連携 | Microsoft Copilot Studio + Microsoft Foundry agent 接続 | Preview | 最高 (Microsoft Copilot Studio はそのまま温存) |
| **E** | モデル / ツール単位 | Microsoft Copilot Studio + Microsoft Foundry モデル (BYOM) | GA | 最高 (Microsoft Copilot Studio はそのまま温存) |
| **F** | モデル / ツール単位 | Microsoft Copilot Studio + MCP server (Microsoft Foundry 含む) | GA | 最高 (Microsoft Copilot Studio はそのまま温存) |

詳細・前提条件・各シナリオの完全手順・選定フローチャートは [`demo-assets/README.md`](demo-assets/README.md) を参照してください。

## 使い方の流れ

1. [`research/copilot-studio-foundry-final-report.md`](research/copilot-studio-foundry-final-report.md) で両プロダクトの違いと「移行 vs 連携」の判断軸を把握する。
2. [`demo-assets/README.md`](demo-assets/README.md) でシナリオ A〜F の概要と選定フローチャートを確認し、目的に合うシナリオを選ぶ。
3. [`demo-assets/00-create-cs-agent.md`](demo-assets/00-create-cs-agent.md) に従って Microsoft Copilot Studio 側を構築する (シナリオ A〜D / F 共通。E は既存エージェントを前提)。
4. 選んだシナリオの README に沿って Microsoft Foundry 側 (またはモデル / MCP server) を構築・接続する。

> 💡 **段階的移行の推奨パス**: いきなり A〜C で全面移行するのではなく、まず **E (モデル品質を 1 Prompt で検証)** → **D (1 機能だけ agent 委譲で検証)** → 必要に応じ **A/B/C で全面移行**、という順で進めると低リスクです。F は D / E と並行して進められます。

## 前提・想定読者

- Microsoft Copilot Studio / Microsoft Foundry いずれかに触れた経験がある開発者・アーキテクト
- 移行や連携の判断材料、または社内デモのシナリオを探している方
- 必要なライセンス・RBAC・SDK バージョンは各シナリオ README に記載

## 注意事項

- 本リポジトリ内の説明・コードは **公開ドキュメントに基づく学習・検証用** です。Preview 機能の仕様は変更される可能性があるため、最終判断は必ず最新の公式ドキュメントで確認してください。
- `research/` のレポートは出典 (脚注) 付きで記述しています。差分や疑義があれば該当出典を参照してください。
- 自然言語の説明・手順は日本語、コード/識別子/公式名称は原文のままです。
