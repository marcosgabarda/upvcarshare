# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import six
from django.contrib.gis.geos import Point
from rest_framework import status
from rest_framework.test import APITestCase

from journeys import DEFAULT_PROJECTED_SRID
from users.models import User
from users.tests.factories import UserFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class UsersAPITests(APITestCase):

    def test_get_current_user(self):
        user = UserFactory(default_position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        url = "/api/v1/users/me/"
        self.client.force_authenticate(user=user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_current_user(self):
        user = UserFactory(default_position=Point(882823.07, 545542.48, srid=DEFAULT_PROJECTED_SRID))
        url = "/api/v1/users/me/"
        self.client.force_authenticate(user=user)
        data = {
            "default_address": "foo",
            "default_position": {
                "type": "Point",
                "coordinates": [-0.37677, 39.46914]
            }
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=user.pk)
        self.assertEquals(
            "SRID=4326;POINT (-0.3767699999999994 39.4691399999998)",
            six.text_type(user.get_default_position_wgs84())
        )
        self.assertEquals("foo", user.default_address)
