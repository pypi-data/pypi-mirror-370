import csv
import json
import time
from typing import Any, Dict, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import requests
from pymdp.control import construct_policies


def send_http_request(
    agent_url: str,
    http_request_method: str,
    call: str = "",
    json_data: Optional[Union[str, Dict[str, Any]]] = None,
    data: Optional[str] = None,
    headers: Dict[str, str] = None,
    params: Dict[str, str] = None,
    polling_timeout_sec: float = 120,
    polling_frequency_sec: float = 0.1,
    etag: Optional[str] = None,
    session: requests.Session = None,
) -> requests.models.Response:
    """
    Sends an HTTP request to a remote server, handling 202 responses with synchronous polling.

    Parameters:
        agent_url (str): The base URL of the agent.
        http_request_method (str): The HTTP method to use.
        call (str): The specific endpoint to call.
        json_data (Optional[Union[str, Dict[str, Any]]]): JSON data to send in the request.
        data (Optional[str]): Data to send in the request (already stringified).
        headers (Dict[str, str]): Headers to include in the request.
        params (Dict[str, str]): URL parameters to include in the request.
        polling_timeout_sec (float): The maximum time to wait for a response.
        polling_frequency_sec (float): The frequency of polling in seconds (or fractions thereof).
        etag (Optional[str]): ETag to match. Will not be used if `If-Match`, `If-None-Match` are set in headers.

    Raises:
        ValueError: If both `json_data` and `data` are provided, or if neither is provided for POST/PUT.
        TimeoutError: If the task does not complete within the expected time.
        requests.exceptions.RequestException: For any HTTP request errors.

    Returns:
        requests.models.Response: The final response from the server.
    """

    ## Check the payload data parameters that both are not set
    if json_data is not None and data is not None:
        raise ValueError(
            'Invalid payload.  Please specify either "json_data" or "data", but not both.'
        )

    if http_request_method in ["POST", "PUT"]:
        if json_data is None and data is None:
            raise ValueError(
                'Invalid payload.  Please specify either "json_data" or "data".'
            )

    ## Set ETag as an If-Match, but only if neither If-Match nor If-None-Match are set in headers
    if etag is not None:
        if headers is None:
            headers = {}
        if "If-Match" not in headers and "If-None-Match" not in headers:
            headers["If-Match"] = etag

    ## Send an API request and handle async polling if needed.
    response = _send_raw_http_request(
        agent_url,
        http_request_method,
        call,
        json_data,
        data,
        headers,
        params,
        session=session,
    )

    # Check if response contains a task ID that needs polling
    if response.status_code == 202:
        task_id = response.json().get("id")
        if task_id:
            return _poll_task_status(
                agent_url,
                task_id,
                polling_timeout_sec=polling_timeout_sec,
                polling_frequency_sec=polling_frequency_sec,
                session=session,
            )

        raise ValueError(f"Task id not found {response.text}")

    return response


def _poll_task_status(
    agent_url: str,
    task_id: str,
    polling_timeout_sec: float = 120,
    polling_frequency_sec: float = 0.1,
    session: requests.Session = None,
) -> requests.models.Response:
    """
    Poll the status endpoint until task completion or failure.

    Parameters:
        agent_url (str): Base URL of the agent
        task_id (str): ID of the task to poll
        polling_timeout_sec (float): Maximum amount of time to wait in seconds
        polling_frequency_sec (float): Delay between polling attempts in seconds

    Raises:
        TimeoutError: If the task does not complete within the expected time
        ValueError: If the task fails or returns an error

    Returns:
        requests.models.Response: The final response with task results
    """
    url = f"{agent_url}/status/{task_id}"

    max_polling_cycles = int(polling_timeout_sec / polling_frequency_sec)

    if session is None:
        session = requests.Session()

    for _ in range(max_polling_cycles):
        response = session.get(url)
        response.raise_for_status()
        status_data = response.json()

        if status_data["status"] == "failed" or status_data["error"] is not None:
            raise ValueError(f"Task {task_id} failed: {status_data['error']}")
        elif status_data["status"] == "completed":
            # Replace the content of the response with the "result" from the status_data
            response._content = json.dumps(status_data["result"]).encode()
            if "X-VFG-ETag" in response.headers:
                # rewrite to use ETag here, so that callers have a consistent interface
                response.headers["ETag"] = response.headers["X-VFG-ETag"]
            return response

        time.sleep(polling_frequency_sec)

    raise TimeoutError(f"Task {task_id} did not complete within the expected time")


def _send_raw_http_request(
    agent_url: str,
    http_request_method: str,
    call: str = "",
    json_data: Optional[Union[str, Dict[str, Any]]] = None,
    data: Optional[str] = None,
    headers: Dict[str, str] = None,
    params: Dict[str, str] = None,
    session: requests.Session = None,
) -> requests.models.Response:
    """
    Send an API request across a port for GET, PUT, and POST and a call. Optionally takes json_data
    as input for put or post.

    Parameters:
        agent_url (str): The base URL of the agent.
        http_request_method (str): The HTTP method to use.
        call (str): The specific endpoint to call.
        json_data (Optional[Union[str, Dict[str, Any]]]): JSON data to send in the request.
        data (Optional[str]): Data to send in the request (already stringified).
        headers (Dict[str, str]): Headers to include in the request.
        params (Dict[str, str]): URL parameters to include in the request.

    Raises:
        ValueError: If both `json_data` and `data` are provided, or if neither is provided for POST/PUT.
        requests.exceptions.RequestException: For any HTTP request errors.

    Returns:
        requests.models.Response: The response from the server.
    """

    url = f"{agent_url}/{call}"

    if session is None:
        session = requests.Session()

    # Headers
    if headers is None:
        headers = {}

    # set content type, if not set
    if "Content-Type" not in headers:
        headers["Content-Type"] = "application/json"

    # set resource control, if not set, for graph modification calls
    if call == "graph" and http_request_method.lower() != "get":
        if (
            "If-Modified-Since" not in headers
            and "If-None-Match" not in headers
            and "If-Match" not in headers
        ):
            headers["If-Match"] = "*"

    if http_request_method.lower() == "get":
        return session.get(url, headers=headers, params=params)
    elif http_request_method.lower() == "put":
        return session.put(
            url, headers=headers, params=params, data=data, json=json_data
        )
    elif http_request_method.lower() == "post":
        return session.post(
            url, headers=headers, params=params, data=data, json=json_data
        )
    elif http_request_method.lower() == "delete":
        return session.delete(url, headers=headers, params=params)
    else:
        raise ValueError(
            "Invalid HTTP request method. Must be 'GET', 'PUT', 'DELETE', or 'POST'."
        )


def send_csv_request(
    agent_url: str,
    data: str,
    call: str = "import",
    skip_sanity_check: bool = False,
    polling_timeout_sec: float = 120,
    polling_frequency_sec: float = 0.1,
    session: requests.Session = None,
):
    """
    POST CSV data over an API request across a port using the import call.

    Parameters:
        agent_url (str): The base URL of the agent.
        data (str): CSV data to send in the request.
        call (str): The specific endpoint to call. Defaults to "import".
        skip_sanity_check (bool): Whether to skip sanity check. Defaults to False.
        polling_timeout_sec (float): Maximum time to wait for a response.
        polling_frequency_sec (float): Frequency of polling in seconds.

    Returns:
        requests.models.Response: The response from the server.
    """

    headers = dict()
    headers["Content-Type"] = "application/csv"

    if call == "import":
        headers["X-Skip-Sanity-Check"] = "true" if skip_sanity_check else "false"

    # Send the POST request with the CSV data
    return send_http_request(
        agent_url=agent_url,
        http_request_method="post",
        call=call,
        data=data,
        headers=headers,
        polling_timeout_sec=polling_timeout_sec,
        polling_frequency_sec=polling_frequency_sec,
        session=session,
    )


def inference_payload(variables: Union[str, list], evidence: dict) -> dict:
    """
    Constructs the JSON payload for inference (default to PGMPY) based on an evidence input.

    Parameters:
        variables (Union[str, list]): A string or list of variable names to perform inference on.
        evidence (dict): A dictionary containing evidence where keys are variable names and values are observed values.

    Returns:
        dict: A dictionary representing the JSON payload for the inference request.
    """

    payload = {
        "variables": variables,
        "evidence": {k: v for k, v in evidence.items()},
        "library": "pgmpy",
    }

    return payload


def learning_payload(
    variables: list = None,
    observations: list = None,
    csv_path: str = None,
    algorithm: str = None,
    library: str = None,
) -> dict:
    """
    Takes in either:
    1) A list of variables and a nested list of observations for each variable. Each element of the
       nested list is like a new "row" of observations.
    2) A CSV file path with variables as column headers (first row) and observations as subsequent
       rows.

    The input is then parsed to create the JSON payload in the appropriate format.
    The data are turned into a string with the following structure:

    "{var1, var2,...}\n{obs1, obs2,...}\n{obs1, obs2,...}\n..."

    where observations are repeated for each row of observations available.
    No default library or algorithm is set.

    Parameters:
        variables (list): A list of variable names.
        observations (list): A nested list of observations corresponding to the variables.
        csv_path (str): Path to a CSV file containing variables and observations.
        algorithm (str): The learning algorithm to use (e.g., "maximum_likelihood_estimation", "expectation_maximization", "bayesian_estimation", "bayesian_em").
        library (str): The library to use for learning (e.g., "pgmpy", "verses").

    Returns:
        dict: A dictionary representing the JSON payload for the learning request.
    """

    # TODO: Assert that observation dims (per row) match number of variables

    if csv_path is not None:  # Read in the CSV file and turn it into a string
        with open(csv_path, "r") as file:
            csv_reader = csv.reader(file)
            rows = [",".join(row) for row in csv_reader]
            csv_string = "\n".join(rows)
    else:  # Joins variables and observations into a single string according expected format
        if variables is None:
            raise ValueError("`variables` must be provided if not using a CSV file.")
        if observations is None:
            raise ValueError("`observations` must be provided if not using a CSV file.")
        variables = ",".join(variables)
        # observations = "".join(["\n" + ",".join(row) for row in observations])
        observations = "".join(["\n" + ",".join(map(str, row)) for row in observations])
        csv_string = variables + observations

    payload = {"observations_csv": csv_string}

    # Add library to the payload if specified
    if library is not None:
        payload["library"] = library

    # Add algorithm to the payload if specified
    if algorithm is not None:
        payload["algorithm"] = algorithm

    return payload


def control_payload(
    observation: Union[int, str, Dict[str, Union[int, str]]],
    policy_len: int,
    learn_likelihoods: bool = False,
    learn_transitions: bool = False,
    learn_initial_state_priors: bool = False,
) -> dict:
    """
    Constructs the JSON payload for action selection (default to pymdp) based on an evidence input.

    Parameters:
    observation (Union[int, str, Dict[str, Union[int, str]]]): Observation to be used in the payload
    policy_len (int): integer representing the length of the policy.
    learn_likelihoods (bool): Whether to learn likelihoods.  Defaults to False.
    learn_transitions (bool): Whether to learn transitions.  Defaults to False.
    learn_initial_state_priors (bool): Whether to learn initial state priors.  Defaults to False.

    Returns:
        dict: A dictionary representing the JSON payload for the control request.
    """

    payload = {
        "library": "pymdp",
        "observation": observation,
        "policy_len": policy_len,
        "learn_likelihoods": learn_likelihoods,
        "learn_transitions": learn_transitions,
        "learn_initial_state_priors": learn_initial_state_priors,
    }
    return payload


def onehot(
    size: int, position: int
) -> np.ndarray[Any, np.dtype[np.floating[Any] | np.float64]]:
    """
    Generates a one hot numpy array

    Parameters:
        size (int): size of the array
        position (int): position in the array for the 1 hot

    Returns:
        np.ndarray[Any, np.dtype[np.floating[Any] | np.float64]]: a one hot numpy array of dimension "size" with a 1 at the specified "position" and zeros for all other elements of the array
    """

    array = np.zeros(size)
    array[position] = 1
    return array


def control_map(controls: list[str], chosen_action: int) -> str:
    """
    Maps from the integer dummy encoding of an action to the action's string name

    Example: If the controls=["left", "right"] and chosen_action=1 then this function returns
             "right".

    Parameters:
        controls (list[str]): A list of strings containing possible actions
        chosen_action (int): An integer encoding of the selected action

    Returns:
        str : The string representation of the action
    """
    return controls[chosen_action]


def policy_map(policy_space: list[list[str]], chosen_policy: int) -> list[str]:
    """
    Maps from the integer dummy encoding of a policy in the policy space and the policy string

    Example: If policy_space=[["left", "right"], ["right", "left"], ["up", "down"]] and
             chosen_policy=2 then this function returns ["up", "down"].

    Parameters:
        policy_space (list[list[str]]) : The space of possible policies pursued by the agent. Can be
                                         obtained by using get_policy_space().
        chosen_policy (int)            : An integer encoding the chosen policy in the policy space.

    Returns:
        list[str] : A policy list which contains a sequence of actions as a string.
    """
    return policy_space[chosen_policy]


def get_policy_space(
    n_states: list[int],
    n_actions: list[int],
    policy_len: int,
    actions: list[str] = None,
) -> list[list[list[str]]]:
    """
    Constructs the space of all policies possible for the agent to pursue.

    Note that this function can be used for multiple observation modalities or state factor which
    is why the inputs for n_states and n_actions are lists.

    Parameters:
        n_states (list[int])  : A list of the number of states for each state factor.
        n_actions (list[int]) : A list of the number of actions for each state factor.
        policy_len (int)      : Length of policy (i.e. number of actions).
        actions (list[str])   : String representation of possible actions.

    Returns:
        list[list[list[str]]]: Either the string representation of the policy space or the dummy encoding of the policy space.
    """

    # Enumerate all possible policies given the number of states, actions, and the policy length
    policies = construct_policies(
        num_states=n_states, num_controls=n_actions, policy_len=policy_len
    )
    n_policies = len(policies)

    # Create the policy space (integer encoding)
    policy_space = [policies[p].tolist() for p in range(n_policies)]

    if (
        actions
    ):  # Converts policy space from integer representation to string representation
        action_mapping = {i: actions[i] for i in range(len(actions))}
        return [
            [[action_mapping[element[0]]] for element in sublist]
            for sublist in policy_space
        ]
    # just return the policy space
    return policy_space


def plot_categorical(
    x: list,
    y: list,
    xlabel: str = None,
    ylabel: str = None,
    title: str = None,
    color: str = "dodgerblue",  # Color of distribution bars
    rotation: int = 0,  # Rotation of x-axis labels
):
    """
    Helper function to plot a categorical distribution as a bar plot.


    Parameters:
        x (list): A list of categories or x-axis values.
        y (list): A list of values corresponding to each category in x.
        xlabel (list, optional): A list of labels for the x-axis. Defaults to None.
        ylabel (list, optional): A list of labels for the y-axis. Defaults to None.
        title (str, optional): The title of the plot. Defaults to None.
        color (str, optional): The color of the bars in the plot. Defaults to "dodgerblue".
        rotation (int, optional): The rotation angle of the x-axis labels. Defaults to 0.
    """

    plt.bar(x, y, color=color)
    plt.xticks(rotation=rotation)
    plt.xlabel(xlabel if xlabel is not None else "X")
    plt.ylabel(ylabel if ylabel is not None else "Y")
    plt.title(title if title is not None else "no title")
    plt.show()


def flatten_nested_list(nested_list: list) -> list:
    """Helper function that flattens a nested list.

    Parameters:
        nested_list (list): A list of categories or x-axis values.

    Returns:
        list: A flattened list.

    """
    flat_list = []
    for e in nested_list:
        if isinstance(e, list):
            flat_list.extend(flatten_nested_list(e))
        else:
            flat_list.append(e)
    return flat_list
