from django.db import transaction
from django.db.models import Q

from adversaries.models import Adversary, Tactic, Tag, Experience, \
    Feature, DamageProfile, BasicAttack, AdversaryExperience


def _remove_none_field(d):
    return {k: v for k, v in d.items() if v is not None}


@transaction.atomic
def create_adversary(dto):
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

    adv = Adversary.objects.create(**adv_kwargs)

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


def update_adversary(dto):
    pass
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
