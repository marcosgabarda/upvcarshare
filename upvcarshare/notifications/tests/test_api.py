# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import json

import random
from rest_framework import status
from rest_framework.test import APITestCase

from journeys import GOING
from journeys.tests.factories import CampusFactory, JourneyFactory, JourneyTemplateFactory
from journeys.tests.factories import ResidenceFactory
from notifications import JOIN
from notifications import LEAVE
from notifications.tests.factories import NotificationFactory
from users.tests.factories import UserFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class NotificationAPITests(APITestCase):

    @staticmethod
    def _make_journey(user=None, kind=GOING):
        user = UserFactory() if user is None else user
        origin = ResidenceFactory(user=user)
        destination = CampusFactory()
        return JourneyFactory(
            template=JourneyTemplateFactory(user=user, residence=origin, campus=destination, kind=kind)
        )

    def test_get_notifications(self):
        user = UserFactory()
        [NotificationFactory(
            user=user,
            verb=random.choice([JOIN, LEAVE]),
            actor=UserFactory(),
            target=self._make_journey(user)
        ) for _ in range(5)]
        [NotificationFactory(
            user=UserFactory(),
            verb=random.choice([JOIN, LEAVE]),
            actor=UserFactory(),
            target=self._make_journey(user)
        ) for _ in range(5)]
        url = "/api/v1/notifications/"
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertEquals(5, len(response_data['results']))
