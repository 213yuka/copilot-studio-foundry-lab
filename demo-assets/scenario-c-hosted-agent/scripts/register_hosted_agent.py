"""
Scenario C Phase 6: ビルド済みコンテナを Foundry に Hosted Agent として登録。

前提:
- ACR にイメージが push 済み (例: acrxxx.azurecr.io/helpdesk-hosted:v1) — README §6
- Project Managed Identity に AcrPull (Container Registry Repository Reader) 付与済み — README §6.4
- 管理スクリプト用依存関係をインストール済み:
    pip install -r requirements-scripts.txt

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT     = "<Foundry project endpoint>"
    $env:AGENT_IMAGE                  = "acrxxx.azurecr.io/helpdesk-hosted:v1"
    $env:KNOWLEDGE_VECTOR_STORE_ID    = "<vector_store_id>"
    $env:FOUNDRY_MODEL_NAME           = "gpt-4.1-mini"
    python register_hosted_agent.py

参考:
- https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent
- https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent#poll-for-version-status
"""

import os
import sys
import time

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentProtocol,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential


POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 600  # 通常 1 分以内に active。余裕を持って 10 分を上限。


def _wait_until_active(project: AIProjectClient, agent_name: str, agent_version: str) -> str:
    """バージョンが ``active`` / ``failed`` / タイムアウトになるまでポーリングする。"""
    deadline = time.time() + POLL_TIMEOUT_SECONDS
    while time.time() < deadline:
        info = project.agents.get_version(
            agent_name=agent_name, agent_version=agent_version
        )
        # SDK バージョンによって dict / モデル両方の戻り値があり得るため、両対応にする。
        status = (
            info["status"] if isinstance(info, dict) else getattr(info, "status", None)
        )
        print(f"[poll] {agent_name}@{agent_version} status={status}")
        if status == "active":
            return status
        if status == "failed":
            error = (
                info.get("error")
                if isinstance(info, dict)
                else getattr(info, "error", None)
            )
            raise RuntimeError(f"Hosted agent provisioning failed: {error}")
        time.sleep(POLL_INTERVAL_SECONDS)
    raise TimeoutError(
        f"Hosted agent {agent_name}@{agent_version} did not become active within "
        f"{POLL_TIMEOUT_SECONDS}s"
    )


def main() -> None:
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    image = os.environ["AGENT_IMAGE"]
    vs_id = os.environ.get("KNOWLEDGE_VECTOR_STORE_ID", "")
    model = os.environ.get("FOUNDRY_MODEL_NAME", "gpt-4.1-mini")

    env_vars = {
        "AZURE_AI_MODEL_DEPLOYMENT_NAME": model,
        "FOUNDRY_MODEL_NAME": model,
    }
    if vs_id:
        env_vars["KNOWLEDGE_VECTOR_STORE_ID"] = vs_id

    with DefaultAzureCredential() as cred, AIProjectClient(
        endpoint=endpoint, credential=cred, allow_preview=True
    ) as project:
        definition = HostedAgentDefinition(
            container_protocol_versions=[
                ProtocolVersionRecord(
                    protocol=AgentProtocol.RESPONSES, version="1.0.0"
                )
            ],
            cpu="1",
            memory="2Gi",
            image=image,
            environment_variables=env_vars,
        )

        agent = project.agents.create_version(
            agent_name="helpdesk-hosted",
            definition=definition,
        )

        print(f"agent_name        = {agent.name}")
        print(f"agent_version     = {agent.version}")

        try:
            status = _wait_until_active(
                project, agent_name=agent.name, agent_version=agent.version
            )
            print(f"agent_status      = {status}")
        except (RuntimeError, TimeoutError) as exc:
            print(f"[ERROR] {exc}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()

