from .base import BASE_DIR


print("Loading LOCAL settings")


DEBUG = True
SECRET_KEY = "dev-insecure-key"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
