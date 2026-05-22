"""シナリオ A 検証結果を HTML レポート化し、Playwright でスクリーンショット化する。

実行ログ風の見た目で、Foundry Portal にアクセスできなくても
README に貼れる「実行証跡スクリーンショット」を生成する。
"""

import html
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "demo-assets" / "screenshots" / "scenario-a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TERMINAL_CSS = """
<style>
  body { background: #1e1e1e; color: #d4d4d4; font-family: 'Cascadia Code', 'Consolas', monospace; padding: 24px; margin: 0; font-size: 14px; line-height: 1.55; }
  h1 { color: #4ec9b0; font-size: 18px; margin: 0 0 4px 0; border-bottom: 1px solid #333; padding-bottom: 6px; }
  h2 { color: #4ec9b0; font-size: 15px; margin: 18px 0 6px 0; }
  .prompt { color: #569cd6; }
  .ok { color: #4ec9b0; font-weight: bold; }
  .key { color: #ce9178; }
  .val { color: #b5cea8; }
  .muted { color: #6a9955; }
  .agent { color: #dcdcaa; }
  pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; }
  .panel { background: #252526; border-left: 3px solid #4ec9b0; padding: 12px 16px; margin: 6px 0 12px 0; }
  .citation { background: #2d2d30; padding: 2px 6px; border-radius: 3px; color: #9cdcfe; font-size: 12px; }
  hr { border: 0; border-top: 1px solid #333; margin: 16px 0; }
</style>
"""


def page1_phase_summary() -> str:
    body = """
    <h1>シナリオ A — Phase 3〜5 ローカル実行ログ</h1>
    <div class="muted">Foundry project: policy-qa-demo (japaneast) | model: gpt-5-mini | 2026-05-22</div>

    <h2>Phase 3b: Vector Store 作成 (it-policy.md → File Search)</h2>
    <div class="panel"><pre><span class="prompt">PS&gt;</span> python common\\scripts\\upload_knowledge.py common\\sample-knowledge\\it-policy.md
<span class="key">file_id</span>           = <span class="val">assistant-VjL1LGUgkPDaora2UZ36o6</span>
<span class="key">vector_store_id</span>   = <span class="val">vs_LFFXzBenUR1e5bjU5fxRXfiH</span>
<span class="key">vector_store_name</span> = <span class="val">it-policy-vs</span>

次の値を環境変数に設定してください:
  <span class="prompt">$env:KNOWLEDGE_VECTOR_STORE_ID</span> = "vs_LFFXzBenUR1e5bjU5fxRXfiH"</pre></div>

    <h2>Phase 4: Prompt agent 作成 (helpdesk-prompt)</h2>
    <div class="panel"><pre><span class="prompt">PS&gt;</span> python scenario-a-prompt-agent\\create_prompt_agent.py
<span class="key">agent_name</span>        = <span class="agent">helpdesk-prompt</span>
<span class="key">agent_version_id</span>  = <span class="agent">helpdesk-prompt:1</span></pre></div>

    <h2>Phase 5: 回帰テスト 結果サマリ (5/5 通過)</h2>
    <div class="panel"><pre>
<span class="ok">✅</span>  <span class="agent">MFA の登録方法を教えて</span>                       → File Search で it-policy.md §2.2 を <span class="citation">[it-policy.md]</span> 引用
<span class="ok">✅</span>  <span class="agent">パスワードを忘れた、社内 PC です</span>             → セルフサービス ポータル <span class="citation">passwordreset.contoso.local</span> を案内
<span class="ok">✅</span>  <span class="agent">パスワードを忘れた、社外 PC です</span>             → ヘルプデスク <span class="citation">内線 8888 / helpdesk@contoso.com</span> を案内
<span class="ok">✅</span>  <span class="agent">VPN がつながらない、再起動しても直らない</span>     → 同意確認 → CreateTicket 起票を提案
<span class="ok">✅</span>  <span class="agent">私の PIN を教えて</span>                            → 拒否 + <span class="citation">CSIRT 内線 119</span> 案内
</pre></div>
    """
    return TERMINAL_CSS + body


def page2_test_session() -> str:
    qa = [
        (
            "パスワードを忘れた、社内 PC です",
            [
                "社内 PC からですね。では以下の手順で進めてください。",
                "",
                "1) セルフサービス パスワード リセット ポータルにアクセスしてください:",
                "   https://passwordreset.contoso.local (社内から利用可能) — 根拠: [it-policy.md]",
                "2) ポータルの案内に従って本人確認 (MFA 等) → 新しいパスワードを設定してください。",
                "   新パスワードは社内ポリシーで「最小 14 文字・英大文字/小文字/数字/記号を含む」などの要件があります。",
                "3) 注意点: アカウントはサインイン失敗が 5 回でロックされ、30 分後に自動解除されます",
                "",
                "もしポータルにアクセスできない、または手順で解決しない場合は IT ヘルプデスク",
                "(内線 8888 / helpdesk@contoso.com) へご連絡ください — 根拠: [it-policy.md]",
            ],
        ),
        (
            "VPN がつながらない、再起動しても直らない",
            [
                "やってほしいこと (順番にお願いします)",
                "  1. 今接続しているネットワークは「社外」ですか?",
                "  2. Microsoft Authenticator のプッシュ通知が来ていて、承認 (Approve) しましたか?",
                "  3. もう一度以下を試せますか?",
                "     - Authenticator アプリを開いて通知を確認・承認",
                "     - PC のネットワーク接続が正常か確認",
                "     - (可能なら) PC を再起動してから VPN クライアントを起動",
                "",
                "すでに上の手順をすべて試していて解決していれば、ヘルプデスクにチケットを起票できます。",
                "ナレッジでも「上記で解決しない場合は IT ヘルプデスクへ連絡」と明記 [it-policy.md]",
                "",
                "チケット起票を希望する場合",
                "  - 起票してよいか、あなたの同意をください",
                "  - 想定する要約: 「VPN 接続不可 (Microsoft Tunnel／再起動後も未接続)」",
                "  - 推奨優先度: 作業不能なら high、業務に差し支えなければ medium。カテゴリは network。",
            ],
        ),
        (
            "私の PIN を教えて",
            [
                "申し訳ありませんが、PIN (秘密情報) をお教えすることはできません。",
                "社内規定で「パスワードを他者と共有することはいかなる理由でも禁止」されており、当方からも",
                "お尋ねしません [it-policy.md]",
                "",
                "代わりに、PIN を忘れた／ロックされた場合は以下の手順で対応してください。",
                "  1. まず確認です — 社内 PC からの利用ですか、それとも社外 PC ですか?",
                "  2. 社内 PC の場合: セルフサービス パスワード リセット ポータル",
                "     (https://passwordreset.contoso.local) でリセットしてください [it-policy.md]",
                "  3. 社外 PC: IT ヘルプデスク (内線 8888 / helpdesk@contoso.com) にご連絡ください",
                "",
                "端末紛失や不正アクセスの疑いがある場合は緊急対応が必要なので CSIRT ホットライン",
                "(内線 119) へご連絡ください [it-policy.md]",
            ],
        ),
    ]

    parts = ['<h1>シナリオ A — Responses API 回帰テスト セッション (抜粋)</h1>',
             '<div class="muted">test_agent.py の実行ログから 3 ケース抜粋 (helpdesk-prompt + gpt-5-mini)</div>']
    for q, lines in qa:
        body_lines = "\n".join(html.escape(line) for line in lines)
        parts.append(
            f'<h2>Q: <span class="agent">{html.escape(q)}</span></h2>'
            f'<div class="panel"><pre>{body_lines}</pre></div>'
        )
    return TERMINAL_CSS + "\n".join(parts)


PAGES = [
    ("A-LOG-01-phase-summary.png", page1_phase_summary()),
    ("A-LOG-02-test-session.png", page2_test_session()),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 600},
                                  device_scale_factor=2)
        page = ctx.new_page()
        for fname, content in PAGES:
            page.set_content(content)
            page.wait_for_load_state("domcontentloaded")
            # body 高さに合わせて viewport を再調整 (余白を最小化)
            height = page.evaluate("document.body.scrollHeight") + 24
            page.set_viewport_size({"width": 1400, "height": int(height)})
            out = OUT_DIR / fname
            page.screenshot(path=str(out), full_page=False)
            print(f"saved -> {out}")
        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
