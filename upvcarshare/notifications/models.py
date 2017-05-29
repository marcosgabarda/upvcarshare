# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import six
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from django.templatetags.l10n import localize
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.six import python_2_unicode_compatible
from django.utils.timezone import pytz
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel

from notifications import JOIN, LEAVE, CANCEL, MESSAGE, CONFIRM, REJECT, THROW_OUT
from notifications.manager import NotificationManager


@python_2_unicode_compatible
class Notification(TimeStampedModel):
    """A notification is a record of an action on the system. The 'actor' makes an 'action' (optional), according
    to a 'verb' over a 'target' (optional).

    <actor> <verb> <time>
    <actor> <verb> <target> <time>
    <actor> <verb> <action> <target> <time>

    Based on: http://activitystrea.ms/specs/atom/1.0/
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications')

    # - Actor
    actor_content_type = models.ForeignKey(ContentType, related_name='notify_actor')
    actor_object_id = models.PositiveIntegerField()
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')

    # - Verb
    verb = models.CharField(max_length=255)

    # - Target
    target_content_type = models.ForeignKey(ContentType, related_name='notify_target', blank=True, null=True)
    target_object_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    # - Action object
    action_content_type = models.ForeignKey(ContentType, related_name='notify_action', blank=True, null=True)
    action_object_id = models.PositiveIntegerField(blank=True, null=True)
    action = GenericForeignKey('action_content_type', 'action_object_id')

    read = models.BooleanField(default=False, blank=False)

    objects = NotificationManager()

    def __str__(self):
        return self.text(strip_html=True)

    def text(self, strip_html=False):
        """Creates the text representation of the notification."""
        value = ""
        try:
            time_zone = pytz.timezone("Europe/Madrid")
            target_date = timezone.localtime(self.target.departure, time_zone)
            target_date = localize(target_date)
            if self.verb == JOIN:
                # actor is a user and target is a journey
                value = _("%(user)s se ha <strong>unido</strong> al viaje <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
            elif self.verb == LEAVE:
                value = _("%(user)s ha <strong>abandonado</strong> el viaje <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
            elif self.verb == THROW_OUT:
                value = _("%(user)s te ha <strong>expulsado</strong> del viaje <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
            elif self.verb == CONFIRM:
                value = _("%(user)s te ha <strong>confirmado</strong> para el viaje <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
            elif self.verb == REJECT:
                value = _("%(user)s te ha <strong>rechazado</strong> para el viaje <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
            elif self.verb == CANCEL:
                value = _("El viaje <strong>%(journey)s</strong> del %(date)s ha sido <strong>cancelado</strong>") % {
                    "journey": six.text_type(self.actor).lower(),
                    "date": target_date,
                }
            elif self.verb == MESSAGE:
                value = _("%(user)s ha mandado un <strong>nuevo mensaje</strong> en <strong>%(journey)s</strong> del %(date)s") % {
                    "user": six.text_type(self.actor),
                    "journey": six.text_type(self.target).lower(),
                    "date": target_date,
                }
        except AttributeError:
            pass
        if strip_html:
            value = strip_tags(value)
        return mark_safe(value)

    def link(self):
        from journeys.models import Journey
        if isinstance(self.target, Journey):
            return reverse("journeys:details", kwargs={"pk": self.target.pk})
        return None
