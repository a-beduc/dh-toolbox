from adversaries.dtos.dto import DamageDTO, BasicAttackDTO, ExperienceDTO, \
    FeatureDTO, TacticDTO, TagDTO, AdversaryDTO
from adversaries.dtos.dto_patch import AdversaryPatchDTO
from api.v1.helpers.sentinel import present, get_or_unset


def to_damage_dto(data):
    if not data:
        return None

    return DamageDTO(
        dice_number=data.get("dice_number"),
        dice_type=data.get("dice_type"),
        bonus=data.get("bonus"),
        damage_type=data.get("damage_type"),
    )


def to_basic_attack_dto(data):
    if not data:
        return None

    dmg = data.get("damage")
    dmg_dto = None
    if dmg:
        dmg_dto = to_damage_dto(data.get("damage"))

    return BasicAttackDTO(
        name=data.get("name"),
        range=data.get("range"),
        damage=dmg_dto,
    )


def to_experience_dtos(data_list):
    data_in = data_list or []
    return [ExperienceDTO(name=data["name"], bonus=data.get("bonus"))
            for data in data_in]


def to_feature_dtos(data_list):
    data_in = data_list or []
    return [FeatureDTO(name=data["name"],
                       type=data.get("type"),
                       description=data.get("description")
                       )
            for data in data_in]


def to_tactic_dtos(data_list):
    data_in = data_list or []
    return [TacticDTO(name=data) for data in data_in]


def to_tag_dtos(data_list):
    data_in = data_list or []
    return [TagDTO(name=data) for data in data_in]


def to_adversary_dto(validated_data):
    return AdversaryDTO(
        name=validated_data["name"],
        tier=validated_data.get("tier"),
        type=validated_data.get("type"),
        description=validated_data.get("description"),
        difficulty=validated_data.get("difficulty"),
        threshold_major=validated_data.get("threshold_major"),
        threshold_severe=validated_data.get("threshold_severe"),
        hit_point=validated_data.get("hit_point"),
        horde_hit_point=validated_data.get("horde_hit_point"),
        stress_point=validated_data.get("stress_point"),
        atk_bonus=validated_data.get("atk_bonus"),
        source=validated_data.get("source"),
        status=validated_data.get("status"),
        basic_attack=to_basic_attack_dto(validated_data.get("basic_attack")),
        tactics=to_tactic_dtos(validated_data.get("tactics")),
        tags=to_tag_dtos(validated_data.get("tags")),
        experiences=to_experience_dtos(validated_data.get("experiences")),
        features=to_feature_dtos(validated_data.get("features")),
    )


def to_adversary_patch_dto(validated_data):
    """TODO refactoring"""
    if present(validated_data, "basic_attack"):
        ba = to_basic_attack_dto(validated_data.get("basic_attack"))
    else:
        ba = get_or_unset(validated_data, "basic_attack")

    if present(validated_data, "tactics"):
        tactics = to_tactic_dtos(validated_data.get("tactics"))
    else:
        tactics = get_or_unset(validated_data, "tactics")

    if present(validated_data, "tags"):
        tags = to_tag_dtos(validated_data.get("tags"))
    else:
        tags = get_or_unset(validated_data, "tags")

    if present(validated_data, "experiences"):
        experiences = to_experience_dtos(validated_data.get("experiences"))
    else:
        experiences = get_or_unset(validated_data, "experiences")

    if present(validated_data, "features"):
        features = to_feature_dtos(validated_data.get("features"))
    else:
        features = get_or_unset(validated_data, "features")

    return AdversaryPatchDTO(
        name=get_or_unset(validated_data, "name"),
        tier=get_or_unset(validated_data, "tier"),
        type=get_or_unset(validated_data, "type"),
        description=get_or_unset(validated_data, "description"),
        difficulty=get_or_unset(validated_data, "difficulty"),
        threshold_major=get_or_unset(validated_data, "threshold_major"),
        threshold_severe=get_or_unset(validated_data, "threshold_severe"),
        hit_point=get_or_unset(validated_data, "hit_point"),
        horde_hit_point=get_or_unset(validated_data, "horde_hit_point"),
        stress_point=get_or_unset(validated_data, "stress_point"),
        atk_bonus=get_or_unset(validated_data, "atk_bonus"),
        source=get_or_unset(validated_data, "source"),
        status=get_or_unset(validated_data, "status"),
        basic_attack=ba,
        tactics=tactics,
        tags=tags,
        experiences=experiences,
        features=features
    )
