import sys
if "pytest" in sys.modules:
    from fusion_solar_api.FusionSolarAPI import FusionSolarAPI
else:
    from bgp_data_interface.fusion_solar_api.FusionSolarAPI import FusionSolarAPI

import pandas as pd
from typing import Dict, Any

class FusionSolar:

    _fs: FusionSolarAPI

    def __init__(self, username: str, password: str) -> None:
        self._fs = FusionSolarAPI(username, password)

    # def forecast(self, params: Dict[str, Any]) -> pd.DataFrame:
    #     return self._wu.forecast(params)

    def historical(self, params: Dict[str, Any]={}) -> pd.DataFrame:
        return self._fs.historical(params)
