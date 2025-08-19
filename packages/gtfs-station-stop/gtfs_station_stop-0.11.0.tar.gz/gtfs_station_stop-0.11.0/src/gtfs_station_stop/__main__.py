#!/usr/bin/python
import argparse
import asyncio
import importlib.metadata
import time
from pprint import pprint

import dotenv

from gtfs_station_stop.calendar import Calendar
from gtfs_station_stop.feed_subject import FeedSubject
from gtfs_station_stop.route_status import RouteStatus
from gtfs_station_stop.schedule import GtfsSchedule
from gtfs_station_stop.station_stop import StationStop
from gtfs_station_stop.station_stop_info import (  # noqa: F401
    StationStopInfoDataset,
)
from gtfs_station_stop.stop_times import StopTimesDataset
from gtfs_station_stop.trip_info import TripInfoDataset  # noqa: F401

if __name__ == "__main__":
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser(
        prog="GTFS Station Stop", description="Use for static and realtime GTFS info"
    )

    parser.add_argument(
        "-v", "--version", action="store_true", help="display the module version"
    )
    parser.add_argument(
        "-i",
        "--info-zip",
        help="input GTFS zip file path of static data",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "-k",
        "--headers",
        nargs="*",
        help="Headers to add to requests, typically used for for API authentication, example: 'Api-Key: xyz123'",  # noqa: E501
        default=[],
    )
    parser.add_argument(
        "-u", "--feed-urls", help="feed URL list", nargs="*", default=[]
    )
    parser.add_argument(
        "-s",
        "--stops",
        help="list of stops to check for arrivals and alerts",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "-r",
        "--routes",
        help="list of routes to check for alerts",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "--lang", type=str, default="en", help="language to read alerts", nargs="?"
    )
    parser.add_argument(
        "--do-async", action="store_true", help="update using asynchronous functions"
    )

    args = parser.parse_args()

    if args.version:
        print(importlib.metadata.version("gtfs_station_stop"))
        exit(0)

    start_time = time.time()

    # Get the API Key, argument takes precedent of environment variable
    headers: dict[str, str] = {}
    for h in args.headers:
        key, val = (x.strip() for x in h.split(":"))
        headers[key] = val

    ssids = None
    tids = None
    calendar = None
    stop_times_dataset = None

    if args.do_async and args.info_zip:
        schedule = GtfsSchedule()
        asyncio.run(schedule.async_update_schedule(*args.info_zip))
        ssids, tids, calendar = (
            schedule.station_stop_info_ds,
            schedule.trip_info_ds,
            schedule.calendar,
        )

    elif args.info_zip:
        ssids = StationStopInfoDataset(*args.info_zip, headers=headers)
        tids = TripInfoDataset(*args.info_zip, headers=headers)
        calendar = Calendar(*args.info_zip, headers=headers)
        stop_times_dataset = StopTimesDataset(*args.info_zip, headers=headers)

    if calendar is not None:
        # Print out the current active service IDs
        print()
        print("SERVICES:")
        print("=========")
        exptabs: int = max(len(v.service_id) + 2 for v in calendar.services.values())
        for s in calendar.get_active_services():
            print(f"{s.service_id}:\t\033[92m active \033[00m".expandtabs(exptabs))
        for s in calendar.get_inactive_services():
            print(f"{s.service_id}:\t\033[91m inactive \033[00m".expandtabs(exptabs))

    feed_subject = FeedSubject(args.feed_urls, headers=headers)
    station_stops = [StationStop(id, feed_subject) for id in args.stops]
    route_statuses = [RouteStatus(id, feed_subject) for id in args.routes]

    if args.do_async:
        asyncio.run(feed_subject.async_update())
    else:
        station_stops = [StationStop(id, feed_subject) for id in args.stops]
        route_statuses = [RouteStatus(id, feed_subject) for id in args.routes]
        feed_subject.update()

    print()
    print("Arrival Status:")
    print("===============")
    if len(station_stops) == 0:
        print("none")
    for stop in station_stops:
        if ssids is not None:
            print(ssids[stop.id])
            pprint(
                [
                    [
                        arrival.route,
                        arrival.time,
                        arrival.trip,
                        tids.get_close_match(arrival.trip, calendar),
                    ]
                    for arrival in sorted(
                        stop.get_time_to_arrivals(stop_times_dataset=stop_times_dataset)
                    )
                ]
            )
            print(stop.alerts)

    print()
    print("Route Status:")
    print("===============")
    if len(route_statuses) == 0:
        print("none")
    for route in route_statuses:
        for alert in route.alerts:
            print(f"Alert! {route.id}")
            print(alert.header_text.get(args.lang))
            print(alert.description_text.get(args.lang))
            print()
            print()

    print(
        f"Processed {len(args.feed_urls)} feeds and {len(args.info_zip)} static info zipfiles in {time.time() - start_time:.3f} seconds"  # noqa E501
    )
