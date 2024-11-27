from .base import *

SECRET_KEY = 'django-insecure-lr=bw=_l&+(yf45d9-o6ip6^h&%82ou1ah82@7on*l@d(ml@8f'
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'djangogram',
        "USER": "admin",
        "PASSWORD": "admin",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

ALLOWED_HOSTS = []

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
