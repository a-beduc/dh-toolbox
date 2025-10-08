import pytest
from adversaries.models import DamageProfile, BasicAttack


@pytest.fixture
def flat_dp():
    return DamageProfile.objects.create(bonus=1)


@pytest.fixture
def roll_dp():
    return DamageProfile.objects.create(dice_number=1, dice_type=2)


@pytest.fixture
def basic_attack(roll_dp):
    return BasicAttack.objects.create(name="Sword", damage=roll_dp)
