"""
Caching setting by default in-memory without need to configure anything.
"""

# Caching
# https://docs.djangoproject.com/en/4.2/topics/cache/

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211',
    }
}
