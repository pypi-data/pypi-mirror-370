import json
import logging
import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import pytest
import pyvfg
from genius_client_sdk.model import VFG_VERSION, GeniusModel
from pyvfg import ModelType, VariableRole
from test_fixtures import (
    start_simple_http_server_always_returns_200,
    start_simple_http_server_always_returns_400,
)

# Sample BIF content for testing
SAMPLE_BIF_CONTENT = """
network unknown {
}
variable Cloudy {
    type discrete [ 2 ] { 0, 1 };
}
variable Rain {
    type discrete [ 2 ] { 0, 1 };
}
probability ( Cloudy ) {
    table 0.5, 0.5 ;
}
probability ( Rain | Cloudy ) {
    ( 0 ) 0.8, 0.2;
    ( 1 ) 0.2, 0.8;
}
"""


@pytest.fixture(scope="function", autouse=False)
def start_server():
    server_process = start_simple_http_server_always_returns_200()
    yield
    server_process.shutdown()


@pytest.fixture(scope="function", autouse=False)
def start_server_bad():
    server_process = start_simple_http_server_always_returns_400()
    yield
    server_process.shutdown()


def test_add_metadata_defaults():
    model = GeniusModel()
    model.add_metadata()
    assert model.vfg.metadata.model_type is ModelType.BayesianNetwork
    assert model.vfg.metadata.model_version is None
    assert model.vfg.metadata.description is None


def test_add_metadata_values():
    model = GeniusModel()
    model.add_metadata(
        model_type=ModelType.MarkovRandomField, description="test", model_version="1.0"
    )
    assert model.vfg.metadata.model_type is ModelType.MarkovRandomField
    assert model.vfg.metadata.model_version == "1.0"
    assert model.vfg.metadata.description == "test"


def test_model_with_metadata_is_serializable():
    model = GeniusModel()
    model.add_metadata()

    model_str = json.dumps(model.vfg.to_dict())
    assert (
        model_str
        == '{"version": "'
        + VFG_VERSION
        + '", "metadata": {"model_type": "bayesian_network"}, "variables": {}, "factors": []}'
    )


def test_model_version():
    model = GeniusModel()
    assert model.version == model.vfg.version


def test_add_variables():
    model = GeniusModel()
    model.add_variables([("var1", ["v11", "v12"]), ("var2", ["v21", "v22"])])
    assert sorted(model.get_variable_names()) == ["var1", "var2"]
    assert sorted(model.get_variable_values("var1")) == ["v11", "v12"]
    assert sorted(model.get_variable_values("var2")) == ["v21", "v22"]


def test_adds_variable_with_role():
    model = GeniusModel()
    model.add_variable("var1", ["v11", "v12"], role=VariableRole.Latent)
    assert sorted(model.get_variable_names()) == ["var1"]
    assert sorted(model.get_variable_values("var1")) == ["v11", "v12"]
    assert model.get_variable_role("var1") == VariableRole.Latent


def test_adds_factor_with_role_name():
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    assert model.vfg.factors[0].role == "likelihood"
    assert model.vfg.factors[0].variables == ["var1"]


def test_adds_factor_with_role_preference_sets_logits_distribution():
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="preference")
    assert model.vfg.factors[0].role == "preference"
    assert model.vfg.factors[0].distribution == "logits"


def test_adds_factor_without_role_name():
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1")
    assert model.vfg.factors[0].variables == ["var1"]
    assert model.vfg.factors[0].distribution == "categorical"
    assert (model.vfg.factors[0].values == np.array([0.1, 0.9])).all()
    assert model.vfg.factors[0].role is None


def test_add_factor_without_variables_raises_exception():
    model = GeniusModel()
    with pytest.raises(Exception) as excinfo:
        model.add_factor(np.array([0.1, 0.9]), "var1")
    assert "Variables must be added to the model before factors can be added." in str(
        excinfo.value
    )


def test_add_factor_with_nonexistent_variable_raises_assertion():
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    with pytest.raises(AssertionError) as excinfo:
        model.add_factor(np.array([0.1, 0.9]), "var2")
    assert "Variables var2 not in the list of added variables." in str(excinfo.value)


def test_add_factor_with_mismatched_dimensions_raises_assertion():
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    with pytest.raises(AssertionError):
        model.add_factor(np.array([[0.1, 0.9], [0.2, 0.8]]), "var1")
    assert "Number of variables associated with factor does not match the dimension of the factor values."


def test_validate_model_with_all_components(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    model.validate()
    assert model.vfg.factors[0].role == "likelihood"
    assert model.vfg.variables["var1"].elements == ["v1", "v2"]


def test_validate_model_missing_components_raises_exception(start_server_bad):
    model = GeniusModel()
    model.vfg.factors.append(
        pyvfg.Factor(
            variables=[],
            distribution=pyvfg.Distribution.Categorical,
            counts=[],
            values=[],
        )
    )
    with pytest.raises(Exception) as exception_info:
        model.validate()
    assert "MissingProbability" in str(exception_info.value)


def test_add_variable_toggles_flag(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    assert "var1" in model.vfg.variables
    assert model.vfg.variables["var1"].elements == ["v1", "v2"]


def test_add_factor_toggles_flag(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    assert model.vfg.factors[0].role == "likelihood"
    assert model.vfg.factors[0].variables == ["var1"]
    assert np.all(model.vfg.factors[0].values == np.array([0.1, 0.9]))


def test_save_model_creates_json_file(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    file_path = "model.json"
    model.save(file_path)

    assert os.path.exists(file_path)
    with open(file_path, "r") as f:
        saved_model = json.load(f)
    assert saved_model["variables"]["var1"]["elements"] == ["v1", "v2"]
    assert saved_model["factors"][0]["role"] == "likelihood"


def test_visualize_model_creates_graph(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    model.visualize()
    assert True  # Assuming visualize does not raise an exception


def test_get_variable_values_returns_correct_values(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    values = model.get_variable_values("var1")
    assert values == ["v1", "v2"]


def test_get_variable_names_returns_correct_names(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    names = model.get_variable_names()
    assert names == ["var1"]


def test_get_factor_attributes_returns_correct_attributes(start_server):
    model = GeniusModel()
    model.add_variable("var1", ["v1", "v2"])
    model.add_factor(np.array([0.1, 0.9]), "var1", role="likelihood")
    attributes = model.get_factor_attributes(0, "role")
    assert str(attributes) == "FactorRole.Likelihood"


def test_initializes_with_default_version():
    model = GeniusModel()
    assert model.vfg.version == VFG_VERSION
    assert model.vfg.factors == []
    assert model.vfg.variables == {}


def test_initializes_with_json_path(start_server):
    json_path = "path/to/json"
    with patch(
        "builtins.open",
        mock_open(read_data='{"factors": [], "variables": {}, "version": "1.0.0"}'),
    ):
        model = GeniusModel(json_path=json_path)
    assert model.vfg.version == "1.0.0"
    assert model.vfg.factors == []
    assert model.vfg.variables == {}


def test_initializes_logger_correctly():
    with patch.object(
        logging, "getLogger", return_value=MagicMock()
    ) as mock_get_logger:
        GeniusModel()
        mock_get_logger.assert_called_once_with("genius_client_sdk.model.GeniusModel")


def test_get_factor_distribution():
    model = GeniusModel()
    model.vfg.factors.append(
        pyvfg.Factor(
            distribution=pyvfg.Distribution.Categorical,
            variables=[],
            counts=[],
            values=[],
        )
    )
    distribution = model.get_factor_attributes(factor_id=0, attribute="distribution")

    assert distribution == "categorical"


def test_get_factor_attributes_unrecognized_attribute():
    model = GeniusModel()

    with patch.object(model, "_to_vfg") as mock_to_vfg:
        mock_to_vfg.return_value = type(
            "MockVFG", (object,), {"factors": {0: type("MockFactor", (object,), {})()}}
        )()

        with pytest.raises(
            KeyError,
            match=r"Unrecognized attribute unknown_attribute\. Attribute must be one of 'variables', 'distribution', 'values', or 'role'\.",
        ):
            model.get_factor_attributes(0, "unknown_attribute")


def test_add_factor_with_parents():
    model = GeniusModel()

    # Add variables first
    model.add_variable("A", ["0", "1"])
    model.add_variable("B", ["0", "1"])
    model.add_variable("C", ["0", "1"])

    # Define factor values
    values = np.array([[[0.1, 0.9], [0.8, 0.2]], [[0.3, 0.7], [0.6, 0.4]]])

    # Add factor with parents
    model.add_factor(values=values, target="A", parents=["B", "C"])

    # Check if the factor was added correctly
    assert len(model.vfg.factors) == 1
    assert model.vfg.factors[0].variables == ["A", "B", "C"]


def test_does_not_send_to_remote():
    agent_url = "http://localhost:8000"
    model = GeniusModel(agent_url=agent_url)
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = {"vfg": None, "errors": []}

    with patch("requests.post", return_value=response_mock) as mock_post:
        model.validate()
        mock_post.assert_not_called()


def test_parse_validation_errors_missing():
    agent_url = "http://localhost:8000"
    model = GeniusModel(agent_url=agent_url)

    validation_errors = model.validate(model_type=ModelType.BayesianNetwork)
    assert validation_errors == []


def test_load_model_from_bif():
    """Test the method with a mocked converter to verify correct behavior and interface."""

    # Create a temporary BIF file with sample content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".bif") as tmp_file:
        tmp_file.write(SAMPLE_BIF_CONTENT)
        bif_path = tmp_file.name

    try:
        # Create GeniusModel and load the BIF file
        model = GeniusModel()

        with patch(
            "genius_client_sdk.converters.bif_to_vfg.bif_to_vfg"
        ) as mock_bif_to_vfg:
            # Create a mock return value that simulates the converted VFG
            mock_vfg = {
                "version": VFG_VERSION,
                "metadata": {
                    "model_type": "bayesian_network",
                    "model_version": "1.0",
                    "description": "Converted from BIF format",
                },
                "variables": {
                    "Cloudy": {"elements": ["0", "1"]},
                    "Rain": {"elements": ["0", "1"]},
                },
                "factors": [
                    {
                        "variables": ["Cloudy"],
                        "distribution": "categorical",
                        "values": [0.5, 0.5],
                    },
                    {
                        "variables": ["Rain", "Cloudy"],
                        "distribution": "categorical_conditional",
                        "values": [[0.8, 0.2], [0.2, 0.8]],
                    },
                ],
            }
            mock_bif_to_vfg.return_value = mock_vfg

            # Load the model
            result = model.load_model_from_bif(bif_path)

            # Check the mock was called with correct arguments
            mock_bif_to_vfg.assert_called_once_with(
                bif_path, output_path=None, verbose=False
            )

            # Check method returns self for chaining
            assert result is model

            # Check the model contains the expected elements
            assert set(model.get_variable_names()) == {"Cloudy", "Rain"}
            assert model.get_factor_attributes(0, "variables") == ["Cloudy"]
            assert model.get_factor_attributes(1, "variables") == ["Rain", "Cloudy"]

    finally:
        # Clean up the temporary file
        os.unlink(bif_path)


def test_load_model_from_bif_integration():
    """Integration test for loading a model from a BIF file using the actual converter."""

    # Create a temporary BIF file with sample content
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".bif") as tmp_file:
        tmp_file.write(SAMPLE_BIF_CONTENT)
        bif_path = tmp_file.name

    try:
        # Create GeniusModel and load the BIF file
        model = GeniusModel()
        model.load_model_from_bif(bif_path)

        # Verify the model was loaded properly
        assert "Cloudy" in model.get_variable_names()
        assert "Rain" in model.get_variable_names()
        assert len(model.vfg.factors) == 2

        # Check that variables have the correct elements
        assert model.get_variable_values("Cloudy") == ["0", "1"]
        assert model.get_variable_values("Rain") == ["0", "1"]
    finally:
        # Clean up the temporary file
        os.unlink(bif_path)


def test_load_model_from_bif_file_not_found():
    """Test that load_model_from_bif raises FileNotFoundError for non-existent files."""

    model = GeniusModel()

    # Test with a non-existent file
    non_existent_path = "non_existent_file.bif"

    with pytest.raises(FileNotFoundError):
        model.load_model_from_bif(non_existent_path)


def test_load_model_from_bif_cardinality_error():
    """Test that load_model_from_bif raises ValueError for cardinality mismatches."""

    # Create a BIF file with cardinality mismatch (more probability values than states)
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".bif") as tmp_file:
        tmp_file.write("""
            network unknown {
            }
            variable A {
                type discrete [ 2 ] { 0, 1 };
            }
            probability ( A ) {
                table 0.3, 0.3, 0.4 ;  # 3 values for a binary variable
            }
            """)
        bif_path = tmp_file.name

    try:
        model = GeniusModel()

        # This should raise a ValueError due to cardinality mismatch
        with pytest.raises(ValueError) as excinfo:
            model.load_model_from_bif(bif_path)

        # Verify the error message mentions cardinality
        assert "has 3 values, but the variable has 2 states" in str(excinfo.value)
    finally:
        os.unlink(bif_path)


def test_load_model_from_bif_parse_error():
    """Test that load_model_from_bif raises an exception for invalid BIF files."""

    # Create an invalid BIF file (missing closing brackets)
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".bif") as tmp_file:
        tmp_file.write("""
            network unknown {
            }
            variable B {
                type discrete [ 2 ] { 0, 1  # Missing closing bracket
            }
            probability ( B ) {
                table 0.5, 0.5 ;
            }
            """)
        bif_path = tmp_file.name

    try:
        model = GeniusModel()

        # With our stricter validation, we expect this to raise an exception
        with pytest.raises(KeyError):
            model.load_model_from_bif(bif_path)
    finally:
        # Clean up the temporary file
        os.unlink(bif_path)
