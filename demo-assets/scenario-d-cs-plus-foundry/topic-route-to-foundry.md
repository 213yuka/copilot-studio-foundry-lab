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

## サブエージェント側の Instructions (必須)

> ⚠️ **必ず Foundry agent 本体 (サブエージェント) の Instructions / System prompt に下記を追加してください**。これがないと、サブエージェントが Copilot Studio (親) を介さず直接ユーザーに返答してしまい、Copilot Studio 側の Adaptive Card / トピック分岐 / 課金カウントが乱れます。
>
> 公式 (`guidance/multi-agent-patterns`) verbatim:
>
> > **Single response principle: Subagents are researchers, not responders.**
>
> > Add to every subagent's instructions:
> > _"You're a subagent. **Do NOT reply to the user directly.** Return your findings to the orchestrator (the parent agent). The orchestrator will compose the user-facing answer. Use **NEVER / DO NOT / ONLY** when stating constraints to maximize compliance."_

`FoundryDeepResearch` (Foundry 側 Prompt agent / Workflow agent / Hosted agent) の Instructions に最低限以下を含めてください (日本語化例):

```
あなたは Copilot Studio 親エージェント (`IT-Helpdesk-Sample`) のサブエージェントです。
- **NEVER** ユーザーに直接返答しないでください。
- **DO NOT** Adaptive Card / 画像 / 装飾 を返さないでください。
- **ONLY** 親エージェントが整形しやすいよう、調査結果を構造化テキスト (見出し / 箇条書き) で返してください。
- 不確定な情報には必ず「確認できていない」と明示し、根拠 URL を併記してください。
- 親エージェントが追加情報を要求した場合のみ続報を返してください。
```

> 補足 (multi-agent-patterns):
>
> - "Subagents are researchers, not responders." — サブエージェントは研究者であって、応答者ではない。
> - **Single response principle** に違反すると、ユーザー体験 (ダブル メッセージ / 文体差) とテレメトリ (発火カウントの重複) が乱れます。
> - Connected agents は最大 **30〜40 choices of action** を境に再設計を検討する目安 (`authoring-add-other-agents`)。

---

## 設計のコツ

1. **既存 Topic と Foundry agent の境界線を Description に明文化** する
2. オーケストレータが迷う発話 (グレーゾーン) を意識的にテスト発話に入れる
3. Foundry agent 側の `instructions` にも **「定型タスクは Copilot Studio 側で処理されるはずなので、ここに来た時点で高度な質問のはず」** を書いておくと暴走を防げる
4. 接続後すぐに **Copilot Studio Analytics の Topic 発火率**と **Foundry portal の Tracing 呼出率**を 1 週間モニタし、想定通り振り分けされているか確認
5. 想定外の振り分けが起きたら Description を磨き込む (再デプロイ不要、Copilot Studio 側の保存だけで反映)
