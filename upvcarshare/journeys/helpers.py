# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime
from copy import copy

from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.utils import timezone
from django.utils.timezone import make_aware

from journeys import DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID


def make_point(point, origin_coord_srid, destiny_coord_srid):
    origin_coord = SpatialReference(origin_coord_srid)
    destination_coord = SpatialReference(destiny_coord_srid)
    trans = CoordTransform(origin_coord, destination_coord)
    transformed_point = copy(point)
    transformed_point.transform(trans)
    return transformed_point


def make_point_wgs84(point, origin_coord_srid=DEFAULT_PROJECTED_SRID):
    """Gets a copy of the given point on WGS84 coordinates system."""
    return make_point(point, origin_coord_srid=origin_coord_srid, destiny_coord_srid=DEFAULT_WGS84_SRID)


def make_point_projected(point, origin_coord_srid=DEFAULT_WGS84_SRID):
    """Gets a copy of the given point on projected coordinates system."""
    return make_point(point, origin_coord_srid=origin_coord_srid, destiny_coord_srid=DEFAULT_PROJECTED_SRID)


def date_to_datetime(date):
    """Converts a date into time date."""
    if isinstance(date, datetime.date):
        date = datetime.datetime.combine(date, time=datetime.time(0, 0, 0, 0))
    return date


def first_day_current_week():
    """Gets the first date of the current week."""
    today = timezone.now().date()
    date = date_to_datetime(today)
    return date - datetime.timedelta(days=date.weekday())


def last_day_current_week():
    """Gets the first date of the week."""
    return first_day_current_week() + datetime.timedelta(days=7)


def default_until(today):
    finish_date = today.replace(day=1, month=9)
    if today.month >= 9:
        finish_date = finish_date.replace(year=finish_date.year + 1)
    return finish_date


def expand(journey_template):
    """Expands given journey using recurrence field to create new journeys."""
    recurrence_dates = journey_template.recurrence_dates()
    journeys = []
    for dates in recurrence_dates:
        journeys.append(
            journey_template.create_journey(
                departure=dates[0],
                arrival=dates[1]
            )
        )
    return journeys
