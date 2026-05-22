"""Microsoft Learn 公式ドキュメントのスクリーンショットを取得 (認証不要)。
README から参照画像としてリンクするためのリファレンス キャプチャ。
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "demo-assets" / "screenshots" / "scenario-a" / "reference-docs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


PAGES = [
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview",
        "ref-01-agents-overview.png",
    ),
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code",
        "ref-02-quickstart.png",
    ),
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/file-search",
        "ref-03-file-search.png",
    ),
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec",
        "ref-04-openapi-tool.png",
    ),
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/runtime-components",
        "ref-05-runtime-components.png",
    ),
    (
        "https://learn.microsoft.com/en-us/azure/ai-foundry/concepts/rbac-foundry",
        "ref-06-rbac-foundry.png",
    ),
]


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        page = ctx.new_page()
        for url, fname in PAGES:
            print(f"-> {fname}\n   {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                time.sleep(3)  # 残りのスクリプト読み込み
                # cookie banner を閉じる
                try:
                    btn = page.locator('button:has-text("Accept")').first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        time.sleep(1)
                except Exception:
                    pass
                page.screenshot(path=str(OUT_DIR / fname), full_page=False)
                print(f"   saved -> {OUT_DIR / fname}")
            except Exception as e:
                print(f"   error: {e}")
        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
