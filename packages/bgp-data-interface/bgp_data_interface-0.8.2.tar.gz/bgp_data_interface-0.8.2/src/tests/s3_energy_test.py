import credentials

from sys import path
path.append('./src/bgp_data_interface')
from s3_energy import S3Energy
from utils import location


import pandas as pd


def test_init_s3() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        'bgp-energy-data'
    )

    assert api is not None
    assert isinstance(api, S3Energy)


def test_s3_download() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        'bgp-energy-data'
    )
    df = api.download()

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.shape == (96, 19)
    assert df.iloc[0, 0] == '2025-01-15 00:00:00'
    assert df.iloc[-1, 0] == '2025-01-15 23:45:00'


def test_s3_upload() -> None:
    api = S3Energy(
        credentials.ENERGY_AWS_ACCESS_KEY,
        credentials.ENERGY_AWS_SECRET_KEY,
        'bgp-energy-data'
    )
    df = pd.read_csv("src/tests/dummy.csv")
    df.info()
    print(df)
    
    api.upload(df, file="dummy2.csv")


