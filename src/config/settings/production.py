import os
from django.core.exceptions import ImproperlyConfigured


def env_required(env_variable):
    try:
        return os.environ[env_variable]
    except KeyError:
        error_msg = f'Set the {env_variable} environment variable'
        raise ImproperlyConfigured(error_msg)


DEBUG = False

SECRET_KEY = env_required('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = [h.strip() for h in env_required('ALLOWED_HOSTS').split(",")
                 if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS must not be empty in Production.")

# set prod settings later
# DATABASES should be PostgresSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env_required("PGNAME"),
        'USER': env_required("PGUSER"),
        'PASSWORD': env_required("PGPASSWORD"),
        'HOST': os.getenv("PGHOST", "localhost"),
        'PORT': int(os.getenv("PGPORT", "5432")),
    }
}
