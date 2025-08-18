import sys
if "pytest" in sys.modules:
    from weather_api_api.WeatherAPI import WeatherAPI as WAPI
else:
    from bgp_data_interface.weather_api_api.WeatherAPI import WeatherAPI as WAPI

import pandas as pd
from typing import Dict, Any

class WeatherAPI:

    _wapi: WAPI

    def __init__(self, api_key: str) -> None:
        self._wapi = WAPI(api_key)

    def forecast(self, params: Dict[str, Any]={}) -> pd.DataFrame:
        return self._wapi.forecast(params)

    def historical(self, params: Dict[str, Any]={}) -> pd.DataFrame:
        return self._wapi.historical(params)
