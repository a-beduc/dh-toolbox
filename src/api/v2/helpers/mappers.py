from adversaries.dtos.dto import DamageDTO, BasicAttackDTO, ExperienceDTO, \
    FeatureDTO, TacticDTO, TagDTO, AdversaryDTO


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


def to_adversary_dto(validated_data, *, author_id):
    return AdversaryDTO(
        author_id=author_id,
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
