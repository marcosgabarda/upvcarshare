# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from test_plus import TestCase

from journeys import GOING
from journeys.tests.factories import CampusFactory, JourneyTemplateFactory
from journeys.tests.factories import ResidenceFactory, JourneyFactory
from notifications import JOIN, LEAVE
from notifications.models import Notification
from users.tests.factories import UserFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class NotificationTests(TestCase):

    @staticmethod
    def _make_journey(user=None, kind=GOING):
        user = UserFactory() if user is None else user
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        template = JourneyTemplateFactory(user=user, residence=origin, campus=destination, kind=kind)
        return JourneyFactory(template=template)

    def test_join_generation(self):
        initial_user = UserFactory()
        user = UserFactory()
        journey = self._make_journey(initial_user)
        journey.join_passenger(user)
        self.assertEquals(1, Notification.objects.filter(user=initial_user, verb=JOIN).count())

    def test_leave_generation(self):
        initial_user = UserFactory()
        user = UserFactory()
        journey = self._make_journey(initial_user)
        journey.join_passenger(user)
        journey.confirm_passenger(user)
        journey.leave_passenger(user)
        self.assertEquals(1, Notification.objects.filter(user=initial_user, verb=JOIN).count())
        self.assertEquals(1, Notification.objects.filter(user=initial_user, verb=LEAVE).count())
