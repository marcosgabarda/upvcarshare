# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime
import factory
from django.contrib.gis.geos import Point
from django.utils import timezone

from journeys import GOING, DEFAULT_PROJECTED_SRID
from users.tests.factories import UserFactory


class ResidenceFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    position = factory.LazyFunction(lambda: Point(883877.34, 547084.05, srid=DEFAULT_PROJECTED_SRID))
    distance = 500

    class Meta:
        model = "journeys.Residence"


class CampusFactory(factory.django.DjangoModelFactory):
    name = "Vera"
    position = factory.LazyFunction(lambda: Point(887483.60, 547842.30, srid=DEFAULT_PROJECTED_SRID))
    distance = 500

    class Meta:
        model = "journeys.Campus"


class JourneyFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    residence = factory.SubFactory(ResidenceFactory)
    campus = factory.SubFactory(CampusFactory)
    departure = factory.LazyFunction(lambda: timezone.now() + datetime.timedelta(days=1))
    kind = GOING

    class Meta:
        model = "journeys.Journey"


class TransportFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = "journeys.Transport"
