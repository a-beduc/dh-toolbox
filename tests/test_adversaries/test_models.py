import pytest
from django.core.exceptions import ValidationError as Django_ValidationError
from django.db import IntegrityError as Django_IntegrityError
from django.db.models.deletion import ProtectedError as Django_ProtectedError

from adversaries.models import Tactic, DamageProfile, DamageType, BasicAttack, \
    Experience, Feature, Adversary


# --- TACTIC TESTS --- #
@pytest.mark.django_db
def test_tactic_create_and_get():
    Tactic.objects.bulk_create([
        Tactic(name="Ambush"),
        Tactic(name="Flank")
    ])

    assert Tactic.objects.filter(name="Ambush").exists()

    saved = Tactic.objects.get(name="Ambush")
    assert saved.pk is not None
    assert saved.name == "Ambush"


@pytest.mark.django_db
def test_tactic_unique_name():
    Tactic.objects.create(name="Stalk")
    with pytest.raises(Django_IntegrityError):
        Tactic.objects.create(name="Stalk")


# --- DAMAGE PROFILE TESTS --- #
@pytest.mark.django_db
def test_damage_profile_defaults():
    dp = DamageProfile.objects.create()
    assert dp.dice_number == 0
    assert dp.dice_type == 0
    assert dp.bonus == 0
    assert dp.damage_type == DamageType.PHYSICAL


@pytest.mark.django_db
def test_damage_profile_unique_entity():
    DamageProfile.objects.create(bonus=5)
    with pytest.raises(Django_IntegrityError):
        DamageProfile.objects.create(bonus=5)


@pytest.mark.parametrize(
    "dice_nbr, dice_type, flat, dice_nbr_value, dice_type_value, flat_value",
    [
        ("pos_dice", "valid_type", "pos_flat", 1, 6, 1),
        ("null_dice", "null_type", "pos_flat", 0, 0, 1),
        ("pos_dice", "valid_type", "null_flat", 1, 4, 0),
        ("null_dice", "null_type", "null_flat", 0, 0, 0),
        ("pos_dice", "valid_type", "neg_flat", 1, 2, -1),
        ("null_dice", "null_type", "null_flat", 0, 0, 0),
    ]
)
@pytest.mark.django_db
def test_damage_profile_valid(dice_nbr, dice_type, flat,
                              dice_nbr_value, dice_type_value, flat_value):
    dp = DamageProfile(dice_number=dice_nbr_value,
                       dice_type=dice_type_value,
                       bonus=flat_value)
    dp.full_clean()
    dp.save()


@pytest.mark.parametrize(
    "dice_nbr, dice_type, flat, dice_nbr_value, dice_type_value, flat_value",
    [
        ("null_dice", "valid_type", "pos_flat", 0, 6, 1),
        ("neg_dice", "valid_type", "pos_flat", -1, 6, 1),
        ("null_dice", "valid_type", "null_flat", 0, 6, 0),
        ("neg_dice", "valid_type", "null_flat", -1, 6, 0),
        ("null_dice", "valid_type", "neg_flat", 0, 6, -1),
        ("neg_dice", "valid_type", "neg_flat", -1, 6, -1),
        ("pos_dice", "invalid_type", "pos_flat", 1, 0, 1),
        ("pos_dice", "invalid_type", "pos_flat", 1, 1, 1),
        ("pos_dice", "invalid_type", "pos_flat", 1, -6, 1),
        ("pos_dice", "invalid_type", "pos_flat", 1, 1, 1),
    ]
)
@pytest.mark.django_db
def test_damage_profile_invalid(dice_nbr, dice_type, flat,
                                dice_nbr_value, dice_type_value, flat_value):
    dp = DamageProfile(dice_number=dice_nbr_value,
                       dice_type=dice_type_value,
                       bonus=flat_value)
    with pytest.raises(Django_ValidationError):
        dp.full_clean()


@pytest.mark.django_db
def test_damage_type_choices_is_valid():
    """Not sure about the resilience of this test, not a fan of hard coded pk,
    may modify later."""
    dp_bth = DamageProfile.objects.create(dice_number=1, dice_type=4, bonus=0,
                                          damage_type=DamageType.BOTH)
    dp_phy = DamageProfile.objects.create(dice_number=1, dice_type=4, bonus=0,
                                          damage_type=DamageType.PHYSICAL)
    dp_mag = DamageProfile.objects.create(dice_number=1, dice_type=4, bonus=0,
                                          damage_type=DamageType.MAGICAL)

    dp_bth.full_clean()
    dp_phy.full_clean()
    dp_mag.full_clean()

    dp_bth.save()
    dp_phy.save()
    dp_mag.save()

    assert DamageProfile.objects.get(pk=1).damage_type == "BTH"
    assert DamageProfile.objects.get(pk=2).damage_type == "PHY"
    assert DamageProfile.objects.get(pk=3).damage_type == "MAG"


# --- BASIC ATTACK TESTS --- #
@pytest.mark.django_db
def test_basic_attack_unique_entity(flat_dp):
    BasicAttack.objects.create(name="Dagger", damage=flat_dp)
    with pytest.raises(Django_IntegrityError):
        BasicAttack.objects.create(name="Dagger", damage=flat_dp)


@pytest.mark.django_db
def test_basic_attack_default_values(flat_dp, roll_dp):
    flat = BasicAttack.objects.create(name="Flat", damage=flat_dp)
    roll = BasicAttack.objects.create(name="Roll", damage=roll_dp)

    assert flat.range == "MELEE"
    assert roll.range == "MELEE"


@pytest.mark.django_db
def test_basic_attack_fk_protect(basic_attack):
    """You can't delete a DamageProfile entity that is used by at least
    one BasicAttack"""
    dp = basic_attack.damage
    with pytest.raises(Django_ProtectedError):
        dp.delete()

    # need to remove the BasicAttack before deleting the DamageProfile
    basic_attack.delete()
    dp.delete()


# --- EXPERIENCE TESTS --- #
@pytest.mark.django_db
def test_experience_unique_entity():
    Experience.objects.create(name="Keen Senses", bonus=3)
    with pytest.raises(Django_IntegrityError):
        Experience.objects.create(name="Keen Senses", bonus=3)


@pytest.mark.django_db
def test_experience_same_name_different_bonus():
    Experience.objects.create(name="Keen Senses", bonus=3)
    Experience.objects.create(name="Keen Senses", bonus=2)
    assert Experience.objects.count() == 2


@pytest.mark.django_db
def test_experience_negative_bonus():
    Experience.objects.create(name="Keen Senses", bonus=-3)


# --- FEATURE TESTS --- #
# TODO: These tests needs to be reworked when feature model is expanded
@pytest.mark.django_db
def test_feature_type_choices_validation():
    f = Feature.objects.create(name="Relenteless", type=Feature.Type.PASSIVE)
    f.full_clean()
    f.save()

    bad = Feature(name="Weird", type="NOPE")
    with pytest.raises(Django_ValidationError):
        bad.full_clean()


@pytest.mark.django_db
def test_adversary_defaults_and_relations(basic_attack):
    adv = Adversary.objects.create(name="Burrower", basic_attack=basic_attack)

    assert adv.tier == Adversary.Tier.ONE
    assert adv.type == Adversary.Type.STANDARD

    t1 = Tactic.objects.create(name="Ambush")
    t2 = Tactic.objects.create(name="Flank")
    adv.tactics.add(t1, t2)

    e1 = Experience.objects.create(name="Keen Senses", bonus=3)
    e2 = Experience.objects.create(name="Relentless", bonus=1)
    adv.experiences.add(e1, e2)

    f1 = Feature.objects.create(name="Earth Eruption",
                                type=Feature.Type.ACTION)
    adv.features.add(f1)

    # adv in memory is not updated, adv in db is (resync here)
    adv.refresh_from_db()
    assert adv.tactics.count() == 2
    assert adv.experiences.count() == 2
    assert adv.features.count() == 1


@pytest.mark.django_db
def test_adversary_requires_basic_attack():
    with pytest.raises(Django_IntegrityError):
        Adversary.objects.create(name="Burrower")
