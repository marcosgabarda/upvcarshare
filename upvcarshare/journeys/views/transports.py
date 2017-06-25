# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View

from journeys.forms import TransportForm
from journeys.models import Transport


class TransportListView(LoginRequiredMixin, View):
    """Shows the list of users' transports."""
    template_name = "transports/list.html"

    def get(self, request):
        data = {
            "transports": Transport.objects.filter(user=request.user)
        }
        return render(request, self.template_name, data)


class CreateTransportView(LoginRequiredMixin, View):
    """Handles the creation of a new transport."""
    template_name = "transports/create.html"
    form = TransportForm

    def get(self, request):
        data = {
            "form": self.form(user=request.user)
        }
        return render(request, self.template_name, data)

    def post(self, request):
        form = self.form(request.POST, user=request.user)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, _('Has creado el transporte correctamente'))
            return redirect(request.GET.get("next", "journeys:transports"))
        data = {"form": form}
        return render(request, self.template_name, data)


class EditTransportView(LoginRequiredMixin, View):
    """Handles the edition of a new transport."""
    template_name = "transports/edit.html"
    form = TransportForm

    def get(self, request, pk):
        transport = get_object_or_404(Transport, pk=pk, user=request.user)
        data = {
            "form": self.form(instance=transport, user=request.user),
            "transport": transport
        }
        return render(request, self.template_name, data)

    def post(self, request, pk):
        transport = get_object_or_404(Transport, pk=pk, user=request.user)
        form = self.form(request.POST, user=request.user, instance=transport)
        if form.is_valid():
            messages.success(request, _('Has editado el transporte correctamente'))
            return redirect("journeys:transports")
        data = {
            "form": form,
            "transport": transport
        }
        return render(request, self.template_name, data)


class DeleteTransportView(LoginRequiredMixin, View):
    pass
