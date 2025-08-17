from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from hypothesis import given
from hypothesis.strategies import (
    DataObject,
    data,
    datetimes,
    just,
    sampled_from,
    timezones,
)
from pytest import raises

from utilities.hypothesis import zoned_date_times
from utilities.tzdata import HongKong, Tokyo
from utilities.tzlocal import LOCAL_TIME_ZONE, LOCAL_TIME_ZONE_NAME
from utilities.zoneinfo import (
    UTC,
    _EnsureTimeZoneInvalidTZInfoError,
    _EnsureTimeZonePlainDateTimeError,
    ensure_time_zone,
    get_time_zone_name,
)

if TYPE_CHECKING:
    from utilities.types import TimeZone


class TestEnsureTimeZone:
    @given(
        data=data(),
        case=sampled_from([
            (HongKong, HongKong),
            (Tokyo, Tokyo),
            (UTC, UTC),
            (dt.UTC, UTC),
        ]),
    )
    def test_time_zone(
        self, *, data: DataObject, case: tuple[ZoneInfo | dt.timezone, ZoneInfo]
    ) -> None:
        time_zone, expected = case
        zone_info_or_str: ZoneInfo | dt.timezone | TimeZone = data.draw(
            sampled_from([time_zone, get_time_zone_name(time_zone)])
        )
        result = ensure_time_zone(zone_info_or_str)
        assert result is expected

    def test_local(self) -> None:
        result = ensure_time_zone("local")
        assert result is LOCAL_TIME_ZONE

    @given(data=data(), time_zone=timezones())
    def test_standard_zoned_date_time(
        self, *, data: DataObject, time_zone: ZoneInfo
    ) -> None:
        datetime = data.draw(datetimes(timezones=just(time_zone)))
        result = ensure_time_zone(datetime)
        assert result is time_zone

    @given(data=data(), time_zone=timezones())
    def test_whenever_zoned_date_time(
        self, *, data: DataObject, time_zone: ZoneInfo
    ) -> None:
        datetime = data.draw(zoned_date_times(time_zone=time_zone))
        result = ensure_time_zone(datetime)
        assert result is time_zone

    def test_error_invalid_tzinfo(self) -> None:
        time_zone = dt.timezone(dt.timedelta(hours=12))
        with raises(
            _EnsureTimeZoneInvalidTZInfoError, match="Unsupported time zone: .*"
        ):
            _ = ensure_time_zone(time_zone)

    @given(datetime=datetimes())
    def test_error_local_datetime(self, *, datetime: dt.datetime) -> None:
        with raises(_EnsureTimeZonePlainDateTimeError, match="Plain datetime: .*"):
            _ = ensure_time_zone(datetime)


class TestGetTimeZoneName:
    @given(data=data(), time_zone=sampled_from(["Asia/Hong_Kong", "Asia/Tokyo", "UTC"]))
    def test_main(self, *, data: DataObject, time_zone: TimeZone) -> None:
        zone_info_or_str: ZoneInfo | TimeZone = data.draw(
            sampled_from([ZoneInfo(time_zone), time_zone])
        )
        result = get_time_zone_name(zone_info_or_str)
        assert result == time_zone

    def test_local(self) -> None:
        result = get_time_zone_name("local")
        assert result == LOCAL_TIME_ZONE_NAME


class TestTimeZones:
    @given(time_zone=sampled_from([HongKong, Tokyo, UTC]))
    def test_main(self, *, time_zone: ZoneInfo) -> None:
        assert isinstance(time_zone, ZoneInfo)
