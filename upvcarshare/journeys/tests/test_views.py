# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

from django.utils import timezone
from test_plus import TestCase

from journeys import GOING, RETURN
from journeys.models import Journey, Residence
from journeys.tests.factories import JourneyFactory, ResidenceFactory, CampusFactory
from users.tests.factories import UserFactory


class JourneyViewTests(TestCase):
    user_factory = UserFactory

    def setUp(self):
        self.user = self.make_user(username="foo")

    def test_get_create_journey(self):
        url_name = "journeys:create"
        self.assertLoginRequired(url_name)
        with self.login(self.user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_post_create_journey(self):
        self.assertLoginRequired("journeys:create")
        with self.login(self.user):
            data = {
                "residence": ResidenceFactory(user=self.user).pk,
                "campus": CampusFactory().pk,
                "kind": GOING,
                "free_places": 4,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            }
            response = self.post(url_name="journeys:create", data=data)
            self.response_200(response)
            self.assertEquals(1, Journey.objects.count())

    def test_get_edit_journey(self):
        journey = JourneyFactory(user=self.user)
        url_name = "journeys:edit"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(self.user):
            response = self.get(url_name, pk=journey.pk)
            self.response_200(response=response)

    def test_post_edit_journey(self):
        journey = JourneyFactory(user=self.user, kind=GOING)
        url_name = "journeys:edit"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(self.user):
            data = {
                "residence": ResidenceFactory(user=self.user).pk,
                "campus": CampusFactory().pk,
                "kind": RETURN,
                "free_places": 4,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            }
            response = self.post(url_name=url_name, pk=journey.pk, data=data)
            self.response_200(response=response)
            journey = Journey.objects.get(pk=journey.pk)
            self.assertEquals(RETURN, journey.kind)

    def test_get_recommended_journey(self):
        url_name = "journeys:recommended"
        self.assertLoginRequired(url_name)
        with self.login(self.user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_get_user_list_journey(self):
        url_name = "journeys:user-list"
        self.assertLoginRequired(url_name)
        with self.login(self.user):
            response = self.get(url_name)
            self.response_200(response=response)


class ResidenceViewTests(TestCase):
    user_factory = UserFactory

    def setUp(self):
        self.user = self.make_user(username="foo")

    def test_get_create_residence(self):
        url_name = "journeys:create-residence"
        self.assertLoginRequired(url_name)
        with self.login(self.user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_post_create_residence(self):
        self.assertLoginRequired("journeys:create-residence")
        with self.login(self.user):
            data = {
                "name": "Home",
                "address": "foo",
                "position": "POINT (-0.3819 39.4625)",
                "distance": 500,
            }
            response = self.post(url_name="journeys:create-residence", data=data)
            self.response_200(response)
            self.assertEquals(1, Residence.objects.count())

    def test_get_edit_residence(self):
        residence = ResidenceFactory(user=self.user)
        url_name = "journeys:edit-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(self.user):
            response = self.get(url_name, pk=residence.pk)
            self.response_200(response=response)

    def test_post_edit_residence(self):
        residence = ResidenceFactory(user=self.user)
        url_name = "journeys:edit-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(self.user):
            data = {
                "name": "Home",
                "address": "bar",
                "position": "POINT (-0.3819 39.4625)",
                "distance": 500
            }
            response = self.post(url_name=url_name, pk=residence.pk, data=data)
            self.response_200(response=response)
            residence = Residence.objects.get(pk=residence.pk)
            self.assertEquals(data["address"], residence.address)
