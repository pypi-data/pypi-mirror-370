from typing import List, Optional

from rasa.agents.agent_manager import AgentManager
from rasa.agents.exceptions import AgentNotFoundException
from rasa.core.available_agents import (
    AgentConfig,
    AgentMCPServerConfig,
    AvailableAgents,
)
from rasa.core.available_endpoints import AvailableEndpoints
from rasa.shared.agents.utils import get_protocol_type
from rasa.shared.core.domain import Domain
from rasa.shared.core.flows import FlowsList
from rasa.shared.core.flows.steps import CallFlowStep


def resolve_agent_config(
    agent_config: AgentConfig,
    available_endpoints: AvailableEndpoints,
) -> Optional[AgentConfig]:
    if agent_config is None:
        return None

    connections = agent_config.connections
    mcp_connections: List[AgentMCPServerConfig] = (
        connections.mcp_servers
        if connections and connections.mcp_servers is not None
        else []
    )

    for mcp_server in mcp_connections:
        for mcp_server_endpoint in available_endpoints.mcp_servers or []:
            if mcp_server_endpoint.name == mcp_server.name:
                mcp_server.url = mcp_server_endpoint.url
                mcp_server.type = mcp_server_endpoint.type

    return agent_config


async def initialize_agents(
    flows: FlowsList,
    domain: Domain,
    sub_agents: AvailableAgents,
) -> None:
    """Iterate over flows and create/connect the referenced agents."""
    agent_manager: AgentManager = AgentManager()
    endpoints = AvailableEndpoints.get_instance()

    for flow in flows.underlying_flows:
        for step in flow.steps:
            if isinstance(step, CallFlowStep):
                if flows.flow_by_id(step.call) is not None:
                    continue

                if step.is_calling_mcp_tool():
                    # The call step is calling an MCP tool, so we don't need to
                    # initialize any agent.
                    continue

                if not step.is_calling_agent():
                    raise AgentNotFoundException(step.call)

                agent_name = step.call
                agent_config = sub_agents.get_agent_config(agent_name)
                resolved_agent_config = resolve_agent_config(agent_config, endpoints)
                protocol_type = get_protocol_type(step, agent_config)

                await agent_manager.connect_agent(
                    agent_name,
                    protocol_type,
                    resolved_agent_config,
                )
