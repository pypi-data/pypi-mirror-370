from datetime import datetime
import pandas as pd
from bgp_data_interface.pi_api.pi_api import PI_API

BTW_TAG_WEBIDS = './src/bgp_data_interface/pi_api/BTW_tag_webids.csv'

PI_SERVER_PATH = "\\\\TH00P01PVMPIS01\\"

PI_TAG = "W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL1_29"
WEB_ID = "F1DPPy8YwSxNYU-f1KfNW4G4PwZqsAAAVEgwMFAwMVBWTVBJUzAxXFctVEgtQlRXLU1JQ1JPU0NBREEuRDEuQVBMXzFfUF9XVEdfVE9UQUwxXzI5"

class Bothong:

    _pi: PI_API
    _tag_webids: pd.DataFrame

    def __init__(self, username: str, password: str) -> None:
        self._pi = PI_API(username, password)
        data: pd.DataFrame = pd.read_csv(BTW_TAG_WEBIDS)
        self._tag_webids = data[['Tags', 'web_ids']]

    def get_summary(self, 
            start_time: datetime,
            end_time: datetime) -> pd.DataFrame:

        params = {
            'timeZone': 'Asia/Bangkok',
            'summaryDuration': '15m',
            'summaryType': 'Average',
            'calculationBasis': 'TimeWeighted'  # or 'EventWeighted' depending on your needs
        }

        return self._pi.get_summary(
            self._tag_webids,
            params,
            start_time,
            end_time)

    def get_latest_summary(self) -> pd.DataFrame:

        params = {
            'timeZone': 'Asia/Bangkok',
        }

        return self._pi.get_latest_summary(
            self._tag_webids,
            params
        )
