from abc import ABC, abstractmethod
from typing import Dict, Union

from genius_client_sdk.datamodel.api import DictResponse


class AgentRunner(ABC):
    """AgentRunner is the interface for running an agent."""

    @abstractmethod
    def infer(
        self,
        variables: Union[str, list],
        evidence: dict,
    ) -> DictResponse:
        pass

    @abstractmethod
    def act(
        self,
        observation: Union[int, str, Dict[str, Union[int, str]]],
        policy_len: int = 2,
        learn_likelihoods: bool = False,
        learn_transitions: bool = False,
        learn_initial_state_priors: bool = False,
    ) -> DictResponse:
        pass
