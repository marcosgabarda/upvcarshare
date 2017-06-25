# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

import floppyforms
import pytz
import re
from django import forms
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _

from journeys import JOURNEY_KINDS, GOING, RETURN, DEFAULT_GOOGLE_MAPS_SRID, \
    DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID
from journeys.helpers import expand, make_point
from journeys.models import Residence, Journey, Campus, Transport, JourneyTemplate
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
            "address": forms.HiddenInput(attrs={"class": "form-control", "ng-value": "address"}),
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

    class Meta:
        model = Journey
        fields = ["free_places", "departure", "arrival"]
        widgets = {
            "free_places": forms.NumberInput(attrs={"class": "form-control"}),
            "departure": floppyforms.DateTimeInput(attrs={"class": "form-control"}),
            "arrival": floppyforms.DateTimeInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(JourneyForm, self).__init__(*args, **kwargs)

    def clean_free_places(self):
        free_places = self.cleaned_data["free_places"]
        transport = self.instance.template.transport if self.instance is not None else None
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


class SmartJourneyTemplateForm(forms.ModelForm):

    origin = forms.CharField(widget=forms.HiddenInput(), required=False)
    destiny = forms.CharField(widget=forms.HiddenInput(), required=False)

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

    free_places = forms.IntegerField(
        label=_("Plazas libres"),
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        help_text=_("Dejar en blanco para usar el valor por defecto del transporte seleccionado")
    )

    class Meta:
        model = JourneyTemplate
        fields = ["origin", "destiny", "i_am_driver", "transport",
                  "free_places", "departure", "recurrence", "arrival", "time_window"]
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
            "recurrence": forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(SmartJourneyTemplateForm, self).__init__(*args, **kwargs)
        if self.user:
            self.fields['transport'].queryset = Transport.objects.filter(
                user=self.user
            )

    def clean_origin(self):
        origin = self.cleaned_data["origin"]
        if not origin:
            raise forms.ValidationError(_("El origen obligatorio"))
        data = origin.split(":")
        models = {"residence": Residence, "campus": Campus}
        try:
            return models.get(data[0]).objects.get(pk=data[1])
        except (ObjectDoesNotExist, IndexError, AttributeError):
            raise forms.ValidationError(_("Lugar de origen no válido"))

    def clean_destiny(self):
        destiny = self.cleaned_data["destiny"]
        if not destiny:
            raise forms.ValidationError(_("El destino obligatorio"))
        data = destiny.split(":")
        models = {"residence": Residence, "campus": Campus}
        try:
            return models.get(data[0]).objects.get(pk=data[1])
        except (ObjectDoesNotExist, IndexError, AttributeError):
            raise forms.ValidationError(_("Lugar de destino no válido"))

    def clean_departure(self):
        departure = self.cleaned_data["departure"]
        departure = timezone.localtime(departure, pytz.timezone("UTC"))
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
        if not free_places and transport:
            free_places = transport.default_places
        if transport is not None and free_places > transport.default_places:
            raise forms.ValidationError(_("No puedes ofertar más plazas que las que tienes en el transporte"))
        return free_places

    def clean_recurrence(self):
        """Delete bad data from recurrence."""
        recurrence = self.cleaned_data["recurrence"]
        recurrence = re.sub(r"DTSTART=.+;", "", recurrence)
        recurrence = re.sub(r"BYSECOND=NAN", "", recurrence)
        return recurrence

    def save(self, commit=True, **kwargs):
        """When save a journey form, you have to provide an user."""
        user = self.user
        if "user" in kwargs:
            assert isinstance(kwargs["user"], User)
            user = kwargs.get("user")
        journey_template = super(SmartJourneyTemplateForm, self).save(commit=False)
        journey_template.user = user
        journey_template.driver = user if self.cleaned_data["i_am_driver"] else None
        # Smart origin, destiny and kind
        origin = self.cleaned_data["origin"]
        destiny = self.cleaned_data["destiny"]
        attribute_selector = {
            Residence: "residence",
            Campus: "campus",
        }
        attribute = attribute_selector[origin.__class__]
        setattr(journey_template, attribute, origin)
        attribute = attribute_selector[destiny.__class__]
        setattr(journey_template, attribute, destiny)
        journey_template.kind = GOING if isinstance(origin, Residence) else RETURN
        if commit:
            journey_template.save()
            # Expand journey recurrence
            expand(journey_template)
        return journey_template


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

    def clean_departure_time(self):
        departure_date = self.cleaned_data["departure_date"]
        departure_time = self.cleaned_data["departure_time"]
        departure_datetime = make_aware(
            datetime.datetime.combine(departure_date, departure_time),
            pytz.timezone("Europe/Madrid")
        )
        time_zone = pytz.timezone("UTC")
        departure_datetime = timezone.localtime(departure_datetime, time_zone)
        return departure_datetime.time()

    def search(self, user):
        position = self.cleaned_data["position"]
        distance = self.cleaned_data["distance"]
        departure_date = self.cleaned_data["departure_date"]
        departure_time = self.cleaned_data["departure_time"]
        departure = make_aware(datetime.datetime.combine(departure_date, departure_time), timezone=pytz.timezone("UTC"))
        search_by_time = self.cleaned_data.get("search_by_time", False)
        time_window = self.cleaned_data["time_window"]
        return Journey.objects.search(
            user=user, position=position, distance=distance,
            departure=departure, time_window=time_window,
            search_by_time=search_by_time
        )
