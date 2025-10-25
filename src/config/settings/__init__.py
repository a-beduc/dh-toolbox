import os
from django.core.exceptions import ImproperlyConfigured
from config.settings.base import *


ENV_NAME = os.getenv("ENV_NAME")
if not ENV_NAME:
    raise ImproperlyConfigured("ENV_NAME is not set. "
                               "Expected: Local / Testing / Production.")

env = ENV_NAME.strip().lower()

if env == 'production':
    from .production import *
elif env == 'testing':
    from .testing import *
elif env == 'local':
    from .local import *
else:
    raise ImproperlyConfigured(
        f"Unknown ENV_NAME='{ENV_NAME}'. "
        f"Expected: Local / Testing / Production."
    )


def _guardrails():
    if env == "production":
        if DEBUG:
            raise ImproperlyConfigured("DEBUG must be False in Production.")
        if not SECRET_KEY:
            raise ImproperlyConfigured("SECRET_KEY must be set in Production.")
        if not ALLOWED_HOSTS:
            raise ImproperlyConfigured(
                "ALLOWED_HOSTS must not be empty in Production.")
        engine = DATABASES["default"]["ENGINE"]
        if engine.endswith("sqlite3"):
            raise ImproperlyConfigured("SQLite is not allowed in Production.")


_guardrails()
