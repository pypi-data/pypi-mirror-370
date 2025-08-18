from datetime import datetime, timedelta
import pandas as pd
import requests

RANGE_URL =    "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly"
HOURLY_URL = "https://data.tmd.go.th/nwpapi/v1/forecast/location/hourly/at"

DEFAULT_HOURLY_PARAMS = {
    "lat":"13.10",
    "lon":"100.10",
    "fields":"tc,rh,slp,rain,ws10m,wd10m,cloudlow,cloudmed,cloudhigh,cond",
    "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
    "hour":"0",
    "duration":"24"
}


FIELDS = {
    'tc': 'temperature_c',
    'rh': 'relative_humidity_%',
    'slp': 'sea_level_pressure_hpa',
    'rain': 'rain_mm',
    'ws10m': 'wind_speed_10m_mps',
    'wd10m': 'wind_direction_10m_degree',
    'cloudlow': 'cloud_low_%',
    'cloudmed': 'cloud_medium_%',
    'cloudhigh': 'cloud_high_%',
    'cond': 'weather_condition'
}

# hourly variables
# https://data.tmd.go.th/nwpapi/doc/apidoc/forecast_location.html

CONDITIONS = [
    (1, 'ท้องฟ้าแจ่มใส', 'Clear'),
    (2, 'มีเมฆบางส่วน', 'Partly cloudy'),
    (3, 'เมฆเป็นส่วนมาก', 'Cloudy'),
    (4, 'มีเมฆมาก', 'Overcast'),
    (5, 'ฝนตกเล็กน้อย', 'Light rain'),
    (6, 'ฝนปานกลาง', 'Moderate rain'),
    (7, 'ฝนตกหนัก', 'Heavy rain'),
    (8, 'ฝนฟ้าคะนอง', 'Thunderstorm'),
    (9, 'อากาศหนาวจัด', 'Very cold'),
    (10, 'อากาศหนาว', 'Cold'),
    (11, 'อากาศเย็น', 'Cool'),
    (12, 'อากาศร้อนจัด', 'Very hot'),
]

class TMD_API:

    def __init__(self, token: str) -> None:
        self.headers = {
            'accept': "application/json",
            'authorization': f"Bearer {token}"
        }


    def range(self) -> dict:
        response = requests.request("GET", 
            RANGE_URL,
            headers=self.headers,
        )

        if response.status_code != 200:
            print(f"Failed to retrieve hourly forecast. ({response.status_code})")

        return response.json()['hourly_data']


    def forecast(self, params: dict) -> pd.DataFrame:
        new_params = {}

        if 'latitude' in params and 'longitude' in params:
            new_params['lat'] = params['latitude']
            new_params['lon'] = params['longitude']

        if 'fields' in params:
            new_params['fields'] = params['fields']

        if 'start_date' in params and 'end_date' in params:
            start_date = pd.to_datetime(params['start_date'])
            end_date = pd.to_datetime(params['end_date'])
            duration = ((end_date - start_date).days + 1) * 24
            new_params['date'] = start_date.strftime('%Y-%m-%d')
            new_params['hour'] = start_date.hour
            new_params['duration'] = min(48, duration)
        else:
            today = datetime.today()
            new_params['date'] = today.strftime('%Y-%m-%d')
            new_params['hour'] = 0
            new_params['duration'] = 24

        return self._hourly_forecast(new_params)


    def _hourly_forecast(self, params: dict) -> pd.DataFrame:
        all_params = DEFAULT_HOURLY_PARAMS | params

        response = requests.request("GET", 
            HOURLY_URL,
            headers=self.headers,
            params= all_params,
        )

        if response.status_code != 200:
            print(f"Failed to retrieve hourly forecast. ({response.status_code})")

        data = response.json()['WeatherForecasts'][0]
        formatted = [[o['time']] + 
                [o['data'][key.strip()] for key in all_params['fields'].split(',')]
            for o in data['forecasts']
        ]

        columns = ['date_time'] + [FIELDS[key] for key in all_params['fields'].split(',')]

        df = pd.DataFrame(data=formatted, columns=columns)
        df['date_time'] = pd.to_datetime(df['date_time'])

        return df
