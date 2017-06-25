# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.utils.translation import ugettext_lazy as _, ugettext

from journeys.forms import ResidenceForm
from journeys.models import Residence


class CreateResidenceView(LoginRequiredMixin, View):
    """View to show journey creation form and to handle its creation."""

    template_name = "residences/create.html"

    def get(self, request):
        initial = {
            "address": request.user.default_address,
            "position": request.user.default_position,
            "distance": request.user.default_distance,
        }
        form = ResidenceForm(initial=initial)
        data = {
            "form": form
        }
        return render(request, self.template_name, data)

    def post(self, request):
        form = ResidenceForm(request.POST)
        data = {
            "form": form
        }
        if form.is_valid():
            residence = form.save(user=request.user)
            messages.success(request, ugettext('Has creado el lugar "%s"') % residence.name)
            return redirect(request.GET.get("next", "journeys:residences"))
        return render(request, self.template_name, data)


class EditResidenceView(LoginRequiredMixin, View):
    """View to edit residences."""

    template_name = "residences/edit.html"

    def get(self, request, pk):
        residence = get_object_or_404(Residence, pk=pk, user=request.user)
        form = ResidenceForm(instance=residence)
        data = {
            "form": form,
            "residence": residence,
        }
        return render(request, self.template_name, data)

    def post(self, request, pk):
        residence = get_object_or_404(Residence, pk=pk, user=request.user)
        form = ResidenceForm(request.POST, instance=residence)
        data = {
            "form": form,
            "residence": residence,
        }
        if form.is_valid():
            form.save(user=request.user)
            return redirect("journeys:residences")
        messages.error(request, form.errors)
        return render(request, self.template_name, data)


class CurrentUserResidencesView(LoginRequiredMixin, View):
    """View to show to the user the list of his created residences."""

    template_name = "residences/list.html"

    def get(self, request):
        data = {
            "residences": Residence.objects.filter(user=request.user)
        }
        return render(request, self.template_name, data)


class DeleteResidence(LoginRequiredMixin, View):
    """Deletes a residence if there is no journeys related."""

    @staticmethod
    def get(request, pk):
        residence = get_object_or_404(Residence, pk=pk, user=request.user)
        if residence.journeys.count() == 0:
            residence.delete()
            messages.success(request, _('Has borrado el lugar'))
            return redirect("journeys:residences")
        messages.error(request, _('No puedes borrar este lugar'))
        return redirect("journeys:residences")
