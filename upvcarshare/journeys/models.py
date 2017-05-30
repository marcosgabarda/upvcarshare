# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from copy import copy
from functools import reduce
import datetime

from django.conf import settings
from django.db.models import Q
from django.contrib.gis.db import models
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.measure import D
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel
from recurrence.fields import RecurrenceField

from core.models import GisTimeStampedModel
from journeys import JOURNEY_KINDS, GOING, RETURN, DEFAULT_DISTANCE, DEFAULT_PROJECTED_SRID, DEFAULT_WGS84_SRID, \
    DEFAULT_TIME_WINDOW, PASSENGER_STATUSES, UNKNOWN, CONFIRMED, REJECTED, DEFAULT_GOOGLE_MAPS_SRID
from journeys.exceptions import NoFreePlaces, NotAPassenger, AlreadyAPassenger
from journeys.helpers import make_point_wgs84, make_point
from journeys.managers import JourneyManager, ResidenceManager, MessageManager
from notifications import JOIN, LEAVE, CANCEL, CONFIRM, REJECT, THROW_OUT
from notifications.decorators import dispatch


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
        point = make_point(
            self.position, origin_coord_srid=DEFAULT_PROJECTED_SRID, destiny_coord_srid=DEFAULT_WGS84_SRID
        )
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
    address = models.TextField(verbose_name=_("dirección"), help_text=_("La dirección del lugar, según quieras que la vean los demás."))

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
        verbose_name=_("lugar"),
        related_name="journeys"
    )
    campus = models.ForeignKey(
        "journeys.Campus",
        verbose_name=_("campus"),
        related_name="journeys"
    )
    kind = models.PositiveIntegerField(choices=JOURNEY_KINDS, verbose_name=_("tipo de viaje"))
    free_places = models.PositiveIntegerField(default=4, verbose_name=_("plazas libres"), blank=True, null=True)
    total_passengers = models.PositiveIntegerField(default=0, verbose_name=_("total pasajeros"), blank=True, null=True)
    departure = models.DateTimeField(verbose_name=_("fecha y hora de salida*"))
    arrival = models.DateTimeField(verbose_name=_("fecha y hora de llegada estimada*"), null=True, blank=True)
    time_window = models.PositiveIntegerField(
        verbose_name=_("ventana de tiempo"),
        help_text=_("Se buscarán por los viajes que salgan hasta con estos minutos de antelación"),
        default=DEFAULT_TIME_WINDOW,
        blank=True
    )
    transport = models.ForeignKey(
        "journeys.Transport",
        related_name="journeys",
        verbose_name=_("Medio de transporte utilizado"),
        null=True,
        blank=True
    )
    disabled = models.BooleanField(default=False, verbose_name=_("marcar como deshabilitado"))
    recurrence = RecurrenceField(verbose_name=_("¿Vas a realizar este viaje más de una vez?"), null=True, blank=True)
    parent = models.ForeignKey("journeys.Journey", null=True, blank=True, related_name="children")

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

    @property
    def has_recurrence(self):
        return self.children.exists() or self.parent is not None

    def __str__(self):
        return self.description(strip_html=True)

    def get_title(self):
        """Gets the title for event calendar."""
        return self.description(strip_html=True)

    def get_start(self):
        """Gets the time to departure on ISO format."""
        return self.departure.isoformat()

    def get_end(self):
        """Gets the time to arrival on ISO format."""
        if self.arrival:
            return self.arrival.isoformat()
        return (self.departure + datetime.timedelta(minutes=30)).isoformat()

    def recurrence_journeys(self):
        journeys = Journey.objects.filter(pk=self.pk)
        if self.children.exists():
            journeys = Journey.objects.filter(
                Q(pk__in=self.children.all().values_list("pk", flat=True)) |
                Q(pk=self.pk)
            )
        elif self.parent:
            journeys = self.parent.children.all()
            journeys = Journey.objects.filter(
                Q(pk__in=self.parent.children.all().values_list("pk", flat=True)) |
                Q(pk=self.parent.pk)
            )
        return journeys

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
        return self.passengers.filter(status=CONFIRMED).count()

    def current_free_places(self):
        """Gets the current number of free places."""
        if self.free_places is not None:
            return self.free_places - self.count_passengers()
        return 0

    @dispatch(JOIN)
    def join_passenger(self, user, join_to=None):
        """A user joins a journey.
        :param user:
        :param join_to:
        """
        # Join only one
        if join_to is None or join_to == "one":
            if self.passengers.filter(user=user).exists() or self.driver == user:
                raise AlreadyAPassenger()
            if self.count_passengers() < self.free_places:
                passenger = Passenger.objects.create(
                    journey=self,
                    user=user,
                    status=UNKNOWN
                )
                return passenger
        # Join to recurrence
        elif join_to is not None and join_to == "all":
            if self.has_recurrence:
                journeys = self.recurrence_journeys()
                journeys = journeys.filter(departure__gte=self.departure)
                passengers = []
                for journey in journeys:
                    try:
                        passengers.append(journey.join_passenger(user))
                    except (NoFreePlaces, AlreadyAPassenger):
                        pass
                return passengers
        # Join only some of the recurrence
        elif join_to is not None and len(join_to.split("/")) > 0:
            dates = map(lambda item: datetime.datetime.strptime(item, "%d/%m/%Y"), join_to.split(","))
            conditions = [Q(departure__day=date.day, departure__month=date.month, departure__year=date.year) for date in dates]
            journeys = self.recurrence_journeys()
            journeys = journeys.filter(reduce(lambda x, y: x | y, conditions))
            print(journeys)
            passengers = []
            for journey in journeys:
                try:
                    passengers.append(journey.join_passenger(user))
                except (NoFreePlaces, AlreadyAPassenger):
                    pass
            return passengers
        raise NoFreePlaces()

    @dispatch(LEAVE)
    def leave_passenger(self, user):
        """A user leave a journey.
        :param user:
        """
        if not self.is_passenger(user=user):
            raise NotAPassenger()
        self.passengers.filter(user=user).delete()
        self.total_passengers -= 1
        if self.total_passengers < 0:
            self.total_passengers = 0
        self.save()

    @dispatch(THROW_OUT)
    def throw_out(self, user):
        """A user is throw out from a journey.
        :param user:
        """
        self.leave_passenger(user)

    @dispatch(CONFIRM)
    def confirm_passenger(self, user):
        """Confirms the user as passenger."""
        if not self.is_passenger(user=user, all_passengers=True):
            raise NotAPassenger()
        # self.passengers.filter(user=user).update(status=CONFIRMED)
        passenger = self.passengers.filter(user=user).first()
        if passenger:
            passengers = passenger.recurrence()
            passengers.update(status=CONFIRMED)
            self.total_passengers += 1
            self.save()

    @dispatch(REJECT)
    def reject_passenger(self, user):
        """Confirms the user as passenger."""
        if not self.is_passenger(user=user, all_passengers=True):
            raise NotAPassenger()
        # self.passengers.filter(user=user).update(status=REJECTED)
        passenger = self.passengers.filter(user=user).first()
        if passenger:
            passengers = passenger.recurrence()
            passengers.update(status=REJECTED)

    def is_passenger(self, user, all_passengers=False):
        """Checks if the given user is a passenger of this journey."""
        if not all_passengers:
            return self.passengers.filter(user=user, status=CONFIRMED).exists()
        return self.passengers.filter(user=user).exists()

    def recommended(self, ignore_full=False):
        """Gets recommended journeys for this journey.
        :returns QuerySet:
        """
        if self.driver == self.user:
            return Journey.objects.none()
        result = Journey.objects.recommended(user=self.user, kind=self.kind, journey=self, ignore_full=ignore_full)
        return result

    def needs_driver(self):
        """Checks if the journey needs a driver."""
        return self.driver is None

    def are_there_free_places(self):
        """Check if there are free places."""
        return self.current_free_places() > 0

    def is_fulfilled(self):
        """Check if the journey is already fulfilled by the given user."""
        return self.needs_driver() and self.recommended(ignore_full=True).filter(passengers__user=self.user).exists()

    def fulfilled_by(self):
        """Gets journeys who are fulfilling this one."""
        if not self.is_fulfilled():
            return None
        return self.recommended(ignore_full=True).filter(passengers__user=self.user)

    def distance(self):
        """Gets the journey distance."""
        return self.residence.position.distance(self.campus.position) / 1000

    def is_messenger_allowed(self, user):
        """Check if the user is allowed to make messenger actions."""
        return not(self.user != user and not self.is_passenger(user))

    @dispatch(CANCEL)
    def cancel(self):
        """Cancels a journey."""
        self.disabled = True
        self.save()

    def passengers_list(self, user):
        """Gets the suitable list of passenger for this user."""
        if self.user == user:
            return self.passengers.all()
        elif self.is_passenger(user):
            return self.passengers.filter(status=CONFIRMED)
        return Passenger.objects.none()

    def save(self, **kwargs):
        """Override save to set the default time window value. Default value not set in Oracle."""
        if not self.time_window:
            self.time_window = DEFAULT_TIME_WINDOW
        return super(Journey, self).save(**kwargs)


class Passenger(TimeStampedModel):
    """A user who has joined a journey."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    journey = models.ForeignKey("journeys.Journey", related_name="passengers")
    status = models.PositiveIntegerField(choices=PASSENGER_STATUSES, default=UNKNOWN)

    class Meta:
        unique_together = ["user", "journey"]

    def recurrence(self):
        journeys = self.journey.recurrence_journeys()
        conditions = [Q(journey__pk=journey.pk) for journey in journeys]
        passengers = Passenger.objects.filter(reduce(lambda x, y: x | y, conditions))
        return passengers

    def has_recurrence(self):
        """Check if there is more than one request for the recourrence of
        the journey.
        """
        passengers = self.recurrence()
        return passengers.count() > 1


@python_2_unicode_compatible
class Transport(TimeStampedModel):
    """Saves the transport data for a user."""
    name = models.CharField(max_length=64, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="transports")
    default_places = models.PositiveIntegerField(verbose_name=_("Plazas libres"), default=4)
    brand = models.TextField(verbose_name=_("Marca"), max_length=250, blank=True, default="")
    model = models.TextField(verbose_name=_("Modelo"), max_length=250, blank=True, default="")
    color = models.TextField(verbose_name=_("Color"), max_length=250, blank=True, default="")

    def __str__(self):
        return self.name

    def description(self):
        return " ".join([self.brand, self.model, self.color])

    def count_used_journeys(self):
        return self.journeys.count()


class Message(TimeStampedModel):
    """Message send by a passenger of the journey."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages")
    journey = models.ForeignKey("journeys.Journey", related_name="messages")
    content = models.TextField()

    objects = MessageManager()
