import sys
if "pytest" in sys.modules:
    from tmd_api.TMD_API import TMD_API
else:
    from bgp_data_interface.tmd_api.TMD_API import TMD_API

import pandas as pd
from typing import Dict, Any

class TMD:

    _tmd_api: TMD_API

    def __init__(self, token: str) -> None:
        self._tmd_api = TMD_API(token)

    def forecast(self, params: Dict[str, Any]={}) -> pd.DataFrame:
        return self._tmd_api.forecast(params)

    # def historical(self, params: Dict[str, Any]) -> pd.DataFrame:
    #     return self._tmd_api.historical(params)
