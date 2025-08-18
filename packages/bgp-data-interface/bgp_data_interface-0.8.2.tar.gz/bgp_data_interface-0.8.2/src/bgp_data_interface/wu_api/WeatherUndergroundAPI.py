from datetime import datetime
import pandas as pd
import pytz
import requests
from typing import Any


API_URL = 'http://api.weather.com/v1/location/{:s}/observations/historical.json?apiKey={:s}&units=e&startDate={:s}&endDate={:s}'

BKK_TZ = pytz.timezone('Asia/Bangkok')

# Suvarnabhumi Airport, Bangkok, Thailand
DEFAULT_WU_CODE = 'VTBS:9:TH'  

class WeatherUndergroundAPI:

    api_key: str

    def __init__(self, api_key: str) -> None:

        self.api_key = api_key


    def historical(self, params: dict[str, Any], ) -> pd.DataFrame:

        wu_code = DEFAULT_WU_CODE
        if 'wu_code' in params:
            wu_code = params['wu_code']
        
        start = pd.Timestamp.now(tz=BKK_TZ).strftime("%Y%m%d")
        if 'start_date' in params:
            sdate = datetime.strptime(params['start_date'], "%Y-%m-%d")
            start = sdate.strftime("%Y%m%d")

        end = pd.Timestamp.now(tz=BKK_TZ).strftime("%Y%m%d")
        if 'end_date' in params:
            edate = datetime.strptime(params['end_date'], "%Y-%m-%d")
            end = edate.strftime("%Y%m%d")

        url = API_URL.format(wu_code, self.api_key, start, end)

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Unable to fetch data (Status code: {response.status_code})")
            return pd.DataFrame()

        data = response.json()
        df = pd.DataFrame(data['observations'])
        df = df.drop([
            'key', 'class', 'expire_time_gmt', 'obs_id', 'obs_name',
            'wx_icon', 'icon_extd', 
        ], axis=1)
        df = df.rename(columns={
            'valid_time_gmt': 'date_time',
            'wx_phrase': 'weather_condition',
        })
        df['date_time'] = pd.to_datetime(df['date_time'], unit='s', utc=True)
        df['date_time'] = df['date_time'].dt.tz_convert(BKK_TZ)

        return df
