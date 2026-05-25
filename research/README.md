# research — Microsoft Copilot Studio × Microsoft Foundry 調査レポート

本ディレクトリは Microsoft Copilot Studio と Microsoft Foundry の機能差・移行可否・連携パターン・最新アップデートを公式ドキュメント (Microsoft Learn / 公式 GitHub サンプル) と突き合わせて整理した調査レポートを格納しています。

## 構成

| ファイル | 内容 |
|---|---|
| [`copilot-studio-foundry-final-report.md`](./copilot-studio-foundry-final-report.md) | 製品比較レポート (両プロダクトの違い) |
| [`copilot-studio-updates-2025-2026.md`](./copilot-studio-updates-2025-2026.md) | Microsoft Copilot Studio 側の 2025〜2026 年アップデート追跡 |
| [`microsoft-foundry-updates-2025-2026.md`](./microsoft-foundry-updates-2025-2026.md) | Microsoft Foundry 側の 2025〜2026 年アップデート追跡 |

## 出典ポリシー

1. **一次情報は Microsoft Learn を最優先** とする。
2. 一次情報と本リポジトリの実装が乖離している場合は、その差分を明示する。
3. URL は引用時点の最終確認日 (例: `2026-05 時点`) を併記する。Microsoft 側で URL が再構成されることがあるため、404 発生時は更新する。
4. Preview / Early Access Preview 機能は SLA 対象外であること、本番運用時に破壊的変更が起こりうることを必ず併記する。
5. **公式名称を略さない**: Microsoft Copilot Studio / Microsoft Foundry をそれぞれ "CS" / "MF" 等に略さない。Microsoft 公式の略称 (AKS / ACR / ACA 等) のみ、初出時にフルネーム併記で使用可。

## 更新方針

- レポートは **定期的に最新化** が必要です。Microsoft Copilot Studio / Microsoft Foundry の機能ステータス (Preview ↔ GA) は四半期単位で変動するため、最低でも 3 か月に 1 度の見直しを推奨します。
- 過去レポートはバージョン管理 (git history) で追跡されます。CHANGELOG 形式で各レポート末尾に「最終更新日」と「次回見直し目安」を記載することを推奨します。

## 報告 / 議論

公式ドキュメントとレポートの差分、または新規シナリオ案 (現状の 7 シナリオ A〜F + H を超える提案) は、Issue を立ててから PR を送付してください。詳細は [`../CONTRIBUTING.md`](../CONTRIBUTING.md) を参照。

> ℹ️ かつて "新規シナリオ候補" として提案されていた **H (APIM AI Gateway)** は、`demo-assets/scenario-h-apim-ai-gateway/` として **正式に独立シナリオ化済み**です (+ 横断補助ドキュメント `../docs/governance.md` / `../docs/cost-finops.md`)。
