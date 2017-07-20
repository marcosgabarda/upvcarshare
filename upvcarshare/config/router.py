# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter

from journeys.api.v1.resources import TransportResource, ResidenceResource, CampusResource, JourneyResource, \
    join_journey, leave_journey, recommended_journeys, cancel_journey, journey_messages, MessageResource, \
    confirm_journey, reject_journey, recurrence_journeys
from notifications.api.v1.resources import NotificationResource
from users.api.v1.resources import me, UserResource

router = SimpleRouter()

router.register(r'users', viewset=UserResource)
router.register(r'transports', viewset=TransportResource)
router.register(r'residences', viewset=ResidenceResource)
router.register(r'campus', viewset=CampusResource)
router.register(r'messages', viewset=MessageResource)
router.register(r'journeys', viewset=JourneyResource)
router.register(r'notifications', viewset=NotificationResource)

urlpatterns = [
    url(r'^journeys/recommended/$', recommended_journeys, kwargs={'pk': None}, name='all-recommended-journeys'),
    url(r'^journeys/(?P<pk>[^/.]+)/cancel/$', cancel_journey, name='cancel-journeys'),
    url(r'^journeys/(?P<pk>[^/.]+)/recommended/$', recommended_journeys, name='recommended-journeys'),
    url(r'^journeys/(?P<pk>[^/.]+)/recurrence/$', recurrence_journeys, name='recurrence-journeys'),
    url(r'^journeys/(?P<pk>[^/.]+)/join/$', join_journey, name='join-journey'),
    url(r'^journeys/(?P<pk>[^/.]+)/confirm/$', confirm_journey, name='confirm-journey'),
    url(r'^journeys/(?P<pk>[^/.]+)/reject/$', reject_journey, name='reject-journey'),
    url(r'^journeys/(?P<pk>[^/.]+)/leave/$', leave_journey, name='leave-journey'),
    url(r'^journeys/(?P<pk>[^/.]+)/messages/$', journey_messages, name='journey-messages'),
    url(r'^users/me/$', me, kwargs={'pk': 'me'}),
    url(r'^', include(router.urls)),
]
