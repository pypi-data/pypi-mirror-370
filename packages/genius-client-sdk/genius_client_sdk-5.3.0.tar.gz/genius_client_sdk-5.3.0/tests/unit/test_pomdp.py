import pytest
import numpy as np
from genius_client_sdk.pomdp import POMDPModel
from test_fixtures import start_simple_http_server_always_returns_200


def test_validate_model_with_all_components():
    httpd = start_simple_http_server_always_returns_200()
    try:
        model = POMDPModel()
        model.add_variable("var1", ["a", "b"])
        model.add_variable("var2", ["a", "b"])
        model.add_variable("var3", ["a", "b"])
        model.add_variable("output", values=["high", "low"])
        model.add_likelihood_factor(np.array([0.1, 0.9]), "var1")
        model.add_transition_factor(np.array([0.2, 0.8]), "var2")
        model.add_preference_factor(np.array([0.3, 0.7]), "var3")
        model.add_state_variable("state", ["s1", "s2"])
        model.add_observation_variable("obs", ["o1", "o2"])
        model.add_action_variable("action", ["a1", "a2"])
        model.add_prior_factor(np.array([0.1, 0.9]), "var1")

        # filler so that we don't have "floating variables", which are validation errors.
        output_factor = np.random.rand(2, 2, 2, 2)
        model.add_factor(
            values=output_factor, target="output", parents=["state", "obs", "action"]
        )
        model.vfg.factors[-1].normalize()  # pre-normalize

        model.validate(correct_errors=True)
    finally:
        httpd.shutdown()
    assert model.flags == {
        "likelihood": True,
        "transition": True,
        "preference": True,
        "state": True,
        "observation": True,
        "control": True,
    }


def test_validate_model_missing_components_raises_exception():
    model = POMDPModel()
    with pytest.raises(Exception) as excinfo:
        model.validate()
    assert "The following components are missing from the POMDP model" in str(
        excinfo.value
    )


def test_add_likelihood_factor_toggles_flag():
    model = POMDPModel()
    model.add_variable("var1", [])
    model.add_likelihood_factor(np.array([0.1, 0.9]), "var1")
    assert model.flags["likelihood"] is True


def test_add_transition_factor_toggles_flag():
    model = POMDPModel()
    model.add_variable("var2", [])
    model.add_transition_factor(np.array([0.2, 0.8]), "var2")
    assert model.flags["transition"] is True


def test_add_preference_factor_toggles_flag():
    model = POMDPModel()
    model.add_variable("var3", [])
    model.add_preference_factor(np.array([0.3, 0.7]), "var3")
    assert model.flags["preference"] is True


def test_add_state_variable_toggles_flag():
    model = POMDPModel()
    model.add_state_variable("state", ["s1", "s2"])
    assert model.flags["state"] is True


def test_add_observation_variable_toggles_flag():
    model = POMDPModel()
    model.add_observation_variable("obs", ["o1", "o2"])
    assert model.flags["observation"] is True


def test_add_action_variable_toggles_flag():
    model = POMDPModel()
    model.add_action_variable("action", ["a1", "a2"])
    assert model.flags["control"] is True
