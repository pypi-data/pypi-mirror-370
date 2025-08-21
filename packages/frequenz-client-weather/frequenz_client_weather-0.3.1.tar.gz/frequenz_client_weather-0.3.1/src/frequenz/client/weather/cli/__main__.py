# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""CLI tool to iterate over historical weather forecast data and print it in CSV format."""

import argparse
import asyncio
from datetime import datetime, timedelta

from frequenz.client.base.channel import ChannelOptions, KeepAliveOptions, SslOptions

from frequenz.client.weather._client import Client
from frequenz.client.weather._types import ForecastFeature, Location


def main() -> None:
    """Parse arguments and run the client."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        type=str,
        help="URL of the Weather service",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["historical", "live"],
        required=True,
        help="Operation mode: historical or live forecasts",
    )
    parser.add_argument(
        "--feature",
        type=str,
        nargs="+",
        choices=[e.name for e in ForecastFeature],
        help="Feature names",
        required=True,
    )
    parser.add_argument(
        "--location",
        type=lambda s: tuple(map(float, s.split(","))),  # One-liner lambda
        required=True,
        help='Location in lat,lon format (e.g., "37.7749,-122.4194")',
    )

    parser.add_argument(
        "--start",
        type=datetime.fromisoformat,
        help="Start datetime in YYYY-MM-DDTHH:MM:SS format (historical mode only)",
    )
    parser.add_argument(
        "--end",
        type=datetime.fromisoformat,
        help="End datetime in YYYY-MM-DDTHH:MM:SS format (historical mode only)",
    )

    args = parser.parse_args()

    # Validate arguments based on mode
    if args.mode == "historical":
        if args.start is None or args.end is None:
            parser.error("--start and --end are required in historical mode")
    else:
        if args.start is not None or args.end is not None:
            parser.error("--start and --end can only be used in historical mode")

    try:
        asyncio.run(
            run(
                service_address=args.url,
                location=args.location,
                feature_names=args.feature,
                start=args.start,
                end=args.end,
                mode=args.mode,
            )
        )
    except KeyboardInterrupt:
        print("\nReceived interrupt, shutting down...")


async def run(  # pylint: disable=too-many-arguments
    *,
    service_address: str,
    location: tuple[float, float],
    feature_names: list[str],
    start: datetime | None,
    end: datetime | None,
    mode: str,
) -> None:
    """Run the client.

    Args:
        service_address: service address
        location: location in lat, lon format
        feature_names: feature names
        start: start datetime (historical mode only)
        end: end datetime (historical mode only)
        mode: operation mode ("historical" or "live")
    """
    client = Client(
        service_address,
        channel_defaults=ChannelOptions(
            ssl=SslOptions(enabled=False),
            keep_alive=KeepAliveOptions(
                enabled=True,
                timeout=timedelta(minutes=5),
                interval=timedelta(seconds=20),
            ),
        ),
    )

    features = [ForecastFeature[feature_name] for feature_name in feature_names]
    locations = [
        Location(
            latitude=location[0],
            longitude=location[1],
            country_code="",
        ),
    ]

    print("creation_ts,validity_ts,latitude,longitude,feature,value")

    if mode == "historical":
        # ignore type error because start and end are not None in historical mode
        iterator = await client.stream_historical_forecast(
            features=features, locations=locations, start=start, end=end  # type: ignore[arg-type]
        )
        async for forecasts in iterator:
            for fc in forecasts.flatten():
                row = (
                    fc.creation_ts,
                    fc.validity_ts,
                    fc.latitude,
                    fc.longitude,
                    fc.feature,
                    fc.value,
                )
                print(",".join(str(e) for e in row))
    else:
        receiver = await client.stream_live_forecast(
            locations=locations,
            features=features,
        )
        while True:
            live_forecasts = await receiver.receive()
            for fc in live_forecasts.flatten():
                row = (
                    fc.creation_ts,
                    fc.validity_ts,
                    fc.latitude,
                    fc.longitude,
                    fc.feature,
                    fc.value,
                )
                print(",".join(str(e) for e in row))
            print("--------Waiting for next forecast---------")


if __name__ == "__main__":
    main()
