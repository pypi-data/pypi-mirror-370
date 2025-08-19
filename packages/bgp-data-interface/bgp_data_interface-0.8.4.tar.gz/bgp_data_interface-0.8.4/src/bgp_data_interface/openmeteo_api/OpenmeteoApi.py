import openmeteo_requests
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse

import os
import pandas as pd
import requests_cache
from retry_requests import retry
from typing import Any

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY = 'hourly'
MINUTELY_15 = 'minutely_15'
START_DATE = 'start_date'
END_DATE = 'end_date'

DATE_TIME_COL = 'date_time'

today = pd.Timestamp.now()
yesterday = today - pd.Timedelta(days=1)

DEFAULT_PARAMS: dict[str, Any] = {
    "latitude": 13.4916354486428,
    "longitude": 100.85609829815238,
    "timezone": "Asia/Bangkok",
}

ARCHIVE_PARAMS: dict[str, Any] = DEFAULT_PARAMS | {
    START_DATE: yesterday.strftime('%Y-%m-%d'),
    END_DATE: yesterday.strftime('%Y-%m-%d'),
    HOURLY: [
        "temperature_2m", "relative_humidity_2m", "dew_point_2m",
        "apparent_temperature", "precipitation", "rain", "snowfall", "snow_depth",
        "weather_code", "pressure_msl", "surface_pressure", "cloud_cover",
        "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high",
        "et0_fao_evapotranspiration", "vapour_pressure_deficit", "wind_speed_10m",
        "wind_speed_100m", "wind_direction_10m", "wind_direction_100m",
        "wind_gusts_10m", "soil_temperature_0_to_7cm", "soil_temperature_7_to_28cm",
        "soil_temperature_28_to_100cm", "soil_temperature_100_to_255cm",
        "soil_moisture_0_to_7cm", "soil_moisture_7_to_28cm",
        "soil_moisture_28_to_100cm", "soil_moisture_100_to_255cm",
        "boundary_layer_height", "wet_bulb_temperature_2m",
        "total_column_integrated_water_vapour", "is_day", "sunshine_duration",
        "albedo", "snow_depth_water_equivalent", "shortwave_radiation",
        "diffuse_radiation", "global_tilted_irradiance", "shortwave_radiation_instant",
        "diffuse_radiation_instant", "global_tilted_irradiance_instant",
        "direct_radiation", "direct_normal_irradiance", "terrestrial_radiation",
        "direct_radiation_instant", "direct_normal_irradiance_instant",
        "terrestrial_radiation_instant", "temperature_2m_spread",
        "dew_point_2m_spread", "precipitation_spread", "snowfall_spread",
        "shortwave_radiation_spread", "direct_radiation_spread", "pressure_msl_spread",
        "cloud_cover_low_spread", "cloud_cover_mid_spread", "cloud_cover_high_spread",
        "wind_speed_10m_spread", "wind_speed_100m_spread", "wind_direction_10m_spread",
        "wind_direction_100m_spread", "wind_gusts_10m_spread",
        "soil_temperature_0_to_7cm_spread", "soil_temperature_7_to_28cm_spread",
        "soil_temperature_28_to_100cm_spread", "soil_temperature_100_to_255cm_spread",
        "soil_moisture_0_to_7cm_spread", "soil_moisture_7_to_28cm_spread",
        "soil_moisture_28_to_100cm_spread", "soil_moisture_100_to_255cm_spread"
    ],
}

FORECAST_PARAMS: dict[str, Any] = DEFAULT_PARAMS | {
    START_DATE: today.strftime('%Y-%m-%d'),
    END_DATE: today.strftime('%Y-%m-%d'),
    MINUTELY_15: [
        "temperature_2m", "precipitation", "freezing_level_height",
        "wind_speed_80m", "visibility", "shortwave_radiation",
        "global_tilted_irradiance", "diffuse_radiation_instant",
        "relative_humidity_2m", "rain", "sunshine_duration",
        "wind_direction_10m", "cape", "direct_radiation",
        "terrestrial_radiation", "direct_normal_irradiance_instant",
        "dew_point_2m", "snowfall", "weather_code", "wind_direction_80m",
        "lightning_potential", "diffuse_radiation",
        "shortwave_radiation_instant", "global_tilted_irradiance_instant",
        "apparent_temperature", "snowfall_height", "wind_speed_10m",
        "wind_gusts_10m", "is_day", "direct_normal_irradiance",
        "direct_radiation_instant", "terrestrial_radiation_instant"
    ],
    HOURLY: [
        "precipitation_probability", "showers",
        "snow_depth", "pressure_msl",
        "surface_pressure", "cloud_cover", "cloud_cover_low",
        "cloud_cover_mid", "cloud_cover_high",
        "evapotranspiration", "et0_fao_evapotranspiration",
        "vapour_pressure_deficit",
        "wind_speed_120m", "wind_speed_180m",
        "wind_direction_120m", "wind_direction_180m",
        "temperature_80m", "temperature_120m",
        "temperature_180m", "soil_temperature_0cm", "soil_temperature_6cm",
        "soil_temperature_18cm", "soil_temperature_54cm",
        "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm",
        "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm",
        "soil_moisture_27_to_81cm", "uv_index", "uv_index_clear_sky",
        "wet_bulb_temperature_2m",
        "total_column_integrated_water_vapour", "lifted_index",
        "convective_inhibition", "boundary_layer_height"
    ],
}

class OpenmeteoAPI:

    client = None

    def __init__(self) -> None:
        self.__setup()

    def __setup(self) -> None:
        cache_file = '.cache'
        if os.environ.get('AWS_EXECUTION_ENV') is not None:
            cache_file = '/tmp/.cache'

        cache_session = requests_cache.CachedSession(cache_file, expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)


    def forecast(self, params: dict[str, Any]) -> pd.DataFrame:

        params = FORECAST_PARAMS | params

        responses = self.client.weather_api(FORECAST_URL, params=params)
        response = responses[0]

        fifteen_df = self._populate_fifteen_minutely(response, params)
        one_hour_df = self._populate_one_hour(response, params)

        df = pd.DataFrame()
        if params[MINUTELY_15] and params[HOURLY]:
            df = pd.merge(fifteen_df, one_hour_df, on=DATE_TIME_COL, how="left")
        elif params[MINUTELY_15]:
            df = fifteen_df
        elif params[HOURLY]:
            df = one_hour_df
        else:
            return df

        df[DATE_TIME_COL] = df[DATE_TIME_COL] \
            .dt.tz_convert(params['timezone']) \
            .dt.tz_localize(None)

        return df


    def _populate_fifteen_minutely(self, 
            response: WeatherApiResponse,
            params: dict[str, Any]) -> pd.DataFrame:

        if not params[MINUTELY_15]:
            return pd.DataFrame()

        minutely_15 = response.Minutely15()
        fifteen: dict[str, Any] = {
            "date_time": pd.date_range(
                start=pd.to_datetime(minutely_15.Time(), unit="s", utc=True),
                end=pd.to_datetime(minutely_15.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=minutely_15.Interval()),
                inclusive = "right"
        )}

        for i, variable_name in enumerate(params[MINUTELY_15]):
            fifteen[variable_name] = minutely_15.Variables(i).ValuesAsNumpy()

        return pd.DataFrame(fifteen)


    def _populate_one_hour(self,
            response: WeatherApiResponse,
            params: dict[str, Any],
            interpolate=True) -> pd.DataFrame:

        if not params[HOURLY]:
            return pd.DataFrame()

        hourly = response.Hourly()
        one_hour: dict[str, Any] = {
            "date_time": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive = "right"
        )}

        for i, variable_name in enumerate(params[HOURLY]):
            one_hour[variable_name] = hourly.Variables(i).ValuesAsNumpy()

        one_hour_df = pd.DataFrame(one_hour)
        if not interpolate:
            return one_hour_df

        return self._interpolate_1hour_to_15min(one_hour_df)


    def _interpolate_1hour_to_15min(self, one_hour: pd.DataFrame) -> pd.DataFrame:
        one_hour = one_hour.set_index(DATE_TIME_COL)
        fifteen = one_hour.resample('15min').interpolate(method='linear')
        fifteen = fifteen.reset_index()

        return fifteen


    def historical(self, params: dict[str, Any]) -> pd.DataFrame:
        params = ARCHIVE_PARAMS | params

        responses = self.client.weather_api(ARCHIVE_URL, params=params)
        df = self._populate_one_hour(responses[0], params, interpolate=False)

        if params[HOURLY]:
            df[DATE_TIME_COL] = df[DATE_TIME_COL] \
                .dt.tz_convert(params['timezone']) \
                .dt.tz_localize(None)

        return df
