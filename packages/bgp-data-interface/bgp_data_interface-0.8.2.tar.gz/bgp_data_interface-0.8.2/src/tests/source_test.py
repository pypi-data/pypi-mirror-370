from sys import path
path.append('./src/bgp_data_interface')
from utils import source



def test_get_sources() -> None:
    sources = source.get_sources()
    # ['fusion_solar', 'weather_api', 'openmeteo', 'weather_underground', 'tmd']

    assert isinstance(sources, list)
    assert len(sources) == 5
    assert source.FUSION_SOLAR in sources
    assert source.OPENMETEO in sources
    assert source.TMD in sources
    assert source.WEATHER_UNDERGROUND in sources
    assert source.WEATHER_API in sources



def test_get_historical_sources() -> None:
    sources = source.get_historical_sources()
    # ['fusion_solar', 'openmeteo', 'weather_api', 'weather_underground']

    assert isinstance(sources, list)
    assert len(sources) == 4
    assert source.FUSION_SOLAR in sources
    assert source.OPENMETEO in sources
    assert source.WEATHER_UNDERGROUND in sources
    assert source.WEATHER_API in sources



def test_get_forecast_sources() -> None:
    sources = source.get_forecast_sources()
    # ['openmeteo', 'weather_api', 'tmd']

    assert isinstance(sources, list)
    assert len(sources) == 3
    assert source.OPENMETEO in sources
    assert source.WEATHER_API in sources
    assert source.FUSION_SOLAR not in sources

