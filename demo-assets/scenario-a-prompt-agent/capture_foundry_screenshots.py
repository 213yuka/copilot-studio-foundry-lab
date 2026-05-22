"""Foundry Portal のスクリーンショットを撮影。

- Persistent context (chromium) を使い、サインイン状態を user-data ディレクトリに保存
- 初回は MFA を含むサインインが必要 (ブラウザが開いた状態でユーザーが操作)
- 2 回目以降は cookies が再利用され、自動で各ページに移動 → スクリーンショット
"""

import os
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOT_DIR = REPO_ROOT / "demo-assets" / "screenshots" / "scenario-a"
PROFILE_DIR = Path(__file__).resolve().parent / ".pw-profile"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

# Foundry project は environment variable で指定
ENDPOINT = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "")
# https://<resource>.services.ai.azure.com/api/projects/<project>
# → portal URL は https://ai.azure.com/foundryProject/overview?wsid=...
#
# 以下の値は環境変数から読み込む (公開リポジトリにテナント固有 ID を残さないため)。
#   AZURE_SUBSCRIPTION_ID  : Azure サブスクリプション GUID
#   AZURE_RESOURCE_GROUP   : リソースグループ名 (例: rg-aoai)
#   FOUNDRY_RESOURCE_NAME  : Azure AI Foundry (Cognitive Services account) のリソース名
#   FOUNDRY_PROJECT_NAME   : Foundry プロジェクト名
SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "<YOUR_SUBSCRIPTION_ID>")
RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "<YOUR_RESOURCE_GROUP>")
RESOURCE_NAME = os.environ.get("FOUNDRY_RESOURCE_NAME", "<YOUR_FOUNDRY_RESOURCE>")
PROJECT_NAME = os.environ.get("FOUNDRY_PROJECT_NAME", "<YOUR_FOUNDRY_PROJECT>")

if any(v.startswith("<") for v in (SUBSCRIPTION_ID, RESOURCE_GROUP, RESOURCE_NAME, PROJECT_NAME)):
    print(
        "[warn] AZURE_SUBSCRIPTION_ID / AZURE_RESOURCE_GROUP / FOUNDRY_RESOURCE_NAME / "
        "FOUNDRY_PROJECT_NAME のいずれかが未設定です。実行前に環境変数で指定してください。",
        file=sys.stderr,
    )

WSID = (
    f"/subscriptions/{SUBSCRIPTION_ID}"
    f"/resourceGroups/{RESOURCE_GROUP}"
    f"/providers/Microsoft.CognitiveServices/accounts/{RESOURCE_NAME}"
    f"/projects/{PROJECT_NAME}"
)


PAGES = [
    # (url, filename, wait_selector_or_seconds)
    ("https://ai.azure.com/", "A-01-foundry-home.png", 10),
    (f"https://ai.azure.com/foundryProject/overview?wsid={WSID}", "A-02-project-overview.png", 12),
    (f"https://ai.azure.com/foundryProject/agents?wsid={WSID}", "A-03-agents-list.png", 12),
    (f"https://ai.azure.com/foundryProject/agents/helpdesk-prompt?wsid={WSID}", "A-04-agent-detail.png", 15),
    (f"https://ai.azure.com/foundryProject/data?wsid={WSID}", "A-05-data-vector-stores.png", 12),
    (f"https://ai.azure.com/foundryProject/modelsAndEndpoints?wsid={WSID}", "A-06-models-endpoints.png", 12),
]


def main() -> None:
    headless = "--headless" in sys.argv
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=headless,
            viewport={"width": 1600, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for url, fname, wait in PAGES:
            print(f"-> {fname}")
            print(f"   {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            except Exception as e:
                print(f"   navigation timeout/error: {e}")
            # サインイン画面に到達した場合、ユーザーに sign in を促す (初回のみ)
            if not headless and "login.microsoftonline.com" in page.url:
                print("   サインインが必要です。ブラウザでサインインを完了してください…")
                # サインイン完了まで最大 5 分待機
                page.wait_for_url(lambda u: "login.microsoftonline.com" not in u, timeout=300_000)
                # サインイン後にもう一度 navigate
                page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            time.sleep(wait)
            try:
                page.screenshot(path=str(SCREENSHOT_DIR / fname), full_page=False)
                print(f"   saved -> {SCREENSHOT_DIR / fname}")
            except Exception as e:
                print(f"   screenshot failed: {e}")

        ctx.close()


if __name__ == "__main__":
    main()
