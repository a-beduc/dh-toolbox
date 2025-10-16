from django.db import transaction

from adversaries.models import Adversary, Tactic, Tag, Experience, \
    Feature, DamageProfile, BasicAttack


def remove_none_field(d):
    return {k: v for k, v in d.items() if v is not None}


@transaction.atomic
def create_adversary(dto):
    ba_obj = None
    if dto.basic_attack is not None:
        dmg = dto.basic_attack.damage
        dp_kwargs = remove_none_field({
            "dice_number": dmg.dice_number,
            "dice_type": dmg.dice_type,
            "bonus": dmg.bonus,
            "damage_type": dmg.damage_type,
        })
        dp_obj, _ = DamageProfile.objects.get_or_create(**dp_kwargs)

        ba_kwargs = remove_none_field({
            "name": dto.basic_attack.name,
            "range": dto.basic_attack.range,
            "damage": dp_obj,
        })
        ba_obj, _ = BasicAttack.objects.get_or_create(**ba_kwargs)

    adv_kwargs = remove_none_field({
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

    adv = Adversary.objects.create(**adv_kwargs)

    for t in dto.tactics:
        obj, _ = Tactic.objects.get_or_create(name=t.name)
        adv.tactics.add(obj)
    for tg in dto.tags:
        obj, _ = Tag.objects.get_or_create(name=tg.name)
        adv.tags.add(obj)
    for exp in dto.experiences:
        e, _ = Experience.objects.get_or_create(name=exp.name, bonus=exp.bonus)
        adv.experiences.add(e)
    for f in dto.features:
        feat, _ = Feature.objects.get_or_create(
            name=f.name, type=Feature.Type(f.type), description=f.description)
        adv.features.add(feat)

    return adv
