FUSION_SOLAR = 'fusion_solar'
OPENMETEO = 'openmeteo'
TMD = 'tmd'
WEATHER_UNDERGROUND = 'weather_underground'
WEATHER_API = 'weather_api'

_historical_sources = [
    FUSION_SOLAR,
    OPENMETEO,
    WEATHER_API,
    WEATHER_UNDERGROUND,
]

_forecast_sources = [
    OPENMETEO,
    WEATHER_API,
    TMD,
]

def get_sources() -> list[str]:
    return list(set(_historical_sources + _forecast_sources))

def get_historical_sources() -> list[str]:
    return _historical_sources

def get_forecast_sources() -> list[str]:
    return _forecast_sources
