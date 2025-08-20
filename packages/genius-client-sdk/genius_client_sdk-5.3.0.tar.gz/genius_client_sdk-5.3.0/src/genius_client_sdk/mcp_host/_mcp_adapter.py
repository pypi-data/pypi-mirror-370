from typing import Dict, Union
from genius_client_sdk.agent import GeniusAgent
from genius_client_sdk.datamodel.api import DictResponse
from genius_client_sdk.mcp_host.tools.runner import AgentRunner


class GeniusMCPAgentAdapter(AgentRunner):
    """AgentAdapter is the interface for running an agent."""

    def __init__(self, agent: GeniusAgent):
        assert isinstance(agent, GeniusAgent), (
            "agent must be an instance of GeniusAgent"
        )

        self.agent = agent

    def infer(
        self,
        variables: Union[str, list],
        evidence: dict,
    ) -> DictResponse:
        return self.agent.infer(variables=variables, evidence=evidence)

    def act(
        self,
        observation: Union[int, str, Dict[str, Union[int, str]]],
        policy_len: int = 2,
        learn_likelihoods: bool = False,
        learn_transitions: bool = False,
        learn_initial_state_priors: bool = False,
    ) -> DictResponse:
        return self.agent.act(
            observation=observation,
            policy_len=policy_len,
            learn_likelihoods=learn_likelihoods,
            learn_transitions=learn_transitions,
            learn_initial_state_priors=learn_initial_state_priors,
        )
