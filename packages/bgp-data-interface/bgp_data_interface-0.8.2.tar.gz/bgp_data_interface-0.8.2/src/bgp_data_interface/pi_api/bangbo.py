from datetime import datetime
import pandas as pd
from bgp_data_interface.pi_api.pi_api import PI_API

BBO_TAG_WEBIDS = './src/bgp_data_interface/pi_api/BBO_tag_webids.csv'

PI_SERVER_PATH = "\\\\TH00P01PVMPIS01\\"

class Bangbo:

    _pi: PI_API
    _tag_webids: pd.DataFrame

    def __init__(self, username: str, password: str) -> None:
        self._pi = PI_API(username, password)
        data: pd.DataFrame = pd.read_csv(BBO_TAG_WEBIDS)
        self._tag_webids = data[['Tags', 'web_ids']]

    def get_summary(self, 
            start_time: datetime,
            end_time: datetime) -> pd.DataFrame:

        params = {
            'timeZone': 'Asia/Bangkok',
            'summaryDuration': '15m',
            'summaryType': 'Average',
            'calculationBasis': 'TimeWeighted'  # or 'EventWeighted'
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
