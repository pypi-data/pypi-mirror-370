import asyncio

from typing import Union

from mcp.server.stdio import stdio_server
from dotenv import load_dotenv

from genius_client_sdk.agent import GeniusAgent
from genius_client_sdk.auth import (
    ApiKeyConfig,
)
from genius_client_sdk.mcp_host._mcp_adapter import GeniusMCPAgentAdapter
from genius_client_sdk.mcp_host._mcp_server import create_mcp_agent_server
from genius_client_sdk.mcp_host._mcp_env import get_config_from_env

load_dotenv()


async def run_mcp_agent_cli(
    protocol: str, hostname: str, port: int, auth_config: Union[ApiKeyConfig]
) -> None:
    """Wrap Genius around Host MCP server."""

    # Agent -> AgentServer
    agent = GeniusAgent(
        agent_http_protocol=protocol,
        agent_hostname=hostname,
        agent_port=port,
        auth_config=auth_config,
    )
    # Use current agent model and check connection
    agent.get_model_from_server()
    agent_server = create_mcp_agent_server(GeniusMCPAgentAdapter(agent))
    agent_server_options = agent_server.create_initialization_options()

    async with stdio_server() as (read_stream, write_stream):
        await agent_server.run(read_stream, write_stream, agent_server_options)


def main():
    # Configuration and Authentication
    (protocol, hostname, port, auth_config) = get_config_from_env()

    asyncio.run(
        run_mcp_agent_cli(
            protocol=protocol, hostname=hostname, port=port, auth_config=auth_config
        )
    )


if __name__ == "__main__":
    main()
