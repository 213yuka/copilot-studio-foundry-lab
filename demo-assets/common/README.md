# demo-assets/common — 共通素材ガイド

シナリオ A〜C (Microsoft Foundry agent 本体を作る系) で共通利用する素材です。シナリオ E / F でも一部を流用できます。

## ディレクトリ構成

```
common/
├── README.md          ← このファイル
├── sample-knowledge/
│   └── it-policy.md   ← Contoso 架空 IT 規定 (Markdown)
├── tools/
│   └── create-ticket.openapi.yaml  ← OpenAPI 3.0.1 (CreateTicket / httpbin.org)
└── scripts/
    └── upload_knowledge.py         ← Vector Store 作成 (シナリオ A〜C 共通)
```

## ファイル別の役割

### `sample-knowledge/it-policy.md`

- Contoso 架空 IT 規定 (Markdown 単一ファイル)。
- シナリオ A〜C の File Search Vector Store に取り込んで利用します。
- **PII を含まない**ことを前提に作成されています。改変する場合は秘密区分・PII 混入有無を必ず確認してください。

### `tools/create-ticket.openapi.yaml`

- OpenAPI 3.0.1。`operationId: create_ticket` (snake_case)。
- ダミー エンドポイント `https://httpbin.org/post` を指しています。本番転用時は **必ず社内 API エンドポイントに置換** し、認証スキーム (Bearer / API Key) を追加してください。
- `required: [summary, priority, category, user_consent]` を満たす呼出のみ受理する設計。
- シナリオ C 配下に同名コピー (`scenario-c-hosted-agent/tools/create-ticket.openapi.yaml`) があります。Windows で symlink が使えないため、Docker ビルド コンテキスト用に複製しています。**変更時は両方を同じ内容に更新** してください。

### `scripts/upload_knowledge.py`

- Microsoft Foundry の Vector Store にファイルを登録し、`vector_store_id` を取得するスクリプト。
- 新 SDK の `vector_stores.files.upload_and_poll` を優先利用し、利用不可な場合は `vector_stores.create` + ポーリングへフォールバックします。
- 公式 (`concepts/limits-quotas-regions`) に従い、`RateLimitError` / 一時的 5xx に対して **指数バックオフ + ジッター** でリトライします (最大 5 回)。
- 環境変数:
  - `FOUNDRY_PROJECT_ENDPOINT` (必須)
- 出力:
  - `file_id` / `vector_store_id` を標準出力に表示。

## 変更ルール

| 変更内容 | 必須対応 |
|---|---|
| `it-policy.md` の本文変更 | シナリオ A〜C の Vector Store を再アップロード。Playground での回答内容が想定どおりか手動で再確認 |
| `create-ticket.openapi.yaml` 変更 | `scenario-c-hosted-agent/tools/` 配下のコピーも同内容に更新 |
| `upload_knowledge.py` のリトライ・SDK 切替 | シナリオ A〜C で実際に Vector Store 作成が成功することを手動で確認 |

## 本番エンドポイント差替手順 (推奨)

1. **OpenAPI**: `servers[].url` を社内 API のホストに変更。`operationId` は snake_case を維持。
2. **認証**: `components.securitySchemes` に `Bearer` / `OAuth2` を追加し、`security` で参照。
3. **Vector Store**: 本番 PDF / Markdown を `it-policy.md` と差替え、PII を含まないことを再確認。
4. **PII マスキング**: ログ・トレーシングを Application Insights に送る場合、出力本文に対する PII マスキングを実装してください (例: 電話番号・メール・社員番号の正規表現置換)。

## 関連シナリオ

- [`scenario-a-prompt-agent/README.md`](../scenario-a-prompt-agent/README.md)
- [`scenario-b-workflow-agent/README.md`](../scenario-b-workflow-agent/README.md)
- [`scenario-c-hosted-agent/README.md`](../scenario-c-hosted-agent/README.md)
