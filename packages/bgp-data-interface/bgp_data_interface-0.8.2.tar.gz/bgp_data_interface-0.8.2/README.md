# B.Grimm Power Data Interface


This is a python library for accessing internal and public data e.g. PI, AMR, openmeteo, etc.

## Table of Contents

1. [Installation](#installation)
1. [Openmeteo API](#openmeteo-api)
    -  [Forecast data](#forecast-data)
    - [Historical data](#historical-data)
1. [Weather Underground](#weather-underground)
    - [Historical data](#historical-data-1)
1. [Weather API](#weather-api)
    - [Forecast data](#forecast-data-1)
    - [Historical data](#historical-data-2)
1. [TMD API](#tmd-api)
    - [Forecast data](#forecast-data-2)
1. [Fusion Solar](#fusion-solar)
    - [Historical data](#historical-data-3)
1. [PI API](#pi-api)
1. [BGP Weather Data S3 Bucket](#bgp-weather-data-s3-bucket)
1. [Utilities](#utilities)
    - [Location](#location)
    - [Source](#source)



## Installation

```sh
pip install bgp-data-interface
```

or to upgrade

```sh
pip install bgp-data-interface --upgrade
```


## Openmeteo API

### Forecast data

> Openmeteo allows retrieving **15 minute interval** of forecast data for **up to 16 days** \
> and past forecast data **back to around 3 months**.

Calling openmeteo with empty dict will retrieve today's forecast data at Bangbo site with all parameters.

```py
    from bgp_data_interface.openmeteo import Openmeteo

    df = Openmeteo().forecast({})
```

Passing different location parameters will retrieve forecast data at the different site.

```py
    from bgp_data_interface.utils import location

    loc = location.get_location(location.ABP)

    api = Openmeteo()
    df = api.forecast({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    })
```

Passing datetime parameters will specify the forecast data period.

```py
    api = Openmeteo()
    today = pd.Timestamp.now()
    df = api.forecast({
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
    })
```

Passing hourly and minutely_15 parameters will filter the resulting forecast data.

```py
    api = Openmeteo()
    df = api.forecast({
        "hourly": [],
        "minutely_15": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    })
```

### Historical data

> There could be **around 5-day delay** before historical data can be retrieved.


Calling openmeteo with empty dict will retrieve yesterday's historical data at Bangbo site with all parameters.

```py
    from bgp_data_interface.openmeteo import Openmeteo

    df = Openmeteo().historical({})
```

Passing different location parameters will retrieve historical data at the different site.

```py
    from bgp_data_interface.utils import location

    loc = location.get_location(location.ABP)

    api = Openmeteo()
    df = api.historical({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    })
```

Passing datetime parameters will specify the historical data period.

```py
    api = Openmeteo()
    last2days = pd.Timestamp.now() + pd.Timedelta(days=-2)
    df = api.historical({
        "start_date": last2days.strftime("%Y-%m-%d"),
        "end_date": (last2days + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
    })
```

Passing hourly and empty minutely parameters will filter only the selected hourly historical data.

```py
    api = Openmeteo()
    df = api.historical({
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
        "minutely_15": [],
    })
```


Passing empy hourly and minutely parameters will filter only the selected minutely historical data.

```py
    api = Openmeteo()
    df = api.historical({
        "hourly": [],
        "minutely_15": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"],
    })
```




## Weather Underground

To call Weather Underground API, you will need an API key from Weather Underground

### Historical data

Calling Weather Underground with empty dict will retrieve today's historical data at Suvarnabhumi airport.

```py
    from bgp_data_interface.wu import WeatherUndergroundAPI

    api = WeatherUndergroundAPI(API_KEY)
    df = api.historical({})
```


Passing datetime parameters will specify the historical data period.

```py
    api = WeatherUndergroundAPI(API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({
        'start_date': yesterday.strftime('%Y-%m-%d'),
        'end_date': yesterday.strftime('%Y-%m-%d'),
    })
```


Passing `wu_code` parameter will retrieve historical data at the airport.

```py
    from bgp_data_interface.utils import location

    api = WeatherUndergroundAPI(API_KEY)
    loc = location.get_airport(location.CNX)

    df = api.historical({
        'wu_code': loc['weather_underground_code'],
    })
```



## Weather API

To call Weather API, you will need an API key from Weather API.

### Forecast data

> The API allows retrieving **hourly data** of forecast data from today up to **3 days**.

Calling weather API with empty dict will retrieve today's forecast data at Bangbo site.

```py
    from bgp_data_interface.weather_api import WeatherAPI

    api = WeatherAPI(API_KEY)
    df = api.forecast({})
```

Passing `start_date` and `end_date` parameter will specify the forecast data period (up to 3 days).

```py
    api = WeatherAPI(API_KEY)
    today = pd.Timestamp.now()

    df = api.forecast({
        "start_date": today.strftime("%Y-%m-%d"),
        "end_date": (today + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
    })
```

Passing different location parameters will retrieve forecast data at the different site.

```py
    from bgp_data_interface.utils import location

    loc = location.get_location(location.ABP)
    api = WeatherAPI(API_KEY)

    df = api.forecast({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    })
```



### Historical data

> The API allows retrieving **hourly data** of historical data from today back to **7 days**.


Calling weather API with empty dict will retrieve yesterday's historical data at Bangbo site.

```py
    from bgp_data_interface.weather_api import WeatherAPI

    api = WeatherAPI(API_KEY)
    df = api.historical({})
```

Passing datetime parameters will specify the historical data period.

```py
    api = WeatherAPI(API_KEY)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({
        "start_date": yesterday.strftime("%Y-%m-%d"),
        "end_date": yesterday.strftime("%Y-%m-%d"),
    })
```


Passing different location parameters will retrieve historical data at the different site.

```py
    from bgp_data_interface.utils import location

    loc = location.get_location(location.ABP)
    api = WeatherAPI(API_KEY)

    df = api.historical({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    })
```




## TMD API

### Forecast data

> The API allows retrieving **hourly data** of forecast data upto **48 hours**. 


Calling TMD API with empty dict will retrieve today's forecast data at Bangbo site.

```py
    from bgp_data_interface.tmd import TMD

    api = TMD(TOKEN)
    df = api.forecast({})
```


Passing datetime parameters will specify the forecast data period.

```py
    api = TMD(TOKEN)
    today = pd.Timestamp.today()

    df = api.forecast({
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': (today + pd.Timedelta(days=1)).strftime('%Y-%m-%d'),
    })
```


Passing different location parameters will retrieve forecast data at the different site.

```py
    from bgp_data_interface.utils import location

    api = TMD(TOKEN)
    loc = location.get_location(location.CNX)

    df = api.forecast({
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
    })
```




## Fusion Solar

### Historical data

To call Fusion solar API, you will need a fusion solar account.

Calling Fusion solar with empty dict will retrieve yesterday's historical data at Veranda Hua Hin.

```py
    from bgp_data_interface.fusion_solar import FusionSolar

    api = FusionSolar(USERNAME, PASSWORD)
    df = api.historical({})
```


Passing datetime parameters will specify the historical data period.

```py
    api = FusionSolar(USERNAME, PASSWORD)
    last3days = pd.Timestamp.now() + pd.Timedelta(days=-3)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.historical({
        'start_date': last3days.strftime('%Y-%m-%d'),
        'end_date': yesterday.strftime('%Y-%m-%d'),
    })
```


Passing `fs_code` parameter will retrieve historical data at the airport.

```py
    from bgp_data_interface.utils import location

    api = FusionSolar(USERNAME, PASSWORD)
    loc = location.get_airport(location.VHH)

    df = api.historical({
        'fs_code': loc['fusion_solar_code'],
    })
```






## PI API


To retrieve webIDs from PI tags, use `get_webids` with a list of tags.

```py
    from bgp_data_interface.pi import PI

    api = PI(USERNAME, PASSWORD)
    webids = pi.get_webids(SERVER, ['first PI tag', 'second PI tag'])
```

To retrieve a summary data during a time period, use `get_summary` with
1. a dataframe of PI tags and PI webIDs
1. PI parameters dict
1. start timestamp
1. end timestamp

```py
    pi = PI(USERNAME, PASSWORD)

    tag_webids = pd.DataFrame([['a PI tag', 'a PI webID']])
    params = {
        'timeZone': 'Asia/Bangkok',
        'summaryDuration': '15m',
        'summaryType': 'Average',
        'calculationBasis': 'TimeWeighted'
    }

    df = pi.get_summary(tag_webids, params,
            pd.Timestamp('2024-12-01 00:00:00'),
            pd.Timestamp('2024-12-01 01:00:00'))
```


To retrieve only the latest summary data, use `get_latest_summary` with
1. a dataframe of PI tags and PI webIDs
1. PI parameters dict

```py
    pi = PI(USERNAME, PASSWORD)

    tag_webids = pd.DataFrame([['a PI tag', 'a PI webID']])
    params = {
        'timeZone': 'Asia/Bangkok',
        'summaryDuration': '15m',
        'summaryType': 'Average',
        'calculationBasis': 'TimeWeighted'
    }
    df = pi.get_latest_summary(tag_webids, params)
```


To retrieve a summary data from Bangbo site during a time period, use `get_bangbo_summary` with start timestamp and end timestamp.

```py
    pi = PI(USERNAME, PASSWORD)
    df = pi.get_bangbo_summary(pd.Timestamp('2024-12-01 00:00:00'),
                        pd.Timestamp('2024-12-01 01:00:00'))
```


To retrieve only the latest summary data from Bangbo site, use `get_bangbo_latest_summary`.

```py
    pi = PI(USERNAME, PASSWORD)
    df = pi.get_bangbo_latest_summary()
```


To retrieve a summary data from Bothong site during a time period, use `get_bothong_summary` with start timestamp and end timestamp.

```py
    pi = PI(USERNAME, PASSWORD)
    df = pi.get_bothong_summary(pd.Timestamp('2024-12-01 00:00:00'),
                        pd.Timestamp('2024-12-01 01:00:00'))
```


To retrieve only the latest summary data from Bothong site, use `get_bothong_latest_summary`.

```py
    pi = PI(USERNAME, PASSWORD)
    df = pi.get_bothong_latest_summary()
```




## BGP Weather Data S3 Bucket

Weather data from different sources are collected at the company S3 bucket, you can retrieve the data using this s3 API. The access key and secret key can be requested at the admin.

Calling the API with empty dict will retrieve today's forecast data at Bang Bo from openmeteo.

```py
    from bgp_data_interface.s3 import S3

    api = S3(AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME)
    df = api.retrieve({})
```


Type (forecast, historical), source, location and time period can be specified to retrieve the weather data.

```py
    from bgp_data_interface.s3 import S3
    from bgp_data_interface.utils import location, source

    api = S3(AWS_ACCESS_KEY, AWS_SECRET_KEY, BUCKET_NAME)
    yesterday = pd.Timestamp.now() + pd.Timedelta(days=-1)

    df = api.retrieve({
        'type': 'historical',
        'source': source.WEATHER_API,
        'location': location.ABP,
        'start_date': yesterday.strftime('%Y-%m-%d'),
        'end_date': yesterday.strftime('%Y-%m-%d')
    })
```



## Utilities


### Location

Location utilties are used by various weather data APIs to retrieve
weather data at the most frequent locations.

To retrieve the list of locations provided, use `get_location_keys()`

```py
    from bgp_data_interface.utils import location

    keys = location.get_location_keys()
    # ['BBO', 'ABP', 'ABPR', 'BIP', 'BPLC', 'GLB', 'VHH', 'CNX', 'DMK', 'KOP', 'PHS', 'SVB', 'UTP']
```

To retrieve only the list of power plant sites, use `get_site_keys()`

```py
    keys = location.get_site_keys()
    # ['BBO', 'ABP', 'ABPR', 'BIP', 'BPLC', 'GLB', 'VHH']
```

To retrieve only the list of airports, use `get_airport_keys()`

```py
    keys = location.get_airport_keys()
    # ['CNX', 'DMK', 'KOP', 'PHS', 'SVB', 'UTP']
```

You can also use location constants e.g. BBO, ABP, ABPR, etc.

```py
    from bgp_data_interface.utils import location

    location.BBO
    # 'BBO'

    location.ABP
    # 'ABP'
```


To retrieve the information on each location, use `get_location()`

```py
    from bgp_data_interface.utils import location

    loc = location.get_location(location.BBO)
    # {
    #     'name': 'Bang Bo',
    #     'abbreviation': 'BBO',
    #     'latitude': 13.4916354486428,
    #     'longitude': 100.85609829815238
    # }

    location.get_location(location.SVB)
    # {
    #     'name': 'Suvarnabhumi Airport',
    #     'abbreviation': 'SVB',
    #     'latitude': 13.683402925860605,
    #     'longitude': 100.74685929073979,
    #     'weather_underground_code': 'VTBS:9:TH'
    # }
```


To retrieve only the latitude and longitude of the location, use `get_latlong()`

```py
    from bgp_data_interface.utils import location

    loc = location.get_latlong(location.BBO)
    # {
    #     'latitude': 13.4916354486428,
    #     'longitude': 100.85609829815238
    # }
```



### Source

To retrieve the list of sources provided, use `get_sources()`

```py
    from bgp_data_interface.utils import source

    sources = source.get_sources()
    # ['fusion_solar', 'weather_api', 'openmeteo', 'weather_underground', 'tmd']
```



To retrieve only the list of sources with historical data, use `get_historical_sources()`

```py
    from bgp_data_interface.utils import source

    sources = source.get_historical_sources()
    # ['fusion_solar', 'openmeteo', 'weather_api', 'weather_underground']
```



To retrieve only the list of sources with forecast data, use `get_forecast_sources()`

```py
    from bgp_data_interface.utils import source

    sources = source.get_forecast_sources()
    # ['openmeteo', 'weather_api', 'tmd']
```



You can also use source constants e.g. OPENMETEO, TMD, etc.

```py
    from bgp_data_interface.utils import source

    location.OPENMETEO
    # 'openmeteo'

    location.TMD
    # 'tmd'
```



