import os

import genius_client_sdk as gc
import numpy as np
import pandas as pd
import pytest

from conftest import SDK_MEMORY_LIMIT, SDK_REQUEST_TIMEOUT


def model_validate(protocol, hostname, port, data_url, rebin_factor) -> bool:
    agent = gc.agent.GeniusAgent(
        agent_http_protocol=protocol,  # env['AGENT_HTTP_PROTOCOL'],
        agent_hostname=hostname,  # env['AGENT_HOSTNAME'],
        agent_port=port,  # env['AGENT_PORT']
    )

    df = pd.read_parquet(data_url)
    df.reset_index(drop=True, inplace=True)
    # rebin and floor
    df["destin"] = (df["destin"] / rebin_factor).apply(np.floor)
    df["origin"] = (df["origin"] / rebin_factor).apply(np.floor)
    # df = df.head(10000)
    variables = ["destin", "origin", "month", "day", "hour"]
    values = {var: np.sort(df[var].unique()).astype(str).tolist() for var in variables}
    levels = {var: len(vals) for var, vals in values.items()}

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
    model.add_factor(
        values=np.full(
            (
                levels["destin"],
                levels["origin"],
                levels["month"],
                levels["day"],
                levels["hour"],
            ),
            1 / levels["destin"],
        ),
        target="destin",
        parents=["origin", "month", "day", "hour"],
    )

    validation_errors = model.validate()
    return validation_errors


@pytest.mark.slow
@pytest.mark.limit_memory(f"{SDK_MEMORY_LIMIT} MB")
@pytest.mark.timeout(SDK_REQUEST_TIMEOUT)
@pytest.mark.parametrize(
    "rebin_factor",
    [10, 7, 4, 2, 1],
)
def test_agent_model_validate_gpil_492(rebin_factor):
    protocol = os.getenv("SDK_AGENT_HTTP_PROTOCOL", "http")
    hostname = os.getenv("SDK_AGENT_HOSTNAME", "localhost")
    port = os.getenv("SDK_AGENT_PORT", "3000")

    # data_url = 'https://github.com/dmixsmi/rnd/raw/refs/heads/main/data/taxi_ride_requests.parquet'
    data_url = "packages/genius-client-sdk/tests/fixtures/taxi_ride_requests.parquet"

    results = model_validate(protocol, hostname, port, data_url, rebin_factor)
    assert results == []
