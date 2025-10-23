import pytest
from django.db import IntegrityError

from adversaries.models import Adversary, DamageProfile, BasicAttack, Tactic, \
    Tag, Experience, Feature, DamageType, AdversaryExperience
from adversaries.dto import AdversaryDTO, BasicAttackDTO, DamageDTO, \
    TacticDTO, TagDTO, ExperienceDTO, FeatureDTO
from adversaries.services import create_adversary, _sync_experiences, \
    put_adversary


@pytest.fixture
def dummy_dto_package(
        *,
        name="Ashen Tyrant",
        tier="1",
        type_="SOL",
        description="Big scary bug",
        difficulty="14",
        threshold_major="8",
        threshold_severe=15,
        hit_point="8",
        horde_hit_point=None,
        stress_point=3,
        atk_bonus="+3",
        source="Darrington Press",
        status="DRA",
        ba_name="Claws",
        ba_range="Very Close",
        dmg_dice_number="1",
        dmg_dice_type="12",
        dmg_bonus="2",
        dmg_type="PHY",
        tags=("fire", "desert"),
        tactics=("Flank", "Ambush"),
        features=(
                ("Relentless", "PAS", "Act twice"),
                ("Spit Acid", "ACT", "Cone"),
        ),
        experiences=(("Burrow", 2), ("Flank", 3)),
        with_basic_attack=True
):
    basic_attack = None
    if with_basic_attack:
        damage = DamageDTO(
            dice_number=int(dmg_dice_number),
            dice_type=int(dmg_dice_type),
            bonus=int(dmg_bonus),
            damage_type=dmg_type,
        )
        basic_attack = BasicAttackDTO(
            name=ba_name, range=ba_range, damage=damage
        )

    tags_output = [TagDTO(name=t) for t in tags]
    tactics_output = [TacticDTO(name=t) for t in tactics]
    features_output = [FeatureDTO(name=n, type=t, description=d)
                       for (n, t, d) in features]
    experiences_output = [ExperienceDTO(name=n, bonus=b)
                          for (n, b) in experiences]

    return {
        "name": name,
        "tier": tier,
        "type": type_,
        "description": description,
        "difficulty": difficulty,
        "threshold_major": threshold_major,
        "threshold_severe": threshold_severe,
        "hit_point": hit_point,
        "horde_hit_point": horde_hit_point,
        "stress_point": stress_point,
        "atk_bonus": atk_bonus,
        "source": source,
        "status": status,
        "basic_attack": basic_attack,
        "tags": tags_output,
        "tactics": tactics_output,
        "features": features_output,
        "experiences": experiences_output,
    }


# --- CREATE TESTS --- #
@pytest.mark.django_db
def test_create_adversary_minimal_default(conf_account):
    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Goblin"
    )

    adv = create_adversary(dto)

    assert Adversary.objects.count() == 1
    assert adv.author == conf_account
    assert adv.name == "Goblin"
    assert adv.tier == Adversary.Tier.UNSPECIFIED
    assert adv.type == Adversary.Type.UNSPECIFIED
    assert adv.description is None
    assert adv.difficulty is None
    assert adv.threshold_major is None
    assert adv.threshold_severe is None
    assert adv.hit_point is None
    assert adv.horde_hit_point is None
    assert adv.stress_point is None
    assert adv.atk_bonus is None
    assert adv.source is None
    assert adv.status == Adversary.Status.UNSPECIFIED
    assert adv.basic_attack is None
    assert adv.tactics.count() == 0
    assert adv.tags.count() == 0
    assert adv.experiences.count() == 0
    assert adv.features.count() == 0


@pytest.mark.django_db
def test_create_adversary_with_nested_and_m2m(conf_account, dummy_dto_package):
    dto = AdversaryDTO(author_id=conf_account.id, **dummy_dto_package)
    adv = create_adversary(dto)
    adv.refresh_from_db()

    # simple fields
    assert adv.author == conf_account
    assert adv.name == "Ashen Tyrant"
    assert adv.tier == 1
    assert adv.type == "SOL"
    assert adv.description == "Big scary bug"
    assert adv.difficulty == 14
    assert adv.threshold_major == 8
    assert adv.threshold_severe == 15
    assert adv.hit_point == 8
    assert adv.horde_hit_point is None
    assert adv.stress_point == 3
    assert adv.atk_bonus == 3
    assert adv.source == "Darrington Press"
    assert adv.status == Adversary.Status.DRAFT

    # objects counts created
    assert Adversary.objects.count() == 1
    assert DamageProfile.objects.count() == 1
    assert BasicAttack.objects.count() == 1
    assert Tactic.objects.count() == 2
    assert Tag.objects.count() == 2
    assert Experience.objects.count() == 2
    assert Feature.objects.count() == 2

    # basic attack
    ba = adv.basic_attack
    assert ba.name == "Claws"
    assert ba.range == "Very Close"

    dp = adv.basic_attack.damage
    assert ((dp.dice_number, dp.dice_type, dp.bonus, dp.damage_type) ==
            (1, 12, 2, DamageType.PHYSICAL))

    # M2M content
    assert set(adv.tactics.values_list("name", flat=True)) == {
        "Flank", "Ambush"
    }
    assert set(adv.tags.values_list("name", flat=True)) == {"fire", "desert"}
    assert set(adv.features.values_list("name", "type", "description")) == {
        ("Relentless", Feature.Type.PASSIVE, "Act twice"),
        ("Spit Acid", Feature.Type.ACTION, "Cone"),
    }

    # experiences via AdversaryExperience
    adv_exps = (
        AdversaryExperience.objects.filter(adversary=adv)
        .select_related("experience")
        .values_list("experience__name", "bonus")
    )
    assert set(adv_exps) == {("Burrow", 2), ("Flank", 3)}


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
