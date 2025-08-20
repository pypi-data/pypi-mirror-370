import numpy as np

from genius_client_sdk.model import GeniusModel


import pandas as pd


def test_validate_medium_factors_gpil_345():
    # df = pd.read_parquet('https://github.com/dmixsmi/rnd/raw/refs/heads/main/data/taxi_ride_requests.parquet')
    df = pd.read_parquet(
        "packages/genius-client-sdk/tests/fixtures/taxi_ride_requests.parquet"
    )
    df.reset_index(drop=True, inplace=True)
    # df.to_csv('observations.csv', index=False, quotechar='"', quoting=csv.QUOTE_ALL)

    variables = ["origin", "month", "day", "hour"]
    values = {var: np.sort(df[var].unique()).astype(str).tolist() for var in variables}
    levels = {var: len(vals) for var, vals in values.items()}
    assert levels == {"origin": 77, "month": 12, "day": 31, "hour": 24}

    model = GeniusModel()
    for var in variables:
        model.add_variable(var, values[var])
        model.add_factor(
            values=np.full(levels[var], 1 / levels[var]), target=var, parents=[]
        )

    model.add_factor(
        values=np.full(
            (levels["origin"], levels["month"], levels["day"], levels["hour"]),
            1 / levels["origin"],
        ),
        target="origin",
        parents=["month", "day", "hour"],
    )

    error_patches = model.vfg.validate()

    assert error_patches.patches == []


def test_validate_large_factors_gpil_345():
    df = pd.read_parquet(
        "packages/genius-client-sdk/tests/fixtures/taxi_ride_requests.parquet"
    )
    df.reset_index(drop=True, inplace=True)
    # df.to_csv('observations.csv', index=False, quotechar='"', quoting=csv.QUOTE_ALL)

    variables = ["destin", "origin", "month", "day", "hour"]
    values = {var: np.sort(df[var].unique()).astype(str).tolist() for var in variables}
    levels = {var: len(vals) for var, vals in values.items()}
    assert levels == {"destin": 77, "origin": 77, "month": 12, "day": 31, "hour": 24}

    model = GeniusModel()
    for var in variables:
        model.add_variable(var, values[var])
        model.add_factor(
            values=np.full(levels[var], 1 / levels[var]), target=var, parents=[]
        )

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

    error_patches = model.vfg.validate()

    assert error_patches.patches == []
