import pytest
from django.db import IntegrityError

from adversaries.dtos.dto import AdversaryDTO, BasicAttackDTO, DamageDTO, \
    TacticDTO, TagDTO, ExperienceDTO, FeatureDTO
from adversaries.models import Adversary, DamageProfile, BasicAttack, Tactic, \
    Tag, Experience, Feature, DamageType, AdversaryExperience
from adversaries.services import create_adversary, put_adversary


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


# --- PUT TESTS --- #
@pytest.mark.django_db
def test_put_adversary_minimal_default(conf_account):
    Adversary.objects.create(name="Goblin", author_id=conf_account.id)

    adv_db = list(Adversary.objects.all())

    assert Adversary.objects.count() == 1
    assert adv_db[0].name == "Goblin"
    assert adv_db[0].id == 1

    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Dragon"
    )
    adv_get = Adversary.objects.get(pk=1)
    adv = put_adversary(adv_get, dto)

    assert Adversary.objects.count() == 1
    assert adv.author == conf_account
    assert adv.name == "Dragon"
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
def test_put_adversary_minimal_reset_data_to_default(conf_account,
                                                     dummy_dto_package):
    dto = AdversaryDTO(author_id=conf_account.id, **dummy_dto_package)
    create_adversary(dto)

    adv_db = list(Adversary.objects.all())

    assert Adversary.objects.count() == 1
    assert adv_db[0].name == "Ashen Tyrant"
    assert adv_db[0].id == 1

    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Dragon"
    )
    adv_get = Adversary.objects.get(pk=1)
    adv = put_adversary(adv_get, dto)

    assert Adversary.objects.count() == 1
    assert adv.author == conf_account
    assert adv.name == "Dragon"
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
def test_put_adversary_overwrite_nested_and_m2m(conf_account,
                                                dummy_dto_package):
    # seed
    seed_dto = AdversaryDTO(author_id=conf_account.id, **dummy_dto_package)
    adv = create_adversary(seed_dto)

    assert Adversary.objects.count() == 1
    assert DamageProfile.objects.count() == 1
    assert BasicAttack.objects.count() == 1
    assert set(adv.tags.values_list("name", flat=True)) == {"fire", "desert"}
    assert set(adv.tactics.values_list("name", flat=True)) == {"Flank",
                                                               "Ambush"}
    assert set(adv.features.values_list("name", "type", "description")) == {
        ("Relentless", Feature.Type.PASSIVE, "Act twice"),
        ("Spit Acid", Feature.Type.ACTION, "Cone"),
    }
    assert set(
        AdversaryExperience.objects
        .filter(adversary=adv)
        .select_related("experience")
        .values_list("experience__name", "bonus")
    ) == {("Burrow", 2), ("Flank", 3)}

    # PUT payload
    update_dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Ashen Wyrm",
        tier=2,
        type="SOL",
        description="Older, meaner bug",
        difficulty=16,
        threshold_major=9,
        threshold_severe=18,
        hit_point=10,
        horde_hit_point=None,
        stress_point=4,
        atk_bonus=5,
        source="Field Notes",
        status="DRA",
        basic_attack=BasicAttackDTO(
            name="Bite",
            range="Close",
            damage=DamageDTO(
                dice_number=2, dice_type=8, bonus=0, damage_type="MAG"
            ),
        ),
        tags=[TagDTO(name="ash")],
        tactics=[TacticDTO(name="Ambush"), TacticDTO(name="Charge")],
        features=[
            FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
            FeatureDTO(name="Tail Swipe", type="ACT", description="Line"),
        ],
        experiences=[
            ExperienceDTO(name="Flank", bonus=5),
            ExperienceDTO(name="Tunnel", bonus=1),
        ],
    )

    # PUT
    adv_db = Adversary.objects.get(pk=adv.pk)
    updated = put_adversary(adv_db, update_dto)

    # simple fields updated
    assert Adversary.objects.count() == 1
    assert updated.author == conf_account
    assert updated.name == "Ashen Wyrm"
    assert updated.tier == 2
    assert updated.type == "SOL"
    assert updated.description == "Older, meaner bug"
    assert updated.difficulty == 16
    assert updated.threshold_major == 9
    assert updated.threshold_severe == 18
    assert updated.hit_point == 10
    assert updated.horde_hit_point is None
    assert updated.stress_point == 4
    assert updated.atk_bonus == 5
    assert updated.source == "Field Notes"
    assert updated.status == Adversary.Status.DRAFT

    # Basic attack
    assert BasicAttack.objects.count() == 2
    assert DamageProfile.objects.count() == 2
    ba = updated.basic_attack
    assert (ba.name, ba.range) == ("Bite", "Close")
    dp = ba.damage
    assert (dp.dice_number, dp.dice_type, dp.bonus, dp.damage_type) == (2, 8, 0, DamageType.MAGICAL)

    # M2M sets are *replaced* to match the DTO order/content
    assert set(updated.tags.values_list("name", flat=True)) == {"ash"}
    assert set(updated.tactics.values_list("name", flat=True)) == {"Ambush", "Charge"}

    # Feature
    assert Feature.objects.count() == 3
    assert set(updated.features.values_list("name", "type", "description")) == {
        ("Relentless", Feature.Type.PASSIVE, "Act twice"),
        ("Tail Swipe", Feature.Type.ACTION, "Line"),
    }

    # Experience
    adv_exps = (
        AdversaryExperience.objects.filter(adversary=updated)
        .select_related("experience")
        .values_list("experience__name", "bonus")
    )
    assert set(adv_exps) == {("Flank", 5), ("Tunnel", 1)}

    assert Tag.objects.count() == 3
    assert Tactic.objects.count() == 3
    assert Experience.objects.count() == 3
