# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

import floppyforms
from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from journeys import JOURNEY_KINDS, GOING, RETURN, DEFAULT_GOOGLE_MAPS_SRID, \
    DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID
from journeys.helpers import expand, make_point
from journeys.models import Residence, Journey, Campus, Transport
from users.models import User


class ResidenceForm(forms.ModelForm):
    """Form to edit and create residences."""

    position = forms.CharField(
        label=_("Posición en el mapa"),
        help_text=_("Selecciona la posición en el mapa y establece el radio máximo al que te quieres desplazar"),
        widget=forms.HiddenInput()
    )
    distance = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = Residence
        fields = ["name", "address", "position", "distance"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
        }

    def clean_position(self):
        position = self.cleaned_data["position"]
        position_point = GEOSGeometry(position, srid=DEFAULT_WGS84_SRID)
        position_projected_point = make_point(
            position_point, origin_coord_srid=DEFAULT_WGS84_SRID, destiny_coord_srid=DEFAULT_PROJECTED_SRID
        )
        return position_projected_point

    def clean_distance(self):
        distance = self.cleaned_data["distance"]
        return int(distance)

    def save(self, commit=True, **kwargs):
        """When save a residence form, you have to provide an user."""
        assert "user" in kwargs
        assert isinstance(kwargs["user"], User)
        residence = super(ResidenceForm, self).save(commit=False)
        residence.user = kwargs.get("user")
        if commit:
            residence.save()
        return residence


class JourneyForm(forms.ModelForm):

    i_am_driver = forms.BooleanField(
        label=_("¿Eres conductor?"),
        required=False,
        initial=False,
        widget=forms.RadioSelect(
            choices=((True, _('Sí')), (False, _('No'))),
        )
    )

    class Meta:
        model = Journey
        fields = ["residence", "campus", "kind", "i_am_driver", "transport", "free_places", "departure", "time_window",
                  "arrival", "recurrence"]
        widgets = {
            "transport": forms.Select(attrs={"class": "form-control"}),
            "residence": forms.Select(attrs={"class": "form-control"}),
            "campus": forms.Select(attrs={"class": "form-control"}),
            "kind": forms.Select(attrs={"class": "form-control"}),
            "free_places": forms.NumberInput(attrs={"class": "form-control"}),
            "departure": floppyforms.DateTimeInput(attrs={"class": "form-control"}),
            "arrival": floppyforms.DateTimeInput(attrs={"class": "form-control"}),
            "time_window": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(JourneyForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['residence'].queryset = Residence.objects.filter(user=self.user)
            self.fields['transport'].queryset = Transport.objects.filter(user=self.user)

    def clean_free_places(self):
        free_places = self.cleaned_data["free_places"]
        transport = self.cleaned_data["transport"]
        if transport is not None and free_places > transport.default_places:
            raise forms.ValidationError(_("No puedes ofertar más plazas que las que tienes en el transporte"))
        return free_places

    def clean_departure(self):
        departure = self.cleaned_data["departure"]
        time_window = self.cleaned_data.get("time_window", 30)
        now = timezone.now()
        if departure < now:
            raise forms.ValidationError(_("No puedes crear viajes en el pasado"))
        overlaps = Journey.objects.overlaps(self.user, departure, time_window)
        if (self.instance.pk and overlaps.exclude(pk=self.instance.pk).exists()) or \
            (self.instance.pk is None and overlaps.exists()):
            raise forms.ValidationError(_("Ya tienes un viaje que sale muy cerca de esta hora"))
        return departure

    def clean_arrival(self):
        arrival = self.cleaned_data.get("arrival")
        departure = self.cleaned_data.get("departure")
        if arrival and departure:
            departure = self.cleaned_data["departure"]
            now = timezone.now()
            if arrival < now:
                raise forms.ValidationError(_("No puedes crear viajes en el pasado"))
            if arrival < departure:
                raise forms.ValidationError(_("No puedes crear viajes que llegues antes de salir"))
        return arrival

    def save(self, commit=True, **kwargs):
        """When save a journey form, you have to provide an user."""
        user = self.user
        if "user" in kwargs:
            assert isinstance(kwargs["user"], User)
            user = kwargs.get("user")
        journey = super(JourneyForm, self).save(commit=False)
        journey.user = user
        journey.driver = user if self.cleaned_data["i_am_driver"] else None
        if commit:
            journey.save()
        return journey


class SmartJourneyForm(forms.ModelForm):

    origin = forms.CharField(widget=forms.HiddenInput())
    destiny = forms.CharField(widget=forms.HiddenInput())

    i_am_driver = forms.BooleanField(
        label=_("¿Soy conductor?*"),
        required=False,
        initial=False,
        widget=forms.RadioSelect(
            choices=((True, _('Sí')), (False, _('No'))),
            attrs={
                "ng-model": "iAmDriver",
                "ng-change": "changeDriverStatus"
            }
        )
    )

    class Meta:
        model = Journey
        fields = ["origin", "destiny", "i_am_driver", "transport",
                  "free_places", "departure", "arrival", "time_window",
                  "recurrence"]
        widgets = {
            "transport": forms.Select(attrs={"class": "form-control"}),
            "kind": forms.Select(attrs={"class": "form-control"}),
            "free_places": forms.NumberInput(attrs={"class": "form-control"}),
            "departure": floppyforms.DateTimeInput(
                attrs={"class": "form-control"}
            ),
            "arrival": floppyforms.DateTimeInput(
                attrs={"class": "form-control"}
                ),
            "time_window": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(SmartJourneyForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['transport'].queryset = Transport.objects.filter(
                user=self.user
            )

    def clean_origin(self):
        origin = self.cleaned_data["origin"]
        data = origin.split(":")
        models = {"residence": Residence, "campus": Campus}
        try:
            return models.get(data[0]).objects.get(pk=data[1])
        except (ObjectDoesNotExist, IndexError, AttributeError):
            raise forms.ValidationError(_("Lugar de origen no válido"))

    def clean_destiny(self):
        destiny = self.cleaned_data["destiny"]
        data = destiny.split(":")
        models = {"residence": Residence, "campus": Campus}
        try:
            return models.get(data[0]).objects.get(pk=data[1])
        except (ObjectDoesNotExist, IndexError, AttributeError):
            raise forms.ValidationError(_("Lugar de destino no válido"))

    def clean_departure(self):
        departure = self.cleaned_data["departure"]
        time_window = self.cleaned_data.get("time_window", 30)
        now = timezone.now()
        if departure < now:
            raise forms.ValidationError(_("No puedes crear viajes en el pasado"))
        if Journey.objects.overlaps(self.user, departure, time_window).exists():
            raise forms.ValidationError(_("Ya tienes un viaje que sale muy cerca de esta hora"))
        return departure

    def clean_arrival(self):
        arrival = self.cleaned_data.get("arrival")
        departure = self.cleaned_data.get("departure")
        if arrival and departure:
            departure = self.cleaned_data["departure"]
            now = timezone.now()
            if arrival < now:
                raise forms.ValidationError(_("No puedes crear viajes en el pasado"))
            if arrival < departure:
                raise forms.ValidationError(_("No puedes crear viajes que llegues antes de salir"))
        return arrival

    def clean_free_places(self):
        free_places = self.cleaned_data["free_places"]
        transport = self.cleaned_data["transport"]
        if transport is not None and free_places > transport.default_places:
            raise forms.ValidationError(_("No puedes ofertar más plazas que las que tienes en el transporte"))
        return free_places


    def save(self, commit=True, **kwargs):
        """When save a journey form, you have to provide an user."""
        user = self.user
        if "user" in kwargs:
            assert isinstance(kwargs["user"], User)
            user = kwargs.get("user")
        journey = super(SmartJourneyForm, self).save(commit=False)
        journey.user = user
        journey.driver = user if self.cleaned_data["i_am_driver"] else None
        # Smart origin, destiny and kind
        origin = self.cleaned_data["origin"]
        destiny = self.cleaned_data["destiny"]
        attribute_selector = {
            Residence: "residence",
            Campus: "campus",
        }
        attribute = attribute_selector[origin.__class__]
        setattr(journey, attribute, origin)
        attribute = attribute_selector[destiny.__class__]
        setattr(journey, attribute, destiny)
        journey.kind = GOING if isinstance(origin, Residence) else RETURN
        if commit:
            journey.save()
            # Expand journey recurrence
            journeys = expand(journey)
            Journey.objects.bulk_create(journeys)
        return journey


class FilterForm(forms.Form):
    """Form to filter search results."""

    kind = forms.IntegerField(
        label=_("Tipo de viaje"),
        required=False,
        widget=forms.Select(
            attrs={"class": "form-control"},
            choices=JOURNEY_KINDS
        )
    )
    distance = forms.IntegerField(
        label=_("Distancia (metros)"),
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control"},
        ),
    )


class CancelJourneyForm(forms.Form):
    """Form to handle the cancellation of a journey. A cancellation needs a
    confirmation of the user.
    """
    pass


class ConfirmRejectJourneyForm(forms.Form):
    """Form to get the user to confirm or reject."""

    user = forms.IntegerField(widget=forms.HiddenInput())

    def clean_user(self):
        user_pk = self.cleaned_data["user"]
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            raise forms.ValidationError(_("El usuario no existe"))
        return user


class TransportForm(forms.ModelForm):
    """Form to create transport data."""

    class Meta:
        model = Transport
        fields = ["name", "default_places", "brand", "model", "color"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "default_places": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "brand": floppyforms.TextInput(attrs={"class": "form-control"}),
            "model": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(TransportForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        """When save a transport form, you have to provide an user."""
        user = self.user
        if "user" in kwargs:
            assert isinstance(kwargs["user"], User)
            user = kwargs.get("user")
        transport = super(TransportForm, self).save(commit=False)
        transport.user = user
        if commit:
            transport.save()
        return transport


class SearchJourneyForm(forms.Form):
    """Form to search journeys."""

    position = forms.CharField(widget=forms.HiddenInput())
    distance = forms.CharField(widget=forms.HiddenInput())
    departure_date = forms.DateField(
        label=_("Fecha de salida"),
        widget=floppyforms.DateInput(attrs={"class": "form-control"})
    )
    departure_time = forms.TimeField(
        label=_("Hora de salida"),
        widget=floppyforms.DateInput(attrs={"class": "form-control"})
    )
    search_by_time = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput()
    )
    time_window = forms.IntegerField(
        label=_("Margen de tiempo, en minutos"),
        initial=30,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    def clean_position(self):
        position = self.cleaned_data["position"]
        position_point = GEOSGeometry(position, srid=DEFAULT_GOOGLE_MAPS_SRID)
        position_projected_point = make_point(
            position_point, origin_coord_srid=DEFAULT_GOOGLE_MAPS_SRID,
            destiny_coord_srid=DEFAULT_PROJECTED_SRID
        )
        return position_projected_point

    def clean_distance(self):
        distance = self.cleaned_data["distance"]
        return float(distance)

    def search(self, user):
        position = self.cleaned_data["position"]
        distance = self.cleaned_data["distance"]
        departure_date = self.cleaned_data["departure_date"]
        departure_time = self.cleaned_data["departure_time"]
        departure = datetime.datetime.combine(departure_date, departure_time)
        search_by_time = self.cleaned_data.get("search_by_time", False)
        time_window = self.cleaned_data["time_window"]
        return Journey.objects.search(
            user=user, position=position, distance=distance,
            departure=departure, time_window=time_window,
            search_by_time=search_by_time
        )
