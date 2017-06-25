# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import floppyforms
from django import forms
from django.contrib.gis import admin

from core.widgets import OsmPointWidget
from journeys import DEFAULT_GOOGLE_MAPS_SRID, DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID
from journeys.helpers import make_point_projected, make_point
from journeys.models import Residence, Journey, Campus, Message, Transport, \
    Passenger, JourneyTemplate


class PlaceAdminForm(forms.ModelForm):

    position = floppyforms.gis.PointField(widget=OsmPointWidget(), srid=DEFAULT_WGS84_SRID)

    class Meta:
        model = Residence
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(PlaceAdminForm, self).__init__(*args, **kwargs)
        self.initial["position"] = make_point(
            self.initial["position"],
            origin_coord_srid=DEFAULT_PROJECTED_SRID,
            destiny_coord_srid=DEFAULT_WGS84_SRID
        )

    def clean_position(self):
        position = self.cleaned_data["position"]
        position = make_point_projected(position, origin_coord_srid=DEFAULT_WGS84_SRID)
        return position

    def save(self, commit=True):
        return super(PlaceAdminForm, self).save(commit=commit)


class ResidenceAdminForm(PlaceAdminForm):
    class Meta:
        model = Residence
        fields = "__all__"


class CampusAdminForm(PlaceAdminForm):
    class Meta:
        model = Campus
        fields = "__all__"


@admin.register(Residence)
class ResidenceAdminForm(admin.GeoModelAdmin):
    list_display = ["id", "user", "name", "address", "position", "created"]
    form = ResidenceAdminForm


@admin.register(Campus)
class CampusAdminForm(admin.GeoModelAdmin):
    list_display = ["id", "name", "position", "created"]
    form = CampusAdminForm


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ["id", "departure", "created"]


@admin.register(JourneyTemplate)
class JourneyAdmin(admin.ModelAdmin):
    list_display = ["id", "residence", "campus", "kind", "created"]


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "journey", "departure", "status", "created"]

    def departure(self, instance):
        return instance.journey.departure


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "journey", "content", "created"]


@admin.register(Transport)
class TransportAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "name", "default_places", "brand", "model",
                    "color", "created"]
