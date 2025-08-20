import logging

import numpy as np

from pyvfg import ModelType, errors

from genius_client_sdk.configuration import default_agent_config
from genius_client_sdk.model import GeniusModel


class POMDPModel(GeniusModel):
    """
    Creates a POMDP style factor graph model. This class is really just a wrapper around the
    GeniusModel class with constrained functionality to enable the user to create a POMDP
    model. Strictly speaking, one can create it with the GeniusModel class but the convenience
    functions in this class make the process easier and include checks to make sure all the
    necessary model components are present.

    A POMDP model requires preset factors (with specific roles) and specific variables. The initial
    state prior is optional. Each time a component is added, the corresponding flags dict is toggled to true.
    """

    def __init__(
        self,
        agent_url: str = default_agent_config.agent_url,
        json_path=None,
    ):
        """
        Initializes the POMDPModel.

        Parameters:
            agent_url (str): The URL of the agent to connect to. Defaults to the default agent URL.
            json_path (str, optional): The path to the JSON file for the model. Defaults to None.
        """
        super().__init__(agent_url=agent_url, json_path=json_path)
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        # Flags are toggled when each model component is added to the model
        self.flags = {
            "likelihood": False,
            "transition": False,
            "preference": False,
            "state": False,
            "observation": False,
            "control": False,
        }

    """ POMDP factors """

    def add_likelihood_factor(
        self,
        values: np.ndarray,
        target: str,
        parents: list[str] = None,
        counts: np.ndarray = None,
    ) -> None:
        """
        Initializes the POMDPModel.

        Parameters:
            values (np.ndarray): The values for the factor.
            target (str): The target variable for the factor.
            parents (list[str], optional): The parent variables for the factor. Defaults to None.
            counts (np.ndarray, optional): The counts for the factor. Defaults to None.
        """
        self.add_factor(
            values=values,
            target=target,
            parents=parents,
            counts=counts,
            role="likelihood",
        )
        self._toggle_flag("likelihood")

    def add_transition_factor(
        self,
        values: np.ndarray,
        target: str,
        parents: list[str] = None,
        counts: np.ndarray = None,
    ) -> None:
        """
        Adds a transition factor to the model.

        Parameters:
            values (np.ndarray): The values for the factor.
            target (str): The target variable for the factor.
            parents (list[str], optional): The parent variables for the factor. Defaults to None.
            counts (np.ndarray, optional): The counts for the factor. Defaults to None.
        """
        self.add_factor(
            values=values,
            target=target,
            parents=parents,
            counts=counts,
            role="transition",
        )
        self._toggle_flag("transition")

    def add_prior_factor(
        self,
        values: np.ndarray,
        target: str,
        parents: list[str] = None,
        counts: np.ndarray = None,
    ) -> None:
        """
        Adds a prior factor to the model.

        Parameters:
            values (np.ndarray): The values for the factor.
            target (str): The target variable for the factor.
            parents (list[str], optional): The parent variables for the factor. Defaults to None.
            counts (np.ndarray, optional): The counts for the factor. Defaults to None.
        """
        self.add_factor(
            values=values,
            target=target,
            parents=parents,
            counts=counts,
            role="initial_state_prior",
        )

    def add_preference_factor(
        self,
        values: np.ndarray,
        target: str,
        parents: list[str] = None,
        counts: np.ndarray = None,
    ) -> None:
        """
        Adds a preference factor to the model.

        Parameters:
            values (np.ndarray): The values for the factor.
            target (str): The target variable for the factor.
            parents (list[str], optional): The parent variables for the factor. Defaults to None.
            counts (np.ndarray, optional): The counts for the factor. Defaults to None.
        """
        self.add_factor(
            values=values,
            target=target,
            parents=parents,
            counts=counts,
            role="preference",
        )
        self._toggle_flag("preference")

    """ POMDP variables """

    def add_state_variable(self, name: str, values: list) -> None:
        """
        Adds a state variable to the model.

        Parameters:
            name (str): The name of the state variable.
            values (list): The values for the state variable.
        """
        self.add_variable(name=name, values=values)
        self._toggle_flag("state")

    def add_observation_variable(self, name: str, values: list) -> None:
        """
        Adds an observation variable to the model.

        Parameters:
            name (str): The name of the observation variable.
            values (list): The values for the observation variable.
        """
        self.add_variable(name=name, values=values)
        self._toggle_flag("observation")

    def add_action_variable(self, name: str, values: list) -> None:
        """
        Adds an action variable to the model.

        Parameters:
            name (str): The name of the action variable.
            values (list): The values for the action variable.
        """
        self.add_variable(name=name, values=values)
        self._toggle_flag("control")

    """ Other methods """

    def _check_flags(self):
        """
        Runs through each flag and determines which are false.

        Raises:
            Exception: If any required components are missing from the POMDP model.
        """
        false_keys = [key for key, value in self.flags.items() if not value]

        if false_keys:
            raise Exception(
                f"The following components are missing from the POMDP model: {false_keys}"
            )

    def _toggle_flag(self, component: str):
        """
        Toggles a flag from false to true.

        Parameters:
            component (str): The component whose flag is to be toggled.
        """
        if not self.flags[component]:
            self.flags[component] = True

    def validate(
        self,
        model_type: ModelType = ModelType.FactorGraph,
        correct_errors: bool = False,
        verbose: bool = True,
    ) -> list[errors.ValidationError]:
        """
        Method override for parent class that just adds the _check_flags() statement to ensure all
        model components are present before validation.

        Parameters:
            model_type (ModelType): Defines the type of model the model should be validated as. Defaults to ModelType.FactorGraph.
            correct_errors (bool): If True, the validate endpoint will attempt to correct fixable errors. Defaults to False.
            verbose (bool): If True, prints a success message upon validation. Defaults to True.
        """
        self._check_flags()

        return super().validate(
            model_type=model_type,
            correct_errors=correct_errors,
            verbose=verbose,
        )
