"""コード ファイルを VS Code 風のシンタックス ハイライト付きで HTML 化 → Playwright で画像化。
README にコード スニペットを「資料っぽい画像」として埋め込むため。
"""

import html
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "demo-assets" / "screenshots" / "scenario-a"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Prism.js を CDN から読み込んで簡易シンタックス ハイライト
TEMPLATE = """<!doctype html>
<html><head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-okaidia.min.css">
<style>
  body {{ background:#1e1e1e; color:#ddd; font-family:'Cascadia Code','Consolas',monospace; margin:0; padding:0; }}
  .titlebar {{ background:#3c3c3c; color:#ccc; padding:8px 16px; font-size:12px; border-bottom:1px solid #1e1e1e; display:flex; align-items:center; gap:8px; }}
  .dot {{ width:11px; height:11px; border-radius:50%; }}
  .dot.r {{ background:#ff5f56; }} .dot.y {{ background:#ffbd2e; }} .dot.g {{ background:#27c93f; }}
  .fname {{ margin-left:12px; color:#fff; font-size:13px; }}
  pre {{ margin:0; padding:18px 22px; font-size:13px; line-height:1.55; background:#272822 !important; }}
  code {{ font-family:'Cascadia Code','Consolas',monospace; }}
</style>
</head><body>
  <div class="titlebar">
    <span class="dot r"></span><span class="dot y"></span><span class="dot g"></span>
    <span class="fname">{filename}</span>
  </div>
  <pre><code class="language-{lang}">{code}</code></pre>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-yaml.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>
</body></html>"""


FILES = [
    (
        "../common/tools/create-ticket.openapi.yaml",
        "yaml",
        "create-ticket.openapi.yaml",
        "A-CODE-01-openapi-yaml.png",
        None,  # 全部
    ),
    (
        "create_prompt_agent.py",
        "python",
        "create_prompt_agent.py",
        "A-CODE-02-prompt-agent-script.png",
        (70, 99),  # main 関数のあたり
    ),
    (
        "../common/sample-knowledge/it-policy.md",
        "markdown",
        "it-policy.md (抜粋 §2.3 パスワード忘れ・ロックアウト時の対応)",
        "A-CODE-03-it-policy-md.png",
        (30, 70),
    ),
]


def main() -> None:
    base = Path(__file__).resolve().parent
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1300, "height": 800},
                                  device_scale_factor=2)
        page = ctx.new_page()
        for rel, lang, fname, out, line_range in FILES:
            text = (base / rel).read_text(encoding="utf-8")
            if line_range:
                lines = text.splitlines()
                start, end = line_range
                text = "\n".join(lines[start - 1:end])
            content = TEMPLATE.format(
                filename=html.escape(fname),
                lang=lang,
                code=html.escape(text),
            )
            page.set_content(content)
            # Prism がハイライトを終えるまで待機
            page.wait_for_timeout(800)
            height = page.evaluate("document.body.scrollHeight") + 8
            page.set_viewport_size({"width": 1300, "height": int(height)})
            target = OUT_DIR / out
            page.screenshot(path=str(target), full_page=False)
            print(f"saved -> {target}")
        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
