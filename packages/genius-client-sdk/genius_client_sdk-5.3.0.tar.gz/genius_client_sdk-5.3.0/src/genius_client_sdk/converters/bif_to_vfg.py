#!/usr/bin/env python
"""
BIF to VFG Converter for VERSES SDK

Description:
    This module converts Bayesian Interchange Format (.bif) files to VERSES Factor Graph (VFG) format
    compliant with version 0.5.0 spec. BIF is a common file format for representing Bayesian networks,
    while VFG is VERSES' JSON-based universal factor graph notation.

Features:
    - Parses BIF files containing variable definitions and probability tables
    - Supports both prior and conditional probability distributions
    - Converts probabilistic relationships to the appropriate factor graph representation
    - Maintains proper tensor dimensionality and orientation
    - Adds appropriate metadata for the Genius SDK compatibility
"""

import os
import json
import re
import numpy as np
import logging

logger = logging.getLogger(__name__)


def read_bif_file(filename):
    """
    Read a .bif file and return its content.

    Args:
        filename (str): The path to the BIF file to read.

    Returns:
        str: The content of the .bif file.
    """
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        logger.warning(f"BIF file not found: {filename}")
        raise


def parse_bif_content(bif_content, verbose=False):
    """
    Parse the content of a .bif file using regex patterns.

    Args:
        bif_content (str): The content of the .bif file.
        verbose (bool): Whether to print verbose output.

    Returns:
        tuple: A tuple containing states, parents, and values dictionaries.
    """
    # Regex patterns
    variable_pattern = re.compile(r"variable\s+(\w+)\s*\{")
    variable_type_pattern = re.compile(
        r"\s*type\s+discrete\s*\[\s*\d+\s*\]\s*\{\s*(.+?)\s*\}\s*;", re.DOTALL
    )
    probability_pattern = re.compile(
        r"probability\s*\(\s*(\w+)(?:\s*\|\s*(.+?))?\s*\)\s*\{", re.DOTALL
    )
    table_pattern = re.compile(r"\s*table\s+(.+?)\s*;", re.DOTALL)
    condition_pattern = re.compile(r"\s*\((.+?)\)\s+(.+?)\s*;", re.DOTALL)

    states = {}  # Dictionary with BIF variables as keys and variable categories as values
    parents = {}  # Dictionary with BIF variables as keys and dependencies as values
    values = {}  # Dictionary with variables as keys and probability values

    lines = bif_content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Match variable declaration
        var_match = variable_pattern.match(line)
        if var_match:
            var_name = var_match.group(1)

            # Look for the type in subsequent lines
            for j in range(i + 1, min(i + 10, len(lines))):
                type_match = variable_type_pattern.match(lines[j])
                if type_match:
                    states[var_name] = [
                        val.strip() for val in type_match.group(1).split(",")
                    ]
                    if verbose:
                        logger.info(
                            f"Found variable: {var_name} with states: {states[var_name]}"
                        )
                    break
            i += 1
            continue

        # Match probability declaration
        prob_match = probability_pattern.match(line)
        if prob_match:
            var_name = prob_match.group(1)
            conditional_vars = prob_match.group(2)

            if conditional_vars:
                # Conditional probability
                parents[var_name] = [v.strip() for v in conditional_vars.split(",")]

                # Parse conditional probability table
                probs = []
                k = i + 1
                while k < len(lines) and not lines[k].strip().startswith("}"):
                    cond_match = condition_pattern.match(lines[k].strip())
                    if cond_match:
                        conditions = [c.strip() for c in cond_match.group(1).split(",")]
                        prob_values = [
                            float(p.strip()) for p in cond_match.group(2).split(",")
                        ]
                        probs.append((conditions, prob_values))
                    k += 1

                # Store in structured format for tensor building
                values[var_name] = {"type": "conditional", "data": probs}

                if verbose:
                    logger.info(
                        f"Found conditional probability for {var_name} given {parents[var_name]}"
                    )
            else:
                # Prior probability
                parents[var_name] = []

                # Look for table in subsequent lines
                for j in range(i + 1, min(i + 10, len(lines))):
                    table_match = table_pattern.match(lines[j])
                    if table_match:
                        prob_values = np.array(
                            [float(p.strip()) for p in table_match.group(1).split(",")]
                        )
                        values[var_name] = {"type": "prior", "data": prob_values}
                        if verbose:
                            logger.info(
                                f"Found prior probability for {var_name}: {values[var_name]}"
                            )
                        break

            i += 1
            continue

        i += 1

    return states, parents, values


def create_vfg_model(states, parents, values, version="0.5.0"):
    """
    Create a VFG model from the parsed BIF data, using direct tensor construction.

    This function transforms the parsed BIF data into a VFG model by:
    1. Converting variables and their states to VFG format
    2. Creating properly shaped tensors for both prior and conditional probability distributions
    3. Ensuring correct tensor dimensionality with the target variable in the first position
    4. Populating tensor values according to the BIF file's probability specifications

    For prior probabilities (variables with no parents), a simple 1D array is created.
    For conditional probabilities, an N-dimensional tensor is constructed where:
    - The first dimension corresponds to the target variable's states
    - Subsequent dimensions correspond to parent variables' states
    - Values are placed at indices matching the state configurations from the BIF file

    The function handles both:
    - Prior probability tables (where variables have no parents)
    - Conditional probability tables (CPTs) with single or multiple parent variables

    Args:
        states (dict): Dictionary mapping variable names to their possible states.
        parents (dict): Dictionary mapping variables to their parent variables.
        values (dict): Dictionary mapping variables to structured probability values
                      where each entry has a 'type' ('prior' or 'conditional') and 'data'.
        version (str): VFG format version.

    Returns:
        dict: VFG model in dictionary format with proper variable, factor, and metadata structures.

    Raises:
        ValueError: If the probability values don't match the expected cardinality of variables.
    """
    # Get model variables in VFG format
    variables = {k: {"elements": v} for k, v in states.items()}

    # Create factors with proper tensor shapes
    factors = []

    for var_name, var_parents in parents.items():
        # Define the factor variables array with target variable first
        factor_vars = [var_name] + var_parents

        # Determine distribution type based on presence of parents
        distribution = "categorical_conditional" if var_parents else "categorical"

        # Build dimensions for tensor based on variable cardinalities
        dims = [len(states[v]) for v in factor_vars]

        # Create and populate the tensor based on probability type
        if values[var_name]["type"] == "prior":
            # Validate that prior probability matches variable cardinality
            prob_values = values[var_name]["data"]
            if len(prob_values) != dims[0]:
                raise ValueError(
                    f"Prior probability for variable '{var_name}' has {len(prob_values)} values, "
                    f"but the variable has {dims[0]} states. These must match."
                )

            # Convert numpy array to Python list
            tensor_values = prob_values.tolist()
        else:  # 'conditional'
            # Initialize tensor of the correct shape
            tensor = np.zeros(dims)

            # Get expected number of parent state combinations
            expected_combinations = np.prod(dims[1:])
            actual_combinations = len(values[var_name]["data"])

            if actual_combinations != expected_combinations:
                raise ValueError(
                    f"Conditional probability for variable '{var_name}' has {actual_combinations} "
                    f"parent state combinations, but expected {expected_combinations} combinations "
                    f"based on parent variables {var_parents}."
                )

            # Fill in the tensor based on conditional probabilities
            for conditions, prob_values in values[var_name]["data"]:
                # Validate probabilities match target variable cardinality
                if len(prob_values) != dims[0]:
                    raise ValueError(
                        f"Conditional probability for variable '{var_name}' with condition {conditions} "
                        f"has {len(prob_values)} values, but the variable has {dims[0]} states. These must match."
                    )

                # Get indices for parent values
                try:
                    parent_indices = [
                        states[parent].index(cond)
                        for parent, cond in zip(var_parents, conditions)
                    ]
                except ValueError:
                    raise ValueError(
                        f"Invalid parent state value in condition {conditions} for variable '{var_name}'. "
                        f"Please ensure all parent state values are valid."
                    )

                # For each target variable value, set the probability
                for target_idx, prob in enumerate(prob_values):
                    # Create the index tuple: [target_idx, parent1_idx, parent2_idx, ...]
                    idx = tuple([target_idx] + parent_indices)
                    tensor[idx] = prob

            # Convert numpy array to Python list
            tensor_values = tensor.tolist()

        # Create the factor entry
        factor = {
            "variables": factor_vars,
            "distribution": distribution,
            "values": tensor_values,
        }

        factors.append(factor)

    # Assemble VFG model with proper metadata
    vfg_model = {
        "version": version,
        "factors": factors,
        "variables": variables,
        "metadata": {
            "model_type": "bayesian_network",
            "model_version": "1.0",
            "description": "Converted from BIF format using genius_client_sdk.converters.bif_to_vfg",
        },
    }

    return vfg_model


def save_vfg_to_file(output_path, vfg_model):
    """
    Save the VFG model to a JSON file.

    Args:
        output_path (str): The path where to save the VFG file.
        vfg_model (dict): The VFG model to save.

    Returns:
        None
    """
    with open(output_path, "w") as file:
        json.dump(vfg_model, file, indent=4)
    logger.info(f"VFG saved to {output_path}")


def bif_to_vfg(bif_path, output_path=None, verbose=False, version="0.5.0"):
    """
    Convert a BIF file to VFG format.

    Args:
        bif_path (str): Path to the BIF file to convert.
        output_path (str, optional): Path where to save the VFG file. If None, will create a path based on input filename.
        verbose (bool, optional): Whether to print verbose output.
        version (str, optional): VFG format version.

    Returns:
        dict: The VFG model as a dictionary.
    """
    # Read the BIF file
    bif_content = read_bif_file(bif_path)

    # Parse the BIF content
    states, parents, values = parse_bif_content(bif_content, verbose)

    # Create the VFG model
    vfg_model = create_vfg_model(states, parents, values, version)

    # Save the VFG model if an output path is provided
    if output_path:
        save_vfg_to_file(output_path, vfg_model)
    elif bif_path:
        # Default output path
        filename = os.path.basename(bif_path).split(".")[0]
        default_output_path = f"{filename}_vfg_v{version.replace('.', '_')}.json"
        save_vfg_to_file(default_output_path, vfg_model)

    return vfg_model
