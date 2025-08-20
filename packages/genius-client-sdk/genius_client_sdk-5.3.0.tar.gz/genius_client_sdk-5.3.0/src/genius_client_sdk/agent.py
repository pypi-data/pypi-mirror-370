# -*- coding: utf-8 -*-
import json
import logging
from typing import Dict, Union

import pyvfg

from genius_client_sdk.auth import (
    AuthConfig,
    NoAuthConfig,
    new_session_from_auth_config,
)
from genius_client_sdk.configuration import BaseAgentConfig, default_agent_config
from genius_client_sdk.datamodel.api import DictResponse
from genius_client_sdk.datamodel.api import AutoBinVariable

from genius_client_sdk.model import GeniusModel
from genius_client_sdk.utils import (
    control_payload,
    inference_payload,
    learning_payload,
    send_csv_request,
    send_http_request,
)


class GeniusAgent:
    """
    The GeniusAgent class is used as a wrapper around fastAPI to communicate to and from the Genius
    agent. This class has the following capabilities enabled by the API calls:
    - POST /graph of genius model loaded from a JSON or from the GeniusModel class
    - GET /graph of genius model and print/view its contents
    - DELETE /graph to unload the model from the agent
    - POST /infer to perform inference given some evidence and a variable of interest
    - POST /learn to perform parameter learning given an input CSV or list of variables and their
      observations
    - POST /actionselection to perform action selection given a POMDP model structure and
      observation vector
    - POST /import to perform structure learning given a CSV data file
    - POST /validate-csv to perform validation on a CSV data file
    - POST /simulate to perform simulation on a POMDP model structure
    - POST /auto-bin-one-off to perform automatic binning of a given column by clustering

    At the moment, it is assumed that the user connects to a local GeniusAgent. In the future,
    initializing this class will have options to specify a URL and port.
    """

    def __init__(
        self,
        agent_http_protocol: str = default_agent_config.agent_http_protocol,
        agent_hostname: str = default_agent_config.agent_hostname,
        agent_port: int = default_agent_config.agent_port,
        auth_config: AuthConfig = NoAuthConfig(),
    ) -> None:
        """
        Initializes the GeniusAgent instance.

        Parameters:
            agent_http_protocol (str): The HTTP protocol for the agent. Defaults to 'http'.
            agent_hostname (str): The hostname for the agent. Defaults to 'localhost'.
            agent_port (int): The port number for the agent. Defaults to 3000.
            auth_config (AuthConfig): The auth configuration for the agent. Defaults to NoAuthConfig()
        """
        self.model = None
        self.learning_history = None
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.agent_http_protocol = agent_http_protocol
        self.agent_hostname = agent_hostname
        self.agent_port = agent_port
        self.agent_url = BaseAgentConfig.AGENT_URL_FORMAT.format_map(locals())
        self.auth_config = auth_config
        self._session = new_session_from_auth_config(self.auth_config)

    def load_model_from_json(self, json_path: str) -> None:
        """
        Loads a JSON model from a path.

        Parameters:
            json_path (str): The path to the JSON file containing the model.
        """

        # Turn into GeniusModel class
        self.load_genius_model(
            GeniusModel(
                agent_url=self.agent_url,
                json_path=json_path,
            )
        )

    def load_genius_model(self, model: GeniusModel) -> None:
        """
        Loads a model from the GeniusModel class.

        Parameters:
            model (GeniusModel): An instance of the GeniusModel class.
        """

        # POST /graph with dict representation of JSON model
        self.model = model

        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="graph",
            json_data={"vfg": json.loads(self.model.vfg.model_dump_json())},
            session=self._session,
        )
        if "ETag" in response.headers:
            self.model.etag = response.headers["ETag"]

        assert response.status_code == 200, "Loading model failed: " + str(
            response.text
        )

    def unload_model(self) -> None:
        """
        Unloads the model locally and from the server
        """
        response = send_http_request(
            self.agent_url,
            http_request_method="delete",
            call="graph",
            session=self._session,
        )
        assert response.status_code == 200, "Unloading model failed: " + str(
            response.text
        )
        self.model = None

    def get_model_from_server(
        self,
        verbose: bool = False,
    ) -> None:
        """
        Gets the JSON model from the remote agent and updates the local model.
        """

        response = send_http_request(
            self.agent_url,
            http_request_method="get",
            call="graph",
            session=self._session,
        )

        if response.status_code == 204:
            # we have no more model on remote, clearing
            self.model = None
            return

        assert response.status_code == 200, (
            f"Error retrieving graph: {str(response.text)}."
        )

        # Update the agent's model
        self.model = GeniusModel()
        vfg_json = response.json().get("vfg")
        self.model.vfg = pyvfg.vfg_upgrade(vfg_json)
        if "ETag" in response.headers:
            self.model.etag = response.headers["ETag"]

        # Prints out JSON model file
        if verbose:
            self.logger.info(json.dumps(vfg_json, indent=4))

    def log_model(
        self, summary: bool = False, logging_level: int = logging.INFO
    ) -> None:
        """
        Prints the JSON model to logs.
        Optionally, summarizes the model in a (slightly) more readable format.

        Parameters:
            summary (bool): If True, prints a summarized view of the model. Defaults to False.
            logging_level (int): The logging level to use. Defaults to DEFAULT_LOGGING_LEVEL.
        """

        if not self.model:
            raise Exception(
                "No model loaded. load_genius_model() must be run before viewing the model."
            )

        # Log summarized and easy-to-read view of model contents instead of raw JSON
        if summary:
            self.logger.log(logging_level, "Model contents:")

            # Log number of variables in the model and their names
            x = f"{len(self.model.get_variable_names())} variables: {sorted(self.model.get_variable_names())}"
            self.logger.log(logging_level, x)

            # Log number of factors in the model and their names
            n_factors = len(self.model.vfg.factors)
            factor_vars = [
                self.model.get_factor_attributes(factor_id=f, attribute="variables")
                for f in range(n_factors)
            ]
            self.logger.log(
                logging_level, f"{n_factors} factors: {sorted(factor_vars)}"
            )

            # Log all factor probabilities
            self.logger.log(logging_level, "Factor probabilities:")
            for f in range(n_factors):
                self.logger.log(
                    logging_level,
                    str(
                        self.model.get_factor_attributes(
                            factor_id=f, attribute="values"
                        )
                    ),
                )
                self.logger.log(logging_level, "\n")
        else:
            self.logger.log(
                logging_level, self.model.vfg.model_dump_json(indent=4)
            )  # Prints raw JSON model

    def infer(
        self,
        variables: Union[str, list],
        evidence: dict,
        verbose: bool = True,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> DictResponse:
        """
        Run inference based on input variable to infer and evidence (observed data).

        Parameters:
            variables (list): A list of the variable(s) to infer.
            evidence (dict): A dictionary containing observed data.
            verbose (bool): If True, prints out probabilities. Defaults to True.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.

        Returns:
            dict: A dictionary containing the inference result.
        """

        assert self.model is not None, (
            "Model must be set and loaded to agent prior to calling infer."
        )

        # Collects input into correct schema for the API request
        payload = inference_payload(variables=variables, evidence=evidence)

        # POST /infer with variables and evidence.  This operation is async.
        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="infer",
            json_data=payload,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            etag=self.model.etag,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Error performing inference: {str(response.text)}."
        )

        # Rearranges return from API so that success and error are now under metadata
        parsed_inference_result = json.loads(response.text)
        inference_result = {
            "evidence": parsed_inference_result["result"]["evidence"],
            "probabilities": parsed_inference_result["result"]["probabilities"],
            "metadata": {
                "success": parsed_inference_result["success"],
                "error": parsed_inference_result["error"],
            },
        }
        # Add optional metadata properties if they are present
        if (
            "metadata" in parsed_inference_result
            and parsed_inference_result["metadata"] is not None
        ):
            if "execution_time" in parsed_inference_result["metadata"]:
                inference_result["metadata"]["execution_time"] = (
                    parsed_inference_result["metadata"]["execution_time"]
                )
            if "memory_used" in parsed_inference_result["metadata"]:
                inference_result["metadata"]["memory_used"] = parsed_inference_result[
                    "metadata"
                ]["memory_used"]

        # Prints out probabilities
        if verbose:
            self.logger.info(inference_result["probabilities"])

        return inference_result

    def learn(
        self,
        variables: list = None,
        observations: list = None,
        csv_path: str = None,
        algorithm: str = None,
        library: str = None,
        verbose: bool = False,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> None:
        """
        Run learning based on observations of variables. Accepts either a list of variables and
        nested list of observations or a path to a CSV file.

        Parameters:
            variables (list): A list of variables to learn.
            observations (list): A nested list of observations for the variables.
            csv_path (str): The path to a CSV file containing the observations.
            algorithm (str): The learning algorithm to use (e.g., "maximum_likelihood_estimation", "expectation_maximization", "bayesian_estimation", "bayesian_em"). Defaults to None.
            library (str): The library to use for learning (e.g., "pgmpy", "verses"). Defaults to None.
            verbose (bool): If True, prints out the JSON model file. Defaults to False.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.
        """

        assert self.model is not None, (
            "Model must be set and loaded to agent prior to calling learn."
        )

        # Collects input into correct schema for the API request
        payload = learning_payload(
            variables=variables,
            observations=observations,
            csv_path=csv_path,
            algorithm=algorithm,
            library=library,
        )
        self.logger.info(json.dumps(payload, indent=4))
        # POST /learn with variables/observations or CSV containing this information.  This operation is async.
        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="learn",
            json_data=payload,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            etag=self.model.etag,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Error performing parameter learning: {str(response.text)}."
        )

        self.logger.info(
            "Parameter learning successful. Use log_model() to see updated probabilities."
        )

        # Extract response data
        response_json = response.json()
        result = response_json.get("result", {})

        # Extract and store the history data
        self.learning_history = result.get("history")

        # Update the agent's model, as set_graph is called in the /learn handler
        self.model.vfg = pyvfg.vfg_upgrade(result.get("updated_model"))

        # Update the cached etag
        if "ETag" in response.headers:
            self.model.etag = response.headers["ETag"]

        # Prints out JSON model file
        if verbose:
            self.logger.info(self.model.vfg.model_dump_json(indent=4))

            # Also log the learning history if available
            if self.learning_history:
                self.logger.info("Learning history:")
                self.logger.info(json.dumps(self.learning_history, indent=4))

    def act(
        self,
        observation: Union[int, str, Dict[str, Union[int, str]]],
        policy_len: int = 2,
        learn_likelihoods: bool = False,
        learn_transitions: bool = False,
        learn_initial_state_priors: bool = False,
        verbose: bool = True,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> DictResponse:
        """
        Performs action selection given an observation array and policy length.

        Parameters:
            observation (Union[int, str, Dict[str, Union[int, str]]]): The observation data.
            policy_len (int): The length of the policy. Defaults to 2.
            learn_likelihoods (bool): Whether to learn likelihoods. Defaults to False.
            learn_transitions (bool): Whether to learn transitions. Defaults to False.
            learn_initial_state_priors (bool): Whether to learn initial state priors. Defaults to False.
            verbose (bool): If True, prints out the action, inferred state, and policy distribution. Defaults to True.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.

        Returns:
            dict: A dictionary containing the action selection result.
        """

        assert self.model is not None, (
            "Model must be set and loaded to agent prior to calling act."
        )

        # TODO: Assert number of observations matches observation variable length

        # Collects input into correct scheme for the API request
        payload = control_payload(
            observation=observation,
            policy_len=policy_len,
            learn_likelihoods=learn_likelihoods,
            learn_transitions=learn_transitions,
            learn_initial_state_priors=learn_initial_state_priors,
        )

        # POST /actionselection with observation and policy length.  This operation is async.
        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="actionselection",
            json_data=payload,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            etag=self.model.etag,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Action selection failed: {str(response.text)}."
        )

        # Rearranges return from API so that success and error are now under metadata
        control_result = json.loads(response.text)

        # Update the agent's model, as set_graph is called in the /actionselection handler
        # Do this before redefining 'control_result'
        self.model.vfg = pyvfg.vfg_upgrade(control_result["result"]["updated_vfg"])
        if "ETag" in response.headers:
            self.model.etag = response.headers["ETag"]

        # control_result is defined in GPAI-159
        control_result = {
            "belief_state": control_result["result"].get("belief_state", {}),
            "policy_belief": control_result["result"].get("policy_belief", {}),
            "efe_components": control_result["result"].get("efe_components", {}),
            "action_data": control_result["result"].get("action_data", {}),
            "metadata": {
                "success": control_result.get("success", []),
                "error": control_result.get("error", []),
                "warnings": control_result.get("warnings", []),
                # These were removed from GPIL
                #                "execution_time": control_result["metadata"]["execution_time"],
                # Note: memory_used is an array, e.g. [0.125, "MB"]
                #                "memory_used": control_result["metadata"]["memory_used"],
            },
        }

        if verbose:
            self.logger.info(f"Action: {control_result['action_data']}")
            self.logger.info(f"Inferred state: {control_result['belief_state']}")
            self.logger.info(f"Policy distribution: {control_result['policy_belief']}")

        return control_result

    def structure_learning(
        self,
        csv_path: str = None,
        skip_sanity_check: bool = False,
        load_model_to_agent: bool = True,
        verbose: bool = False,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> None:
        """
        Performs structure learning given a CSV file. Structure learning entails taking a dataset
        and attempting to build the dependencies from it in a probabilistic model.

        If the load_model_to_agent argument is True, the model is sent to the connected agent.

        Parameters:
            csv_path (str): The path to the CSV file.
            skip_sanity_check (bool): If True, skips the sanity check. Defaults to False.
            load_model_to_agent (bool): If True, loads the model to the agent. Defaults to True.
            verbose (bool): If True, prints out the JSON model file. Defaults to False.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.
        """

        # Open the CSV file and read its contents
        with open(csv_path, "r") as file:
            csv_data = file.read()

        # POST /import with loaded CSV
        response = send_csv_request(
            self.agent_url,
            call="import",
            data=csv_data,
            skip_sanity_check=skip_sanity_check,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Error performing structure learning: {str(response.text)}."
        )

        self.logger.info(
            "Structure learning successful. Use log_model() to see learned structure."
        )

        result_model = response.json().get("result")

        if load_model_to_agent:
            self.logger.info("Loading model to agent...")
            # Send model dict to GeniusModel class
            self.model = GeniusModel(agent_url=self.agent_url)
            self.model.vfg = pyvfg.vfg_upgrade(result_model)

        # Prints out JSON model file
        if verbose:
            self.logger.info(json.dumps(result_model, indent=4))

    def validate_csv(
        self,
        csv_path: str,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> None:
        """
        Performs validation on a given CSV file.

        Parameters:
            csv_path (str): The path to the CSV file.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.
        """

        # Open the CSV file and read its contents
        with open(csv_path, "r") as file:
            csv_data = file.read()

        # POST /validate-csv with loaded CSV
        response = send_csv_request(
            self.agent_url,
            call="validate-csv",
            data=csv_data,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Error performing csv validation: {json.dumps(response.json())}."
        )

    def simulate(
        self,
        num_steps: int,
        policy_len: int,
        initial_state: dict,
        env: dict = None,
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> DictResponse:
        """
        Performs a simulation on the model given a library, number of steps, policy length, and initial state.

        Parameters:
            num_steps (int): The number of steps to simulate.
            policy_len (int): The length of the policy.
            initial_state (dict): The initial state for the simulation.
            env (dict): The environment for the simulation. Defaults to None.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.

        Returns:
            dict: A dictionary containing the simulation result.
        """

        assert self.model is not None, (
            "Model must be set and loaded to agent prior to calling simulate."
        )

        payload = {
            "library": "pymdp",
            "num_steps": num_steps,
            "policy_len": policy_len,
            "initial_state": initial_state,
            "env": env,
        }

        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="simulate",
            json_data=payload,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            etag=self.model.etag,
            session=self._session,
        )

        assert response.status_code == 200, f"Simulation failed: {str(response.text)}."

        return json.loads(response.text)["result"]

    def auto_bin_one_off(
        self,
        csv_path: str,
        variables: dict[str, AutoBinVariable],
        polling_timeout_sec: float = 120,
        polling_frequency_sec: float = 0.1,
    ) -> (DictResponse, str | None):
        """
        Automatically bins a given column by clustering.

        Parameters:
            csv_path (str): The path to the CSV file.
            variables (dict[str, AutoBinVariable]): A dictionary of variables to bin.
                The keys are the variable names and the values are AutoBinVariable instances.
            polling_timeout_sec (float): The maximum time to wait in seconds for interference to complete.  Defaults to 120 seconds.
            polling_frequency_sec (float): The time to wait in seconds in between checking if the task has completed.  Defaults to 0.1 seconds.

        Returns:
            dict: A dictionary containing the binning result.
        """

        with open(csv_path, "r") as file:
            csv_data = file.read()

        payload = {"csv": csv_data, "variables": variables}

        response = send_http_request(
            self.agent_url,
            http_request_method="post",
            call="auto-bin-one-off",
            json_data=payload,
            polling_timeout_sec=polling_timeout_sec,
            polling_frequency_sec=polling_frequency_sec,
            session=self._session,
        )

        assert response.status_code == 200, (
            f"Auto binning failed: {str(response.text)}."
        )

        auto_bin_response = json.loads(response.text)

        return auto_bin_response["result"], auto_bin_response["binned_csv"]
