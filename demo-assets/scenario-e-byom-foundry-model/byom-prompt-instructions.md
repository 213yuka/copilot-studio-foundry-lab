# シナリオ E 用 Prompt サンプル: チケット要約 (Bring-your-own-model)

Microsoft Copilot Studio の **Tools → Add a tool → New tool → Prompt** に貼り付けて利用する想定のサンプル Instructions です。`IT-Helpdesk-Sample` エージェントで `CreateTicket` が起票したチケットの本文を要約する Prompt を想定しています。

```
あなたは Contoso 株式会社の社内 IT ヘルプデスクのアシスタントです。

# 入力
- ticket_summary: チケットの件名
- ticket_body: ユーザーから受け取った相談内容 (日本語の自然文)
- conversation_context: (任意) ここまでのチャット履歴の要約

# 出力
- 100 文字以内の日本語要約 1 行
- 緊急度 (high / medium / low) を 1 語で
- 推奨対応カテゴリ (account / vpn / mfa / hardware / other) を 1 語で

# 制約
- パスワード / MFA コード / PIN 等の秘密情報は出力しない
- 個人を特定できる情報 (氏名・電話番号・メール) は伏字 [REDACTED] に置換する
- 出力は次の JSON で:
  {
    "summary_ja": "...",
    "priority": "...",
    "category": "..."
  }
```

## 想定する Foundry モデル

| 用途 | 推奨モデル | 備考 |
|---|---|---|
| 日本語要約 (コスト最適) | `gpt-4o-mini` | chat completion / 画像非対応 |
| 日本語要約 (品質重視) | `gpt-4o` | chat completion / 画像対応 |
| 添付スクリーンショットから情報抽出 | `gpt-4o` または `Phi-3.5-vision-instruct` | image 入力対応 |
| ファインチューン社内モデル | (社内デプロイ名) | base model は親モデル名を指定 |

## 接続後の動作確認シナリオ

1. Microsoft Copilot Studio の Test pane でチケット起票を含む会話を流す
2. `CreateTicket` の HTTP Request ノード直後にこの Prompt を呼ぶ
3. JSON が期待通りに返ることを確認
4. Foundry portal → Models + Endpoints → 対象 deployment → Monitoring でリクエスト発生を確認

## 既知の注意点

- Prompt の Instructions に `[REDACTED]` を明記しないと、モデルによっては個人情報をそのまま要約に含めることがあります。
- 出力 JSON が崩れる場合は Foundry 側で **JSON mode / Structured Outputs** に対応したモデル (例: `gpt-4o`, `gpt-4o-mini`) を選択してください。
- `o1` 系モデルは system prompt をサポートしない仕様のため、Instructions の内容を user message に集約する必要があります (Microsoft Copilot Studio の Prompt 編集画面でも適宜調整)。
