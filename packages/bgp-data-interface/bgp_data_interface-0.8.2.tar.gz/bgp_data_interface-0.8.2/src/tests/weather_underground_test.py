import credentials

from sys import path
path.append('./src/bgp_data_interface')
from wu import WeatherUnderground
from utils import location


import pandas as pd



def test_init_wu() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)

    assert api is not None
    assert isinstance(api, WeatherUnderground)


def test_historical_no_params() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    df = api.historical()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_empty_params() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    df = api.historical({})

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_yesterday() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({
        'start_date': yesterday.strftime("%Y-%m-%d"),
        'end_date': yesterday.strftime("%Y-%m-%d"),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (48, 38)


def test_historical_today() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    now = pd.Timestamp.now()

    df = api.historical({
        'start_date': now.strftime("%Y-%m-%d"),
        'end_date': now.strftime("%Y-%m-%d"),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_cnx() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    loc = location.get_airport(location.CNX)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_dmk() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    loc = location.get_airport(location.DMK)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_phs() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    loc = location.get_airport(location.PHS)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_svb() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    loc = location.get_airport(location.SVB)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38


def test_historical_utp() -> None:
    api = WeatherUnderground(credentials.WU_API_KEY)
    loc = location.get_airport(location.UTP)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 38
