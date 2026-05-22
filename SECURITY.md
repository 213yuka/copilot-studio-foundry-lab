# Security Policy

## 脆弱性の報告窓口

本リポジトリのコード・サンプル・設定ファイルにセキュリティ上の問題を発見した場合は、**公開 Issue ではなく GitHub Private Security Advisory** を一次窓口として報告してください。

- Private Security Advisory の作成手順: GitHub リポジトリの `Security` タブ → `Advisories` → `New draft security advisory` → 詳細を記入して送信
- 公式ドキュメント: <https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability>

## サポート対象

| 対象 | スコープ |
|---|---|
| `demo-assets/scenario-*/` 以下のサンプル コード | 報告対象 |
| `demo-assets/common/` の共通スクリプト・OpenAPI | 報告対象 |
| Microsoft Copilot Studio / Microsoft Foundry / Microsoft Agent Framework / Azure SDK 本体 | Microsoft 側の脆弱性報告窓口へお願いします (下記 §3) |

## 含めて欲しい情報

- 影響を受けるファイルとコミット ハッシュ (例: `b3a691c`)
- 再現手順 (環境 / 必要権限 / 入力)
- 想定される影響 (情報漏えい / 権限昇格 / DoS / プロンプト インジェクション 等)
- 既知の回避策 (あれば)

## OpenAPI / シークレットの取扱い

- 本リポジトリの `demo-assets/common/tools/*.openapi.yaml` および各シナリオ配下の OpenAPI は **デモ用のダミー エンドポイント** を指しています。実環境に転用する場合は、エンドポイント・認証スキームを必ず差し替えてください。
- `azure.yaml` / `agent.yaml` / `.env*` 等にシークレット (Project endpoint の実値 / API キー / 接続文字列 / Bearer token) を含めないでください。`.gitignore` に `.env` / `.env.*` を登録済みです。
- 誤ってシークレットをコミットした場合は、Issue では報告せず、まず GitHub のサポートに連絡して履歴のパージを依頼してください。同時に該当キーを失効・再発行してください。

## Microsoft 側プロダクトの脆弱性

Microsoft Copilot Studio、Microsoft Foundry、Microsoft Agent Framework、Azure SDK、Microsoft 公開モデル (Azure OpenAI / Foundry models) 自体の脆弱性は、Microsoft Security Response Center (MSRC) へ報告してください。

- MSRC: <https://msrc.microsoft.com/report>

## 対応 SLA (努力目標)

本リポジトリは個人用サンプルのため、商用 SLA は提供していません。報告いただいた内容については、可能な範囲で 14 日以内に最初のトリアージを行うことを目標とします。
