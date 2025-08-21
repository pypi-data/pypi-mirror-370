# License: MIT
# Copyright © 2023 Frequenz Energy-as-a-Service GmbH

"""Types used by the Weather Forecast API client."""

from __future__ import annotations  # required for constructor type hinting

import datetime as dt
import enum
import logging
import typing
from collections import namedtuple
from dataclasses import dataclass

import numpy as np
from frequenz.api.common.v1 import location_pb2
from frequenz.api.weather.v1 import weather_pb2

# Set up logging
_logger = logging.getLogger(__name__)


class ForecastFeature(enum.Enum):
    """Weather forecast features available through the API."""

    UNSPECIFIED = weather_pb2.ForecastFeature.FORECAST_FEATURE_UNSPECIFIED
    """Unspecified forecast feature."""

    TEMPERATURE_2_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_TEMPERATURE_2_METRE
    )
    """Temperature at 2m above the earth's surface."""

    U_WIND_COMPONENT_100_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_100_METRE
    )
    """Eastward wind component at 100m altitude."""

    V_WIND_COMPONENT_100_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_100_METRE
    )
    """Northward wind component at 100m altitude."""

    U_WIND_COMPONENT_10_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_U_WIND_COMPONENT_10_METRE
    )
    """Eastward wind component at 10m altitude."""

    V_WIND_COMPONENT_10_METRE = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_V_WIND_COMPONENT_10_METRE
    )
    """Northward wind component at 10m altitude."""

    SURFACE_SOLAR_RADIATION_DOWNWARDS = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_SOLAR_RADIATION_DOWNWARDS
    )
    """Surface solar radiation downwards."""

    SURFACE_NET_SOLAR_RADIATION = (
        weather_pb2.ForecastFeature.FORECAST_FEATURE_SURFACE_NET_SOLAR_RADIATION
    )
    """Surface net solar radiation."""

    @classmethod
    def from_pb(
        cls, forecast_feature: weather_pb2.ForecastFeature.ValueType
    ) -> ForecastFeature:
        """Convert a protobuf ForecastFeature value to ForecastFeature enum.

        Args:
            forecast_feature: protobuf forecast feature to convert.

        Returns:
            Enum value corresponding to the protobuf message.
        """
        if not any(t.value == forecast_feature for t in ForecastFeature):
            _logger.warning(
                "Unknown forecast feature %s. Returning UNSPECIFIED.", forecast_feature
            )
            return cls.UNSPECIFIED

        return ForecastFeature(forecast_feature)


SOLAR_PARAMETERS = {
    ForecastFeature.SURFACE_SOLAR_RADIATION_DOWNWARDS,
    ForecastFeature.SURFACE_NET_SOLAR_RADIATION,
}


@dataclass(frozen=True)
class Location:
    """Location data.

    Attributes:
        latitude: latitude of the location.
        longitude: longitude of the location.
        country_code: ISO 3166-1 alpha-2 country code of the location.
    """

    latitude: float
    longitude: float
    country_code: str

    @classmethod
    def from_pb(cls, location: location_pb2.Location) -> Location:
        """Convert a protobuf Location message to Location object.

        Args:
            location: protobuf location to convert.

        Returns:
            Location object corresponding to the protobuf message.
        """
        return cls(
            latitude=location.latitude,
            longitude=location.longitude,
            country_code=location.country_code,
        )

    def to_pb(self) -> location_pb2.Location:
        """Convert a Location object to protobuf Location message.

        Returns:
            Protobuf message corresponding to the Location object.
        """
        return location_pb2.Location(
            latitude=self.latitude,
            longitude=self.longitude,
            country_code=self.country_code,
        )


@dataclass(frozen=True)
class Forecasts:
    """Weather forecast data."""

    _forecasts_pb: typing.Union[
        weather_pb2.ReceiveLiveWeatherForecastResponse,
        weather_pb2.ReceiveHistoricalWeatherForecastResponse,
    ]

    @classmethod
    def from_pb(
        cls,
        forecasts: typing.Union[
            weather_pb2.ReceiveLiveWeatherForecastResponse,
            weather_pb2.ReceiveHistoricalWeatherForecastResponse,
        ],
    ) -> Forecasts:
        """Convert a protobuf Forecast message to Forecast object.

        Args:
            forecasts: protobuf message with live forecast data.

        Returns:
            Forecast object corresponding to the protobuf message.
        """
        return cls(_forecasts_pb=forecasts)

    def to_resampled_ndarray(
        self,
        validity_times: list[dt.datetime],
        locations: list[Location] | None = None,
        features: list[ForecastFeature] | None = None,
        solar_offset_sec: int = 1800,
    ) -> np.ndarray[
        # the shape is known to be 3 dimensional, but the length of each dimension is
        # not fixed, so we use typing.Any, instead of the usual const generic
        # parameters.
        tuple[typing.Any, typing.Any, typing.Any],
        np.dtype[np.float64],
    ]:
        """Convert the forecast to a numpy array and resample to the specified validity_times.

        Args:
            validity_times: The validity times to resample to.
            locations: The locations to filter by.
            features: The features to filter by.
            solar_offset_sec: Time offset in seconds to shift solar forecasts

        Returns:
            Numpy array of shape (num_validity_times, num_locations, num_features)
        """
        original_validity_times = self._get_validity_times()
        array = self.to_ndarray_vlf(None, locations, features)
        if not features:
            features = self._get_features()

        resampled_array = self.upsample_vlf(
            array,
            original_validity_times,
            validity_times,
            features,
            solar_offset_sec,
        )

        return resampled_array

    def _get_features(self) -> list[ForecastFeature]:
        """Return the available features in the Forecast.

        Returns:
            List of forecast features.
        """
        if not self._forecasts_pb.location_forecasts:
            return []
        # Features need to only be extracted from one validity time
        # from one location as they are equal across all
        first_location = self._forecasts_pb.location_forecasts[0]
        if not first_location.forecasts:
            return []

        first_validity_time = first_location.forecasts[0]

        return [
            ForecastFeature.from_pb(feature.feature)
            for feature in first_validity_time.features
        ]

    def _get_validity_times(self) -> list[dt.datetime]:
        """Get validity times of the forecasts.

        Returns:
            List of validity times.
        """
        # All location_forecasts have the same validity times
        first_location = self._forecasts_pb.location_forecasts[0]
        validity_times = []

        for fc in first_location.forecasts:
            validity_times.append(
                dt.datetime.fromtimestamp(fc.valid_time.seconds, tz=dt.UTC)
            )

        return validity_times

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def to_ndarray_vlf(
        self,
        validity_times: list[dt.datetime] | None = None,
        locations: list[Location] | None = None,
        features: list[ForecastFeature] | None = None,
    ) -> np.ndarray[
        # the shape is known to be 3 dimensional, but the length of each dimension is
        # not fixed, so we use typing.Any, instead of the usual const generic
        # parameters.
        tuple[typing.Any, typing.Any, typing.Any],
        np.dtype[np.float64],
    ]:
        """Convert a Forecast object to numpy array and use NaN to mark irrelevant data.

        If any of the filters are None, all values for that parameter will be returned.

        Args:
            validity_times: The validity times to filter by.
            locations: The locations to filter by.
            features: The features to filter by.

        Returns:
            Numpy array of shape (num_validity_times, num_locations, num_features)

        Raises:
            ValueError: If the forecasts data is missing or invalid.
            RuntimeError: If there is an error processing the forecast data.
        """
        # check for empty forecasts data
        if not self._forecasts_pb.location_forecasts:
            raise ValueError("Forecast data is missing or invalid.")

        try:
            num_times = len(self._forecasts_pb.location_forecasts[0].forecasts)
            num_locations = len(self._forecasts_pb.location_forecasts)
            num_features = len(
                self._forecasts_pb.location_forecasts[0].forecasts[0].features
            )

            # Look for the proto indexes of the filtered times, locations and features
            location_indexes = []
            validity_times_indexes = []
            feature_indexes = []

            # get the location indexes of the proto for the filtered locations
            if locations:
                for location in locations:
                    found = False
                    for l_index, location_forecast in enumerate(
                        self._forecasts_pb.location_forecasts
                    ):
                        if location == Location.from_pb(location_forecast.location):
                            location_indexes.append(l_index)
                            found = True
                            break
                    if not found:
                        # remember position of missing location
                        location_indexes.append(-1)
            else:
                location_indexes = list(range(num_locations))

            # get the val indexes of the proto for the filtered validity times
            if validity_times:
                for req_validitiy_time in validity_times:
                    found = False
                    for t_index, val_time in enumerate(
                        self._forecasts_pb.location_forecasts[0].forecasts
                    ):
                        if req_validitiy_time == val_time.valid_time.ToDatetime():
                            validity_times_indexes.append(t_index)
                            found = True
                            break
                    if not found:
                        # remember position of missing validity time
                        validity_times_indexes.append(-1)
            else:
                validity_times_indexes = list(range(num_times))

            # get the feature indexes of the proto for the filtered features
            if features:
                for req_feature in features:
                    found = False
                    for f_index, feature in enumerate(
                        self._forecasts_pb.location_forecasts[0].forecasts[0].features
                    ):
                        if req_feature == ForecastFeature.from_pb(feature.feature):
                            feature_indexes.append(f_index)
                            found = True
                            break
                    if not found:
                        # remember position of missing feature
                        feature_indexes.append(-1)
            else:
                feature_indexes = list(range(num_features))

            array = np.full(
                (
                    len(validity_times_indexes),
                    len(location_indexes),
                    len(feature_indexes),
                ),
                np.nan,
            )

            array_l_index = 0

            for l_index in location_indexes:
                array_t_index = 0

                for t_index in validity_times_indexes:
                    array_f_index = 0

                    for f_index in feature_indexes:
                        # This fails if there was data missing for at least one of the
                        # keys and we don't update the array but leave it as NaN
                        if l_index >= 0 and t_index >= 0 and f_index >= 0:
                            array[array_t_index, array_l_index, array_f_index] = (
                                self._forecasts_pb.location_forecasts[l_index]
                                .forecasts[t_index]
                                .features[f_index]
                                .value
                            )
                        array_f_index += 1

                    array_t_index += 1

                array_l_index += 1

            # Check if the array shape matches the number of filtered times, locations
            # and features
            if validity_times is not None and array.shape[0] != len(validity_times):
                raise ValueError(
                    f"The count of validity times in the array({array.shape[0]}) does "
                    f"not match the requested validity times count ({len(validity_times)})"
                )
            if locations is not None and array.shape[1] != len(locations):
                raise ValueError(
                    f"The count of location in the array ({array.shape[1]}) does not "
                    f"match the requested location count ({len(locations)})"
                )
            if features is not None and array.shape[2] != len(features):
                raise ValueError(
                    f"The count of features in the array ({array.shape[2]}) does not "
                    f"match the requested feature count ({len(features)})"
                )

        # catch all exceptions
        except Exception as e:
            raise RuntimeError("Error processing forecast data") from e

        return array

    # pylint: disable= too-many-arguments, too-many-positional-arguments
    def upsample_vlf(
        self,
        array: np.ndarray[
            tuple[typing.Any, typing.Any, typing.Any], np.dtype[np.float64]
        ],
        validity_times: list[dt.datetime],
        target_times: list[dt.datetime],
        features: list[ForecastFeature],
        solar_offset_sec: int = 1800,
    ) -> np.ndarray[tuple[typing.Any, typing.Any, typing.Any], np.dtype[np.float64]]:
        """Upsample the forecast array to requested timestamps.

        Args:
            array: 3D array from to_ndarray_vlf (time, location, feature)
            validity_times: List of original timestamps
            target_times: List of desired timestamps to interpolate to
            features: List of forecast features
            solar_offset_sec: Time offset in seconds to shift solar forecasts

        Returns:
            Resampled 3D array with same structure interpolated to target timestamps

        Raises:
            ValueError: If input dimensions don't match or timestamps aren't monotonic
        """
        # Check input dimensions
        if array.shape[0] != len(validity_times):
            raise ValueError(
                f"Time dimension of input array ({array.shape[0]}) does not match "
                f"number of validity times ({len(validity_times)})"
            )
        if array.shape[2] != len(features):
            raise ValueError(
                f"Feature dimension of input array ({array.shape[2]}) does not match "
                f"number of features ({len(features)})"
            )

        # Validate target timestamps are strictly increasing
        if not all(t1 < t2 for t1, t2 in zip(target_times[:-1], target_times[1:])):
            raise ValueError("target_times must be strictly increasing")

        vts = np.array([t.timestamp() for t in validity_times])
        tts = np.array([t.timestamp() for t in target_times])

        resampled = np.zeros((len(target_times), array.shape[1], array.shape[2]))

        # Get indices of solar and non-solar features
        solar_idxs = [i for i, f in enumerate(features) if f in SOLAR_PARAMETERS]
        other_idxs = [i for i, f in enumerate(features) if f not in SOLAR_PARAMETERS]

        # Handle non-solar features with direct interpolation
        if other_idxs:
            resampled[..., other_idxs] = np.apply_along_axis(
                lambda x: np.interp(tts, vts, x, np.nan, np.nan),
                axis=0,
                arr=array[..., other_idxs],
            )

        # Handle solar features with shifted interpolation
        if solar_idxs:
            # Shift validity times by solar_offset_sec for solar parameters
            shifted_vts = vts + solar_offset_sec
            resampled[..., solar_idxs] = np.apply_along_axis(
                lambda x: np.interp(
                    tts,
                    shifted_vts,
                    x,
                    np.nan,
                    np.nan,
                ),
                axis=0,
                arr=array[..., solar_idxs],
            )

        return resampled

    def flatten(self) -> list[ForecastData]:
        """Flatten forecast data into a list of ForecastData tuples.

        Returns:
            List of ForecastData tuples containing the flattened forecast data.

        Raises:
            ValueError: If the forecasts data is missing or invalid.
        """
        # check for empty forecasts data
        if not self._forecasts_pb.location_forecasts:
            raise ValueError("Forecast data is missing or invalid.")

        return flatten(list(self._forecasts_pb.location_forecasts))


ForecastData = namedtuple(
    "ForecastData",
    ["creation_ts", "latitude", "longitude", "validity_ts", "feature", "value"],
)


def flatten(
    location_forecasts: list[weather_pb2.LocationForecast],
) -> list[ForecastData]:
    """Flatten a Forecast object to a list of named tuples of data.

    Each tuple contains the following data:
    - creation timestamp
    - latitude
    - longitude
    - validity timestamp
    - feature
    - forecast value

    Args:
        location_forecasts: The location forecasts to flatten.

    Returns:
        List of named tuples with the flattened forecast data.
    """
    data = []
    for location_forecast in location_forecasts:
        for forecasts in location_forecast.forecasts:
            for feature_forecast in forecasts.features:
                # Create and append an instance of the named tuple instead of a plain tuple
                data.append(
                    ForecastData(
                        creation_ts=location_forecast.create_time.ToDatetime(),
                        latitude=location_forecast.location.latitude,
                        longitude=location_forecast.location.longitude,
                        validity_ts=forecasts.valid_time.ToDatetime(),
                        feature=ForecastFeature(feature_forecast.feature),
                        value=feature_forecast.value,
                    )
                )

    return data
