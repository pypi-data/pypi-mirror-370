import credentials

from sys import path
path.append('./src/bgp_data_interface')
from s3_weather import S3Weather
from utils import location


import pandas as pd



def test_init_s3() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')

    assert api is not None
    assert isinstance(api, S3Weather)


def test_s3_retrieve() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({})

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == (today + pd.Timedelta(days=1)).day
    assert df.iloc[-1]['date_time'].hour == 0
    assert 'temperature_2m' in df.columns
    assert 'global_tilted_irradiance' in df.columns


def test_s3_retrieve_location() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({
        'location': location.ABP
    })

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 68)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == (today + pd.Timedelta(days=1)).day
    assert df.iloc[-1]['date_time'].hour == 0




def test_s3_retrieve_type() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    last2days = pd.Timestamp.now() + pd.Timedelta(days=-2)

    df = api.retrieve({
        'type': 'historical',
        'source': 'weather_api',
        'start_date': last2days.strftime('%Y-%m-%d'),
        'end_date': last2days.strftime('%Y-%m-%d')
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == last2days.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == last2days.day
    assert df.iloc[-1]['date_time'].hour == 23




def test_s3_retrieve_date() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-08'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0



def test_s3_retrieve_source() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    df = api.retrieve({
        'source': 'weather_api'
    })

    today = pd.Timestamp.now()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (24, 22)
    assert df.iloc[0]['date_time'].day == today.day
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == today.day
    assert df.iloc[-1]['date_time'].hour == 23


def test_s3_retrieve_too_early_dates() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-07'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0


def test_s3_retrieve_too_late_dates() -> None:
    api = S3Weather(credentials.WEATHER_AWS_ACCESS_KEY, credentials.WEATHER_AWS_SECRET_KEY, 'bgp-weather-data')
    start_date = '2025-05-07'
    end_date = '2025-05-09'
    df = api.retrieve({
        'start_date': start_date,
        'end_date': end_date
    })

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (192, 68)
    assert df.iloc[0]['date_time'].day == 8
    assert df.iloc[0]['date_time'].hour == 0
    assert df.iloc[-1]['date_time'].day == 10
    assert df.iloc[-1]['date_time'].hour == 0

