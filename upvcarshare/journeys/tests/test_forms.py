# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime
import six
from test_plus import TestCase

from journeys import DEFAULT_PROJECTED_SRID, DEFAULT_GOOGLE_MAPS_SRID
from journeys.forms import SearchJourneyForm
from journeys.helpers import make_point
from journeys.tests.factories import JourneyFactory
from users.tests.factories import UserFactory


class JourneysFormsTest(TestCase):

    def test_search_form(self):
        user = UserFactory()
        JourneyFactory(departure=datetime.datetime.now() + datetime.timedelta(days=2), user=user, driver=user)
        journey = JourneyFactory(user=user, driver=user)

        data = {
            "departure": journey.departure,
            "distance": 1000,
            "time_window": 30,
            "position": six.text_type(make_point(
                journey.residence.position,
                origin_coord_srid=DEFAULT_PROJECTED_SRID,
                destiny_coord_srid=DEFAULT_GOOGLE_MAPS_SRID
            ))
        }
        form = SearchJourneyForm(data)
        self.assertTrue(form.is_valid())
        results = form.search(UserFactory())
        self.assertEquals(1, results.count())
