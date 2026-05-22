# シナリオ F 用: Microsoft Copilot Studio MCP onboarding wizard 入力チェックリスト

公式ドキュメント (<https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent>) に基づく、MCP server 接続時の段階別チェックリストです。

## A. 接続前 (MCP server 側)

- [ ] Streamable HTTP transport で待ち受けている (SSE のみは **不可**: 2025-08 以降サポート終了)
- [ ] HTTPS で外部公開されている (Microsoft Copilot Studio から到達可能)
- [ ] サーバーが MCP 規格に準拠 (initialize / tools/list / tools/call / resources/list 等の標準メソッド対応)
- [ ] 公開する各 tool / resource に **description** が設定されている (orchestration の選定根拠)
- [ ] Microsoft Copilot Studio から MCP resource を利用したい場合は **MCP tool の output として resource を返す**設計になっている
- [ ] 認証方式が決定済 (None / API key / OAuth 2.0)
- [ ] (OAuth Manual の場合) Identity Provider 側にアプリ登録済、Callback URL を後で登録する手順を確認済

## B. Microsoft Copilot Studio 側 (Wizard 入力)

公式ステップ通りに入力:

1. **Tools** タブ → **+ Add a tool** → **New tool** → **Model Context Protocol**
2. 以下を入力:
   - [ ] **Server name** (例: `Contoso Helpdesk MCP`)
   - [ ] **Server description** (orchestration の判断材料。1〜2 文で簡潔・具体的に)
   - [ ] **Server URL** (HTTPS endpoint)
3. **Authentication type** を選択し、種別ごとに以下:

   ### None
   - [ ] `Create` のみで完了

   ### API key
   - [ ] **Type**: Header / Query を選択
   - [ ] **Param name** (例: `x-api-key`)
   - [ ] `Create` → 接続作成時に API key 値を入力

   ### OAuth 2.0 — Dynamic Discovery
   - [ ] `Create` のみで自動構成 (推奨。MCP server が DCR + discovery 対応の場合)

   ### OAuth 2.0 — Dynamic
   - [ ] **Authorization URL** (Identity Provider のクライアント登録 + 認可エンドポイント)
   - [ ] **Token URL template** (アクセス トークン取得エンドポイント)
   - [ ] `Create` → 表示された **Callback URL** を Identity Provider 側に登録

   ### OAuth 2.0 — Manual
   - [ ] **Client ID**
   - [ ] **Client Secret**
   - [ ] **Authorization URL**
   - [ ] **Token URL template**
   - [ ] **Refresh URL**
   - [ ] **Scopes** (空白区切り、任意)
   - [ ] `Create` → 表示された **Callback URL** を Identity Provider 側に登録

4. `Next` → `Create a new connection` → `Add to agent`

## C. 接続後 (動作確認)

- [ ] **Tools** タブに MCP server がツールとして表示される
- [ ] MCP server をクリックすると **Tools** タブと **Resources** タブで公開機能が一覧できる
- [ ] **MCP Prompts は表示されない** (公式 verbatim: _"Copilot Studio currently supports MCP tools and resources."_ — Prompts は未対応のため、tool/resource として再設計する必要あり)
- [ ] 不要な tool は **Allow all** を OFF にして個別に無効化済 (運用上の最小権限)
- [ ] Test pane で MCP tool を呼ぶ会話を流し、想定通り tool が選ばれることを確認
- [ ] **Track between topics** をオンにして orchestration の判断ログを確認
- [ ] MCP server 側のログに Microsoft Copilot Studio からのリクエストが到達していることを確認
- [ ] (OAuth の場合) ユーザーがチャットで初回呼出時に consent card に応答する動作を確認
- [ ] **既知の不具合** (`mcp-troubleshooting`) を確認: `exclusiveMinimum` integer の `System.FormatException` / tool definition の複数 type 配列で truncate / Reference type input フィルタ / enum input が string 解釈 などの SDK 由来の問題に該当しないか確認

## D. 運用前 (ガバナンス)

- [ ] Power Platform DLP で `Custom connector` 系の取り扱いを設計 (Business / Non-business 分離)
- [ ] MCP server 側の認可 (OAuth scope / API key の権限) が **最小権限**になっている
- [ ] MCP server 側のレート制限・監視・アラートを設定
- [ ] データ レジデンシー: ユーザー入力が MCP server ホスト地域に流れることを確認・社内承認済
- [ ] MCP server の Description と各 tool description を **業務語彙で具体的に**書き、orchestration の誤呼出を防止
- [ ] 公式注記の取扱 (verbatim): 「When you connect to a non-Microsoft product, including an external MCP server, you're responsible for the tools and resources you access from within Copilot Studio.」を関係者に共有
- [ ] **DLP と MCP の連鎖** (公式 `admin-data-loss-prevention` verbatim): _"Blocking Power Platform connectors also blocks access to tools in connected MCP servers."_ — Power Platform 管理センターで Power Platform connector を Block すると、その connector を経由する MCP server tool もブロックされることを認識・関係者に共有
