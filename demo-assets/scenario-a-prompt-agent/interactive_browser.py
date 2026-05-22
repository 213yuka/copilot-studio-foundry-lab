"""Copilot Studio 手順検証用インタラクティブ ブラウザ ドライバ.

stdin から JSON コマンドを 1 行ずつ受け取り、Playwright で実行する。
コマンド:
  {"cmd": "goto", "url": "...", "wait": 5}
  {"cmd": "shot", "path": "...", "full": false}
  {"cmd": "shot_el", "selector": "...", "path": "..."}
  {"cmd": "click", "selector": "..."}
  {"cmd": "type",  "selector": "...", "text": "..."}
  {"cmd": "fill",  "selector": "...", "text": "..."}
  {"cmd": "wait",  "sec": 5}
  {"cmd": "wait_sel", "selector": "...", "sec": 30}
  {"cmd": "url"}
  {"cmd": "title"}
  {"cmd": "html", "selector": "body", "max": 4000}
  {"cmd": "eval", "js": "..."}
  {"cmd": "key",  "key": "Enter"}
  {"cmd": "quit"}
レスポンスは 1 行 JSON。
"""

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE_DIR = Path(__file__).resolve().parent / ".pw-profile-cs"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def respond(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1600, "height": 1000},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        respond({"ok": True, "msg": "ready", "profile": str(PROFILE_DIR)})

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except Exception as e:
                respond({"ok": False, "err": f"json parse: {e}", "raw": line})
                continue

            cmd = req.get("cmd")
            try:
                if cmd == "quit":
                    respond({"ok": True, "msg": "bye"})
                    break
                elif cmd == "goto":
                    page.goto(req["url"], wait_until="domcontentloaded", timeout=90_000)
                    time.sleep(req.get("wait", 2))
                    respond({"ok": True, "url": page.url})
                elif cmd == "shot":
                    full = req.get("full", False)
                    p_ = req["path"]
                    Path(p_).parent.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=p_, full_page=full)
                    respond({"ok": True, "path": p_})
                elif cmd == "shot_el":
                    el = page.locator(req["selector"]).first
                    p_ = req["path"]
                    Path(p_).parent.mkdir(parents=True, exist_ok=True)
                    el.screenshot(path=p_)
                    respond({"ok": True, "path": p_})
                elif cmd == "click":
                    page.locator(req["selector"]).first.click(timeout=req.get("timeout", 15_000))
                    time.sleep(req.get("wait", 1))
                    respond({"ok": True})
                elif cmd == "type":
                    page.locator(req["selector"]).first.type(req["text"], delay=req.get("delay", 30))
                    respond({"ok": True})
                elif cmd == "fill":
                    page.locator(req["selector"]).first.fill(req["text"])
                    respond({"ok": True})
                elif cmd == "wait":
                    time.sleep(req.get("sec", 1))
                    respond({"ok": True})
                elif cmd == "wait_sel":
                    page.locator(req["selector"]).first.wait_for(timeout=req.get("sec", 30) * 1000)
                    respond({"ok": True})
                elif cmd == "url":
                    respond({"ok": True, "url": page.url})
                elif cmd == "title":
                    respond({"ok": True, "title": page.title()})
                elif cmd == "html":
                    sel = req.get("selector", "body")
                    mx = req.get("max", 4000)
                    html = page.locator(sel).first.inner_html()
                    respond({"ok": True, "html": html[:mx], "len": len(html)})
                elif cmd == "text":
                    sel = req.get("selector", "body")
                    mx = req.get("max", 4000)
                    txt = page.locator(sel).first.inner_text()
                    respond({"ok": True, "text": txt[:mx], "len": len(txt)})
                elif cmd == "eval":
                    val = page.evaluate(req["js"])
                    respond({"ok": True, "val": val})
                elif cmd == "key":
                    page.keyboard.press(req["key"])
                    respond({"ok": True})
                else:
                    respond({"ok": False, "err": f"unknown cmd: {cmd}"})
            except Exception as e:
                respond({"ok": False, "err": str(e), "cmd": cmd})

        ctx.close()


if __name__ == "__main__":
    main()
