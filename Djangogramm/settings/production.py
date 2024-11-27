from .base import *

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', default=False)

if os.getenv("USE_CLOUD_SQL_AUTH_PROXY", None):
    DATABASES["default"]["HOST"] = "127.0.0.1"
    DATABASES["default"]["PORT"] = 5432
