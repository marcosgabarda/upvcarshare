# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

from django import template

register = template.Library()


@register.inclusion_tag('journeys/templatetags/item.html', takes_context=True)
def journey_item(context, journey):
    """Renders a journey as an item list."""
    context["journey"] = journey
    return context


@register.filter
def is_passenger(journey, user):
    return journey.is_passenger(user)
