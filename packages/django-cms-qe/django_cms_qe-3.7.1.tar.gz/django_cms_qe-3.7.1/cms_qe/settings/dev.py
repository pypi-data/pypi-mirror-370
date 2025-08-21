"""
Configuration for development.

Disables all security options.
"""

import os
from pathlib import Path

from .base import *  # noqa: F401,F403 pylint: disable=wildcard-import,unused-wildcard-import

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

DEBUG = True

META_SITE_PROTOCOL = 'http'

SECRET_KEY = '^xzhq0*q1+t0*ihq^^1wuyj3i%y#(38b7d-vlpkm-d(=!^uk6x'

SESSION_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS += [  # noqa: F405
    'debug_toolbar',
    'django_extensions',
]

ROOT_URLCONF = "cms_qe.urls"

MIDDLEWARE += [  # noqa: F405
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

site_resolver = Path(__file__).resolve()

PROJECT_DIR = site_resolver.parent.parent.parent

STATIC_ROOT = os.path.join(PROJECT_DIR, 'staticfiles')

# Caching
# https://docs.djangoproject.com/en/1.11/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(PROJECT_DIR, 'django_cache'),
    }
}

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'db.sqlite3'),
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
