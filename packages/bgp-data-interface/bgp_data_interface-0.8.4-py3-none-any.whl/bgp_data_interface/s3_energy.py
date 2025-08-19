import sys
if "pytest" in sys.modules:
    from s3_bucket.S3Energy import S3Energy as S3EnergyAPI, \
            DEFAULT_CLOUD, DEFAULT_FORECAST, DEFAULT_SITE, DEFAULT_STATE, \
            DEFAULT_FILE, DEFAULT_BUCKET_NAME
else:
    from bgp_data_interface.s3_bucket.S3Energy import S3Energy as S3EnergyAPI, \
            DEFAULT_CLOUD, DEFAULT_FORECAST, DEFAULT_SITE, DEFAULT_STATE, \
            DEFAULT_FILE, DEFAULT_BUCKET_NAME

import pandas as pd


DEFAULT_KEY = "/".join([DEFAULT_CLOUD, DEFAULT_SITE, DEFAULT_FORECAST, DEFAULT_STATE, DEFAULT_FILE])
DEFAULT_EXCEL_KEY = "/".join([DEFAULT_CLOUD, DEFAULT_SITE, DEFAULT_FORECAST, DEFAULT_STATE, "dummy.xlsx"])

class S3Energy:

    _s3eapi: S3EnergyAPI

    def __init__(self,
            access_key: str,
            secret_key: str,
            bucket=DEFAULT_BUCKET_NAME) -> None:

        self._s3eapi = S3EnergyAPI(access_key, secret_key, bucket)



    def retrieve_csv(self, key=DEFAULT_KEY) -> pd.DataFrame:
        
        return self._s3eapi.retrieve_csv(key)
    


    def retrieve_excel(self, key=DEFAULT_EXCEL_KEY) -> pd.DataFrame:
        
        return self._s3eapi.retrieve_excel(key)



    def store_csv(self, df: pd.DataFrame, key: str) -> None:
        
        self._s3eapi.store_csv(df, key)



    def download(self, key: str, destination: str) -> None:

        self._s3eapi.download(key, destination)



    def upload(self, key: str, source: str) -> None:

        self._s3eapi.upload(key, source)
