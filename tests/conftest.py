import pytest

from accounts.models import Account


@pytest.fixture
def conf_account():
    return Account.objects.create(username="lou")