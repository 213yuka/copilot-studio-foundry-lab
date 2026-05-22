"""
Scenario C Phase 6: ビルド済みコンテナを Foundry に Hosted Agent として登録。

前提:
- ACR にイメージが push 済み (例: acrxxx.azurecr.io/helpdesk-hosted:v1) — README §6
- Project Managed Identity に AcrPull (Container Registry Repository Reader) 付与済み — README §6.4

使い方:
    $env:FOUNDRY_PROJECT_ENDPOINT     = "<Foundry project endpoint>"
    $env:AGENT_IMAGE                  = "acrxxx.azurecr.io/helpdesk-hosted:v1"
    $env:KNOWLEDGE_VECTOR_STORE_ID    = "<vector_store_id>"
    $env:FOUNDRY_MODEL_NAME           = "gpt-4.1-mini"
    python register_hosted_agent.py

参考: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/deploy-hosted-agent
"""

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentProtocol,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)
from azure.identity import DefaultAzureCredential


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


if __name__ == "__main__":
    main()
