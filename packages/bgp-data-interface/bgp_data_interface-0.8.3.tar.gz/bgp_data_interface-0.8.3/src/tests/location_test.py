from sys import path
path.append('./src/bgp_data_interface')
from utils import location



def test_get_location_keys() -> None:
    keys = location.get_location_keys()
    # ['BBO', 'ABP', 'ABPR', 'BIP', 'BPLC', 'GLB', 'VHH', 'CNX', 'DMK', 'KOP', 'PHS', 'SVB', 'UTP']

    assert isinstance(keys, list)
    assert len(keys) == 13
    assert "BBO" in keys
    assert "ABP" in keys
    assert "ABPR" in keys
    assert "BIP" in keys
    assert "BPLC" in keys
    assert "GLB" in keys
    assert "VHH" in keys
    assert "CNX" in keys
    assert "DMK" in keys
    assert "KOP" in keys
    assert "PHS" in keys
    assert "SVB" in keys
    assert "UTP" in keys


def test_get_site_keys() -> None:
    keys = location.get_site_keys()
    # ['BBO', 'ABP', 'ABPR', 'BIP', 'BPLC', 'GLB', 'VHH']

    assert isinstance(keys, list)
    assert len(keys) == 7
    assert "BBO" in keys
    assert "ABP" in keys
    assert "ABPR" in keys
    assert "BIP" in keys
    assert "BPLC" in keys
    assert "GLB" in keys
    assert "VHH" in keys


def test_get_airport_keys() -> None:
    keys = location.get_airport_keys()
    # ['CNX', 'DMK', 'KOP', 'PHS', 'SVB', 'UTP']

    assert isinstance(keys, list)
    assert len(keys) == 6
    assert "CNX" in keys
    assert "DMK" in keys
    assert "KOP" in keys
    assert "PHS" in keys
    assert "SVB" in keys
    assert "UTP" in keys


def test_get_location() -> None:
    location_data = location.get_location(location.BBO)

    assert location_data is not None
    assert location_data["name"] == "Bang Bo"
    assert location_data["abbreviation"] == location.BBO
    assert location_data["latitude"] == 13.4916354486428
    assert location_data["longitude"] == 100.85609829815238
