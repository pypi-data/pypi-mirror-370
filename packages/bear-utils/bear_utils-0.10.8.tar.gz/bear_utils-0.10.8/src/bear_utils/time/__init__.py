"""A module for Bear Epoch Time utilities centering around the EpochTimestamp class."""

from importlib.metadata import version

from bear_epoch_time import EpochTimestamp, TimerData, TimeTools, add_ord_suffix, create_timer, timer
from bear_epoch_time._helpers import (
    convert_to_milliseconds,
    convert_to_seconds,
    seconds_to_time,
    seconds_to_timedelta,
    timedelta_to_seconds,
)
from bear_epoch_time.constants.date_related import (
    DATE_FORMAT,
    DATE_TIME_FORMAT,
    DT_FORMAT_WITH_SECONDS,
    DT_FORMAT_WITH_TZ,
    DT_FORMAT_WITH_TZ_AND_SECONDS,
    ET_TIME_ZONE,
    PT_TIME_ZONE,
    TIME_FORMAT_WITH_SECONDS,
    UTC_TIME_ZONE,
)


def get_bear_epoch_time_version() -> str:
    """Get the version of the bear_epoch_time package."""
    try:
        return version("bear_epoch_time")
    except Exception:
        return "unknown"


__version__: str = get_bear_epoch_time_version()


__all__ = [
    "DATE_FORMAT",
    "DATE_TIME_FORMAT",
    "DT_FORMAT_WITH_SECONDS",
    "DT_FORMAT_WITH_TZ",
    "DT_FORMAT_WITH_TZ_AND_SECONDS",
    "ET_TIME_ZONE",
    "PT_TIME_ZONE",
    "TIME_FORMAT_WITH_SECONDS",
    "UTC_TIME_ZONE",
    "EpochTimestamp",
    "TimeTools",
    "TimerData",
    "__version__",
    "add_ord_suffix",
    "convert_to_milliseconds",
    "convert_to_seconds",
    "create_timer",
    "seconds_to_time",
    "seconds_to_timedelta",
    "timedelta_to_seconds",
    "timer",
]
