import sys
if "pytest" in sys.modules:
    from pi_api.bangbo import Bangbo
    from pi_api.bothong import Bothong
    from pi_api.pi_api import PI_API
else:
    from bgp_data_interface.pi_api.bangbo import Bangbo
    from bgp_data_interface.pi_api.bothong import Bothong
    from bgp_data_interface.pi_api.pi_api import PI_API

from datetime import datetime
import pandas as pd
from typing import List, Dict, Any

class PI:

    _pi_api: PI_API
    _bangbo: Bangbo
    _bothong: Bothong

    def __init__(self,
                 username: str,
                 password: str) -> None:

        self._pi_api = PI_API(username, password)
        self._bangbo = Bangbo(username, password)
        self._bothong = Bothong(username, password)

    def get_webids(self,
                   server: str,
                   tag_list: List[str]) -> List[str]:

        return self._pi_api.get_webids(server, tag_list)

    def get_summary(self,
                    tag_webids: pd.DataFrame,
                    params: Dict[str, Any],
                    start_time: datetime,
                    end_time: datetime) -> pd.DataFrame:

        return self._pi_api.get_summary(tag_webids, params, start_time, end_time)
    
    def get_latest_summary(self,
                            tag_webids: pd.DataFrame,
                            params: Dict[str, Any]) -> pd.DataFrame:

        return self._pi_api.get_latest_summary(tag_webids, params)



    def get_bangbo_summary(self,
                    start_time: datetime,
                    end_time: datetime) -> pd.DataFrame:

        return self._bangbo.get_summary(start_time, end_time)

    def get_bangbo_latest_summary(self) -> pd.DataFrame:

        return self._bangbo.get_latest_summary()



    def get_bothong_summary(self,
                    start_time: datetime,
                    end_time: datetime) -> pd.DataFrame:

        return self._bothong.get_summary(start_time, end_time)

    def get_bothong_latest_summary(self) -> pd.DataFrame:

        return self._bothong.get_latest_summary()
