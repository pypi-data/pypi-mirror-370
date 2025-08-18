import sys
if "pytest" in sys.modules:
    from s3_bucket.S3Weather import S3Weather as S3WeatherAPI
else:
    from bgp_data_interface.s3_bucket.S3Weather import S3Weather as S3WeatherAPI

import pandas as pd
from typing import Dict, Any

class S3Weather:

    _s3wapi: S3WeatherAPI

    def __init__(self,
            access_key: str,
            secret_key: str,
            bucket: str) -> None:

        self._s3wapi = S3WeatherAPI(access_key, secret_key, bucket)



    def retrieve(self,
            params: Dict[str, Any]={}) -> pd.DataFrame:

        return self._s3wapi.retrieve(params)
