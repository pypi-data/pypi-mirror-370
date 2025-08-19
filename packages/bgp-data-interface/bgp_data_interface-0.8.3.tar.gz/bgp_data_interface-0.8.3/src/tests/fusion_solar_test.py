import credentials

from sys import path
path.append('./src/bgp_data_interface')
from fusion_solar import FusionSolar
import pandas as pd
from utils import location


import pandas as pd



def test_init_fs() -> None:
    api = FusionSolar(
        credentials.FUSION_SOLAR_USERNAME,
        credentials.FUSION_SOLAR_PASSWORD)

    assert api is not None
    assert isinstance(api, FusionSolar)


def test_historical_no_params() -> None:
    api = FusionSolar(
        credentials.FUSION_SOLAR_USERNAME,
        credentials.FUSION_SOLAR_PASSWORD)
    df = api.historical()

    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (288, 12)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_historical_empty_params() -> None:
    api = FusionSolar(
        credentials.FUSION_SOLAR_USERNAME,
        credentials.FUSION_SOLAR_PASSWORD)
    df = api.historical({})

    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (288, 12)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_historical_last3days() -> None:
    api = FusionSolar(
        credentials.FUSION_SOLAR_USERNAME,
        credentials.FUSION_SOLAR_PASSWORD)
    last3days = pd.Timestamp.now() + pd.Timedelta(days=-3)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({
        'start_date': last3days.strftime('%Y-%m-%d'),
        'end_date': yesterday.strftime('%Y-%m-%d'),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (864, 12)
    assert df.iloc[0]['date_time'].day == last3days.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_historical_vhh() -> None:
    api = FusionSolar(
        credentials.FUSION_SOLAR_USERNAME,
        credentials.FUSION_SOLAR_PASSWORD)
    loc = location.get_location(location.VHH)

    df = api.historical({
        'fs_code': loc['fusion_solar_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (288, 12)
