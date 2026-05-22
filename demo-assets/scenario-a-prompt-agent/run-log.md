# シナリオ A: ローカル実行ログ (2026-05-22 検証)

> このファイルは本リポジトリで実際にシナリオ A の Phase 3〜5 を実行した結果のログです。
> 環境: Windows 11 + Python 3.12 + azure-ai-projects 2.1.0 + Foundry project `policy-qa-demo` (japaneast)
> モデル: `gpt-5-mini` (README 想定の `gpt-4.1-mini` を未デプロイ環境向けに代用)

---

## 1. 環境変数

```powershell
$env:FOUNDRY_PROJECT_ENDPOINT  = "https://self-test-pj-resource.services.ai.azure.com/api/projects/policy-qa-demo"
$env:FOUNDRY_MODEL_NAME        = "gpt-5-mini"
```

## 2. Phase 3b: Vector Store にナレッジをアップロード

```powershell
> python common\scripts\upload_knowledge.py common\sample-knowledge\it-policy.md
file_id           = assistant-VjL1LGUgkPDaora2UZ36o6
vector_store_id   = vs_LFFXzBenUR1e5bjU5fxRXfiH
vector_store_name = it-policy-vs
```

```powershell
$env:KNOWLEDGE_VECTOR_STORE_ID = "vs_LFFXzBenUR1e5bjU5fxRXfiH"
```

## 3. Phase 4: Prompt agent を作成

```powershell
> python scenario-a-prompt-agent\create_prompt_agent.py
agent_name        = helpdesk-prompt
agent_version_id  = helpdesk-prompt:1
```

## 4. Phase 5: 回帰テスト (Responses API)

`scenario-a-prompt-agent\test_agent.py` の出力(抜粋、`gpt-5-mini` 平均応答 25 秒前後)。

### 4.1 ✅ `MFA の登録方法を教えて`

> Contoso では全アカウントで Microsoft Authenticator または FIDO2 セキュリティキーによる MFA 登録が必須です。また SMS 認証は段階的に廃止予定です…
>
> 1) Microsoft Authenticator (スマホアプリ) での登録 (一般的手順)
>    - スマートフォンに「Microsoft Authenticator」アプリをインストール…
>    - PC またはブラウザで Microsoft のセキュリティ情報ページにサインイン (例: aka.ms/mfasetup)
>    - 「セキュリティ情報の追加」→「Authenticator アプリ」を選択…
>
> 2) FIDO2 セキュリティ キーでの登録 …

→ `it-policy.md §2.2` を引用しつつ、不足分を LLM の常識で補完(秘密情報を要求しない注意書きも付与)。

### 4.2 ✅ `パスワードを忘れた、社内 PC です`

> 社内 PC からですね。では以下の手順で進めてください。
>
> 1) セルフサービス パスワード リセット ポータルにアクセスしてください: https://passwordreset.contoso.local (社内から利用可能) — 根拠: it-policy.md
> 2) ポータルの案内に従って本人確認 (MFA 等) → 新しいパスワードを設定してください…
> 3) 注意点: アカウントはサインイン失敗が 5 回でロックされ、30 分後に自動解除されます…

→ Topic「PasswordReset」社内分岐を完全再現。

### 4.3 ✅ `パスワードを忘れた、社外 PC です`

> 社外 PC からのご利用ですね。社外からパスワードを忘れた場合は、IT ヘルプデスクへご連絡ください。
> ヘルプデスクが本人確認のうえでリセット手続きを行います (連絡先: 内線 8888 / helpdesk@contoso.com)。[it-policy.md]

→ Topic「PasswordReset」社外分岐を完全再現。

### 4.4 ✅ `VPN がつながらない、再起動しても直らない`

> やってほしいこと (順番にお願いします)
> 1. 今接続しているネットワークは「社外 (自宅／カフェ／モバイル回線等)」ですか?
> 2. Microsoft Authenticator のプッシュ通知が来ていて、承認 (Approve) しましたか?
> 3. もう一度以下を試せますか?
>    - Authenticator アプリを開いて通知を確認・承認
>    - PC のネットワーク接続が正常か確認
>    - (可能なら) PC を再起動してから VPN クライアントを起動
>
> すでに上の手順をすべて試していて解決していれば、ヘルプデスクにチケットを起票できます…
>
> **チケット起票を希望する場合**
> - 起票してよいか、あなたの同意をください
> - 想定する要約: 「VPN 接続不可 (Microsoft Tunnel／再起動後も未接続)」
> - 推奨優先度: 作業不能なら high、業務に差し支えなければ medium。カテゴリは network。

→ ナレッジ手順 → ユーザー同意確認 → CreateTicket 起票の流れを **同意フローを守って提案**。

### 4.5 ✅ `私の PIN を教えて`

> 申し訳ありませんが、PIN (秘密情報) をお教えすることはできません。社内規定で「パスワードを他者と共有することはいかなる理由でも禁止」されており、当方からもお尋ねしません [it-policy.md]
>
> …また、端末紛失や不正アクセスの疑いがある場合は緊急対応が必要なので CSIRT ホットライン (内線 119) へご連絡ください [it-policy.md]

→ 拒否 + CSIRT 案内 + 代替手順案内、すべて Instructions の禁止事項に忠実。

---

## 5. 回帰テスト結果

| 検証項目 | 期待 | 結果 |
|---|---|---|
| MFA 登録 | it-policy.md §2.2 引用 | ✅ |
| パスワード忘れ + 社内 PC | passwordreset.contoso.local 案内 | ✅ |
| パスワード忘れ + 社外 PC | 内線 8888 / helpdesk@contoso.com 案内 | ✅ |
| VPN 不可で続報 | 同意確認 → CreateTicket 提案 | ✅ |
| PIN 要求 | 拒否 + CSIRT 案内 | ✅ |

5/5 (intent 一致率 100%)。応答時間は 20〜27 秒(`gpt-5-mini`、SDK + Foundry round trip 込み)。

---

## 6. 検証中に発見した README/コード課題

| # | 課題 | 対応 |
|---|---|---|
| 1 | `common/scripts/upload_knowledge.py` が旧 API (`agents.upload_file_and_poll`) を呼んでおり、`azure-ai-projects>=2.0` で削除済み | 新 API (`openai.vector_stores.create`) に書き換え |
| 2 | `scenario-a-prompt-agent/create_prompt_agent.py` の OpenAPI auth が `dict` で渡されていたが SDK が `OpenApiAnonymousAuthDetails` クラスを要求 | クラス インスタンスに置き換え |
| 3 | 同上の `spec=OPENAPI_SPEC` が YAML 文字列。SDK は dict 必須 | `yaml.safe_load()` で dict 化 (`pyyaml` を requirements に追加) |
| 4 | Windows で `cmd.exe` 起動時の PATH 切り捨てにより `AzureCliCredential` が「Azure CLI not found」で失敗 | README §10 (トラブルシューティング) に手順追記、または Python 起動前に PATH を短縮 |
| 5 | `gpt-4.1-mini` 想定だが GPT-5 系のみデプロイされた project でも動くことを確認 | README §4.2 でモデル選択肢を補足 |
