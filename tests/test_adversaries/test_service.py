import pytest
from django.db import IntegrityError

from adversaries.dto import AdversaryDTO, BasicAttackDTO, DamageDTO, \
    TacticDTO, AdversaryTagDTO, ExperienceDTO, FeatureDTO
from adversaries.models import Adversary, DamageProfile, BasicAttack, Tactic, \
    AdversaryTag, Experience, Feature, DamageType
from adversaries.services import create_adversary


@pytest.mark.django_db
def test_create_adversary_minimal_default(conf_account):
    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Goblin"
    )

    adv = create_adversary(dto)

    assert Adversary.objects.count() == 1
    assert adv.name == "Goblin"
    assert adv.tier == Adversary.Tier.ONE
    assert adv.type == Adversary.Type.STANDARD
    assert adv.status == Adversary.Status.DRAFT
    assert adv.basic_attack is None
    assert adv.tactics.count() == 0
    assert adv.tags.count() == 0
    assert adv.experiences.count() == 0
    assert adv.features.count() == 0


@pytest.mark.django_db
def test_create_adversary_with_nested_and_m2m(conf_account):
    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Ashen Tyrant",
        tier=3,
        type="SOL",
        status="DRAFT",
        basic_attack=BasicAttackDTO(
            name="Flame Breath",
            damage=DamageDTO(dice_number=6, dice_type=10, bonus=3,
                             damage_type="MAG"),
        ),
        tactics=[TacticDTO(name="flank"), TacticDTO(name="overwhelm")],
        tags=[AdversaryTagDTO(name="dragon"), AdversaryTagDTO(name="fire")],
        experiences=[ExperienceDTO(name="Scorched Earth", bonus=2),
                     ExperienceDTO(name="Flying", bonus=3)],
        features=[FeatureDTO(name="Wing Buffet", type="ACT",
                             description="Push targets")])

    adv = create_adversary(dto)

    assert Adversary.objects.count() == 1
    assert DamageProfile.objects.count() == 1
    assert BasicAttack.objects.count() == 1
    assert Tactic.objects.count() == 2
    assert AdversaryTag.objects.count() == 2
    assert Experience.objects.count() == 2
    assert Feature.objects.count() == 1

    assert adv.name == "Ashen Tyrant"
    assert adv.tier == 3
    assert adv.type == "SOL"

    assert adv.basic_attack == BasicAttack.objects.get(
        name="Flame Breath",
        range=BasicAttack.Range.MELEE,
        damage=DamageProfile.objects.get(
            dice_number=6, dice_type=10, bonus=3, damage_type="MAG"))
    dp = adv.basic_attack.damage
    assert ((dp.dice_number, dp.dice_type, dp.bonus, dp.damage_type) ==
            (6, 10, 3, DamageType.MAGICAL))

    assert set(adv.tactics.values_list("name", flat=True)) == {"flank",
                                                               "overwhelm"}
    assert set(adv.tags.values_list("name", flat=True)) == {"dragon", "fire"}
    assert set(adv.experiences.values_list("name", "bonus")) == {
        ("Scorched Earth", 2), ("Flying", 3)}

    assert set(adv.features.values_list("name", "type", "description")) == {
        ("Wing Buffet", Feature.Type.ACTION, "Push targets")
    }


@pytest.mark.django_db
def test_rollback_on_invalid_damage_constraint(conf_account):
    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Bad Damage",
        basic_attack=BasicAttackDTO(
            name="Weird",
            damage=DamageDTO(dice_number=0, dice_type=6, bonus=1,
                             damage_type="PHY"),
        ),
    )

    with pytest.raises(IntegrityError):
        create_adversary(dto)

    assert Adversary.objects.count() == 0
    assert DamageProfile.objects.count() == 0
    assert BasicAttack.objects.count() == 0
