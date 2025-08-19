import credentials

from sys import path
path.append('./src/bgp_data_interface')
from datetime import datetime
from typing import Any
from utils import location
from weather_api import WeatherAPI


import pandas as pd


def _location_params(site: str) -> dict[str, Any]:
    loc = location.get_location(site)

    return {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    }




def test_init_wapi() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)

    assert api is not None


def test_forecast_no_params() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    df = api.forecast()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == datetime.today().day
    assert df.iloc[-1]['date_time'].day == datetime.today().day


def test_forecast_empty_params() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    df = api.forecast({})

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == datetime.today().day
    assert df.iloc[-1]['date_time'].day == datetime.today().day


def test_bangbo_forecast_hourly() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)

    params = _location_params(location.BBO)
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == datetime.today().day
    assert df.iloc[-1]['date_time'].day == datetime.today().day


def test_forecast_3_days() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    today = pd.Timestamp.today()

    params = _location_params(location.BBO) | {
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": (today + pd.Timedelta(days=2)).strftime("%Y-%m-%d"),
    }
    df = api.forecast(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (72, 22)
    assert df.iloc[0]['date_time'].day == datetime.today().day
    assert df.iloc[-1]['date_time'].day == (datetime.today() + pd.Timedelta(days=2)).day


def test_historical_no_params() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_historical_empty_params() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({})

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_bangbo_historical() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    params = _location_params(location.BBO)
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_abp_historical() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    params = _location_params(location.ABP)
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_abp_historical_yesterday() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    params = _location_params(location.ABP) | {
        "start_date": yesterday.strftime("%Y-%m-%d"),
        "end_date": yesterday.strftime("%Y-%m-%d"),
    }
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == yesterday.day
    assert df.iloc[-1]['date_time'].day == yesterday.day


def test_abp_historical_last_2days() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    now = pd.Timestamp.now()

    params = _location_params(location.ABP) | {
        "start_date": (now + pd.Timedelta(days=-2)).strftime("%Y-%m-%d"),
        "end_date": now.strftime("%Y-%m-%d"),
    }
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (72, 22)
    assert df.iloc[0]['date_time'].day == (now + pd.Timedelta(days=-2)).day
    assert df.iloc[-1]['date_time'].day == now.day


def test_cnx_historical_last_week() -> None:
    api = WeatherAPI(credentials.WEATHER_API_KEY)
    last_week = pd.Timestamp.now() + pd.Timedelta(days=-7)

    params = _location_params(location.CNX) | {
        "start_date": last_week.strftime("%Y-%m-%d"),
        "end_date": last_week.strftime("%Y-%m-%d"),
    }
    df = api.historical(params)

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == last_week.day
    assert df.iloc[-1]['date_time'].day == last_week.day
