print("HEEELLO")

DEBUG = False
SECRET_KEY = "testing-insecure-key"
ALLOWED_HOSTS = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
