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

class S3Energy:

    _s3eapi: S3EnergyAPI

    def __init__(self,
            access_key: str,
            secret_key: str,
            bucket=DEFAULT_BUCKET_NAME) -> None:

        self._s3eapi = S3EnergyAPI(access_key, secret_key, bucket)



    def retrieve_csv(self,
            cloud=DEFAULT_CLOUD,
            site=DEFAULT_SITE,
            forecast=DEFAULT_FORECAST,
            state=DEFAULT_STATE,
            file=DEFAULT_FILE
            ) -> pd.DataFrame:
        
        return self._s3eapi.retrieve_csv(cloud, site, forecast, state, file)
    


    def retrieve_excel(self,
            cloud=DEFAULT_CLOUD,
            site=DEFAULT_SITE,
            forecast=DEFAULT_FORECAST,
            state=DEFAULT_STATE,
            file=DEFAULT_FILE
            ) -> pd.DataFrame:
        
        return self._s3eapi.retrieve_excel(cloud, site, forecast, state, file)



    def store_csv(self,
            df: pd.DataFrame,
            cloud=DEFAULT_CLOUD,
            site=DEFAULT_SITE,
            forecast=DEFAULT_FORECAST,
            state=DEFAULT_STATE,
            file=DEFAULT_FILE
            ) -> None:
        
        self._s3eapi.store_csv(df, cloud, site, forecast, state, file)
