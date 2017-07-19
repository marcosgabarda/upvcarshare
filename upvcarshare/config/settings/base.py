# -*- coding: utf-8 -*-
from os.path import basename, join
from sys import path

import environ
from django.core.urlresolvers import reverse_lazy


# PATH CONFIGURATION
# ------------------------------------------------------------------------------
# environ.Path value to the django repo directory:
ROOT_DIR = environ.Path(__file__) - 4

# environ.Path value to the project directory:
APPS_DIR = environ.Path(__file__) - 3

# Absolute filesystem path to the config directory:
CONFIG_ROOT = str(APPS_DIR.path("config"))

# Absolute filesystem path to the project directory:
PROJECT_ROOT = str(APPS_DIR)

# Absolute filesystem path to the django repo directory:
DJANGO_ROOT = str(ROOT_DIR)

# Project folder:
PROJECT_FOLDER = basename(PROJECT_ROOT)

# Project name:
PROJECT_NAME = basename(PROJECT_ROOT).capitalize()

# Project domain:
PROJECT_DOMAIN = '%s.com' % PROJECT_NAME.lower()

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(CONFIG_ROOT)

# ENV CONFIGURATION
# ------------------------------------------------------------------------------
# See: http://django-environ.readthedocs.io/en/latest/
env = environ.Env()
env.read_env(join(DJANGO_ROOT, '.env'))
env.DB_SCHEMES.update({
    'oracle': 'django.db.backends.oracle',
    'oraclegis': 'django.contrib.gis.db.backends.oracle',
})  # Add support for Oracle and Oracle GIS to Django Environ

# DEBUG CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)
API_DEBUG = DEBUG

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("Marcos Gabarda", 'hey@marcosgabarda.com'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS


# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'UTC'

# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'es-es'

# https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.TimezoneMiddleware',
]

# EMAIL
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL', default='{} <noreply@{}>'.format(PROJECT_NAME, PROJECT_DOMAIN))
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[{}] '.format(PROJECT_NAME))
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)


# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/templates/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path("templates"))
        ],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
                'notifications.context_processors.notifications',
                'journeys.context_processors.passenger_statuses',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'string_if_invalid': 'NULL',
        },
    },
]


# APP CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.gis',
)

THIRD_PARTY_APPS = (
    'django_extensions',
    'floppyforms',
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'recurrence',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.openid',
)

PROJECT_APPS = (
    'core',
    'pages',
    'users',
    'journeys',
    'notifications',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR.path("media"))

# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(APPS_DIR.path("public"))

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path("static/dist")),
)

# https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-STATICFILES_STORAGE
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# https://docs.djangoproject.com/en/dev/ref/settings/#staticfiles-finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_ADAPTER = 'users.adapter.AccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGIN_URL = reverse_lazy('users:sign-in')

# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'openid': {
        'SERVERS': [
            {
                "id": "upv",
                "name": "upv",
                "openid_url": "https://yo.rediris.es/soy/@upv.es"
            }
        ]
    }
}


# TESTING CONFIGURATION
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'production_only': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'development_only': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)-8s [%(name)s:%(lineno)s] %(message)s',
            'datefmt': '%m/%d/%Y %H:%M:%S',
        },
        'simple': {
            'format': '%(levelname)-8s [%(name)s:%(lineno)s] %(message)s',
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'default': {
            'level': 'DEBUG',
            'class': 'logutils.colorize.ColorizingStreamHandler',
        },
        'console_dev': {
            'level': 'DEBUG',
            'filters': ['development_only'],
            'class': 'logutils.colorize.ColorizingStreamHandler',
            'formatter': 'simple',
        },
        'console_prod': {
            'level': 'INFO',
            'filters': ['production_only'],
            'class': 'logutils.colorize.ColorizingStreamHandler',
            'formatter': 'simple',
        },
        'file_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(DJANGO_ROOT, 'logs/log.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'file_sql': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(DJANGO_ROOT, 'logs/sql.log'),
            'maxBytes': 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['production_only'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    # Catch-all modules that use logging
    # Writes to console and file on development, only to console on production
    'root': {
        'handlers': ['console_dev', 'console_prod', 'file_log'],
        'level': 'DEBUG',
    },
    'loggers': {
        # Write all SQL queries to a file
        'django.db.backends': {
            'handlers': ['file_sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        # Ignore DisallowedHost
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        # Email admins when 500 error occurs
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

# REST FRAMEWORK CONFIGURATION
# ------------------------------------------------------------------------------
# http://www.django-rest-framework.org/
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

# GOOGLE MAPS
# ------------------------------------------------------------------------------
GOOGLE_MAPS_API_KEY = env('GOOGLE_MAPS_API_KEY', default="AIzaSyAUuXiJ-kthJMHdXerksxYbqIbrRFrVfG4")


# UPV CREDENTIALS
# ------------------------------------------------------------------------------
UPV_LOGIN_IGNORE = False
UPV_LOGIN_DATA_USERNAME = env("UPV_LOGIN_DATA_USERNAME")
UPV_LOGIN_DATA_PASSWORD = env("UPV_LOGIN_DATA_PASSWORD")
