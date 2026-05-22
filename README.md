# copilot-studio-foundry-lab

Copilot Studio と Microsoft Foundry の **違い・移行・併用パターン** を、調査レポートと実行可能なデモ素材の両面から学習するためのラボ リポジトリです。

> **位置付け**: 公式ドキュメントに基づく調査結果 (`research/`) と、4 つの移行/併用シナリオに対応する再現用素材 (`demo-assets/`) をセットで提供します。プロダクション用テンプレートではなく、**社内勉強会・PoC・お客様デモの出発点**として利用してください。

## ディレクトリ構成

```
.
├── README.md          ← このファイル
├── .gitignore
├── demo-assets/       ← 4 シナリオの再現素材一式 (手順書・サンプル コード・OpenAPI など)
└── research/          ← Copilot Studio vs Foundry の調査レポート (出典付き)
```

| ディレクトリ | 役割 | まず読むファイル |
|---|---|---|
| [`research/`](research/) | Copilot Studio と Foundry の機能差・移行可否・併用パターンの調査結果 | [`copilot-studio-foundry-final-report.md`](research/copilot-studio-foundry-final-report.md) |
| [`demo-assets/`](demo-assets/) | 4 シナリオ (A〜D) の手順書・コード・設定サンプル | [`README.md`](demo-assets/README.md) / [`00-create-cs-agent.md`](demo-assets/00-create-cs-agent.md) |

## 取り扱うシナリオ (demo-assets)

4 シナリオはすべて、共通の出発点として **Copilot Studio に同一の `IT-Helpdesk-Sample` エージェントを構築**し、Foundry 側の受け皿だけを変える構成です。

| シナリオ | Foundry 側の受け皿 | 状態 | Copilot Studio 互換度 |
|---|---|---|---|
| **A** | Prompt agent | GA | 中 (instructions に集約) |
| **B** | Workflow agent | Preview | 高 (Power Fx / ノード継承) |
| **C** | Hosted agent | Preview | 低 (Python コードで再実装) |
| **D** | Copilot Studio + Foundry 併用 | Preview | 最高 (Copilot Studio はそのまま温存) |

詳細・前提条件・各シナリオの完全手順は [`demo-assets/README.md`](demo-assets/README.md) を参照してください。

## 使い方の流れ

1. [`research/copilot-studio-foundry-final-report.md`](research/copilot-studio-foundry-final-report.md) で両プロダクトの違いと「移行 vs 併用」の判断軸を把握する。
2. [`demo-assets/README.md`](demo-assets/README.md) でシナリオ A〜D の概要を確認し、目的に合うシナリオを選ぶ。
3. [`demo-assets/00-create-cs-agent.md`](demo-assets/00-create-cs-agent.md) に従って Copilot Studio 側を構築する (全シナリオ共通)。
4. 選んだシナリオの README に沿って Foundry 側の受け皿を構築・接続する。

## 前提・想定読者

- Copilot Studio / Microsoft Foundry いずれかに触れた経験がある開発者・アーキテクト
- 移行や併用の判断材料、または社内デモのシナリオを探している方
- 必要なライセンス・RBAC・SDK バージョンは各シナリオ README に記載

## 注意事項

- 本リポジトリ内の説明・コードは **公開ドキュメントに基づく学習・検証用** です。Preview 機能の仕様は変更される可能性があるため、最終判断は必ず最新の公式ドキュメントで確認してください。
- `research/` のレポートは出典 (脚注) 付きで記述しています。差分や疑義があれば該当出典を参照してください。
- 自然言語の説明・手順は日本語、コード/識別子/公式名称は原文のままです。
