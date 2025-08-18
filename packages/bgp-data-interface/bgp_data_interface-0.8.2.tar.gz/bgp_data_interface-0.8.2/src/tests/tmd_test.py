import credentials

from sys import path
path.append('./src/bgp_data_interface')
from tmd import TMD
from typing import Any
from utils import location


import pandas as pd




def _location_params(site: str) -> dict[str, Any]:
    loc = location.get_location(site)

    return {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    }


def test_init_tmd() -> None:
    api = TMD(credentials.TMD_TOKEN)

    assert api is not None
    assert isinstance(api, TMD)


def test_forecast_no_params() -> None:
    api = TMD(credentials.TMD_TOKEN)
    df = api.forecast()

    today = pd.Timestamp.today()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_empty_params() -> None:
    api = TMD(credentials.TMD_TOKEN)
    df = api.forecast({})

    today = pd.Timestamp.today()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_today() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast({
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': today.strftime('%Y-%m-%d'),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_2days() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()
    tomorrow = today + pd.Timedelta(days=1)

    df = api.forecast({
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': tomorrow.strftime('%Y-%m-%d'),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == tomorrow.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_cnx() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast(_location_params(location.CNX))

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_dmk() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast(_location_params(location.DMK))   

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_abp() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast(_location_params(location.ABP))

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_forecast_bip() -> None:
    api = TMD(credentials.TMD_TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast(_location_params(location.BIP))

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 11
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23
