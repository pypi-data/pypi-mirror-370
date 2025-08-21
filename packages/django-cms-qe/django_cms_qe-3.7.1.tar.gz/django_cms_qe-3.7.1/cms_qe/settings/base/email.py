"""
Mailing settings, by default app looks for smtp server.
"""

EMAIL_HOST = 'localhost'
EMAIL_PORT = 587  # TLS uses usually 587, not 22

EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

EMAIL_USE_TLS = True  # Prefer to use secure mailing by default
EMAIL_SUBJECT_PREFIX = ''  # Remove Django default prefix

DEFAULT_FROM_EMAIL = 'django_cms_qe@localhost'
