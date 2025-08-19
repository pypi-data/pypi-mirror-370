from sys import path
path.append('./src/bgp_data_interface')
from openmeteo import Openmeteo
from utils import location
from typing import Any


import pandas as pd


def _location_params(site: str) -> dict[str, Any]:
    loc = location.get_location(site)

    return {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    }




def test_init_om() -> None:
    api = Openmeteo()

    assert api is not None


def test_forecast_no_params() -> None:
    api = Openmeteo()
    df = api.forecast()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)


def test_forecast_empty_params() -> None:
    api = Openmeteo()
    df = api.forecast({})

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)


def test_forecast_empty_features() -> None:
    api = Openmeteo()
    df = api.forecast({
        "hourly": [],
        "minutely_15": [],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (0, 0)


def test_forecast_hourly() -> None:
    api = Openmeteo()
    df = api.forecast({
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
        "minutely_15": [],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (93, 4)


def test_forecast_minutely() -> None:
    api = Openmeteo()
    df = api.forecast({
        "hourly": [],
        "minutely_15": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 4)


def test_bangbo_forecast_hourly() -> None:
    api = Openmeteo()

    params = _location_params(location.BBO) | {
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
        "minutely_15": [],
    }
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (93, 4)


def test_bangbo_forecast_minutely() -> None:
    api = Openmeteo()

    params = _location_params(location.BBO) | {
        "hourly": [],
        "minutely_15": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    }
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 4)


def test_bangbo_forecast_all() -> None:
    api = Openmeteo()

    params = _location_params(location.BBO)
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)


def test_abp_forecast_all() -> None:

    params = _location_params(location.ABP)

    api = Openmeteo()
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)


def test_forecast_period() -> None:
    api = Openmeteo()
    today = pd.Timestamp.now()
    df = api.forecast({
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)


def test_historical_no_params() -> None:
    api = Openmeteo()
    df = api.historical()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 73)


def test_historical_empty_params() -> None:
    api = Openmeteo()
    df = api.historical({})

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 73)


def test_historical_empty_features() -> None:
    api = Openmeteo()
    df = api.historical({
        "hourly": []
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (0, 0)


def test_historical_hourly() -> None:
    api = Openmeteo()
    df = api.historical({
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 4)


def test_bangbo_historical_hourly() -> None:
    api = Openmeteo()

    params = _location_params(location.BBO) | {
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    }
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 4)


def test_abp_historical_hourly() -> None:
    api = Openmeteo()

    params = _location_params(location.ABP) | {
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    }
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 4)


def test_abp_historical_all() -> None:
    api = Openmeteo()

    params = _location_params(location.ABP)
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 73)


def test_historical_period() -> None:
    api = Openmeteo()
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)
    df = api.historical({
        "start_date": (yesterday + pd.Timedelta(days=-1)).strftime("%Y-%m-%d"),
        "end_date": yesterday.strftime("%Y-%m-%d"),
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (48, 73)
