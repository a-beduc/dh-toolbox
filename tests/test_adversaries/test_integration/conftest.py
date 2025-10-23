import pytest

from adversaries.models import Adversary


@pytest.fixture
def conf_adv(conf_account):
    return Adversary.objects.create(
        author=conf_account,
        name="testing"
    )
