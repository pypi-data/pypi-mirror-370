import json
import logging
from typing import Any, List, Optional

import networkx as nx
import numpy as np
import pyvfg
from pyvfg import VFG, ModelType, ValidationError, vfg_upgrade, VariableRole

from genius_client_sdk.configuration import default_agent_config
from genius_client_sdk.converters import bif_to_vfg

VFG_VERSION: str = "0.5.0"
"""
Default build version of the application
"""


class GeniusModel:
    """
    The GeniusModel class is used to build factor graphs from scratch. The class has the following
    capabilities:
    - Create a model from a JSON file path
    - Construct model by adding variables or factors
    - Validate a constructed model with POST /validate in the fastAPI
    - Save (export) a model to JSON
    - Visualize the model with networkx
    - Get variable names and values for a given model
    - Get factor attributes for a given model

    Internally, the model is stored in the model instance variable and is a VFG type directly. This is
    a wrapper around it for some ease-of-use functions.

    In the future, many of the methods in this class will become part of pyvfg and this class will
    likely become a wrapper around pyvfg.
    """

    agent_url: str
    vfg: VFG
    logger: Any

    def __init__(
        self,
        agent_url: str = default_agent_config.agent_url,
        json_path: str = None,
        etag: str = None,
    ) -> None:
        """
        Initializes the GeniusModel.

        Parameters:
            agent_url (str): The URL of the agent. Defaults to the default agent URL.
            json_path (str, optional): The path to the JSON file for the model. Defaults to None.
            etag (str, optional): The ETag for the model. Defaults to None.
        """
        self.agent_url = agent_url
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

        """Builds the skeleton JSON model dict."""

        if json_path:
            self._from_json(json_path)
        else:
            self.vfg = VFG(version=VFG_VERSION)
        self.etag = etag

    @property
    def version(self) -> str:
        """
        Returns the version of the model.

        Returns:
            str: The version of the model.
        """
        return self.vfg.version

    def _from_json(self, json_path: str) -> None:
        """
        Loads a JSON file to a dict and validates it.

        Parameters:
            json_path (str): The path to the JSON file.
        """
        with open(json_path, "r") as file:
            json_model = json.load(file)
        if "vfg" in json_model:
            # unwrap wrapped models
            json_model = json_model["vfg"]

        self.vfg = vfg_upgrade(json_model)
        self.validate(verbose=False)

    def add_metadata(
        self,
        model_type: ModelType = ModelType.BayesianNetwork,
        model_version: str = None,
        description: str = None,
    ) -> None:
        """
        Adds metadata to the JSON model dict.

        Parameters:
            model_type (ModelType): The type of the model. Defaults to ModelType.BayesianNetwork.
            model_version (str): The version of the model. Defaults to None.
            description (str): A description of the model. Defaults to None.
        """

        self.vfg.metadata = pyvfg.Metadata(
            model_type=model_type,
            model_version=model_version,
            description=description,
        )

    def add_variables(self, variables: list[tuple[str, list]]) -> None:
        """
        Adds a list of variables to the JSON model dict.

        Parameters:
            variables (list[tuple[str, list]]): The list of variables to add.
        """
        for variable in variables:
            self.add_variable(variable[0], variable[1])

    def add_variable(
        self, name: str, values: List[str], role: Optional[VariableRole] = None
    ) -> None:
        """`
        Adds a variable to the JSON model dict.

        Parameters:
        name (str): The name of the variable.
        values (List[str]): The values for the variable.
        """
        self.vfg.variables[name] = pyvfg.Variable(
            pyvfg.DiscreteVariableNamedElements(elements=values, role=role)
        )

    def add_factor(
        self,
        values: np.ndarray,
        target: str,
        parents: list[str] = None,
        role: str = None,
        counts: np.ndarray = None,
    ):
        """
        Adds a factor to the JSON model. Note: The reason for separating the conditioned variable
        from its parents is to be able to construct the variable list as:

        [conditioning variable, parent_1, parent_2, ...]

        This structure is assumed in the VFG format but not explicitly stated. By asking the user
        to construct the variable and its parents in this way it avoids situations where the user
        might input the variables in the wrong order.

        In the case of marginal distributions the parents field would be left defaulting to None.

        Parameters:
            values (np.ndarray): The values for the factor.
            target (str): The conditioned (target) variable. Defaults to None.
            parents (list[str]): The conditioning (parent) variables.
            role (str, optional): The role of the factor. Defaults to None.
            counts (np.ndarray): The counts for the factor. Defaults to None.
        """

        if parents:
            variables = [target] + parents
        else:
            variables = [target]

        # Checks that variables have been added before attempting to build the factors
        if len(self.vfg.variables) == 0:
            raise Exception(
                "Variables must be added to the model before factors can be added."
            )

        # Assert that factors are part of variable list
        for var in variables:
            added_variables = list(self.vfg.variables.keys())
            assert var in added_variables, (
                f"Variables {var} not in the list of added variables. Added variables: {added_variables}."
            )

        # Assert that number of variables match tensor rank
        assert len(variables) == len(list(values.shape)), (
            "Number of variables associated with factor does not match the dimension of the factor values."
        )

        # Add factor
        factor_dict = {
            "variables": variables,
            "distribution": "categorical_conditional"
            if len(list(values.shape)) > 1
            else "categorical",
            "values": values.tolist(),
            "counts": counts.tolist() if counts is not None else None,
        }

        # Add "role" attribute
        if role:
            factor_dict["role"] = role
            if role == "preference":
                factor_dict["distribution"] = "logits"

        # Add factor to JSON model dict
        self.vfg.factors.append(pyvfg.Factor(**factor_dict))

    def validate(
        self,
        model_type: ModelType = ModelType.FactorGraph,
        correct_errors: bool = False,
        verbose: bool = True,
    ) -> list[ValidationError]:
        """
        Validates that a model is a valid factor graph.

        Parameters:
            model_type (ModelType): Defines the type of model the model should be validated as. Defaults to ModelType.FactorGraph.
            correct_errors (bool): If True, the validate endpoint will attempt to correct fixable errors. Defaults to False.
            verbose (bool): If True, prints a success message upon validation. Defaults to True.
        """
        if correct_errors:
            new_vfg, validation_errors = self.vfg.correct(
                as_model_type=model_type, raise_exceptions=True
            )
            if len(validation_errors) > 0:
                return validation_errors
            else:
                if verbose:
                    self.logger.info("Model validated successfully.")
                return []
        else:
            validation_result = self.vfg.validate_as(
                model_type=model_type, raise_exceptions=True
            )
            return list(validation_result.errors)

    def save(self, out_path: str) -> None:
        """
        Export JSON model dict to JSON file at a given path.

        Parameters:
            out_path (str): The path to save the JSON file.
        """

        self.validate(verbose=False)

        with open(out_path, "w") as f:
            f.write(self.vfg.model_dump_json(indent=4))

        self.logger.info(f"JSON representation of model exported to: {out_path}")

    def visualize(
        self, factor_color: str = "lightgreen", variable_color: str = "lightcoral"
    ) -> None:
        """
        Visualize the JSON model dict.

        Parameters:
            factor_color (str): The color for the factor nodes. Defaults to "lightgreen".
            variable_color (str): The color for the variable nodes. Defaults to "lightcoral".
        """

        self.validate(verbose=False)

        # Gather variable names and the number of variables
        variable_names = list(self.vfg.variables.keys())
        n_variables = len(variable_names)

        # Try to use the role as the factor name; if it does not exist, then name factor by
        # position in the factor list.
        factor_names = []
        factors = self.vfg.factors
        n_factors = len(factors)

        # Collect factor names
        for f in range(n_factors):
            if (
                "role" in factors[f]
            ):  # If the user has input a role, use it as the factor name
                factor_names.append(factors[f]["role"])
            else:  # If the user has not input a role, use the position in the list as the name
                factor_names.append(f"F{f}")

        g = nx.Graph()  # Initialize networkx graph

        # Add factor and variable nodes to networkx graph
        for f in factor_names:
            g.add_node(f)

        for v in variable_names:
            g.add_node(v)

        # Build connection list that shows what factors hook to what nodes
        connection_list = []

        # Loop over factors and use the "variables" attribute to determine connections
        for idx, f in enumerate(self.vfg.factors):
            for v in f.variables:
                connection_list.append((factor_names[idx], v))

        # Add edges to networkx graph
        g.add_edges_from(connection_list)

        # Draw graph
        color_map = [factor_color] * n_factors + [variable_color] * n_variables
        nx.draw(g, with_labels=True, font_color="black", node_color=color_map)

    def _to_vfg(self, json_model: dict):
        """
        Wrapper for vfg_from_json in pyvfg.

        Parameters:
            json_model (dict): The JSON model dict.

        Returns:
            The VFG object created from the JSON model.
        """
        self.validate(verbose=False)
        return vfg_upgrade(json.dumps(json_model))

    def get_variable_values(self, variable_id: str) -> list:
        """
        Wrapper for pyvfg variable elements access.

        Parameters:
            variable_id (str): The ID of the variable.

        Returns:
            list: The values of the variable.
        """
        return self.vfg.variables[variable_id].elements

    def get_variable_role(self, variable_id: str) -> Optional[VariableRole]:
        """
        Gets the role for a variable, if one is set

        Parameters:
            variable_id (str): The ID of the variable.

        Returns:
            VariableRole: The role of the variable.
        """
        variable = self.vfg.variables[variable_id]
        if hasattr(variable.root, "role"):
            return variable.root.role
        return None

    def get_variable_names(self) -> list:
        """
        Wrapper for pyvfg variable keys access.

        Returns:
            list: The names of the variables.
        """
        return list(self.vfg.variables.keys())

    def get_factor_attributes(self, factor_id: int, attribute: str):
        """
        Wrapper for pyvfg factor attributes access.

        Parameters:
            factor_id (int): The ID of the factor.
            attribute (str): The attribute to retrieve.

        Returns:
            The value of the specified attribute.

        Raises:
            KeyError: If the attribute is not recognized.
        """
        if attribute == "variables":
            return self.vfg.factors[factor_id].variables
        elif attribute == "distribution":
            return self.vfg.factors[factor_id].distribution
        elif attribute == "values":
            return self.vfg.factors[factor_id].values
        elif attribute == "role":
            return self.vfg.factors[factor_id].role
        else:
            raise KeyError(
                f"Unrecognized attribute {attribute}. Attribute must be one of 'variables', 'distribution', 'values', or 'role'."
            )

    def load_model_from_bif(
        self, bif_path: str, verbose: bool = False
    ) -> "GeniusModel":
        """
        Loads a model from a Bayesian Interchange Format (BIF) file.

        This method uses the internal BIF to VFG converter to transform the BIF file to VFG format,
        and then loads the resulting model into the GeniusModel instance.

        Parameters:
            bif_path (str): Path to the BIF file to convert and load.
            verbose (bool, optional): Whether to print verbose output during conversion. Defaults to False.

        Returns:
            GeniusModel: The current instance for method chaining.

        Raises:
            FileNotFoundError: If the BIF file does not exist.
            ValueError: If the BIF file contains probability values that don't match variable cardinality.
            Exception: For any other errors encountered during conversion.
        """
        try:
            # Convert BIF to VFG using our internal converter
            vfg_dict = bif_to_vfg.bif_to_vfg(
                bif_path, output_path=None, verbose=verbose
            )

            # Create VFG object from dict and set as model
            self.vfg = vfg_upgrade(vfg_dict)

            # Validate the model - let validation errors bubble up
            self.validate(verbose=verbose)
        except Exception as e:
            self.logger.error(f"Failed to convert BIF file: {e}")
            raise

        # Return self for method chaining
        return self
