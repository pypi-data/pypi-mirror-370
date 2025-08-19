from bgp_data_interface.utils import location
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from mypy_boto3_s3.service_resource import Bucket
import os
import pandas as pd


OUTPUT_DIR = 'outputs'
DEFAULT_SITE = location.BBO
DEFAULT_SOURCE = 'openmeteo'
DEFAULT_TYPE = 'forecast'


class S3Weather:

    bucket: Bucket


    def __init__(self, access_key: str, secret_key: str, bucket_name: str) -> None:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        s3 = session.resource('s3')
        self.bucket = s3.Bucket(bucket_name)



    def retrieve(self, params: dict) -> pd.DataFrame:
        site = params.get('location', DEFAULT_SITE)
        type = params.get('type', DEFAULT_TYPE)
        source = params.get('source', DEFAULT_SOURCE)

        today = pd.Timestamp.now().strftime("%Y-%m-%d")
        start_date = datetime.strptime(params.get('start_date', today), "%Y-%m-%d")
        end_date = datetime.strptime(params.get('end_date', today), "%Y-%m-%d")

        self._download_files(site, type, start_date, end_date, source)
        df = self._combine_files(site, type, start_date, end_date, source)
    
        return df



    def _download_files(self,
            location: str,
            type: str,
            start_date: datetime,
            end_date: datetime,
            source: str) -> None:
        
        for date in pd.date_range(start_date, end_date):
            folder = f"{location}/{type}/{date.year}/"
            filename = date.strftime("%Y%m%d") + f"_{source}.csv"

            os.makedirs(os.path.dirname(f"{OUTPUT_DIR}/{folder}"), exist_ok=True)
            s3_file_key = folder + filename
            local_file_path = f"{OUTPUT_DIR}/{s3_file_key}"

            if not os.path.exists(local_file_path):
                self._download_one_file(s3_file_key, local_file_path)


    def _download_one_file(self, s3_key: str, file_path: str) -> None:
        try:
            self.bucket.download_file(s3_key, file_path)
        except ClientError as ce:
            status_code = ce.response['Error']['Code']
            print(status_code, end=' ', flush=True)

    def _combine_files(self,
            location: str,
            type: str,
            start_date: datetime,
            end_date: datetime,
            source: str) -> pd.DataFrame:

        file_list = []
        for date in pd.date_range(start_date, end_date):
            folder = f"{OUTPUT_DIR}/{location}/{type}/{date.year}/"
            filename = date.strftime("%Y%m%d") + f"_{source}.csv"

            file_path = folder + filename
            if not os.path.exists(file_path):
                continue

            file_list.append(file_path)

        if not file_list:
            return pd.DataFrame()

        df = pd.concat([pd.read_csv(file) for file in file_list], ignore_index=True)
        df['date_time'] = pd.to_datetime(df['date_time'])

        return df
