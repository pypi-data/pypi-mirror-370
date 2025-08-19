import credentials

from sys import path
path.append('./src')
from bgp_data_interface.pi import PI


import pandas as pd

SERVER = "\\\\TH00P01PVMPIS01\\"

TAP_TAG = 'S-TH-BBO-Modbus.CtrlRoom.PQM.TotalActivePower'
TAP_WEBID = 'F1DPPy8YwSxNYU-f1KfNW4G4PwInMAAAVEgwMFAwMVBWTVBJUzAxXFMtVEgtQkJPLU1PREJVUy5DVFJMUk9PTS5QUU0uVE9UQUxBQ1RJVkVQT1dFUg'

BANGBO_COLUMNS = [
    'Date_time',
    'S-TH-BBO-Modbus.CtrlRoom.PQM.TotalActivePower',
    'S-TH-BBO-Modbus.Sub1.WT.Irradiation1',
    'S-TH-BBO-Modbus.Sub1.WT.Irradiation2',
    'S-TH-BBO-Modbus.Sub1.WT.PVTemp1',
    'S-TH-BBO-Modbus.Sub1.WT.PVTemp2',
    'S-TH-BBO-Modbus.Sub1.WT.AmbTemp',
    'S-TH-BBO-Modbus.Sub1.WT.AmbHumidity',
    'S-TH-BBO-Modbus.CtrlRoom.PQM.Energy',
    'S-TH-BBO-Modbus.CtrlRoom.RMUIn.DCSwitchOpen',
    'S-TH-BBO-Modbus.CtrlRoom.RMUOut1.CBSwithOpen',
    'S-TH-BBO-Modbus.CtrlRoom.RMUOut2.CBSwithOpen',
    'S-TH-BBO-Modbus.CtrlRoom.SWG.Open'
]

BOTHONG_COLUMNS = [
    'Date_time',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL1_27',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL1_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL1_29',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL2_27',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL2_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG_TOTAL2_29',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG01_WIND1_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG01_WIND1_27',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG02_WIND1_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG02_WIND1_27',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG03_WIND1_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG03_WIND1_27',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG04_WIND1_28',
    'W-TH-BTW-MicroSCADA.D1.APL_1_P_WTG04_WIND1_27'
]

def test_init_pi() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)

    assert pi is not None

def test_get_webids() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)
    webids = pi.get_webids(SERVER, [TAP_TAG])

    assert webids[0] == TAP_WEBID

def test_get_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)

    tag_webids = pd.DataFrame([[TAP_TAG, TAP_WEBID]])
    params = {
        'timeZone': 'Asia/Bangkok',
        'summaryDuration': '15m',
        'summaryType': 'Average',
        'calculationBasis': 'TimeWeighted'
    }

    df = pi.get_summary(tag_webids, params,
                        pd.Timestamp('2024-12-01 00:00:00'),
                        pd.Timestamp('2024-12-01 01:00:00'))
    
    assert df.columns[0] == 'Date_time'
    assert df.columns[1] == TAP_TAG
    assert df.shape == (4, 2)
    assert df.iloc[0].tolist() == [
        pd.Timestamp('2024-12-01 00:15:00'), 3.8531049918617963
    ]

def test_get_latest_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)

    tag_webids = pd.DataFrame([[TAP_TAG, TAP_WEBID]])
    params = {
        'timeZone': 'Asia/Bangkok',
        'summaryDuration': '15m',
        'summaryType': 'Average',
        'calculationBasis': 'TimeWeighted'
    }
    df = pi.get_latest_summary(tag_webids, params)

    assert df.columns[0] == 'Date_time'
    assert df.columns[1] == TAP_TAG
    assert df.shape == (1, 2)




def test_get_bangbo_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)
    df = pi.get_bangbo_summary(pd.Timestamp('2024-12-01 00:00:00'),
                        pd.Timestamp('2024-12-01 01:00:00'))

    assert df.columns.tolist() == BANGBO_COLUMNS
    assert df.shape == (4, 13)
    assert df.iloc[0].tolist() == [
        pd.Timestamp('2024-12-01 00:15:00'), 3.8531049918617963, 0.5048876354695443,
        0.5048675484845891, 22.04288178809408, 22.048673877546886, 24.434623953620854,
        0.0720359436108789, 47942616.082660735, 0.0, 0.0, 0.0, 0.0
    ]

def test_get_bangbo_latest_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)
    df = pi.get_bangbo_latest_summary()

    assert df.columns.tolist() == BANGBO_COLUMNS
    assert df.shape == (1, 13)




def test_get_bothong_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)
    df = pi.get_bothong_summary(pd.Timestamp('2024-12-01 00:00:00'),
                        pd.Timestamp('2024-12-01 01:00:00'))

    assert df.columns.tolist() == BOTHONG_COLUMNS
    assert df.shape == (4, 15)
    assert df.iloc[0].tolist() == [
        pd.Timestamp('2024-12-01 00:15:00'), 
        8.406077625078208, None, 5357.2364775029,
        None, None, 4908.637376983261,
        6.017494424635026, None,
        4.565993587426732, None,
        0.9591043161092966, None,
        -0.4782757449044889, None
    ]

def test_get_bothong_latest_summary() -> None:
    pi = PI(credentials.PI_USERNAME, credentials.PI_PASSWORD)
    df = pi.get_bothong_latest_summary()

    assert df.columns.tolist() == BOTHONG_COLUMNS
    assert df.shape == (1, 15)
