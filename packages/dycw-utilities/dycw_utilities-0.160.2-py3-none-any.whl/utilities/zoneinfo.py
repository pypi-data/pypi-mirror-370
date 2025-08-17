from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import TYPE_CHECKING, assert_never, cast, override
from zoneinfo import ZoneInfo

from whenever import ZonedDateTime

from utilities.tzlocal import LOCAL_TIME_ZONE

if TYPE_CHECKING:
    from utilities.types import TimeZone, TimeZoneLike


UTC = ZoneInfo("UTC")


##


def ensure_time_zone(obj: TimeZoneLike, /) -> ZoneInfo:
    """Ensure the object is a time zone."""
    match obj:
        case ZoneInfo() as zone_info:
            return zone_info
        case ZonedDateTime() as datetime:
            return ZoneInfo(datetime.tz)
        case "local":
            return LOCAL_TIME_ZONE
        case str() as key:
            return ZoneInfo(key)
        case dt.tzinfo() as tzinfo:
            if tzinfo is dt.UTC:
                return UTC
            raise _EnsureTimeZoneInvalidTZInfoError(time_zone=obj)
        case dt.datetime() as datetime:
            if datetime.tzinfo is None:
                raise _EnsureTimeZonePlainDateTimeError(datetime=datetime)
            return ensure_time_zone(datetime.tzinfo)
        case never:
            assert_never(never)


@dataclass(kw_only=True, slots=True)
class EnsureTimeZoneError(Exception): ...


@dataclass(kw_only=True, slots=True)
class _EnsureTimeZoneInvalidTZInfoError(EnsureTimeZoneError):
    time_zone: dt.tzinfo

    @override
    def __str__(self) -> str:
        return f"Unsupported time zone: {self.time_zone}"


@dataclass(kw_only=True, slots=True)
class _EnsureTimeZonePlainDateTimeError(EnsureTimeZoneError):
    datetime: dt.datetime

    @override
    def __str__(self) -> str:
        return f"Plain datetime: {self.datetime}"


##


def get_time_zone_name(time_zone: TimeZoneLike, /) -> TimeZone:
    """Get the name of a time zone."""
    return cast("TimeZone", ensure_time_zone(time_zone).key)


__all__ = ["UTC", "EnsureTimeZoneError", "ensure_time_zone", "get_time_zone_name"]
