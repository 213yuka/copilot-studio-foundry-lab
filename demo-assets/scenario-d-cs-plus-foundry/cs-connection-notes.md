# Foundry 接続情報メモ (テンプレ)

> Copilot Studio の **Add an agent → Microsoft Foundry** で入力する情報を、Foundry ポータルで取得して控えておくためのテンプレ。
> 機密値そのものはこのファイルにコミットせず、社内の Secret 保管庫に保存すること。

## 1. Foundry 側情報

| 項目 | 値 (記入欄) | 取得元 |
|---|---|---|
| Foundry tenant ID | _(GUID)_ | Foundry ポータル → Settings |
| Foundry project name | _(例: it-helpdesk-prj)_ | Foundry ポータル → Projects |
| **Project endpoint URL** | `https://<your-project>.services.ai.azure.com/api/projects/<project>` | Foundry ポータル → Project overview → Endpoint |
| Region | _(例: eastus2 / japaneast)_ | Project overview |
| **Agent Id** | _(例: asst_xxxxxxxxxxxxxxxx)_ | Foundry ポータル → Agents → 対象 agent → Details |
| Agent display name | _(例: IT-Helpdesk-Prompt-Agent)_ | 同上 |
| 対応シナリオ | □ A (Prompt) / □ B (Workflow) / □ C (Hosted) | — |

## 2. Copilot Studio 側で入力する情報

`Add an agent → Microsoft Foundry` のフォーム入力値:

| フィールド | 入力値の決め方 |
|---|---|
| Connection | 既存接続があれば再利用。無ければ新規作成し Project endpoint URL を入力 |
| Name | Copilot Studio 内で一意。例: `FoundryDeepResearch` |
| Description | **Copilot Studio オーケストレータが呼出判断に使う**。下記サンプル参照 |
| Agent Id | Foundry の Agent Id (`asst_xxx...`) を貼る |

### Description サンプル文言

> 「Contoso 社内 IT に関する **高度な調査依頼** (複数ソースの横断比較 / 最新セキュリティ脅威の解説 / 過去事例の Deep Research) を担当する Foundry 側エージェント。単純な FAQ や定型的なパスワード リセット手順は **このエージェントを呼ばず、Copilot Studio の既存 Topic で処理すること**。」

ポイント:
- **呼ぶべきケース** と **呼ぶべきでないケース** を両方明記する (オーケストレータの誤呼出を防ぐ)
- 既存の Copilot Studio Topic と役割が重複しないように書く

## 3. 動作確認チェックリスト

- [ ] Foundry portal で対象 agent が **新版 portal** で作成されている (旧版は非対応)
- [ ] Copilot Studio の Test pane で「(高度な質問例)」を投げて Foundry agent にルーティングされる
- [ ] Copilot Studio の Test pane で「(既存 FAQ 質問例)」を投げて **既存 Topic** で処理される (Foundry に流れない)
- [ ] Foundry portal の **Tracing** で Copilot Studio 経由の呼出が記録されている
- [ ] Copilot Studio Analytics で session が記録されている
- [ ] DLP ポリシー違反が出ていない
