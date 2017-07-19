# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from config.settings.base import *

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=[PROJECT_DOMAIN])

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env('DJANGO_SECRET_KEY')

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    # Sample: oraclegis://USER:PASSWORD@HOST:PORT/NAME
    'default': env.db('DATABASE_URL'),
}
DATABASES['default']['PORT'] = str(DATABASES['default']['PORT'])  # Fix a problem with Oracle connector
DATABASES['default']['ATOMIC_REQUESTS'] = True
