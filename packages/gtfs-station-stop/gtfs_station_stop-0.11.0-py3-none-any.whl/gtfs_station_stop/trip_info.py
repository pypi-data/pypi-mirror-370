"""Trip Info."""

import os
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from gtfs_station_stop.calendar import Calendar
from gtfs_station_stop.static_dataset import GtfsStaticDataset


class TripInfo:
    """Trip Info."""

    def __init__(self, trip_data_dict: dict):
        self.route_id = trip_data_dict["route_id"]
        self.trip_id = trip_data_dict["trip_id"]
        self.service_id = trip_data_dict["service_id"]
        self.trip_headsign = trip_data_dict.get("trip_headsign", "")
        self.trip_short_name = trip_data_dict.get("trip_short_name", "")
        self.direction_id = trip_data_dict.get("direction_id")
        self.shape_id = trip_data_dict.get("shape_id")

    def __repr__(self):
        return f"{self.trip_id}: {self.route_id} to {self.trip_headsign}"


@dataclass
class TripInfoDataset(GtfsStaticDataset):
    """Dataset for Trip Infos."""

    trip_infos: dict[str, TripInfo]

    def __init__(self, *gtfs_files: os.PathLike, **kwargs):
        self.trip_infos = {}
        self.__cached_route_ids = None
        super().__init__(*gtfs_files, **kwargs)

    def add_gtfs_data(self, zip_filelike: os.PathLike) -> None:
        for line in self._get_gtfs_record_iter(zip_filelike, "trips.txt"):
            trip_id = line["trip_id"]
            self.trip_infos[trip_id] = TripInfo(line)
        # invalidate the cache
        self.__cached_route_ids = None

    def get_close_match(
        self,
        key,
        service_finder: str | Calendar | Iterable[str] | None = None,
        the_date: date | datetime | None = None,
    ) -> TripInfo | None:
        """
        Gets the first close match for a given trip ID using either none, a specific
        service ID, or a calendar and date. When using Calendar, a date can be provided,
        defaults to today.
        """
        if the_date is None:
            the_date = date.today()
        active_services: set[str] = set()
        if isinstance(service_finder, str):
            active_services = {service_finder}
        elif isinstance(service_finder, Calendar):
            active_services = set(
                s.service_id for s in service_finder.get_active_services(the_date)
            )

        if isinstance(the_date, datetime):
            the_date = the_date.date()

        return next(
            (
                trip_info
                for trip_id, trip_info in self.trip_infos.items()
                if key in trip_id
                and (
                    len(active_services) == 0 or trip_info.service_id in active_services
                )
            ),
            None,
        )

    def get_route_ids(self) -> list[str]:
        """Get Route IDs."""
        # cache this as it may be expensive to rerun the querey
        if self.__cached_route_ids is None:
            self.__cached_route_ids = list(
                set(ti.route_id for ti in self.trip_infos.values() if ti.route_id)
            )
        return self.__cached_route_ids

    def __getitem__(self, key) -> TripInfo:
        return self.trip_infos[key]

    def get(self, key: Any, default: Any | None = None):
        """Get Trip Info."""
        return self.trip_infos.get(key, default)
