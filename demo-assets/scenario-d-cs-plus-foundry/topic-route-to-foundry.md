# Copilot Studio 側ルーティング設計サンプル

> Copilot Studio 側で「どんな発話が来たら Foundry agent を呼ぶか」を設計するためのサンプル。
> Copilot Studio のオーケストレータ動作は **Generative orchestration (生成型オーケストレーション)** が有効である前提。

## サンプル: IT-Helpdesk-Sample に Foundry agent を追加するケース

### 既存 Copilot Studio 構成

| 既存 Topic | 動作 |
|---|---|
| `Greeting` | 挨拶を返す |
| `PasswordReset` | 社内/社外 PC 判定 → ガイド → 解決しなければチケット起票 |
| `VPNTrouble` | VPN 接続トラブル シューティング ガイド |
| `Fallback` | 該当 Topic 無し時の応答 |

### 追加する Foundry agent (例: シナリオ A の Prompt agent)

- **役割**: 既存 Topic でカバーされない高度な質問 (新種マルウェア解説 / 規制動向の調査 / 複数ナレッジ横断調査)
- **Name (Copilot Studio 側)**: `FoundryDeepResearch`

### Description (Copilot Studio の Add an agent フォームに入れる文言)

```
Contoso 社内 IT に関する「高度な調査依頼」専用エージェント。

【呼ぶべきケース】
- 最新のサイバー脅威 / 新種マルウェア / 規制動向の調査
- 複数のナレッジ ソースを横断した比較・要約
- 過去のインシデント事例の Deep Research
- 自然言語で曖昧に書かれた、定型 Topic に当てはまらない質問

【呼ぶべきでないケース】
- パスワード リセット (→ 既存 PasswordReset Topic)
- VPN 接続トラブル (→ 既存 VPNTrouble Topic)
- 単純な FAQ (→ 既存 Knowledge)
- 申請フォーム提出 (→ 既存 Power Automate)
```

### Trigger 動作の検証用テスト発話

| ユーザー発話 | 期待するルーティング先 |
|---|---|
| 「パスワード忘れた」 | 既存 `PasswordReset` Topic |
| 「VPN つながらない」 | 既存 `VPNTrouble` Topic |
| 「最近流行ってる Microsoft 365 を狙ったフィッシング手口を、社内ナレッジと最新情報を踏まえて教えて」 | **Foundry agent (`FoundryDeepResearch`)** |
| 「過去 1 年で発生した類似インシデントを比較して」 | **Foundry agent (`FoundryDeepResearch`)** |
| 「こんにちは」 | 既存 `Greeting` Topic |

## 設計のコツ

1. **既存 Topic と Foundry agent の境界線を Description に明文化** する
2. オーケストレータが迷う発話 (グレーゾーン) を意識的にテスト発話に入れる
3. Foundry agent 側の `instructions` にも **「定型タスクは Copilot Studio 側で処理されるはずなので、ここに来た時点で高度な質問のはず」** を書いておくと暴走を防げる
4. 接続後すぐに **Copilot Studio Analytics の Topic 発火率**と **Foundry portal の Tracing 呼出率**を 1 週間モニタし、想定通り振り分けされているか確認
5. 想定外の振り分けが起きたら Description を磨き込む (再デプロイ不要、Copilot Studio 側の保存だけで反映)
