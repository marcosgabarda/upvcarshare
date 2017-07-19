# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from config.settings.base import *

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Note: This key only used for development and testing.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='o#bpi3*=nzn5r-9i!db1&h&oo0%5wmzudw-q2054z9n)u8=uez')

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': env.db(
        'DATABASE_URL', default='spatialite:///{}'.format(str(ROOT_DIR.path('{}.db'.format(PROJECT_NAME.lower()))))
    ),
}
DATABASES['default']['PORT'] = str(DATABASES['default']['PORT'])  # Fix a problem with Oracle connector
DATABASES['default']['ATOMIC_REQUESTS'] = True
SPATIALITE_LIBRARY_PATH = env('SPATIALITE_LIBRARY_PATH', default='/usr/local/lib/mod_spatialite.dylib')

# EMAIL
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env(
    'DJANGO_EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# JUPYTER
# ------------------------------------------------------------------------------
NOTEBOOK_ARGUMENTS = [
    '--port=8000',
]

# UPV CREDENTIALS
# ------------------------------------------------------------------------------
UPV_LOGIN_IGNORE = True
UPV_LOGIN_DATA_USERNAME = env("UPV_LOGIN_DATA_USERNAME")
UPV_LOGIN_DATA_PASSWORD = env("UPV_LOGIN_DATA_PASSWORD")

# DJANGO DEBUG TOOLBAR
# ------------------------------------------------------------------------------
MIDDLEWARE += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ['127.0.0.1', ]

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}
