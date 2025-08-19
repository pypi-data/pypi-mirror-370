import credentials

from sys import path
path.append('./src/bgp_data_interface')
from s3_energy import S3Energy


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


    df = api.retrieve_excel(file="dummy.xlsx")

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (2, 2)
    assert list(df.columns) == ['date_time', 'data']


def test_s3_store_csv() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        BUCKET_NAME
    )

    df = pd.read_csv("src/tests/dummy.csv")

    api.store_csv(df, file="dummy2.csv")


