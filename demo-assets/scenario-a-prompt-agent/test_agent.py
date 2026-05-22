"""シナリオ A の動作確認: Responses API 経由で helpdesk-prompt を呼び出す回帰テスト。

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT = "..."
    python test_agent.py
"""

import os
import time
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
AGENT_NAME = os.environ.get("FOUNDRY_AGENT_NAME", "helpdesk-prompt")

CASES = [
    ("MFA の登録方法を教えて", "file_search で it-policy.md §2.2 を引用"),
    ("パスワードを忘れた、社内 PC です", "社内: passwordreset.contoso.local を案内"),
    ("パスワードを忘れた、社外 PC です", "社外: 内線 8888 / helpdesk@contoso.com を案内"),
    ("VPN がつながらない、再起動しても直らない", "CreateTicket 起票を提案"),
    ("私の PIN を教えて", "拒否 + CSIRT 案内"),
]


def main() -> None:
    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=ENDPOINT, credential=cred, allow_preview=True
    ) as client:
        openai = client.get_openai_client()
        for prompt, expected in CASES:
            print(f"\n=== Q: {prompt}")
            print(f"  期待: {expected}")
            t0 = time.monotonic()
            response = openai.responses.create(
                input=prompt,
                extra_body={
                    "agent_reference": {
                        "name": AGENT_NAME,
                        "type": "agent_reference",
                    }
                },
            )
            elapsed = time.monotonic() - t0
            print(f"  A ({elapsed:.1f}s):")
            text = response.output_text or "(空)"
            for line in text.splitlines():
                print(f"    {line}")


if __name__ == "__main__":
    main()
