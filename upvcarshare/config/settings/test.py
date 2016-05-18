# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from config.settings.base import *

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='o#bpi3*=nzn5r-9i!db1&h&oo0%5wmzudw-q2054z9n)u8=uez')

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# Database in memory for tests
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.spatialite",
        "NAME": ":memory:",
    },
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
SPATIALITE_LIBRARY_PATH = env('DJANGO_EMAIL_BACKEND', default='/usr/local/lib/mod_spatialite.dylib')
