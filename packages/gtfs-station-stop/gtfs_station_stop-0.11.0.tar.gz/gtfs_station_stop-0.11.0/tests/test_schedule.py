"""Test Schedule."""

from dataclasses import asdict

import syrupy.filters
from aiohttp import ClientSession

from gtfs_station_stop.route_info import RouteInfoDataset
from gtfs_station_stop.schedule import (
    GtfsSchedule,
    async_build_schedule,
)
from gtfs_station_stop.stop_times import StopTimesDataset

schedule_filter = syrupy.filters.props("tmp_dir", "tmp_dir_path", "resources")


async def test_async_build_schedule(mock_feed_server, snapshot):
    async with ClientSession() as session:
        schedule: GtfsSchedule = await async_build_schedule(
            *[
                url
                for url in mock_feed_server.static_urls
                if url.endswith("gtfs_static.zip")
            ],
            session=session,
        )
    assert snapshot(exclude=schedule_filter) == asdict(schedule)
    assert isinstance(schedule.stop_times_ds, StopTimesDataset)


async def test_async_build_schedule_add_data_later(mock_feed_server, snapshot):
    schedule: GtfsSchedule = await async_build_schedule(
        *[
            url
            for url in mock_feed_server.static_urls
            if url.endswith("gtfs_static.zip")
        ]
    )
    orig_data = asdict(schedule)

    await schedule.async_build_schedule(
        *[
            url
            for url in mock_feed_server.static_urls
            if url.endswith("gtfs_static_supl.zip")
        ]
    )
    await schedule.async_load_stop_times()

    assert orig_data != asdict(schedule)
    assert snapshot(exclude=schedule_filter) == asdict(schedule)
    assert isinstance(schedule.stop_times_ds, StopTimesDataset)
    assert isinstance(schedule.route_info_ds, RouteInfoDataset)


async def test_stop_time_filtering(mock_feed_server, snapshot):
    schedule: GtfsSchedule = await async_build_schedule(
        *[
            url
            for url in mock_feed_server.static_urls
            if url.endswith("gtfs_static.zip")
        ]
    )
    await schedule.async_load_stop_times({"101N"})

    assert snapshot(
        exclude=syrupy.filters.props("tmp_dir", "tmp_dir_path", "resources")
    ) == asdict(schedule)

    assert schedule.stop_times_ds.get("STOP_TIME_TRIP", 1) is not None
