# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from journeys import DEFAULT_WGS84_SRID
from journeys.helpers import make_point_projected
from journeys.models import Transport, Place, Residence, Campus, Journey, Message
from notifications import MESSAGE
from notifications.decorators import dispatch
from users.api.v1.serializers import UserSerializer


class TransportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transport
        exclude = ["user"]


class PlaceSerializer(serializers.ModelSerializer):

    position = GeometryField(source="get_position_wgs84")

    class Meta:
        model = Place
        fields = ["id", "name", "distance", "position"]

    def validate(self, attrs):
        if 'get_position_wgs84' in attrs:
            position = attrs.pop('get_position_wgs84')
            position.srid = DEFAULT_WGS84_SRID
            attrs['position'] = make_point_projected(position)
        return attrs


class ResidenceSerializer(PlaceSerializer):

    class Meta(PlaceSerializer.Meta):
        model = Residence
        fields = ["id", "name", "distance", "position", "address"]


class CampusSerializer(PlaceSerializer):

    class Meta(PlaceSerializer.Meta):
        model = Campus


class JourneySerializer(serializers.HyperlinkedModelSerializer):

    title = serializers.CharField(source="get_title", read_only=True)
    start = serializers.CharField(source="get_start", read_only=True)
    end = serializers.CharField(source="get_end", read_only=True)

    current_free_places = serializers.IntegerField()

    class Meta:
        model = Journey
        fields = [
            "id",
            "title",
            "kind",
            "free_places",
            "departure",
            "arrival",
            "start",
            "end",
            "disabled",
            "current_free_places",
        ]


class MessageSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    journey = serializers.PrimaryKeyRelatedField(queryset=Journey.objects.all())

    class Meta:
        model = Message
        fields = ["id", "user", "journey", "content", "created"]

    @dispatch(MESSAGE)
    def save(self, **kwargs):
        return super(MessageSerializer, self).save(**kwargs)
