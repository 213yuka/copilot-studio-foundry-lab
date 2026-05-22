# Contributing

このリポジトリへの貢献を歓迎します。Microsoft Copilot Studio と Microsoft Foundry の連携パターン (シナリオ A〜F + 提案中の G/H/I) を、商談・社内デモ・PoC で再利用できる「動くリファレンス実装」として継続的に改善することを目的としています。

## 行動規範

参加にあたっては [Code of Conduct](./CODE_OF_CONDUCT.md) (Contributor Covenant v2.1) を遵守してください。

## ブランチ運用

- `main`: 安定ブランチ。動作確認済みのみ受け入れ。
- 機能追加・修正は feature ブランチを切って Pull Request を送ってください。命名例: `feat/scenario-c-add-azure-yaml` / `fix/scenario-a-rbac-scope`。

## Pull Request のルール

1. **対象シナリオを明示**: PR タイトルの先頭に対象を `[scenario-a]` / `[scenario-c]` / `[common]` / `[docs]` のように付けてください。
2. **公式根拠を引用**: 仕様や挙動に関する記述を追加・変更する場合は、Microsoft Learn / `microsoft/CopilotStudioSamples` / `microsoft-foundry/foundry-samples` などの公式 URL を必ず参照リンクとして PR 本文に記載してください。
3. **Preview / GA を明示**: 機能の状態 (Preview / Early Access Preview / GA) と確認日 (例: `(2026-05 時点)`) を本文中に明記してください。これらは Microsoft 側で変動するため、エビデンスが古くなるとレビュー時に再確認が必要になります。
4. **シークレット非混入**: `.env` / 接続文字列 / API キー / アクセストークン / Project endpoint の実値 / 個人名 / 内線番号など、組織を特定できる情報をコミットしないでください。CI 等で利用する場合は GitHub Secrets を経由してください。
5. **Preview 機能の注意**: Preview の API / ノード タイプ / プロトコルを利用したコード サンプルを追加する場合は、対応する Markdown に `⚠️ Preview` バッジ・SLA 対象外・破壊的変更の可能性を明記してください。

## ローカル動作確認

シナリオ別の前提条件・実行手順は各 `demo-assets/scenario-*/README.md` に記載されています。スクリプトを修正した場合は、対応するシナリオの README §「動作確認」/「テスト」セクションのコマンドが通ることを確認してください。

## ドキュメント変更

- 自然言語ドキュメント (README / Markdown) は **日本語** で書いてください。コード識別子・コマンド・ログ・公式名称は原文を尊重してください。
- 公式名称 (Microsoft Copilot Studio / Microsoft Foundry など) は略しないでください。Microsoft が公式に定めている略称 (AKS / ACR / ACA 等) のみ、初出時にフルネーム併記で使用可能です。

## 質問・議論

- 仕様の解釈で迷ったら、PR を出す前に Issue を立ててください。
- セキュリティ関連の脆弱性報告は [SECURITY.md](./SECURITY.md) を参照してください (GitHub Issue ではなく Private Security Advisory)。
