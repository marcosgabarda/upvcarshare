# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

import recurrence
from django.contrib.gis.geos import Point
from django.utils.timezone import make_naive
from test_plus import TestCase

from journeys import DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID
from journeys.helpers import make_point_wgs84, make_point_projected, date_to_datetime, first_day_current_week, \
    last_day_current_week, expand
from journeys.tests.factories import JourneyFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class JourneysHelpersTest(TestCase):

    def test_make_point_wgs84(self):
        point = Point(882386.0414109999546781, 545432.4779989999951795, srid=DEFAULT_PROJECTED_SRID)
        new_point = make_point_wgs84(point)
        self.assertIsInstance(new_point, Point)

    def test_make_point_projected(self):
        point = Point(-0.40078639978073005, 39.461212909677464, srid=DEFAULT_WGS84_SRID)
        new_point = make_point_projected(point)
        self.assertIsInstance(new_point, Point)

    def test_date_to_datetime(self):
        date = datetime.datetime.today()
        self.assertIsInstance(date_to_datetime(date), datetime.date)

    def test_first_day_current_week(self):
        self.assertIsInstance(first_day_current_week(), datetime.date)

    def test_last_day_current_week(self):
        self.assertIsInstance(last_day_current_week(), datetime.date)

    def test_expand(self):
        journey = JourneyFactory()
        journey.departure = journey.departure.replace(month=1)
        journey.save()

        rule = recurrence.Rule(recurrence.DAILY)
        pattern = recurrence.Recurrence(
            dtstart=make_naive(journey.departure) + datetime.timedelta(days=1),
            dtend=make_naive(journey.departure) + datetime.timedelta(days=20),
            rrules=[rule, ]
        )

        journey.recurrence = pattern
        journey.save()
        journeys = expand(journey)
        self.assertEquals(22, len(journeys))

    def test_expand_september(self):
        journey = JourneyFactory()
        journey.departure = journey.departure.replace(day=1, month=9)
        journey.save()

        rule = recurrence.Rule(recurrence.DAILY)
        pattern = recurrence.Recurrence(
            dtstart=make_naive(journey.departure) + datetime.timedelta(days=1),
            dtend=make_naive(journey.departure) + datetime.timedelta(days=20),
            rrules=[rule, ]
        )

        journey.recurrence = pattern
        journey.save()
        journeys = expand(journey)
        self.assertEquals(22, len(journeys))
