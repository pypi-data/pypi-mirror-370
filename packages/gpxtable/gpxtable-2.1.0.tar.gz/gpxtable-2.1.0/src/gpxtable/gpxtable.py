"""
gpxtable - Create a markdown template from a Garmin GPX file for route information
"""

import math
import re
from datetime import datetime, timedelta, tzinfo
from typing import Optional, Union, List, NamedTuple, TextIO

import astral
import astral.sun
import gpxpy.geo
from gpxpy.gpx import (
    GPX,
    GPXWaypoint,
    GPXRoutePoint,
    GPXTrackPoint,
    PointData,
)

KM_TO_MILES = 0.621371
M_TO_FEET = 3.28084

GPXTABLE_XML_NAMESPACE = {
    "trp": "http://www.garmin.com/xmlschemas/TripExtensions/v1",
    "gpxx": "http://www.garmin.com/xmlschemas/GpxExtensions/v3",
}


GPXTABLE_DEFAULT_WAYPOINT_CLASSIFIER: List[dict] = [
    {
        "symbol": "Gas/Restaurant",
        "search": r"(?=.*\b(Gas|Fuel)\b)(?=.*\b(Lunch|Meal)\b)",
        "delay": 75,
        "marker": "GL",
        "fuel_reset": True,
    },
    {
        "symbol": "Gas Station",
        "search": r"\bGas\b|\bFuel\b|\b\(G\)\b",
        "delay": 15,
        "marker": "G",
        "fuel_reset": True,
    },
    {
        "symbol": "Restaurant",
        "search": r"\bRestaurant\b|\bLunch\b|\bBreakfast\b|\b\Dinner\b|\b\(L\)\b",
        "delay": 60,
        "marker": "L",
    },
    {
        "symbol": "Restroom",
        "search": r"\bRestroom\b|\bBreak\b|\b\(R\)\b",
        "delay": 15,
    },
    {
        "symbol": "Scenic Area",
        "delay": 5,
    },
    {"symbol": "Photo", "search": r"\bPhotos?\b|\b\(P\)\b", "delay": 5},
]
"""
    Additional data used for points if no other timing/type data is found.
    The list is iterated in sequence, the first match is returned.

    Parameters:
        symbol (str): type of waypoint (comment notation)
        search (regex): regular expression matching waypoint name
        delay (int): default delay in minutes
        marker (str): shorthand notation for gas or lunch (a
            meal) or both ("G", "L", "GL")
        fuel_reset (bool): reset due to refueling
"""


class NearestLocationDataExt(NamedTuple):
    """
    Extended class for NearestLocationData

    Includes distance_from_start
    """

    location: GPXTrackPoint
    track_no: int
    segment_no: int
    point_no: int
    distance_from_start: float
    min_distance: float


class GPXTrackExt:
    """
    Extended class for GPXTrack

    usage: ext_track = GPXTrackExt(track)
    """

    def __init__(self, track):
        self.gpx_track = track

    def get_points_data(self, distance_2d: bool = False) -> List[PointData]:
        """
        Returns a list of tuples containing the actual waypoint, its distance from the start,
        track_no, segment_no, and segment_point_no
        """
        distance_from_start = 0.0
        previous_point = None

        # (point, distance_from_start) pairs:
        points = []

        for segment_no, segment in enumerate(self.gpx_track.segments):
            for point_no, point in enumerate(segment.points):
                if previous_point and point_no > 0:
                    if distance_2d:
                        distance = point.distance_2d(previous_point)
                    else:
                        distance = point.distance_3d(previous_point)

                    distance_from_start += distance or 0.0

                points.append(
                    PointData(point, distance_from_start, -1, segment_no, point_no)
                )

                previous_point = point

        return points

    def get_nearest_locations(
        self,
        location: gpxpy.geo.Location,
        threshold_distance: float = 0.01,
        deduplicate_distance: float = 0.0,
    ) -> List[NearestLocationDataExt]:
        """
        Returns:
            list: locations of elements where the location may be on the track

        Parameters:
            threshold_distance: the minimum distance from the track
                so that the point *may* be counted as to be "on the track".
                For example 0.01 means 1% of the track distance.

            deduplicate_distance: absolute distance in meters where a
                duplicate will not be returned in case the track wraps
                around itself.
        """

        def _deduplicate(
            locations: List[NearestLocationDataExt], delta: float = 0.0
        ) -> List[NearestLocationDataExt]:
            previous: Optional[NearestLocationDataExt] = None
            filtered: List[NearestLocationDataExt] = []
            for current in locations:
                if (
                    not previous
                    or (current.distance_from_start - previous.distance_from_start)
                    > delta
                ):
                    filtered.append(current)
                previous = current
            return filtered

        points = self.get_points_data()
        if not points:
            return []

        result: List[NearestLocationDataExt] = []
        distance: Optional[float] = points[-1][1]
        threshold = (distance or 0.0) * threshold_distance
        candidate: Optional[NearestLocationDataExt] = None

        for point, distance_from_start, track_no, segment_no, point_no in points:
            distance = location.distance_3d(point) or math.inf
            if distance < threshold:
                if not candidate or distance < candidate.min_distance:
                    candidate = NearestLocationDataExt(
                        point,
                        track_no,
                        segment_no,
                        point_no,
                        distance_from_start,
                        distance,
                    )
            else:
                if candidate:
                    result.append(candidate)
                    candidate = None
        if candidate:
            result.append(candidate)
        return _deduplicate(result, deduplicate_distance)


class GPXPointMixin:
    """
    :class:`gpxpy.GPXWaypoint` and :class:`gpxpy.GPXRoutePoint` functionality
    extensions
    """

    def __init__(
        self,
        base: Union[GPXWaypoint, GPXRoutePoint],
        point_classifier: Optional[List[dict]] = None,
    ):
        if not isinstance(self, (GPXWaypoint, GPXRoutePoint)):
            raise TypeError("Not extending a GPXWaypoint or GPXRoutePoint")
        super().__init__(
            latitude=base.latitude,  # type: ignore
            longitude=base.longitude,  # type: ignore
            elevation=base.elevation,  # type: ignore
            time=base.time,  # type: ignore
            name=base.name,  # type: ignore
            description=base.description,  # type: ignore
            symbol=base.symbol,  # type: ignore
            type=base.type,  # type: ignore
            comment=base.comment,  # type: ignore
            horizontal_dilution=base.horizontal_dilution,  # type: ignore
            vertical_dilution=base.vertical_dilution,  # type: ignore
            position_dilution=base.position_dilution,  # type: ignore
        )
        self.point_classifier = point_classifier or GPXTABLE_DEFAULT_WAYPOINT_CLASSIFIER
        self.extensions = base.extensions

    def _classify(self):
        if not isinstance(
            self,
            (
                GPXWaypoint,
                GPXRoutePoint,
                GPXWaypointExt,
                GPXRoutePointExt,
            ),
        ):
            raise TypeError("Invalid instance extension")
        for values in self.point_classifier:
            if self.symbol == values["symbol"]:
                return values
            if "search" in values and re.search(
                values["search"], self.name or "", re.I
            ):
                self.symbol = values["symbol"]
                return values
        return {}

    def delay(self) -> timedelta:
        """Layover delay for a given waypoint if not specified"""
        values = self._classify()
        return timedelta(minutes=values.get("delay", 0))

    def marker(self) -> str:
        """Single or dual character marker for a given waypoint e.g. G, L, GL"""
        values = self._classify()
        return values.get("marker", "")

    def fuel_stop(self) -> bool:
        """Is this a fuel stop, should we reset?"""
        values = self._classify()
        return values.get("fuel_reset", False)

    def shaping_point(self) -> bool:
        """Is this route point is a shaping or via point and should be ignored"""
        if not isinstance(
            self,
            (
                GPXWaypoint,
                GPXRoutePoint,
                GPXWaypointExt,
                GPXRoutePointExt,
            ),
        ):
            raise TypeError("Invalid instance extension")
        if not self.name:
            return True
        if self.name.startswith("Via ") or self.name.endswith("(V)"):
            return True
        return any("ShapingPoint" in extension.tag for extension in self.extensions)


class GPXWaypointExt(GPXPointMixin, GPXWaypoint):
    """GPXWaypoint including extra functions from Mixin"""


class GPXRoutePointExt(GPXPointMixin, GPXRoutePoint):
    """GPXRoutePoint including extra functions from Mixin"""

    def delay(self) -> timedelta:
        """layover time at a given RoutePoint (Basecamp extension)"""
        for extension in self.extensions:
            for duration in extension.findall(
                "trp:StopDuration", GPXTABLE_XML_NAMESPACE
            ):
                if match := re.match(r"^PT((\d+)H)?((\d+)M)?$", duration.text):
                    return timedelta(
                        hours=int(match[2] or "0"), minutes=int(match[4] or "0")
                    )
        return super().delay()

    def departure_time(
        self,
        use_departure: Optional[bool] = False,
        depart_at: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """returns datetime object for route point with departure times or None"""
        if use_departure and depart_at:
            return depart_at
        for extension in self.extensions:
            for departure in extension.findall(
                "trp:DepartureTime", GPXTABLE_XML_NAMESPACE
            ):
                return datetime.fromisoformat(departure.text.replace("Z", "+00:00"))
        return None


class GPXTableCalculator:
    """
    Create a waypoint/route-point table based upon GPX information.

    Parameters:
        gpx: gpxpy gpx data
        output: output stream or (stdio if not specified)
        imperial: display in Imperial units (default imperial)
        speed: optional speed of travel for time-distance calculations
        depart_at: if provided, departure time for route or tracks to start
        ignore_times: ignore any timestamps in provided GPX routes or tracks
        display_coordinates: include latitude and longitude of points in table
    """

    # pylint: disable=too-many-instance-attributes

    #: 200m allowed between waypoint and start/end of track
    waypoint_delta = 200.0

    #: 10km between duplicates of the same waypoint on a track
    waypoint_debounce = 10000.0

    #: Assume traveling at 30mph/50kph
    default_travel_speed = 30.0 / KM_TO_MILES

    LLP_HDR = "|        Lat,Lon       "
    LLP_SEP = "| :------------------: "
    LLP_FMT = "| {:-10.4f},{:.4f} "
    OUT_HDR = "| Name                           |   Dist. | GL |  ETA  | Notes"
    OUT_SEP = "| :----------------------------- | ------: | -- | ----: | :----"
    OUT_FMT = "| {:30.30} | {:>7} | {:>2} | {:>5} | {}{}"

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        gpx: GPX,
        output: Optional[TextIO] = None,
        imperial: bool = True,
        speed: float = 30.0 / KM_TO_MILES,
        depart_at: Optional[datetime] = None,
        ignore_times: bool = False,
        display_coordinates: bool = False,
        tz: Optional[tzinfo] = None,
        point_classifier: Optional[List[dict]] = None,
    ) -> None:
        self.gpx = gpx
        self.output = output
        self.speed = (
            speed / KM_TO_MILES if imperial else speed
        ) or self.default_travel_speed
        self.imperial: bool = imperial
        self.depart_at: Optional[datetime] = depart_at
        self.ignore_times: bool = ignore_times
        self.display_coordinates: bool = display_coordinates
        self.tz = tz
        self.point_classifier = point_classifier

    def print_all(self) -> None:
        """
        Output full combination of header, waypoints, and routes.
        """
        self.print_header()
        self.print_waypoints()
        self.print_routes()

    def print_header(self) -> None:
        """
        Output generic information about the GPX data such as name and creator
        """
        if self.gpx.name:
            print(f"## {self.gpx.name}", file=self.output)
        if self.gpx.creator:
            print(f"* {self.gpx.creator}", file=self.output)
        if self.depart_at:
            print(f"* Departure at {self.depart_at:%c %Z}", file=self.output)
        move_data = self.gpx.get_moving_data()
        if move_data and move_data.moving_time:
            print(
                f"* Total moving time: {self._format_time(move_data.moving_time)}",
                file=self.output,
            )
        if dist := self.gpx.length_2d():
            print(
                f"* Total distance: {self._format_long_length(dist, True)}",
                file=self.output,
            )
        if self.speed:
            print(
                f"* Default speed: {self._format_speed(self.speed, True)}",
                file=self.output,
            )

    def _populate_times(self) -> None:
        if not self.depart_at or not self.speed:
            return
        for track_no, track in enumerate(self.gpx.tracks):
            # assume (for now) that if there are multiple tracks, 1 track = 1 day
            depart_at = self.depart_at + timedelta(hours=24 * track_no)
            time_bounds = track.get_time_bounds()
            # handle case where basecamp is putting crap for times in the tracks
            if self.ignore_times or time_bounds.start_time == time_bounds.end_time:
                track.remove_time()
                time_bounds = track.get_time_bounds()
            # if track has legitimate times in it, just adjust our delta for departure
            if time_bounds.start_time:
                track.adjust_time(depart_at - time_bounds.start_time)
            else:
                track.segments[0].points[0].time = depart_at
                track.segments[-1].points[-1].time = depart_at + timedelta(
                    hours=track.length_2d() / (self.speed * 1000)
                )
        self.gpx.add_missing_times()

    def _format_waypoint_entry(
        self, waypoint, track_point, last_gas, last_waypoint, waypoint_delays, layover
    ) -> str:
        result = ""
        if self.display_coordinates:
            result += self.LLP_FMT.format(waypoint.latitude, waypoint.longitude)
        distance_info = (
            self._format_long_length(round(track_point.distance_from_start - last_gas))
            + "/"
            + self._format_long_length(round(track_point.distance_from_start))
            if waypoint.fuel_stop() or last_waypoint
            else f"{self._format_long_length(round(track_point.distance_from_start))}"
        )
        marker_info = (
            waypoint.marker()
            if track_point.distance_from_start > self.waypoint_delta
            and not last_waypoint
            else ""
        )
        arrival_time = (
            (track_point.location.time + waypoint_delays)
            .astimezone(self.tz)
            .strftime("%H:%M")
            if track_point.location.time
            else ""
        )
        layover_info = f" (+{str(layover)[:-3]})" if layover else ""
        return result + self.OUT_FMT.format(
            (waypoint.name or "").replace("\n", " "),
            distance_info,
            marker_info,
            arrival_time,
            waypoint.symbol or "",
            layover_info,
        )

    def print_waypoints(self) -> None:
        """
        Print waypoint information

        Look for all the waypoints associated with tracks present to attempt to reconstruct
        the order and distance of the waypoints. If a departure time has been set, estimate
        the arrival time at each waypoint and probable layover times.
        """

        self._populate_times()
        for track in self.gpx.tracks:
            waypoints = [
                (
                    wp,
                    GPXTrackExt(track).get_nearest_locations(
                        wp, 0.001, deduplicate_distance=self.waypoint_debounce
                    ),
                )
                for wp in (
                    GPXWaypointExt(wpb, self.point_classifier)
                    for wpb in self.gpx.waypoints
                )
                if not wp.shaping_point()
            ]
            waypoints = sorted(
                [(wp, tp) for wp, tps in waypoints for tp in tps],
                key=lambda entry: entry[1].point_no,
            )

            print(f"\n## Track: {track.name}", file=self.output)
            if track.description:
                print(f"* {track.description}", file=self.output)
            print(self._format_output_header(), file=self.output)
            waypoint_delays = timedelta()
            last_gas = 0.0

            for waypoint, track_point in waypoints:
                first_waypoint = waypoint == waypoints[0][0]
                last_waypoint = waypoint == waypoints[-1][0]
                if last_gas > track_point.distance_from_start:
                    last_gas = 0.0  # assume we have filled up between track segments
                layover = (
                    waypoint.delay()
                    if not first_waypoint and not last_waypoint
                    else timedelta()
                )
                print(
                    self._format_waypoint_entry(
                        waypoint,
                        track_point,
                        last_gas,
                        last_waypoint,
                        waypoint_delays,
                        layover,
                    ),
                    file=self.output,
                )
                if waypoint.fuel_stop():
                    last_gas = track_point.distance_from_start
                waypoint_delays += layover
            if almanac := self._sun_rise_set(
                track.segments[0].points[0],
                track.segments[-1].points[-1],
                delay=waypoint_delays,
            ):
                print(f"\n* {almanac}", file=self.output)

    @staticmethod
    def _calculate_distance(previous, current):
        return gpxpy.geo.distance(
            previous[0], previous[1], None, current[0], current[1], None
        )

    def _format_route_point_entry(
        self, point, dist, last_gas, last_point, first_point, timing, delay
    ) -> str:
        result = ""
        if self.display_coordinates:
            result += self.LLP_FMT.format(point.latitude, point.longitude)
        return result + self.OUT_FMT.format(
            (point.name or "").replace("\n", " "),
            (
                f"{self._format_long_length(dist - last_gas)}/{self._format_long_length(dist)}"
                if point.fuel_stop() or last_point
                else f"{self._format_long_length(dist)}"
            ),
            (point.marker() if not first_point and not last_point else ""),
            timing.astimezone(self.tz).strftime("%H:%M") if timing else "",
            point.symbol or "",
            f" (+{str(delay)[:-3]})" if delay else "",
        )

    def print_routes(self) -> None:
        """
        Prints the details of routes and calculates and prints point details.

        Args:
            self: The GPXTableCalculator instance.

        Returns:
            None
        """

        def print_route_details(route):
            print(f"\n## Route: {route.name}", file=self.output)
            if route.description:
                print(f"* {route.description}", file=self.output)
            print(self._format_output_header(), file=self.output)

        def calculate_and_print_point_details(
            point,
            dist,
            last_gas,
            last_point,
            first_point,
            timing,
            delay,
            last_display_distance,
        ):
            if not point.shaping_point():
                if timing:
                    timing += self._travel_time(dist - last_display_distance)
                last_display_distance = dist
                if departure := point.departure_time(first_point, self.depart_at):
                    timing = departure
                delay = (
                    point.delay() if not first_point and not last_point else timedelta()
                )
                if last_gas > dist:
                    last_gas = 0.0
                print(
                    self._format_route_point_entry(
                        point, dist, last_gas, last_point, first_point, timing, delay
                    ),
                    file=self.output,
                )
                if timing:
                    timing += delay
            return timing, last_display_distance

        for route in self.gpx.routes:
            print_route_details(route)
            if not route.points:
                continue

            route_points = [
                GPXRoutePointExt(rp, self.point_classifier) for rp in route.points
            ]
            dist = 0.0
            previous = route_points[0].latitude, route_points[0].longitude
            last_gas = 0.0
            timing = route_points[0].departure_time(True, self.depart_at)

            if timing:
                route_points[0].time = timing
            delay = timedelta()
            last_display_distance = 0.0

            for point in route_points:
                first_point = point is route_points[0]
                last_point = point is route_points[-1]
                timing, last_display_distance = calculate_and_print_point_details(
                    point,
                    dist,
                    last_gas,
                    last_point,
                    first_point,
                    timing,
                    delay,
                    last_display_distance,
                )
                if point.fuel_stop():
                    last_gas = dist
                current = point.latitude, point.longitude
                dist += self._calculate_distance(previous, current)
                for extension in point.extensions:
                    for extension_point in extension.findall(
                        "gpxx:rpt", GPXTABLE_XML_NAMESPACE
                    ):
                        current = (
                            float(extension_point.get("lat")),
                            float(extension_point.get("lon")),
                        )
                        dist += self._calculate_distance(previous, current)
                        previous = current
                previous = current

            if timing:
                route_points[-1].time = timing
            if almanac := self._sun_rise_set(route_points[0], route_points[-1]):
                print(f"\n* {almanac}", file=self.output)

    def _format_output_header(self) -> str:
        header = f"\n{self.OUT_HDR}\n{self.OUT_SEP}"
        if self.display_coordinates:
            header = f"\n{self.LLP_HDR}{self.OUT_HDR}\n{self.LLP_SEP}{self.OUT_SEP}"
        return header

    @staticmethod
    def _format_time(time_s: float) -> str:
        if time_s == 0:
            return "n/a"
        minutes, seconds = divmod(time_s, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    def _format_long_length(self, length: float, units: bool = False) -> str:
        conversion_factor = KM_TO_MILES if self.imperial else 1
        unit = " mi" if self.imperial else " km"
        formatted_length = round(length / 1000.0 * conversion_factor)
        return f'{formatted_length:.0f}{unit if units else ""}'

    def _format_short_length(self, length: float, units: bool = False) -> str:
        if self.imperial:
            length_str = f"{length * M_TO_FEET:.2f}"
            unit_suffix = " ft" if units else ""
        else:
            length_str = f"{length:.2f}"
            unit_suffix = " m" if units else ""

        return length_str + unit_suffix

    def _format_speed(self, speed: Optional[float], units: bool = False) -> str:
        """speed is in kph"""
        speed = speed or 0.0
        if self.imperial:
            return f'{speed * KM_TO_MILES:.2f}{" mph" if units else ""}'
        return f'{speed:.2f}{" km/h" if units else ""}'

    def _travel_time(self, dist: float) -> timedelta:
        """distance is in meters, speed is in km/h"""
        return timedelta(minutes=dist / 1000.0 / self.speed * 60.0)

    def _sun_rise_set(
        self,
        start: Union[GPXRoutePoint, GPXTrackPoint],
        end: Union[GPXRoutePoint, GPXTrackPoint],
        delay: timedelta = timedelta(),
    ) -> str:
        """return sunrise/sunset and start & end info based upon the route start and end point"""
        if not start.time or not end.time:
            return ""

        def create_location_info(name, point):
            return astral.LocationInfo(
                name, "", "", point.latitude, point.longitude
            ).observer

        sun_start = astral.sun.sun(
            create_location_info("Start Point", start), date=start.time
        )
        sun_end = astral.sun.sun(
            create_location_info("End Point", end), date=end.time + delay
        )

        times = {
            "Sunrise": sun_start["sunrise"],
            "Sunset": sun_end["sunset"],
            "Starts": start.time,
            "Ends": end.time + delay,
        }

        retval = f"{start.time.astimezone(self.tz):%x}: " + ", ".join(
            f"{name}: {time.astimezone(self.tz):%H:%M}"
            for name, time in sorted(times.items(), key=lambda kv: kv[1])
        )
        return retval
