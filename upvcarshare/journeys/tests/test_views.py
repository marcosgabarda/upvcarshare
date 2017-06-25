# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

from django.utils import timezone
from test_plus import TestCase

from journeys import GOING, RETURN
from journeys.models import Journey, Residence, Passenger
from journeys.tests.factories import JourneyFactory, ResidenceFactory, CampusFactory, JourneyTemplateFactory
from users.tests.factories import UserFactory
from users.tests.mocks import UPVLoginDataService

try:
    import unittest.mock as mock
except ImportError:
    import mock


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class JourneyViewTests(TestCase):
    user_factory = UserFactory

    def test_get_create_journey(self):
        user = self.make_user(username="foo")
        url_name = "journeys:create"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_post_create_journey(self):
        user = self.make_user(username="foo")
        self.assertLoginRequired("journeys:create")
        with self.login(user):
            data = {
                "origin": "residence:%s" % ResidenceFactory(user=user).pk,
                "destiny": "campus:%s" % CampusFactory().pk,
                "free_places": 4,
                "time_window": 30,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": "",
            }
            response = self.post(url_name="journeys:create", data=data)
            self.response_302(response)
            self.assertEquals(1, Journey.objects.count())

    def test_post_create_arrival_journey(self):
        user = self.make_user(username="foo")
        self.assertLoginRequired("journeys:create")
        with self.login(user):
            data = {
                "origin": "residence:%s" % ResidenceFactory(user=user).pk,
                "destiny": "campus:%s" % CampusFactory().pk,
                "free_places": 4,
                "time_window": 30,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "arrival": (timezone.now() + datetime.timedelta(days=1, minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": "",
            }
            response = self.post(url_name="journeys:create", data=data)
            self.response_302(response)
            self.assertEquals(1, Journey.objects.count())

    def test_post_create_bad_arrival_journey(self):
        user = self.make_user(username="foo")
        self.assertLoginRequired("journeys:create")
        with self.login(user):
            data = {
                "origin": "residence:%s" % ResidenceFactory(user=user).pk,
                "destiny": "campus:%s" % CampusFactory().pk,
                "free_places": 4,
                "time_window": 30,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "arrival": (timezone.now() + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": "",
            }
            response = self.post(url_name="journeys:create", data=data)
            self.response_200(response)
            self.assertEquals(0, Journey.objects.count())

    def test_post_create_bad_departure_journey(self):
        user = self.make_user(username="foo")
        self.assertLoginRequired("journeys:create")
        with self.login(user):
            data = {
                "origin": "residence:%s" % ResidenceFactory(user=user).pk,
                "destiny": "campus:%s" % CampusFactory().pk,
                "free_places": 4,
                "time_window": 30,
                "departure": (timezone.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "arrival": (timezone.now() + datetime.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": "",
            }
            response = self.post(url_name="journeys:create", data=data)
            self.response_200(response)
            self.assertEquals(0, Journey.objects.count())

    def test_get_edit_journey(self):
        user = self.make_user(username="foo")
        journey = JourneyFactory(template=JourneyTemplateFactory(user=user))
        url_name = "journeys:edit"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            response = self.get(url_name, pk=journey.pk)
            self.response_200(response=response)

    def test_post_edit_journey(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user, kind=GOING)
        journey = JourneyFactory(template=template)
        url_name = "journeys:edit"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            data = {
                # "residence": ResidenceFactory(user=user).pk,
                # "campus": CampusFactory().pk,
                # "kind": RETURN,
                "free_places": 3,
                # "time_window": 30,
                "departure": (timezone.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                "recurrence": "",
            }
            response = self.post(url_name=url_name, pk=journey.pk, data=data)
            self.response_302(response=response)
            journey = Journey.objects.get(pk=journey.pk)
            self.assertEquals(data["free_places"], journey.free_places)

    def test_get_recommended_journey(self):
        user = self.make_user(username="foo")
        url_name = "journeys:recommended"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_get_recommended_journey_filter(self):
        user = self.make_user(username="foo")
        url_name = "journeys:recommended"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name, data={"distance": 200, "kind": GOING})
            self.response_200(response=response)

    def test_get_list_journey(self):
        user = self.make_user(username="foo")
        url_name = "journeys:list"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_post_join(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user, kind=GOING)
        journey = JourneyFactory(template=template)
        url_name = "journeys:join"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            response = self.post(url_name=url_name, pk=journey.pk)
            self.response_302(response=response)

    def test_post_join_recurrence_all(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user, kind=GOING)
        journey = JourneyFactory(template=template)
        journeys = [JourneyFactory(template=template) for _ in range(10)]
        url_name = "journeys:join"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            data = {
                "join_to": "all"
            }
            response = self.post(url_name=url_name, pk=journey.pk, data=data)
            self.response_302(response=response)
            self.assertEquals(len(journeys) + 1, Passenger.objects.count())

    def test_post_join_recurrence_one(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user, kind=GOING)
        journey = JourneyFactory(template=template)
        [JourneyFactory(template=template) for _ in range(10)]
        url_name = "journeys:join"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            data = {
                "join_to": "one"
            }
            response = self.post(url_name=url_name, pk=journey.pk, data=data)
            self.response_302(response=response)
            self.assertEquals(1, Passenger.objects.count())

    def test_post_leave(self):
        user = self.make_user(username="foo")
        journey = JourneyFactory(template=JourneyTemplateFactory(user=user))
        journey.join_passenger(user)
        url_name = "journeys:leave"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            response = self.post(url_name=url_name, pk=journey.pk)
            self.response_302(response=response)

    def test_post_throw_out(self):
        user = self.make_user(username="foo")
        journey = JourneyFactory(template=JourneyTemplateFactory(user=user))
        passenger = journey.join_passenger(user)
        url_name = "journeys:throw-out"
        self.assertLoginRequired(url_name, pk=passenger.pk)
        with self.login(user):
            response = self.post(url_name=url_name, pk=passenger.pk)
            self.response_302(response=response)

    def test_cancel_journey(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user)
        journey = JourneyFactory(template=template)
        url_name = "journeys:cancel"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            response = self.get(url_name, pk=journey.pk)
            self.response_200(response=response)

    def test_post_cancel_journey(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user)
        journey = JourneyFactory(template=template)
        url_name = "journeys:cancel"
        self.assertLoginRequired(url_name, pk=journey.pk)
        with self.login(user):
            response = self.post(url_name, pk=journey.pk)
            self.response_302(response=response)
            self.assertTrue(Journey.objects.get(pk=journey.pk).disabled)

    def test_delete_journey(self):
        user = self.make_user(username="foo")
        journeys = [JourneyFactory(template=JourneyTemplateFactory(user=user)) for _ in range(10)]
        journey = JourneyFactory(template=JourneyTemplateFactory(user=user))
        url_name = "journeys:delete"
        self.assertLoginRequired(url_name, pk=journey.pk)
        self.assertEquals(len(journeys) + 1, Journey.objects.count())
        with self.login(user):
            response = self.get(url_name, pk=journey.pk)
            self.response_302(response=response)
            self.assertFalse(Journey.objects.filter(pk=journey.pk).exists())
            self.assertEquals(len(journeys), Journey.objects.count())

    def test_delete_parent_journeys(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user)
        journey = JourneyFactory(template=template)
        journeys = [JourneyFactory(template=template) for _ in range(10)]
        url_name = "journeys:delete"
        self.assertLoginRequired(url_name, pk=journey.pk)
        self.assertEquals(len(journeys) + 1, Journey.objects.count())
        with self.login(user):
            response = self.get(url_name, pk=journey.pk)
            self.response_302(response=response)
            self.assertFalse(Journey.objects.filter(pk=journey.pk).exists())
            self.assertEquals(len(journeys), Journey.objects.count())

    def test_delete_all_journeys(self):
        user = self.make_user(username="foo")
        template = JourneyTemplateFactory(user=user)
        journey = JourneyFactory(template=template)
        journeys = [JourneyFactory(template=template) for _ in range(10)]
        other_journeys = [JourneyFactory() for _ in range(5)]
        url_name = "journeys:delete-all"
        self.assertLoginRequired(url_name, pk=journey.pk)
        self.assertEquals(len(journeys) + len(other_journeys) + 1, Journey.objects.count())
        with self.login(user):
            response = self.get(url_name, pk=journey.pk)
            self.response_302(response=response)
            self.assertFalse(Journey.objects.filter(pk=journey.pk).exists())
            self.assertEquals(len(other_journeys), Journey.objects.count())


@mock.patch('users.models.UPVLoginDataService', new=UPVLoginDataService)
class ResidenceViewTests(TestCase):
    user_factory = UserFactory

    def test_get_create_residence(self):
        user = self.make_user(username="foo")
        url_name = "journeys:create-residence"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_post_create_residence(self):
        user = self.make_user(username="foo")
        self.assertLoginRequired("journeys:create-residence")
        with self.login(user):
            data = {
                "name": "Home",
                "address": "foo",
                "position": "POINT (-0.3819 39.4625)",
                "distance": 500,
            }
            response = self.post(url_name="journeys:create-residence", data=data)
            self.response_302(response)
            self.assertEquals(1, Residence.objects.count())

    def test_get_edit_residence(self):
        user = self.make_user(username="foo")
        residence = ResidenceFactory(user=user)
        url_name = "journeys:edit-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(user):
            response = self.get(url_name, pk=residence.pk)
            self.response_200(response=response)

    def test_post_edit_residence(self):
        user = self.make_user(username="foo")
        residence = ResidenceFactory(user=user)
        url_name = "journeys:edit-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(user):
            data = {
                "name": "Home",
                "address": "bar",
                "position": "POINT (-0.3819 39.4625)",
                "distance": 500
            }
            response = self.post(url_name=url_name, pk=residence.pk, data=data)
            self.response_302(response=response)
            residence = Residence.objects.get(pk=residence.pk)
            self.assertEquals(data["address"], residence.address)

    def test_residences(self):
        user = self.make_user(username="foo")
        ResidenceFactory(user=user)
        url_name = "journeys:residences"
        self.assertLoginRequired(url_name)
        with self.login(user):
            response = self.get(url_name)
            self.response_200(response=response)

    def test_delete_residence(self):
        user = self.make_user(username="foo")
        residence = ResidenceFactory(user=user)
        url_name = "journeys:delete-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(user):
            response = self.get(url_name, pk=residence.pk)
            self.response_302(response=response)

    def test_no_delete_residence(self):
        initial_user = self.make_user(username="foo")
        user = UserFactory()
        residence = ResidenceFactory(user=initial_user)
        url_name = "journeys:delete-residence"
        self.assertLoginRequired(url_name, pk=residence.pk)
        with self.login(user):
            response = self.get(url_name, pk=residence.pk)
            self.response_404(response=response)
