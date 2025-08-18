import boto3
from io import StringIO
from mypy_boto3_s3.service_resource import Bucket
import pandas as pd

DEFAULT_BUCKET_NAME = 'bgp-energy-data'
DEFAULT_CLOUD = 'AWS'
DEFAULT_SITE = 'DUMMY'
DEFAULT_FORECAST = 'solar'
DEFAULT_STATE = 'collected'
DEFAULT_FILE = 'dummy.csv'

class S3Energy:

    bucket: Bucket


    def __init__(self,
            access_key: str,
            secret_key: str,
            bucket_name: str) -> None:

        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        s3 = session.resource('s3')
        self.bucket = s3.Bucket(bucket_name)



    def download(self,
            cloud: str,
            site: str,
            forecast: str,
            state: str,
            file: str,
            ) -> pd.DataFrame:

        key = f"{cloud}/{site}/{forecast}/{state}/{file}"
        obj = self.bucket.Object(key)
        body = obj.get()["Body"]
        csv = body.read().decode('utf-8')

        return pd.read_csv(StringIO(csv), index_col=False)



    def upload(self,
            df: pd.DataFrame,
            cloud: str,
            site: str,
            forecast: str,
            state: str,
            file: str
            ) -> None:

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)

        key = f"{cloud}/{site}/{forecast}/{state}/{file}"
        self.bucket.put_object(
            Key=key,
            Body=csv_buffer.getvalue(),
            ContentType='application/csv')
