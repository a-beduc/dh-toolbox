import pytest

from accounts.models import Account


@pytest.fixture
def conf_account():
    return Account.objects.create(username="lou")


@pytest.fixture
def fast_auth(settings):
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
    settings.AUTH_PASSWORD_VALIDATORS = []
