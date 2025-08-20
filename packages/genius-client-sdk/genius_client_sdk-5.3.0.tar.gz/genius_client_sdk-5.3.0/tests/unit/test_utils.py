from unittest.mock import MagicMock, patch, mock_open

import numpy as np
import pytest
from genius_client_sdk.configuration import default_agent_config
from genius_client_sdk.utils import (
    control_map,
    control_payload,
    flatten_nested_list,
    get_policy_space,
    inference_payload,
    learning_payload,
    onehot,
    plot_categorical,
    policy_map,
    send_csv_request,
    send_http_request,
)
from requests.models import Response
from test_fixtures import (
    PATH_TO_SPRINKLER_LEARNING_PAYLOAD,
    start_simple_http_server_always_returns_200,
)


def test_send_valid_http_requests():
    httpd = start_simple_http_server_always_returns_200()
    try:
        for method in ["GET", "get", "PUT", "put", "POST", "post"]:
            # PUT and POST require a data field to be sent
            data = "data" if method.upper() in ["PUT", "POST"] else None
            response = send_http_request(httpd.get_addr(), method, "test", data=data)
            assert isinstance(response, Response), (
                f"Response for {method} is not of type Response: {response}"
            )
            assert response.status_code == 200, (
                f"Response for {method} is not 200: {response.status_code}"
            )
    finally:
        httpd.shutdown()


def test_send_invalid_http_requests():
    with pytest.raises(
        ValueError,
        match="Invalid HTTP request method. Must be 'GET', 'PUT', 'DELETE', or 'POST'.",
    ):
        send_http_request(default_agent_config.agent_url, "unsupported_method", "test")


def test_send_invalid_data_payload():
    with pytest.raises(
        ValueError,
        match='Invalid payload.  Please specify either "json_data" or "data", but not both.',
    ):
        send_http_request(
            default_agent_config.agent_url,
            "post",
            "infer",
            data="test",
            json_data={"data": "json"},
        )


def test_inference_payload_list_valid():
    payload = inference_payload(["var1", "var2"], {"evidence1": 1})
    assert payload == {
        "variables": ["var1", "var2"],
        "evidence": {"evidence1": 1},
        "library": "pgmpy",
    }


def test_inference_payload_string_valid():
    payload = inference_payload("var", {"evidence1": 1})
    assert payload == {
        "variables": "var",
        "evidence": {"evidence1": 1},
        "library": "pgmpy",
    }


def test_learning_payload_with_csv():
    payload = learning_payload(csv_path=PATH_TO_SPRINKLER_LEARNING_PAYLOAD)
    assert "observations_csv" in payload


def test_learning_payload_without_csv():
    payload = learning_payload(variables=["var1"], observations=[["obs1"]])
    assert payload == {"observations_csv": "var1\nobs1"}


def test_learning_payload_without_csv_missing_variables():
    with pytest.raises(
        ValueError, match="`variables` must be provided if not using a CSV file."
    ):
        learning_payload(observations=[["obs1"]])


def test_learning_payload_without_csv_missing_observations():
    with pytest.raises(
        ValueError, match="`observations` must be provided if not using a CSV file."
    ):
        learning_payload(variables=["var1"])


def test_learning_payload_missing_all_params():
    with pytest.raises(
        ValueError, match="`variables` must be provided if not using a CSV file."
    ):
        learning_payload()


def test_learning_payload_with_algorithm():
    """Test that algorithm parameter is correctly added to the payload."""
    payload = learning_payload(
        variables=["var1"],
        observations=[["obs1"]],
        algorithm="expectation_maximization",
    )
    assert payload == {
        "observations_csv": "var1\nobs1",
        "algorithm": "expectation_maximization",
    }


def test_learning_payload_with_library():
    """Test that library parameter is correctly added to the payload."""
    payload = learning_payload(
        variables=["var1"], observations=[["obs1"]], library="pgmpy"
    )
    assert payload == {"observations_csv": "var1\nobs1", "library": "pgmpy"}


def test_learning_payload_with_algorithm_and_library():
    """Test that both algorithm and library parameters are correctly added to the payload."""
    payload = learning_payload(
        variables=["var1"],
        observations=[["obs1"]],
        algorithm="bayesian_estimation",
        library="verses",
    )
    assert payload == {
        "observations_csv": "var1\nobs1",
        "algorithm": "bayesian_estimation",
        "library": "verses",
    }


def test_learning_payload_with_csv_and_algorithm_library():
    """Test that algorithm and library parameters work with CSV input."""
    with patch("builtins.open", mock_open(read_data="header1,header2\nvalue1,value2")):
        payload = learning_payload(
            csv_path="dummy_path.csv",
            algorithm="maximum_likelihood_estimation",
            library="pgmpy",
        )
        assert "observations_csv" in payload
        assert payload["algorithm"] == "maximum_likelihood_estimation"
        assert payload["library"] == "pgmpy"


def test_control_payload_with_int():
    payload = control_payload(10, 3)
    assert payload == {
        "library": "pymdp",
        "observation": 10,
        "policy_len": 3,
        "learn_likelihoods": False,
        "learn_transitions": False,
        "learn_initial_state_priors": False,
    }


def test_control_payload_with_string():
    payload = control_payload("10", 3)
    assert payload == {
        "library": "pymdp",
        "observation": "10",
        "policy_len": 3,
        "learn_likelihoods": False,
        "learn_transitions": False,
        "learn_initial_state_priors": False,
    }


def test_control_payload_with_dict():
    payload = control_payload(
        {"value": "10"},
        3,
    )
    assert payload == {
        "library": "pymdp",
        "observation": {"value": "10"},
        "policy_len": 3,
        "learn_likelihoods": False,
        "learn_transitions": False,
        "learn_initial_state_priors": False,
    }


def test_control_payload_with_array():
    # An array is no longer a valid observation type
    payload = control_payload(np.array([10]), 3)
    assert payload == {
        "library": "pymdp",
        "observation": [10],
        "policy_len": 3,
        "learn_likelihoods": False,
        "learn_transitions": False,
        "learn_initial_state_priors": False,
    }


def test_onehot_valid():
    array = onehot(5, 2)
    assert (array == np.array([0, 0, 1, 0, 0])).all()


def test_control_map_valid():
    action = control_map(["left", "right"], 1)
    assert action == "right"


def test_policy_map_valid():
    policy = policy_map([["left", "right"], ["right", "left"], ["up", "down"]], 2)
    assert policy == ["up", "down"]


def test_get_policy_space_with_action():
    policy_space = get_policy_space([2], [2], 2, ["left", "right"])
    assert policy_space == [
        [["left"], ["left"]],
        [["left"], ["right"]],
        [["right"], ["left"]],
        [["right"], ["right"]],
    ]


def test_get_policy_space_without_action():
    policy_space = get_policy_space(n_states=[9], n_actions=[5], policy_len=2)
    assert policy_space == [
        [[0], [0]],
        [[0], [1]],
        [[0], [2]],
        [[0], [3]],
        [[0], [4]],
        [[1], [0]],
        [[1], [1]],
        [[1], [2]],
        [[1], [3]],
        [[1], [4]],
        [[2], [0]],
        [[2], [1]],
        [[2], [2]],
        [[2], [3]],
        [[2], [4]],
        [[3], [0]],
        [[3], [1]],
        [[3], [2]],
        [[3], [3]],
        [[3], [4]],
        [[4], [0]],
        [[4], [1]],
        [[4], [2]],
        [[4], [3]],
        [[4], [4]],
    ]


def test_plot_categorical_simple():
    with (
        patch("matplotlib.pyplot.bar") as mock_bar,
        patch("matplotlib.pyplot.xticks") as mock_xticks,
        patch("matplotlib.pyplot.xlabel") as mock_xlabel,
        patch("matplotlib.pyplot.ylabel") as mock_ylabel,
        patch("matplotlib.pyplot.title") as mock_title,
        patch("matplotlib.pyplot.show") as mock_show,
    ):
        plot_categorical([1, 2, 3], [4, 5, 6], "X label", "Y label", "Title")

        mock_bar.assert_called_once_with([1, 2, 3], [4, 5, 6], color="dodgerblue")
        mock_xticks.assert_called_once_with(rotation=0)
        mock_xlabel.assert_called_once_with("X label")
        mock_ylabel.assert_called_once_with("Y label")
        mock_title.assert_called_once_with("Title")
        mock_show.assert_called_once()


def test_plot_categorical_simple_defaults():
    with (
        patch("matplotlib.pyplot.bar") as mock_bar,
        patch("matplotlib.pyplot.xticks") as mock_xticks,
        patch("matplotlib.pyplot.xlabel") as mock_xlabel,
        patch("matplotlib.pyplot.ylabel") as mock_ylabel,
        patch("matplotlib.pyplot.title") as mock_title,
        patch("matplotlib.pyplot.show") as mock_show,
    ):
        plot_categorical([1, 2, 3], [4, 5, 6])

        mock_bar.assert_called_once_with([1, 2, 3], [4, 5, 6], color="dodgerblue")
        mock_xticks.assert_called_once_with(rotation=0)
        mock_xlabel.assert_called_once_with("X")
        mock_ylabel.assert_called_once_with("Y")
        mock_title.assert_called_once_with("no title")
        mock_show.assert_called_once()


def test_flatten_nested_list():
    # Simple nested list
    assert flatten_nested_list([[1, 2], [3, 4]]) == [1, 2, 3, 4]

    # Nested list with different depths
    assert flatten_nested_list([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5]

    # Nested list with empty sublists
    assert flatten_nested_list([[], [1, 2], [], [3, 4], []]) == [1, 2, 3, 4]

    # Nested list with single element sublists
    assert flatten_nested_list([[1], [2], [3], [4]]) == [1, 2, 3, 4]

    # Deeply nested list
    assert flatten_nested_list([1, [2, [3, [4, [5]]]]]) == [1, 2, 3, 4, 5]

    # Nested list with mixed types
    assert flatten_nested_list([1, ["a", [2.5, [True, [None]]]]]) == [
        1,
        "a",
        2.5,
        True,
        None,
    ]


def test_sends_csv_data_successfully():
    agent_url = "http://localhost:8000"
    data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200

    with patch("requests.Session.post", return_value=response_mock) as mock_post:
        response = send_csv_request(agent_url, data)
        mock_post.assert_called_once_with(
            f"{agent_url}/import",
            json=None,
            data=data,
            headers={
                "Content-Type": "application/csv",
                "X-Skip-Sanity-Check": "false",
            },
            params=None,
        )
        assert response.status_code == 200


def test_fails_to_send_csv_data_with_invalid_url():
    agent_url = "http://invalid-url"
    data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 404

    with patch("requests.Session.post", return_value=response_mock) as mock_post:
        response = send_csv_request(agent_url, data)
        mock_post.assert_called_once_with(
            f"{agent_url}/import",
            json=None,
            data=data,
            headers={
                "Content-Type": "application/csv",
                "X-Skip-Sanity-Check": "false",
            },
            params=None,
        )
        assert response.status_code == 404


def test_fails_to_send_csv_data_with_empty_data():
    agent_url = "http://localhost:8000"
    data = ""
    response_mock = MagicMock()
    response_mock.status_code = 400

    with patch("requests.Session.post", return_value=response_mock) as mock_post:
        response = send_csv_request(agent_url, data)
        mock_post.assert_called_once_with(
            f"{agent_url}/import",
            json=None,
            data=data,
            headers={
                "Content-Type": "application/csv",
                "X-Skip-Sanity-Check": "false",
            },
            params=None,
        )
        assert response.status_code == 400
