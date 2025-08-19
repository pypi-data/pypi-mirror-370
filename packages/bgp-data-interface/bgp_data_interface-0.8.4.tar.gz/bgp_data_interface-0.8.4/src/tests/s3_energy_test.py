import credentials

from sys import path
path.append('./src/bgp_data_interface')
from s3_energy import S3Energy


from pathlib import Path
import pandas as pd

BUCKET_NAME = 'bgp-energy-data'


def test_init_s3() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )

    assert api is not None
    assert isinstance(api, S3Energy)


def test_s3_retrieve_csv() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )
    df = api.retrieve_csv()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 19)
    assert df.iloc[0, 0] == '2025-01-15 00:00:00'
    assert df.iloc[-1, 0] == '2025-01-15 23:45:00'


def test_s3_retrieve_excel() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )


    df = api.retrieve_excel()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ['date_time', 'data']
    assert df.iloc[0, 1] == 'hello'
    assert df.iloc[1, 1] == 'world'


def test_s3_store_csv() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )

    df = pd.read_csv("src/tests/dummy.csv")

    key = "/".join(["AWS", "DUMMY", "solar", "collected", "dummy2.csv"])
    api.store_csv(df, key)



def test_s3_download() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )

    key = "/".join(["AWS", "DUMMY", "solar", "collected", "dummy.csv"])
    api.download(key, "dummy.csv")

    filepath = Path("dummy.csv")
    assert filepath.exists()

    filepath.unlink(missing_ok=True)



def test_s3_upload() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )

    key = "/".join(["AWS", "DUMMY", "solar", "collected", "dummy2.csv"])
    api.upload(key, "src/tests/dummy.csv")


