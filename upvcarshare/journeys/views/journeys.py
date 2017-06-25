# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import datetime

import pytz
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.timezone import make_naive
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from journeys import GOING
from journeys.exceptions import AlreadyAPassenger, NoFreePlaces, NotAPassenger
from journeys.forms import SmartJourneyTemplateForm, JourneyForm, FilterForm, \
    ConfirmRejectJourneyForm, SearchJourneyForm
from journeys.models import Residence, Campus, Journey, Passenger


class CreateJourneyView(LoginRequiredMixin, View):
    """View to show journey creation form and to handle its creation."""

    template_name = "journeys/create.smart.html"
    form = SmartJourneyTemplateForm

    @staticmethod
    def _initial_values(request):
        residences = Residence.objects.filter(user=request.user)
        campuses = Campus.objects.all()
        initial_departure = timezone.now().replace(second=0, minute=0) + datetime.timedelta(hours=1)
        initial = {
            "residence": residences.first() if residences.exists() else None,
            "campus": campuses.first() if campuses.exists() else None,
            "kind": GOING,
            "departure": initial_departure,
            "arrival": initial_departure + datetime.timedelta(minutes=30)
        }
        return initial

    def get(self, request):
        initial = self._initial_values(request)
        form = self.form(initial=initial, user=request.user)
        data = {
            "form": form
        }
        # Warnings
        if request.user.transports.count() == 0:
            messages.warning(request, mark_safe(_(
                "Parece que no has creado ningún medio de transporte, "
                "si quieres crear un viaje y que otros compañeros puedan "
                "apuntarse, tienes que <strong>registrar antes un medio de transporte</strong>."
            )))
        if request.user.residences.count() == 0:
            messages.warning(request, mark_safe(_(
                "Parece que no has especificado desde donde o hasta donde sueles viajar. "
                "Para dar de alta un viaje deberás antes <strong>registrar al menos un lugar</strong> para usar "
                "como origen o destino."
            )))
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form(request.POST, user=request.user, initial=self._initial_values(request))
        data = {
            "form": form
        }
        if form.is_valid():
            journey_template = form.save()
            journeys = journey_template.journeys.order_by("-departure")
            return redirect("journeys:details", pk=journeys.first().pk)
        return render(request, self.template_name, data)


class EditJourneyView(LoginRequiredMixin, View):
    """View to edit journeys."""

    template_name = "journeys/edit.html"

    def get(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        form = JourneyForm(
            instance=journey,
            initial={"i_am_driver": journey.driver is not None and journey.driver == request.user},
            user=request.user
        )
        data = {
            "form": form,
            "journey": journey,
        }
        return render(request, self.template_name, data)

    def post(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        form = JourneyForm(request.POST, instance=journey, user=request.user)
        data = {
            "form": form,
            "journey": journey,
        }
        if form.is_valid():
            form.save()
            return redirect("journeys:details", pk=journey.pk)
        return render(request, self.template_name, data)


class JourneyView(LoginRequiredMixin, View):
    """View to journey details."""

    template_name = "journeys/details.html"

    @staticmethod
    def show_passengers(request, journey):
        if journey.user == request.user:
            return True
        return journey.is_passenger(request.user) and journey.count_passengers() > 0 and not journey.needs_driver()

    @staticmethod
    def show_messenger(request, journey):
        if journey.user == request.user and not journey.needs_driver():
            return True
        return journey.is_passenger(request.user)

    def get(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk)
        data = {
            "journey": journey,
            "show_passengers": self.show_passengers(request, journey),
            "show_messenger": self.show_messenger(request, journey),
            "is_fulfilled": journey.is_fulfilled(),
            "fulfilled_by": journey.fulfilled_by(),
            "passengers": journey.passengers_list(request.user),
            "recommended": journey.recommended(),
            "has_recurrence": journey.has_recurrence
        }
        return render(request, self.template_name, data)


class RecommendedJourneyView(LoginRequiredMixin, View):
    """View to show to the user the list of recommended journeys according to his needs."""
    template_name = "journeys/recommended.html"

    def get(self, request):
        filter_form = FilterForm(request.GET)
        kind_filter = None
        override_distance = None
        if filter_form.is_valid():
            kind_filter = filter_form.cleaned_data.get("kind")
            override_distance = filter_form.cleaned_data.get("distance")
        data = {
            "filter_form": filter_form,
            "journeys": Journey.objects.recommended(
                user=request.user,
                kind=kind_filter,
                override_distance=override_distance
            ),
        }
        return render(request, self.template_name, data)


class JourneysView(LoginRequiredMixin, View):
    """View to show to the user the list of his created journeys."""
    template_name = "journeys/list.html"

    def get(self, request):
        journeys = Journey.objects.filter(template__user=request.user).order_by("departure")
        data = {
            "journeys": journeys,
            "journeys_count": journeys.count()
        }
        return render(request, self.template_name, data)


class JoinJourneyView(LoginRequiredMixin, View):
    """View to handle the action of joining a journey. """
    return_to = "journeys:recommended"

    def post(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk)
        join_to = request.POST.get("join_to")
        try:
            journey.join_passenger(request.user, join_to)
            if join_to is not None and len(join_to.split("/")) > 0:
                messages.success(request, _('Has solicitado unirte a alguno de los viajes disponibles'))
            elif join_to == "all":
                messages.success(request, _('Has solicitado unirte a todos los viajes disponibles'))
            else:
                messages.success(request, _('Has solicitado unirte al viaje'))
        except AlreadyAPassenger:
            messages.error(request, _('¡Ya has solicitado unirte al viaje!'))
        except NoFreePlaces:
            messages.error(request, _('No quedan plazas libres en el viaje'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class ConfirmJourneyView(LoginRequiredMixin, View):
    """View to handle the action of joining a journey. """
    return_to = "journeys:recommended"

    def post(self, request, pk):
        passenger = get_object_or_404(Passenger, pk=pk)
        if passenger.journey.user != request.user:
            raise Http404
        form = ConfirmRejectJourneyForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            try:
                passenger.journey.confirm_passenger(user)
            except NotAPassenger:
                messages.success(request, _('El usuario no está en este viaje'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class RejectJourneyView(LoginRequiredMixin, View):
    """View to handle the action of joining a journey. """
    return_to = "journeys:recommended"

    def post(self, request, pk):
        passenger = get_object_or_404(Passenger, pk=pk)
        if passenger.journey.user != request.user:
            raise Http404
        form = ConfirmRejectJourneyForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            try:
                passenger.journey.reject_passenger(user)
            except NotAPassenger:
                messages.success(request, _('El usuario no está en este viaje'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class LeaveJourneyView(LoginRequiredMixin, View):
    """View to handle the action of leaving a journey. """
    return_to = "journeys:recommended"

    def post(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk)
        try:
            journey.leave_passenger(request.user)
            messages.success(request, _('Has dejado el viaje'))
        except NotAPassenger:
            messages.success(request, _('No estás en este viaje'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class ThrowOutPassengerView(LoginRequiredMixin, View):
    """View to handle the action of throw out a passenger. """
    return_to = "journeys:recommended"

    def post(self, request, pk):
        passenger = get_object_or_404(Passenger, pk=pk)
        if passenger.journey.user != request.user:
            raise Http404
        try:
            passenger.journey.throw_out(passenger.user)
            messages.success(request, _('Has expulsado al pasajero'))
        except NotAPassenger:
            messages.success(request, _('No puedes expulsar a este pasajero'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class AcceptPassengerView(LoginRequiredMixin, View):
    """View to accept a request of a possible passenger."""
    return_to = "journeys:recommended"

    def post(self, request, pk):

        passenger = get_object_or_404(Passenger, pk=pk)
        if passenger.journey.user != request.user:
            raise Http404
        try:
            passenger.journey.leave_passenger(passenger.user)
            messages.success(request, _('Has expulsado al pasajero'))
        except NotAPassenger:
            messages.success(request, _('No puedes expulsar a este pasajero'))
        return_to = request.POST.get("return_to", self.return_to)
        return redirect(return_to)


class CancelJourneyView(LoginRequiredMixin, View):
    """View to handle a cancellation of a journey."""
    template_name = "journeys/cancel.html"

    def get(self, request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        data = {
            "journey": journey,
        }
        return render(request, self.template_name, data)

    @staticmethod
    def post(request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        journey.cancel()
        return redirect("journeys:details", pk=journey.pk)


class DeleteJourneyView(LoginRequiredMixin, View):
    """Deletes a journey only if it hasn't driver."""

    @staticmethod
    def get(request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        # Delete only if the journey hasn't driver
        if journey.driver is None:
            journey.delete()
            messages.success(request, _('Has borrado el viaje'))
            return redirect("journeys:list")
        messages.error(request, _('No puedes borrar este viaje'))
        return redirect(reverse("journeys:details", kwargs={"pk": pk}))


class DeleteAllJourneyView(LoginRequiredMixin, View):
    """Deletes a journey only if it hasn't driver."""

    @staticmethod
    def get(request, pk):
        journey = get_object_or_404(Journey, pk=pk, template__user=request.user)
        # Delete only if the journey hasn't driver
        if journey.driver is None:
            if journey.has_recurrence:
                # If has recurrente, delete all future brothers
                journeys = journey.brothers().filter(departure__gte=journey.departure)
                journeys.delete()
            else:
                journey.delete()
            messages.success(request, _('Has borrado el viaje y sus repeticiones'))
            return redirect("journeys:list")
        messages.error(request, _('No puedes borrar este viaje'))
        return redirect(reverse("journeys:details", kwargs={"pk": pk}))


class SearchJourneysView(LoginRequiredMixin, View):
    """View to search journeys."""
    template_name = "journeys/search.html"

    def get(self, request):
        journeys = Journey.objects.none()
        initial_departure = make_naive(timezone.now().replace(second=0, minute=0) + datetime.timedelta(hours=1))
        madrid_tz = pytz.timezone("Europe/Madrid")
        initial_departure = madrid_tz.localize(initial_departure)
        form = SearchJourneyForm(initial={
            "time_window": 30,
            "departure_date": initial_departure.strftime("%d/%m/%Y"),
            "departure_time": initial_departure.strftime("%H:%M"),
        })
        data = {
            "form": form,
            "journeys": journeys,
            "is_query": False
        }
        return render(request, self.template_name, data)

    def post(self, request):
        journeys = Journey.objects.none()
        form = SearchJourneyForm(request.POST)
        if form.is_valid():
            journeys = form.search(user=request.user)
        data = {
            "form": form,
            "journeys": journeys,
            "is_query": True
        }
        return render(request, self.template_name, data)
