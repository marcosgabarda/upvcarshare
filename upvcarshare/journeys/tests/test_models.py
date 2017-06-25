# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from test_plus.test import TestCase

from journeys import GOING, RETURN, DEFAULT_PROJECTED_SRID
from journeys.exceptions import AlreadyAPassenger, NotAPassenger
from journeys.helpers import expand
from journeys.models import Journey, Passenger, Residence, JourneyTemplate
from journeys.tests.factories import ResidenceFactory, CampusFactory, TransportFactory, JourneyFactory, \
    JourneyTemplateFactory
from users.tests.factories import UserFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class JourneyTest(TestCase):
    """Test related with Journey model and manager methods."""

    @staticmethod
    def _make_journey(kind=GOING):
        user = UserFactory()
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplateFactory(user=user, residence=origin, campus=destination, kind=kind)
        return JourneyFactory(template=template)

    def test_smart_create_no_transport(self):
        """Test smart create of a journey without transport."""
        user = UserFactory()
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplate.objects.smart_create(
            user=user, origin=origin, destination=destination, departure=timezone.now() + datetime.timedelta(days=1)
        )
        journeys = expand(template)
        journey = journeys[0]
        self.assertEquals(Journey.objects.count(), 1)
        self.assertEquals(Journey.objects.first(), journey)

    def test_smart_create(self):
        """Test smart create of a journey with transport."""
        user = UserFactory()
        transport = TransportFactory(user=user)
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplate.objects.smart_create(
            user=user, origin=origin, destination=destination, departure=timezone.now() + datetime.timedelta(days=1),
            transport=transport
        )
        journeys = expand(template)
        journey = journeys[0]
        self.assertEquals(Journey.objects.count(), 1)
        self.assertEquals(Journey.objects.first(), journey)
        self.assertEquals(journey.free_places, transport.default_places)
        self.assertEquals(journey.current_free_places(), transport.default_places)
        self.assertIsNotNone(journey.driver)
        self.assertEquals(user, journey.driver)

    def test_origin(self):
        user = UserFactory()
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplateFactory(user=user, residence=origin, campus=destination, kind=GOING)
        journey = JourneyFactory(template=template)
        self.assertEquals(journey.origin, origin)

    def test_destination(self):
        user = UserFactory()
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplateFactory(user=user, residence=origin, campus=destination, kind=GOING)
        journey = JourneyFactory(template=template)
        self.assertEquals(journey.destination, destination)

    def test_join_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        self.assertIsInstance(journey.join_passenger(user), Passenger)
        self.assertFalse(journey.is_passenger(user))
        self.assertEquals(journey.count_passengers(), 0)

    def test_join_and_confirm_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        self.assertIsInstance(journey.join_passenger(user), Passenger)
        journey.confirm_passenger(user)
        self.assertTrue(journey.is_passenger(user))
        self.assertEquals(journey.count_passengers(), 1)

    def test_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        journey.join_passenger(user)
        self.assertEquals(1, Journey.objects.passenger(user).count())

    def test_join_already_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        journey.join_passenger(user)
        try:
            journey.join_passenger(user)
            raised_exception = False
        except AlreadyAPassenger:
            raised_exception = True
        self.assertTrue(raised_exception)

    def test_leave_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        journey.join_passenger(user)
        journey.confirm_passenger(user)
        journey.leave_passenger(user)
        self.assertFalse(journey.is_passenger(user))

    def test_leave_no_passenger(self):
        user = UserFactory()
        journey = self._make_journey()
        try:
            journey.leave_passenger(user)
            raised_exception = False
        except NotAPassenger:
            raised_exception = True
        self.assertTrue(raised_exception)

    def test_available_going_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        # Creates a journey without driver
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(882454.58, 545877.33, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user3, residence=residence3, campus=campus)
        JourneyFactory(template=template)
        self.assertEquals(Journey.objects.available(user=user3, kind=GOING).count(), 2)

    def test_available_return_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus, kind=RETURN)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        # Creates a journey without driver
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545877.33, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user3, residence=residence3, campus=campus, kind=RETURN)
        JourneyFactory(template=template)
        self.assertEquals(Journey.objects.available(user=user3, kind=RETURN).count(), 1)

    def test_available_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus, kind=RETURN)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        # Creates a journey without driver
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545274.90, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user3, residence=residence3, campus=campus, kind=RETURN)
        JourneyFactory(template=template)
        self.assertEquals(Journey.objects.available(user=user3).count(), 2)

    def test_nearby_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545274.90, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user3, driver=user3, residence=residence3, campus=campus)
        JourneyFactory(template=template)
        point = Point(882532.74, 545437.43, srid=DEFAULT_PROJECTED_SRID)
        self.assertEquals(Journey.objects.nearby(
            geometry=point,
            distance=D(m=2500)
        ).count(), 2)

    def test_nearby_going_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545274.90, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user3, driver=user3, residence=residence3, campus=campus)
        JourneyFactory(template=template)
        point = Point(882532.74, 545437.43, srid=DEFAULT_PROJECTED_SRID)
        self.assertEquals(Journey.objects.nearby(
            geometry=point,
            distance=D(m=2500),
            kind=GOING
        ).count(), 2)

    def test_recommended_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545274.90, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user3, driver=user3, residence=residence3, campus=campus)
        JourneyFactory(template=template)
        user4 = UserFactory()
        residence4 = ResidenceFactory(
            user=user4, position=Point(882532.74, 545437.43, srid=DEFAULT_PROJECTED_SRID), distance=2500
        )
        template = JourneyTemplateFactory(user=user4, residence=residence4, campus=campus)
        JourneyFactory(template=template)
        self.assertEquals(Journey.objects.recommended(
            user=user4,
        ).count(), 2)

    def test_recommended_going_query(self):
        # Creates the available journeys with driver...
        user1 = UserFactory()
        residence1 = ResidenceFactory(user=user1, position=Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
        user2 = UserFactory()
        residence2 = ResidenceFactory(user=user2, position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        campus = CampusFactory()
        user3 = UserFactory()
        residence3 = ResidenceFactory(user=user3, position=Point(865621.24, 545274.90, srid=DEFAULT_PROJECTED_SRID))
        template = JourneyTemplateFactory(user=user1, driver=user1, residence=residence1, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user2, driver=user2, residence=residence2, campus=campus)
        JourneyFactory(template=template)
        template = JourneyTemplateFactory(user=user3, driver=user3, residence=residence3, campus=campus)
        JourneyFactory(template=template)
        user4 = UserFactory()
        residence4 = ResidenceFactory(
            user=user4, position=Point(882532.74, 545437.43, srid=DEFAULT_PROJECTED_SRID), distance=2500
        )
        template = JourneyTemplateFactory(user=user4, residence=residence4, campus=campus)
        JourneyFactory(template=template)
        self.assertEquals(Journey.objects.recommended(
            user=user4,
            kind=GOING
        ).count(), 2)

    def test_cancel_journey(self):
        journey = self._make_journey()
        journey.cancel()
        self.assertTrue(Journey.objects.get(pk=journey.pk).disabled)


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class ResidenceTest(TestCase):

    def test_smart_create(self):
        user = UserFactory(
            default_address="bar",
            default_position=Point(882532.74, 545437.43, srid=DEFAULT_PROJECTED_SRID)
        )
        residence = Residence.objects.smart_create(user)
        self.assertIsInstance(residence, Residence)
