import os

import genius_client_sdk as gc
import numpy as np
import pandas as pd
import pytest

from conftest import SDK_MEMORY_LIMIT, SDK_REQUEST_TIMEOUT, TEST_LOOP_COUNT

# changes to the original
data_url = "packages/genius-client-sdk/tests/fixtures/taxi_ride_requests.parquet"


def main():
    gc.__version__

    genv = dict(
        AGENT_HTTP_PROTOCOL=os.getenv("SDK_AGENT_HTTP_PROTOCOL", "http"),
        AGENT_HOSTNAME=os.getenv("SDK_AGENT_HOSTNAME", "localhost"),
        AGENT_PORT=os.getenv("SDK_AGENT_PORT", "3000"),
    )

    agent = gc.agent.GeniusAgent(
        agent_http_protocol=genv["AGENT_HTTP_PROTOCOL"],
        agent_hostname=genv["AGENT_HOSTNAME"],
        agent_port=genv["AGENT_PORT"],
    )

    df = pd.read_parquet(data_url)
    df.reset_index(drop=True, inplace=True)
    print(df)

    variables = ["origin", "month", "day", "hour"]

    values = {var: np.sort(df[var].unique()).astype(str).tolist() for var in variables}

    levels = {var: len(vals) for var, vals in values.items()}
    print(levels)

    model = gc.model.GeniusModel(agent_url=agent.agent_url)

    for var in variables:
        model.add_variable(var, values[var])
        model.add_factor(
            values=np.full(levels[var], 1 / levels[var]), target=var, parents=[]
        )

    # Create factors with uniformly distributed initial probabilities
    model.add_factor(
        values=np.full(
            (levels["origin"], levels["month"], levels["day"], levels["hour"]),
            1 / levels["origin"],
        ),
        target="origin",
        parents=["month", "day", "hour"],
    )

    model.validate()

    agent.load_genius_model(model=model)

    observations = df.loc[0:1, variables].values.astype(int)
    print(observations)

    agent.learn(variables=variables, observations=observations.tolist())

    observations = df.loc[2:3, variables].values.astype(int)
    print(observations)

    agent.learn(variables=variables, observations=observations.tolist())
    return True


@pytest.mark.slow
@pytest.mark.limit_memory(f"{SDK_MEMORY_LIMIT} MB")
@pytest.mark.timeout(SDK_REQUEST_TIMEOUT)
@pytest.mark.parametrize("count", range(TEST_LOOP_COUNT))
def test_learn_incorrect_tensor_shape_gpil_508(count):
    """test wrapper"""
    results = main()
    assert results is True, f"Failed on iteration {count}"


if __name__ == "__main__":
    main()
