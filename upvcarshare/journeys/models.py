# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from copy import copy

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.measure import D
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from core.models import GisTimeStampedModel
from journeys import JOURNEY_KINDS, GOING, RETURN, DEFAULT_DISTANCE, DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID, \
    DEFAULT_TIME_WINDOW
from journeys.exceptions import NoFreePlaces, NotAPassenger, AlreadyAPassenger
from journeys.helpers import make_point_wgs84
from journeys.managers import JourneyManager, ResidenceManager


class Place(GisTimeStampedModel):
    """Abstract class model to represent common data shared by residences and
    campus.

    Uses projected coordinate system for Spain. See: http://spatialreference.org/ref/epsg/2062/
    """
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name=_("nombre"))
    position = models.PointField(srid=DEFAULT_PROJECTED_SRID, verbose_name=_("posición en el mapa"))
    distance = models.PositiveIntegerField(
        verbose_name=_("distancia"),
        help_text=_("Distancia máxima a la que te desplazarías (metros)"),
        default=DEFAULT_DISTANCE,
        blank=True
    )

    class Meta:
        abstract = True

    def get_position_wgs84(self):
        """Transforms position to WGS-84 system."""
        destination_coord = SpatialReference(DEFAULT_WGS84_SRID)
        origin_coord = SpatialReference(DEFAULT_PROJECTED_SRID)
        trans = CoordTransform(origin_coord, destination_coord)
        # Copy transformed point...
        position = copy(self.position)
        position.transform(trans)
        return position

    def set_position_wgs84(self, position):
        """Transforms an input to projected coordinates."""
        self.position = make_point_wgs84(position)
        return self.position

    def google_maps_link(self):
        """Gets a link to Google Maps position"""
        point = self.get_position_wgs84()
        return "http://www.google.com/maps/place/{},{}".format(
            point.coords[1], point.coords[0]
        )

    def nearby(self):
        """Abstract method to search nearby journeys."""
        raise NotImplementedError()


@python_2_unicode_compatible
class Residence(Place):
    """A node where life a user, and my want to go back or departure from
    here. Each residence belongs to a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="residences")
    address = models.TextField(verbose_name=_("dirección"))

    objects = ResidenceManager()

    def __str__(self):
        return self.name if self.name else _("Lugar #%s") % self.pk

    def nearby(self):
        """Search nearby journeys."""
        return Journey.objects.nearby(kind=GOING, geometry=self.position, distance=D(m=self.distance))

    def count_used_journeys(self):
        return self.journeys.count()


@python_2_unicode_compatible
class Campus(Place):
    """A node that represents an university campus."""

    class Meta:
        verbose_name_plural = "campuses"

    def __str__(self):
        return self.name if self.name else _("Campus #%s") % self.pk

    def nearby(self):
        """Search nearby journeys."""
        return Journey.objects.nearby(kind=RETURN, geometry=self.position, distance=D(m=self.distance))


@python_2_unicode_compatible
class Journey(GisTimeStampedModel):
    """A model class to represent a journey between two node."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="journeys", help_text=_("user who creates the journey")
    )
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, help_text=_("user who drives during the journey")
    )
    residence = models.ForeignKey(
        "journeys.Residence",
        verbose_name=_("lugar de origen/destino"),
        related_name="journeys"
    )
    campus = models.ForeignKey(
        "journeys.Campus",
        verbose_name=_("campus de origen/destino"),
        related_name="journeys"
    )
    kind = models.PositiveIntegerField(choices=JOURNEY_KINDS, verbose_name=_("tipo de trayecto"))
    free_places = models.PositiveIntegerField(default=4, verbose_name=_("plazas libres"), blank=True, null=True)
    departure = models.DateTimeField(verbose_name=_("fecha y hora de salida"))
    time_window = models.PositiveIntegerField(
        verbose_name=_("ventana de tiempo"),
        help_text=_("Se buscaran por los trayectos que salgan hasta con estos minutos de antelación"),
        default=DEFAULT_TIME_WINDOW,
        blank=True
    )
    disabled = models.BooleanField(default=False, verbose_name=_("marcar como deshabilitado"))

    objects = JourneyManager()

    @property
    def origin(self):
        """Origin of the journey."""
        if self.kind == GOING:
            return self.residence
        return self.campus

    @property
    def destination(self):
        """Destination of the journey."""
        if self.kind == RETURN:
            return self.residence
        return self.campus

    def __str__(self):
        return self.description(strip_html=True)

    def description(self, strip_html=False):
        """Gets a human read description of the journey."""
        if self.kind == GOING:
            value = _("Viaje de <strong>%(kind)s</strong> a <strong>%(campus_name)s</strong>") % {
                "kind": self.get_kind_display(),
                "campus_name": self.campus.name
            }
        else:
            value = _("Viaje de <strong>%(kind)s</strong> desde <strong>%(campus_name)s</strong>") % {
                "kind": self.get_kind_display(),
                "campus_name": self.campus.name
            }
        if strip_html:
            value = strip_tags(value)
        return mark_safe(value)

    def count_passengers(self):
        """Gets the count of passengers."""
        return self.passengers.count()

    def current_free_places(self):
        """Gets the current number of free places."""
        if self.free_places is not None:
            return self.free_places - self.count_passengers()
        return 0

    def join_passenger(self, user):
        """A user joins a journey.
        :param user:
        """
        if self.passengers.filter(user=user).exists() or self.driver == user:
            raise AlreadyAPassenger()
        if self.count_passengers() < self.free_places:
            return Passenger.objects.create(
                journey=self,
                user=user
            )
        raise NoFreePlaces()

    def leave_passenger(self, user):
        """A user joins a journey.
        :param user:
        """
        if not self.is_passenger(user=user):
            raise NotAPassenger()
        self.passengers.filter(user=user).delete()

    def is_passenger(self, user):
        """Checks if the given user is a passenger of this journey."""
        return self.passengers.filter(user=user).exists()

    def recommended(self):
        """Gets recommended journeys for this journey.
        :returns QuerySet:
        """
        if self.driver == self.user:
            return Journey.objects.none()
        return Journey.objects.recommended(user=self.user, kind=self.kind, journey=self)

    def needs_driver(self):
        """Checks if the journey needs a driver."""
        return self.driver is None

    def are_there_free_places(self):
        """Check if there are free places."""
        return self.current_free_places() > 0

    def is_fulfilled(self):
        """Check if the journey is already fulfilled by the given user."""
        return self.needs_driver() and self.recommended().filter(passengers__user=self.user).exists()

    def fulfilled_by(self):
        """Gets the journey who if fulfilling this one."""
        if not self.is_fulfilled():
            return None
        return self.recommended().filter(passengers__user=self.user).first()

    def distance(self):
        """Gets the journey distance."""
        return self.residence.position.distance(self.campus.position) / 1000

    def cancel(self):
        """Cancels a journey."""
        self.disabled = True
        self.save()


class Passenger(TimeStampedModel):
    """A user who has joined a journey."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    journey = models.ForeignKey("journeys.Journey", related_name="passengers")

    class Meta:
        unique_together = ["user", "journey"]


class Transport(TimeStampedModel):
    """Saves the transport data for a user."""
    name = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="transports")
    default_places = models.PositiveIntegerField(default=4)
