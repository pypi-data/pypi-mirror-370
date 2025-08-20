import json
import logging
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest
from genius_client_sdk.agent import GeniusAgent
from genius_client_sdk.datamodel.api import AutoBinVariable
from genius_client_sdk.model import GeniusModel
from test_fixtures import (
    PATH_TO_SPRINKLER_NOWRAPPER_VFG,
    PATH_TO_SPRINKLER_VFG,
    start_simple_http_server_always_returns_200,
)

with open(PATH_TO_SPRINKLER_NOWRAPPER_VFG, "r") as f:
    SPRINKLER_VFG = json.loads(f.read())


@pytest.fixture(scope="function", autouse=False)
def start_server():
    server_process = start_simple_http_server_always_returns_200()
    yield
    server_process.shutdown()


@pytest.fixture
def agent():
    return GeniusAgent()


def test_version():
    import genius_client_sdk

    assert genius_client_sdk.__version__ is not None


# region Model


def test_get_model_from_server_successful():
    agent = GeniusAgent()
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"vfg": SPRINKLER_VFG}

    with patch("genius_client_sdk.agent.send_http_request", return_value=response_mock):
        agent.get_model_from_server()
        assert agent.model is not None and agent.model.vfg is not None


def test_get_model_from_server_failure():
    agent = GeniusAgent()
    response_mock = MagicMock()
    response_mock.status_code = 400
    response_mock.text = "Error"

    with patch("genius_client_sdk.agent.send_http_request", return_value=response_mock):
        with pytest.raises(AssertionError, match="Error retrieving graph: Error"):
            agent.get_model_from_server()


def test_get_model_from_server_no_graph():
    agent = GeniusAgent()
    response_mock = MagicMock()
    response_mock.status_code = 204
    response_mock.text = "Error"

    with patch("genius_client_sdk.agent.send_http_request", return_value=response_mock):
        agent.get_model_from_server()
        assert agent.model is None


def test_load_model_from_json(agent, start_server):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        agent.load_model_from_json(PATH_TO_SPRINKLER_VFG)
        assert agent.model is not None


def test_load_model_from_json_failure(agent, start_server):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 400
        with pytest.raises(AssertionError):
            agent.load_model_from_json(PATH_TO_SPRINKLER_VFG)


def test_delete_model_successful():
    agent = GeniusAgent()
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.text = "Error"

    with patch("genius_client_sdk.agent.send_http_request", return_value=response_mock):
        agent.unload_model()


def test_delete_model_failure():
    agent = GeniusAgent()
    response_mock = MagicMock()
    response_mock.status_code = 500
    response_mock.text = "Error"

    with patch("genius_client_sdk.agent.send_http_request", return_value=response_mock):
        with pytest.raises(AssertionError, match="Unloading model failed: Error"):
            agent.unload_model()


# endregion

# region Structure learning


def test_structure_learning_successful():
    agent = GeniusAgent()
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200

    with open(PATH_TO_SPRINKLER_NOWRAPPER_VFG, "r") as _f:
        sprinkler_model = json.loads(_f.read())
    response_mock.json.return_value = {"result": sprinkler_model}

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ) as mock_request:
            agent.structure_learning(csv_path="dummy_path.csv", verbose=False)
            assert agent.model.vfg.to_dict() == sprinkler_model
            mock_request.assert_called_once()


def test_structure_learning_fails_with_invalid_csv():
    agent = GeniusAgent()
    csv_data = "invalid_csv_data"
    response_mock = MagicMock()
    response_mock.status_code = 400
    response_mock.text = "Error"

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            with pytest.raises(
                AssertionError, match="Error performing structure learning: Error"
            ):
                agent.structure_learning(csv_path="dummy_path.csv", verbose=False)


def test_structure_learning_calls_parameter_learning():
    agent = GeniusAgent()
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"result": SPRINKLER_VFG}
    load_model_mock = MagicMock()
    load_model_mock.status_code = 200

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            with patch(
                "genius_client_sdk.agent.send_http_request",
                return_value=load_model_mock,
            ):
                agent.structure_learning(csv_path="dummy_path.csv", verbose=False)
                assert agent.model.vfg.to_dict() == SPRINKLER_VFG


def test_structure_learning_verbose_logging():
    agent = GeniusAgent()
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"result": SPRINKLER_VFG}
    load_model_mock = MagicMock()
    load_model_mock.status_code = 200

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            with patch(
                "genius_client_sdk.agent.send_http_request",
                return_value=load_model_mock,
            ):
                with patch.object(agent.logger, "info") as mock_logger_info:
                    agent.structure_learning(csv_path="dummy_path.csv", verbose=True)
                    mock_logger_info.assert_called_with(
                        json.dumps(response_mock.json().get("result"), indent=4)
                    )


def test_structure_learning_passes_correct_agent_url():
    agent1 = GeniusAgent(agent_hostname="localhost")
    agent2 = GeniusAgent(agent_hostname="127.0.0.1")
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"result": SPRINKLER_VFG}
    load_model_mock = MagicMock()
    load_model_mock.status_code = 200

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            with patch(
                "genius_client_sdk.agent.send_http_request",
                return_value=load_model_mock,
            ):
                with patch("genius_client_sdk.agent.GeniusModel") as mock_genius_model:
                    agent1.structure_learning(csv_path="dummy_path.csv")
                    mock_genius_model.assert_called_with(agent_url=agent1.agent_url)
                    agent2.structure_learning(csv_path="dummy_path.csv")
                    mock_genius_model.assert_called_with(agent_url=agent2.agent_url)


# endregion

# region Logs


def test_logs_summarized_model_contents():
    agent = GeniusAgent()
    model = GeniusModel(agent.agent_url, json_path=PATH_TO_SPRINKLER_NOWRAPPER_VFG)

    agent.model = model

    agent.logger = MagicMock()
    agent.log_model(summary=True)
    with patch(
        "genius_client_sdk.agent.send_http_request",
    ) as mock_request:
        mock_request.return_value.status_code = 200

        # these validations could be more robust but this is a start
        agent.logger.log.assert_any_call(logging.INFO, "Model contents:")
        agent.logger.log.assert_any_call(
            logging.INFO, "4 variables: ['cloudy', 'rain', 'sprinkler', 'wet_grass']"
        )
        agent.logger.log.assert_any_call(
            logging.INFO,
            "4 factors: [['cloudy'], ['rain', 'cloudy'], ['sprinkler', 'cloudy'], ['wet_grass', 'sprinkler', 'rain']]",
        )


def test_logs_raw_json_model():
    agent = GeniusAgent()
    model_mock = MagicMock()
    model_mock.json_model = SPRINKLER_VFG
    agent.model = model_mock
    agent.logger = MagicMock()

    agent.log_model(summary=False, logging_level=logging.INFO)

    agent.logger.log.assert_called_with(
        logging.INFO, agent.model.vfg.model_dump_json(indent=4)
    )


def test_fails_to_log_model_when_no_model_loaded():
    agent = GeniusAgent()
    agent.logger = MagicMock()

    with pytest.raises(
        Exception,
        match="No model loaded. load_genius_model\\(\\) must be run before viewing the model.",
    ):
        agent.log_model(summary=False, logging_level=logging.WARNING)


# endregion

# region Infer


def test_infer(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.text = r'{"result": {"evidence": {}, "probabilities": {}}, "success": true, "error": null, "metadata": null}'
        agent.model = GeniusModel()
        result = agent.infer("variable_id", {"evidence": "data"})
        assert "probabilities" in result


def test_infer_failure(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 400
        with pytest.raises(AssertionError):
            agent.infer("variable_id", {"evidence": "data"})


# endregion

# region Learn


def test_learn(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_json = {
            "result": {
                "updated_model": SPRINKLER_VFG,
                "success": True,
                "metadata": {"execution_time": 0.5, "memory_used": [0.125, "MB"]},
            }
        }
        mock_request.return_value.json = lambda: mock_json
        mock_request.return_value.text = json.dumps(mock_json)
        mock_request.return_value.status_code = 200

        # Model must be set prior to calling learn
        agent.model = GeniusModel()
        agent.learn(variables=["var1"], observations=[[1]])

        # Check that the vfg has been updated
        assert len(agent.model.vfg.factors) > 0


def test_learn_failure(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 400
        with pytest.raises(AssertionError):
            agent.learn(variables=["var1"], observations=[[1]])


@patch(
    "builtins.open", new_callable=mock_open, read_data="variable1,variable2\n1,2\n3,4"
)
@patch("genius_client_sdk.agent.send_http_request")
def test_learn_with_mocked_file(mock_send_http_request, mock_file):
    # Mock the response from send_http_request
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": {"updated_model": SPRINKLER_VFG}}
    mock_response.headers = {}
    mock_send_http_request.return_value = mock_response

    # Create an instance of GeniusAgent
    agent = GeniusAgent()
    with patch.object(agent.logger, "info") as mock_logger_info:
        # Model must be set prior to calling learn
        agent.model = GeniusModel()
        # Call the learn method with the mocked file path
        agent.learn(csv_path="mocked_path.csv", verbose=True)

        # Check that the log contains the expected output
        mock_logger_info.assert_called_with(agent.model.vfg.model_dump_json(indent=4))


def test_initial_model_has_no_factors(agent):
    """Test that the vfg is the default empty model when agent is created."""
    agent.model = GeniusModel()
    assert len(agent.model.vfg.factors) == 0


def test_learning_history_initially_none():
    """Test that learning_history is initially None when agent is created."""
    agent = GeniusAgent()
    assert agent.learning_history is None


def test_learning_history_populated():
    """Test that learning_history is populated from the response after learn() is called."""
    agent = GeniusAgent()

    # Create a mock learning history
    mock_learning_history = [
        {"iteration": 1, "log_likelihood": -10.5},
        {"iteration": 2, "log_likelihood": -5.2},
        {"iteration": 3, "log_likelihood": -2.1},
    ]

    # Setup the mock response with learning history
    mock_json = {
        "result": {"updated_model": SPRINKLER_VFG, "history": mock_learning_history}
    }

    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = mock_json
        mock_request.return_value.headers = {}

        # Model must be set prior to calling learn
        agent.model = GeniusModel()
        agent.learn(variables=["var1"], observations=[[1]])

        # Verify learning_history is populated with the mock data
        assert agent.learning_history == mock_learning_history


def test_learning_history_logging_when_verbose():
    """Test that learning_history is logged when verbose=True."""
    agent = GeniusAgent()

    # Create a mock learning history
    mock_learning_history = [
        {"iteration": 1, "log_likelihood": -10.5},
        {"iteration": 2, "log_likelihood": -5.2},
    ]

    # Setup the mock response with learning history
    mock_json = {
        "result": {"updated_model": SPRINKLER_VFG, "history": mock_learning_history}
    }

    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = mock_json
        mock_request.return_value.headers = {}

        # Model must be set prior to calling learn
        agent.model = GeniusModel()

        # Patch the logger to check it's called correctly
        with patch.object(agent.logger, "info") as mock_logger:
            agent.learn(variables=["var1"], observations=[[1]], verbose=True)

            # Check that learning history was logged
            mock_logger.assert_any_call("Learning history:")
            mock_logger.assert_any_call(json.dumps(mock_learning_history, indent=4))


def test_learning_history_not_logged_when_not_verbose():
    """Test that learning_history is not logged when verbose=False."""
    agent = GeniusAgent()

    # Create a mock learning history
    mock_learning_history = [
        {"iteration": 1, "log_likelihood": -10.5},
        {"iteration": 2, "log_likelihood": -5.2},
    ]

    # Setup the mock response with learning history
    mock_json = {
        "result": {"updated_model": SPRINKLER_VFG, "history": mock_learning_history}
    }

    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = mock_json
        mock_request.return_value.headers = {}

        # Model must be set prior to calling learn
        agent.model = GeniusModel()

        # Patch the logger to check it's called correctly
        with patch.object(agent.logger, "info") as mock_logger:
            agent.learn(variables=["var1"], observations=[[1]], verbose=False)

            # Check that learning history messages weren't logged
            learning_history_calls = [
                call
                for call in mock_logger.call_args_list
                if call[0][0] == "Learning history:"
                or call[0][0] == json.dumps(mock_learning_history, indent=4)
            ]
            assert len(learning_history_calls) == 0


def test_learning_history_null_in_response():
    """Test handling when history is null in the response."""
    agent = GeniusAgent()

    # Setup the mock response with null history
    mock_json = {"result": {"updated_model": SPRINKLER_VFG, "history": None}}

    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.json.return_value = mock_json
        mock_request.return_value.headers = {}

        # Model must be set prior to calling learn
        agent.model = GeniusModel()
        agent.learn(variables=["var1"], observations=[[1]])

        # Verify learning_history is None
        assert agent.learning_history is None


# endregion

# region Action Selection


def test_act(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_json = {
            "result": {
                "updated_vfg": SPRINKLER_VFG,
                "action_data": {},
                "belief_state": {},
                "policy_belief": {},
                "efe_components": {},
            },
            "success": True,
            "metadata": {"execution_time": 0.5, "memory_used": [0.125, "MB"]},
        }
        mock_request.return_value.json = lambda: mock_json
        mock_request.return_value.text = json.dumps(mock_json)
        agent.model = GeniusModel()
        result = agent.act(10)
        assert "belief_state" in result
        assert "policy_belief" in result
        assert "efe_components" in result
        assert "action_data" in result
        assert "metadata" in result
        assert "success" in result["metadata"]
        assert "error" in result["metadata"]
        assert "warnings" in result["metadata"]


def test_act_failure(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 400
        with pytest.raises(AssertionError):
            agent.act(10)


# endregion

# region CSV


def test_validate_csv_successful():
    agent = GeniusAgent()
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"errors": [], "warnings": []}

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            agent.validate_csv(csv_path="dummy_path.csv")


def test_validate_csv_failure():
    agent = GeniusAgent()
    csv_data = "variable1,variable2\n1,0\n0,1"
    response_mock = MagicMock()
    response_mock.status_code = 422
    response_mock.json.return_value = {
        "errors": [{"row": 0, "col": 0, "message": "Invalid header name"}],
        "warnings": [],
    }

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch(
            "genius_client_sdk.agent.send_csv_request", return_value=response_mock
        ):
            with pytest.raises(
                AssertionError,
                match="Error performing csv validation:",
            ):
                agent.validate_csv(csv_path="dummy_path.csv")


# endregion

# region Simulation


def test_simulation(agent):
    with patch("genius_client_sdk.agent.send_http_request") as mock_request:
        mock_request.return_value.status_code = 200
        mock_request.return_value.text = r'{"result": {"history":[{"observation":{"observation":7},"belief_state":{},"policy_belief":[],"efe_components":{},"action_data":{},"updated_model":{"version":"0.5.0","metadata":{},"variables":{},"factors":[],"visualization_metadata":null}},{"observation":{"observation":7},"belief_state":{},"policy_belief":[],"efe_components":{},"action_data":{},"updated_model":{"version":"0.5.0","metadata":{},"variables":{},"factors":[],"visualization_metadata":null}}]}}'
        agent.model = GeniusModel()
        result = agent.simulate(
            num_steps=3,
            policy_len=2,
            initial_state={
                "position": 2,
            },
        )
        assert "history" in result
        history = result["history"]
        assert isinstance(history, list)
        assert "observation" in history[0]
        assert "belief_state" in history[0]
        assert "policy_belief" in history[0]
        assert "efe_components" in history[0]
        assert "action_data" in history[0]
        assert "updated_model" in history[0]


# endregion

# region Auto Bin One Off


def test_auto_bin_one_off(agent):
    csv_data = "variable1,variable2\n1,0\n0,1"

    with patch("builtins.open", mock_open(read_data=csv_data)):
        with patch("genius_client_sdk.agent.send_http_request") as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.text = r'{"result": {"score": [0.1, 0.3]}, "binned_csv": "variable1,variable2\n1,0\n0,1"}'
            agent.model = GeniusModel()
            result, binned_csv = agent.auto_bin_one_off(
                csv_path="dummy_path.csv",
                variables=AutoBinVariable(
                    {
                        "score": {
                            "binning_strategy": "quantile",
                            "num_bins": 3,
                            "x_column": "score",
                        }
                    }
                ),
            )
            assert "score" in result
            score = result["score"]
            assert isinstance(score, list)
            assert 0.1 in score

            assert binned_csv is not None
            assert binned_csv == "variable1,variable2\n1,0\n0,1"


# endregion


def test_raises_exception_when_no_model_loaded():
    agent = GeniusAgent()
    with pytest.raises(
        Exception,
        match="No model loaded. load_genius_model\\(\\) must be run before viewing the model.",
    ):
        agent.log_model()
