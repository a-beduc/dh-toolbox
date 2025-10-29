import pytest
from django.db import IntegrityError

from adversaries.dtos.dto import AdversaryDTO, BasicAttackDTO, DamageDTO, \
    TacticDTO, TagDTO, ExperienceDTO, FeatureDTO
from adversaries.dtos.dto_patch import AdversaryPatchDTO, TagPatchDTO, \
    TacticPatchDTO, FeaturePatchDTO, ExperiencePatchDTO, BasicAttackPatchDTO, \
    DamagePatchDTO
from adversaries.models import Adversary, DamageProfile, BasicAttack, Tactic, \
    Tag, Experience, Feature, DamageType, AdversaryExperience
from adversaries.services import adversary_create, adversary_update, \
    adversary_partial_update


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

    adv = adversary_create(dto)

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
    adv = adversary_create(dto)

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
        adversary_create(dto)

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
    adv = adversary_update(adv_get, dto)

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
    adversary_create(dto)

    adv_db = list(Adversary.objects.all())

    assert Adversary.objects.count() == 1
    assert adv_db[0].name == "Ashen Tyrant"
    assert adv_db[0].id == 1

    dto = AdversaryDTO(
        author_id=conf_account.id,
        name="Dragon"
    )
    adv_get = Adversary.objects.get(pk=1)
    adv = adversary_update(adv_get, dto)

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
    adv = adversary_create(seed_dto)

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
    updated = adversary_update(adv_db, update_dto)

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


# --- PATCH TESTS --- #
@pytest.mark.django_db
def test_patch_adversary_minimal(conf_account):
    # Seed
    adv = Adversary.objects.create(name="Goblin", author_id=conf_account.id)
    assert adv.name == "Goblin"

    dto = AdversaryPatchDTO(name="Dragon")
    updated = adversary_partial_update(adv, dto)

    assert updated.pk == adv.pk
    assert updated.name == "Dragon"
    assert updated.tier == Adversary.Tier.UNSPECIFIED
    assert updated.description is None
    assert updated.basic_attack is None
    assert updated.tactics.count() == 0
    assert updated.tags.count() == 0
    assert updated.experiences.count() == 0
    assert updated.features.count() == 0


@pytest.mark.django_db
def test_patch_forgotten_fields_are_ignored_and_none_clears(conf_account,
                                                            dummy_dto_package):
    dto = AdversaryDTO(author_id=conf_account.id, **dummy_dto_package)
    adv = adversary_create(dto)

    assert adv.source == "Darrington Press"
    assert adv.tier == 1
    assert adv.type == "SOL"

    patch = AdversaryPatchDTO(
        description="Now smells like ozone",
        source=None,
    )
    updated = adversary_partial_update(adv, patch)

    assert updated.description == "Now smells like ozone"
    assert updated.source is None
    assert updated.tier == 1
    assert updated.type == "SOL"


@pytest.mark.django_db
def test_patch_m2m_replace_ignore_and_clear(conf_account, dummy_dto_package):
    dto = AdversaryDTO(author_id=conf_account.id, **dummy_dto_package)
    adv = adversary_create(dto)

    # forgotten field are untouched
    p1 = AdversaryPatchDTO(
        name="Ashen Tyrant II",
    )
    adv = adversary_partial_update(adv, p1)
    assert adv.name == "Ashen Tyrant II"
    assert set(adv.tags.values_list("name", flat=True)) == {"fire", "desert"}
    assert set(adv.tactics.values_list("name", flat=True)) == {"Flank",
                                                               "Ambush"}
    assert set(adv.features.values_list("name", "type", "description")) == {
        ("Relentless", Feature.Type.PASSIVE, "Act twice"),
        ("Spit Acid", Feature.Type.ACTION, "Cone"),
    }
    exp_pairs = set(
        AdversaryExperience.objects.filter(adversary=adv)
        .select_related("experience")
        .values_list("experience__name", "bonus")
    )
    assert exp_pairs == {("Burrow", 2), ("Flank", 3)}

    # replace
    p2 = AdversaryPatchDTO(
        tags=[TagPatchDTO(name="ash"), TagPatchDTO(name="ember")],
        tactics=[TacticPatchDTO(name="Ambush"), TacticPatchDTO(name="Charge")],
        features=[
            FeaturePatchDTO(name="Tail Swipe", type="ACT", description="Line"),
            FeaturePatchDTO(name="Relentless", type="PAS",
                            description="Act twice"),
        ],
        experiences=[
            ExperiencePatchDTO(name="Flank", bonus=5),
            ExperiencePatchDTO(name="Tunnel", bonus=1),
        ],
    )
    adv = adversary_partial_update(adv, p2)
    assert set(adv.tags.values_list("name", flat=True)) == {"ash", "ember"}
    assert set(adv.tactics.values_list("name", flat=True)) == {"Ambush",
                                                               "Charge"}
    assert set(adv.features.values_list("name", "type", "description")) == {
        ("Tail Swipe", Feature.Type.ACTION, "Line"),
        ("Relentless", Feature.Type.PASSIVE, "Act twice"),
    }
    exp_pairs = set(
        AdversaryExperience.objects.filter(adversary=adv)
        .select_related("experience")
        .values_list("experience__name", "bonus")
    )
    assert exp_pairs == {("Flank", 5), ("Tunnel", 1)}

    # empty list clears the fields
    p3 = AdversaryPatchDTO(tags=[], tactics=[], features=[], experiences=[])
    adv = adversary_partial_update(adv, p3)
    assert adv.tags.count() == 0
    assert adv.tactics.count() == 0
    assert adv.features.count() == 0
    assert AdversaryExperience.objects.filter(adversary=adv).count() == 0

    # resource remains, only link are cleared
    assert Tag.objects.count() >= 2
    assert Tactic.objects.count() >= 2
    assert Feature.objects.count() >= 2
    assert Experience.objects.count() >= 2


@pytest.mark.django_db
def test_patch_basic_attack_crud_and_partial(conf_account):
    # Seed without BA
    adv = Adversary.objects.create(name="Wasp", author_id=conf_account.id)
    assert adv.basic_attack is None
    assert BasicAttack.objects.count() == 0
    assert DamageProfile.objects.count() == 0

    # Create BA with damage
    p1 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(
            name="Sting",
            range="Close",
            damage=DamagePatchDTO(dice_number=2, dice_type=4, bonus=1,
                                  damage_type="MAG")
        )
    )
    adv = adversary_partial_update(adv, p1)
    assert adv.basic_attack is not None
    ba = adv.basic_attack
    assert (ba.name, ba.range) == ("Sting", "Close")
    dp = ba.damage
    assert (dp.dice_number, dp.dice_type, dp.bonus, dp.damage_type) == (
        2, 4, 1, DamageType.MAGICAL)

    # Partial BA update
    p2 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(name="Impale")
    )
    adv = adversary_partial_update(adv, p2)
    assert BasicAttack.objects.count() == 2

    assert adv.basic_attack_id == 2
    assert adv.basic_attack.name == "Impale"

    dp2 = adv.basic_attack.damage
    assert dp2.pk == 1
    assert (dp2.dice_number, dp2.dice_type, dp2.bonus, dp2.damage_type) == (
        2, 4, 1, DamageType.MAGICAL)

    # Partial DAMAGE update
    p3 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(
            damage=DamagePatchDTO(bonus=3)
        )
    )
    adv = adversary_partial_update(adv, p3)
    dp3 = adv.basic_attack.damage
    # Update DamageProfile created a new row
    assert dp3.pk == 2
    assert (dp3.dice_number, dp3.dice_type, dp3.bonus, dp3.damage_type) == (
        2, 4, 3, DamageType.MAGICAL)

    # Clear BA
    p4 = AdversaryPatchDTO(basic_attack=None)
    adv = adversary_partial_update(adv, p4)
    assert adv.basic_attack is None

    # resource remains, only link are cleared
    assert BasicAttack.objects.count() >= 1
    assert DamageProfile.objects.count() >= 1


@pytest.mark.django_db
def test_patch_update_basic_attack_profile_reuse_basic_attack(conf_account):
    # Seed without BA
    adv = Adversary.objects.create(name="Wasp", author_id=conf_account.id)
    assert adv.basic_attack is None
    assert BasicAttack.objects.count() == 0
    assert DamageProfile.objects.count() == 0

    # Create BA with BA (create new BA)
    p1 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(
            name="Sting",
            range="Close",
            damage=DamagePatchDTO(dice_number=2, dice_type=4, bonus=1,
                                  damage_type="MAG")
        )
    )
    adv = adversary_partial_update(adv, p1)
    assert BasicAttack.objects.count() == 1

    # Update BA (create new BA)
    p2 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(
            name="Sting",
            range="Close",
            damage=DamagePatchDTO(dice_number=1, dice_type=6, bonus=1,
                                  damage_type="MAG")
        )
    )
    adv = adversary_partial_update(adv, p2)
    assert BasicAttack.objects.count() == 2

    # Update BA (Reuse first BA created)
    p3 = AdversaryPatchDTO(
        basic_attack=BasicAttackPatchDTO(
            name="Sting",
            range="Close",
            damage=DamagePatchDTO(dice_number=1, dice_type=6, bonus=1,
                                  damage_type="MAG")
        )
    )
    adversary_partial_update(adv, p3)
    assert BasicAttack.objects.count() == 2
