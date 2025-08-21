# Frequenz Weather API Client

[![Build Status](https://github.com/frequenz-floss/frequenz-client-weather-python/actions/workflows/ci.yaml/badge.svg)](https://github.com/frequenz-floss/frequenz-client-weather-python/actions/workflows/ci.yaml)
[![PyPI Package](https://img.shields.io/pypi/v/frequenz-client-weather)](https://pypi.org/project/frequenz-client-weather/)
[![Docs](https://img.shields.io/badge/docs-latest-informational)](https://frequenz-floss.github.io/frequenz-client-weather-python/)

## Introduction

Weather API Client for Python providing access to historical and live weather forecast data.

## Supported Platforms

The following platforms are officially supported (tested):

- **Python:** 3.11
- **Operating System:** Ubuntu Linux 20.04
- **Architectures:** amd64, arm64

## Contributing

If you want to know how to build this project and contribute to it, please
check out the [Contributing Guide](CONTRIBUTING.md).

## Usage

### Installation

```bash
pip install frequenz-client-weather
```

### Available Features

The available features are listed [here](https://github.com/frequenz-floss/frequenz-api-weather/blob/v0.x.x/proto/frequenz/api/weather/weather.proto#L42).

### Initialize the client

The Client can optionally be initialized with keep alive.

```python
from frequenz.client.weather import Client
from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions
from datetime import timedelta

client = Client(
    service_address,
    channel_defaults=ChannelOptions(
        ssl=SslOptions(
            enabled=False,
        ),
        keep_alive=KeepAliveOptions(
            enabled=True,
            timeout=timedelta(minutes=5),
            interval=timedelta(seconds=20),
        ),
    ),
)
```

### Get historical weather forecast

```python
from datetime import datetime
import pandas as pd
from frequenz.client.weather._types import ForecastFeature, Location

# Define a list of locations, features and a time range to request historical forecasts for
locations = [Location(latitude=46.2276, longitude=15.2137, country_code="DE")]
features = [ForecastFeature.TEMPERATURE_2_METRE, ForecastFeature.V_WIND_COMPONENT_10_METRE]
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)

forecast_iterator = await client.stream_historical_forecast(
    features=features, locations=locations, start=start, end=end
)

# Collect and flatten forecasts
flat_forecasts = [f.flatten() async for f in forecast_iterator]
forecast_records = [record for batch in flat_forecasts for record in batch]

# E.g. convert to DataFrame and sort
forecast_df = pd.DataFrame(forecast_records).sort_values(["create_time", "valid_time", "latitude", "longitude"])
print(forecast_df)
```

### Get live weather forecast

```python
import pandas as pd
from frequenz.client.weather._types import ForecastFeature, Location

# Define a list of locations and features to request live forecasts for
locations = [Location(latitude=46.2276, longitude=15.2137, country_code="DE")]
features = [ForecastFeature.TEMPERATURE_2_METRE, ForecastFeature.V_WIND_COMPONENT_10_METRE]

# Returns a Receiver object that can be iterated over asynchronously
stream = await client.stream_live_forecast(
    locations=locations,
    features=features,
)

# Process incoming forecasts as they arrive
async for forecast in stream:
    # The to_ndarray_vlf method converts the forecast data to a 3D numpy array,
    # where the dimensions correspond to validity_ts, location, feature
    # The method can also take filters for validity_ts, locations and features
    # E.g. filter the forecast for wind features
    wind_forecast = forecast.to_ndarray_vlf(features=[ForecastFeature.V_WIND_COMPONENT_10_METRE])
    print(wind_forecast)

```
## Command Line Interface

The package also provides a command line interface to get weather forecast data.
Use `-h` to see the available options.

### Get historical weather forecast

```bash
weather-cli \
    --url <service-address> \
    --location "40,15" \
    --feature U_WIND_COMPONENT_100_METRE \
    --start 2024-03-14 \
    --end 2024-03-15 \
    --mode historical
```

### Get live weather forecast

```bash
weather-cli \
    --url <service-address> \
    --location "40, 15" \
    --feature TEMPERATURE_2_METRE \
    --mode live
```

