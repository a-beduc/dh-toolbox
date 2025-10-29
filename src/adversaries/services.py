from django.db import transaction
from django.db.models import Q

from adversaries.helpers.sentinel import is_unset
from adversaries.models import Adversary, Tactic, Tag, Experience, \
    Feature, DamageProfile, BasicAttack, AdversaryExperience, DamageType


def _remove_none_field(d):
    return {k: v for k, v in d.items() if v is not None}


@transaction.atomic
def adversary_create(dto):
    """TODO: Optimize queries later (less query if possible)"""
    ba_obj = None
    if dto.basic_attack is not None:
        dp_obj = None
        dmg = dto.basic_attack.damage
        if dmg:
            dp_kwargs = _remove_none_field({
                "dice_number": dmg.dice_number,
                "dice_type": dmg.dice_type,
                "bonus": dmg.bonus,
                "damage_type": dmg.damage_type,
            })
            dp_obj, _ = DamageProfile.objects.get_or_create(**dp_kwargs)

        ba_kwargs = _remove_none_field({
            "name": dto.basic_attack.name,
            "range": dto.basic_attack.range,
            "damage": dp_obj,
        })
        ba_obj, _ = BasicAttack.objects.get_or_create(**ba_kwargs)

    adv_kwargs = _remove_none_field({
        "author_id": dto.author_id,
        "name": dto.name,
        "tier": dto.tier,
        "type": dto.type,
        "description": dto.description,
        "difficulty": dto.difficulty,
        "threshold_major": dto.threshold_major,
        "threshold_severe": dto.threshold_severe,
        "hit_point": dto.hit_point,
        "horde_hit_point": dto.horde_hit_point,
        "stress_point": dto.stress_point,
        "atk_bonus": dto.atk_bonus,
        "basic_attack": ba_obj,
        "source": dto.source,
        "status": dto.status,
    })

    adv = Adversary(**adv_kwargs)
    adv.full_clean()
    adv.save()

    for t in dto.tactics:
        obj, _ = Tactic.objects.get_or_create(name=t.name)
        adv.tactics.add(obj)
    for tg in dto.tags:
        obj, _ = Tag.objects.get_or_create(name=tg.name)
        adv.tags.add(obj)
    for exp in dto.experiences:
        obj, _ = Experience.objects.get_or_create(name=exp.name)
        adv.add_experience(obj, bonus=exp.bonus)
    for f in dto.features:
        feat, _ = Feature.objects.get_or_create(
            name=f.name, type=Feature.Type(f.type), description=f.description)
        adv.features.add(feat)

    return adv


def _sync_experiences(adv, exp_dtos):
    target = {e.name: e.bonus for e in exp_dtos}
    if not target:
        AdversaryExperience.objects.filter(adversary=adv).delete()
        return

    names = list(target.keys())

    names_to_id = dict(
        Experience.objects
        .filter(name__in=names)
        .values_list("name", "id")
    )

    missing = [Experience(name=n) for n in names if n not in names_to_id]
    if missing:
        Experience.objects.bulk_create(missing)
        names_to_id = dict(
            Experience.objects
            .filter(name__in=names)
            .values_list("name", "id")
        )

    seen_ids = set()
    for name, bonus in target.items():
        exp_id = names_to_id[name]
        AdversaryExperience.objects.update_or_create(
            adversary=adv,
            experience_id=exp_id,
            defaults={"bonus": bonus}
        )
        seen_ids.add(exp_id)

    (AdversaryExperience.objects
     .filter(adversary=adv)
     .exclude(experience_id__in=seen_ids)
     .delete())


def _sync_m2m_by_name(m2m_manager, model, dtos):
    names = [t.name for t in dtos]
    if not names:
        m2m_manager.set([])
        return

    names_to_id = dict(
        model.objects
        .filter(name__in=names)
        .values_list("name", "id")
    )

    to_create = [model(name=n) for n in names if n not in names_to_id]
    if to_create:
        model.objects.bulk_create(to_create)
        names_to_id = dict(
            model.objects
            .filter(name__in=names)
            .values_list("name", "id")
        )

    m2m_manager.set([names_to_id[n] for n in names])


def _sync_features(m2m_manager, dtos):
    if not dtos:
        m2m_manager.set([])
        return

    keys = [(f.name, Feature.Type(f.type), f.description) for f in dtos]

    q = Q()
    for n, t, d in keys:
        # |= add 'or Q' to existing Query 'q' to build complete Query
        q |= Q(name=n, type=t, description=d)

    features = Feature.objects.filter(q).only(
        "id", "name", "type", "description")
    existing = {
        (feat.name, feat.type, feat.description): feat.id
        for feat in features
    }

    to_create = [
        Feature(name=n, type=t, description=d)
        for (n, t, d) in keys if (n, t, d) not in existing
    ]

    if to_create:
        Feature.objects.bulk_create(to_create)
        # need to refresh Query stored in cache
        features = Feature.objects.filter(q).only(
            "id", "name", "type", "description")
        existing = {
            (feat.name, feat.type, feat.description): feat.id
            for feat in features
        }

    m2m_manager.set([existing[k] for k in keys])


@transaction.atomic
def adversary_update(adv, dto):
    adv = Adversary.objects.select_for_update().get(pk=adv.pk)

    # --- Simple attributes --- #
    adv.name = dto.name
    adv.tier_value = dto.tier
    adv.type_value = dto.type
    adv.description = dto.description
    adv.difficulty = dto.difficulty
    adv.threshold_major = dto.threshold_major
    adv.threshold_severe = dto.threshold_severe
    adv.hit_point = dto.hit_point
    adv.horde_hit_point = dto.horde_hit_point
    adv.stress_point = dto.stress_point
    adv.atk_bonus = dto.atk_bonus
    adv.source = dto.source
    adv.status_value = dto.status

    # --- Basic Attack --- #
    if dto.basic_attack is None:
        adv.basic_attack = None
    else:
        ba = dto.basic_attack
        dp_obj = None

        if ba.damage is not None:
            d = ba.damage
            dp_obj, _ = DamageProfile.objects.get_or_create(
                dice_number=d.dice_number,
                dice_type=d.dice_type,
                bonus=d.bonus,
                damage_type=d.damage_type
            )

        ba_obj, _ = BasicAttack.objects.get_or_create(
            name=ba.name,
            range=ba.range,
            damage=dp_obj
        )
        adv.basic_attack = ba_obj

    # --- M2M --- #
    _sync_m2m_by_name(adv.tags, Tag, dto.tags)
    _sync_m2m_by_name(adv.tactics, Tactic, dto.tactics)
    _sync_features(adv.features, dto.features)
    _sync_experiences(adv, dto.experiences)

    adv.full_clean()
    adv.save()

    return adv


def _resolve_damage_profile(existing_dp, dto):
    if is_unset(dto):
        return existing_dp

    if dto is None:
        return None

    dice_number = getattr(existing_dp, "dice_number", None)
    dice_type = getattr(existing_dp, "dice_type", None)
    bonus = getattr(existing_dp, "bonus", None)
    damage_type = getattr(existing_dp, "damage_type", None)

    if not is_unset(dto.dice_number):
        dice_number = dto.dice_number
    if not is_unset(dto.dice_type):
        dice_type = dto.dice_type
    if not is_unset(dto.bonus):
        bonus = dto.bonus
    if not is_unset(dto.damage_type):
        damage_type = DamageType(dto.damage_type) \
            if dto.damage_type is not None else None

    if (dice_number is None
            and dice_type is None
            and bonus is None
            and damage_type is None):
        return None

    dp_kwargs = _remove_none_field({
        "dice_number": dice_number,
        "dice_type": dice_type,
        "bonus": bonus,
        "damage_type": damage_type,
    })
    dp, _ = DamageProfile.objects.get_or_create(**dp_kwargs)

    return dp


def _resolve_basic_attack(existing_ba, dto):
    if is_unset(dto):
        return existing_ba

    if dto is None:
        return None

    name = getattr(existing_ba, "name", None)
    range_ba = getattr(existing_ba, "range", None)
    damage = getattr(existing_ba, "damage", None)

    if not is_unset(dto.name):
        name = dto.name
    if not is_unset(dto.range):
        range_ba = dto.range
    damage = _resolve_damage_profile(damage, dto.damage)

    if (name, range_ba, damage) == (None, None, None):
        return None

    ba_kwargs = _remove_none_field({
        "name": name,
        "range": range_ba,
        "damage": damage,
    })
    ba_obj, _ = BasicAttack.objects.get_or_create(**ba_kwargs)

    return ba_obj


@transaction.atomic
def adversary_partial_update(adv, dto):
    adv = Adversary.objects.select_for_update().get(pk=adv.pk)

    simple_attr_map = {
        "name": "name",
        "tier": "tier_value",
        "type": "type_value",
        "description": "description",
        "difficulty": "difficulty",
        "threshold_major": "threshold_major",
        "threshold_severe": "threshold_severe",
        "hit_point": "hit_point",
        "horde_hit_point": "horde_hit_point",
        "stress_point": "stress_point",
        "atk_bonus": "atk_bonus",
        "source": "source",
        "status": "status_value"
    }

    # --- Simple attributes --- #
    for attr in simple_attr_map:
        value = getattr(dto, attr)
        if not is_unset(value):
            setattr(adv, simple_attr_map[attr], value)

    # --- Basic attack --- #
    if not is_unset(dto.basic_attack):
        adv.basic_attack = _resolve_basic_attack(adv.basic_attack,
                                                 dto.basic_attack)

    # --- M2M --- #
    if not is_unset(dto.tactics):
        _sync_m2m_by_name(adv.tactics, Tactic, dto.tactics)

    if not is_unset(dto.tags):
        _sync_m2m_by_name(adv.tags, Tag, dto.tags)

    if not is_unset(dto.experiences):
        _sync_experiences(adv, dto.experiences)

    if not is_unset(dto.features):
        _sync_features(adv.features, dto.features)

    adv.full_clean()
    adv.save()
    return adv
