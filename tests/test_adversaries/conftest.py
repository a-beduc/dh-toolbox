import pytest

from accounts.models import Account
from adversaries.models import DamageProfile, BasicAttack


@pytest.fixture
def conf_flat_dp():
    return DamageProfile.objects.create(bonus=1)


@pytest.fixture
def conf_roll_dp():
    return DamageProfile.objects.create(dice_number=1, dice_type=2)


@pytest.fixture
def conf_basic_attack(conf_roll_dp):
    return BasicAttack.objects.create(name="Sword", damage=conf_roll_dp)


@pytest.fixture
def conf_account():
    return Account.objects.create(username="lou")
