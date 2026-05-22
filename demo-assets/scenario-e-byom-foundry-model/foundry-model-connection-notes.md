# Microsoft Copilot Studio で接続する `Azure AI Foundry` コネクタの控え

Microsoft Copilot Studio から Microsoft Foundry のモデルを Bring-your-own-model (BYOM) で呼び出すために、Foundry 側で控えておく値のテンプレです。Power Platform の Connection 作成時に **deployment name** / **base model name** を入力するので、表記揺れが無いよう Foundry portal からコピーした値をそのまま貼り付けてください。

| 項目 | 値 | 取得場所 |
|---|---|---|
| Foundry project endpoint URL | `https://<resource>.services.ai.azure.com/api/projects/<project>` | Foundry portal → project → Overview → Libraries → Foundry |
| Subscription ID | | Foundry portal → project → Overview → Project details |
| Resource group | | 同上 |
| Foundry resource name | | 同上 |
| Foundry project name | | 同上 |
| 接続用リージョン | | デプロイしたモデルと同じリージョンに揃える |
| Model deployment 1: deployment name | | Models + Endpoints → 対象 deployment → Name |
| Model deployment 1: base model name | | Models + Endpoints → 対象 deployment → Model name |
| Model deployment 1: capability | (chat completion / image-capable / fine-tuned 等) | |
| Power Platform connector | `Azure AI Foundry` | Power Platform admin center → Data policies |
| Connection 作成者 (Maker) | | Microsoft Copilot Studio の Maker アカウント |

## Power Platform DLP の事前確認

- 管理 portal: <https://admin.powerplatform.microsoft.com>
- Data policies → 対象環境のポリシー → `Azure AI Foundry` コネクタが **Business** または **Non-business** に配置されていることを確認 (Blocked の場合は Microsoft Copilot Studio からの接続が失敗します)。

## Responsible AI チェックリスト

- [ ] Foundry 側 deployment に **Content filter** (Azure AI Content Safety) を設定済み
- [ ] Foundry 側で **Guardrails** (jailbreak / prompt injection 対策) を設定済み
- [ ] 会話履歴の保存 (Responses API の `store` 等) について法令・社内規程に整合
- [ ] データ レジデンシー: Microsoft Copilot Studio 環境のリージョンと Foundry deployment のリージョンが一致
- [ ] 課金: Microsoft Copilot Studio Message Capacity と Foundry モデル従量課金の予算割当が整理済み
