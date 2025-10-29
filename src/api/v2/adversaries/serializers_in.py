from rest_framework import serializers

from adversaries.helpers.normalizers import normalize_choices


class DamageIn(serializers.Serializer):
    dice_number = serializers.IntegerField(required=False, allow_null=True,
                                           min_value=0)
    dice_type = serializers.IntegerField(required=False, allow_null=True,
                                         min_value=0)
    bonus = serializers.IntegerField(required=False, allow_null=True)
    damage_type = serializers.CharField(required=False, allow_null=True)

    def validate_damage_type(self, value):
        return normalize_choices(value, "DMG_TYPE")


class BasicAttackIn(serializers.Serializer):
    name = serializers.CharField()
    range = serializers.CharField(required=False, allow_null=True)
    damage = DamageIn(required=False, allow_null=True)

    def validate_range(self, value):
        return normalize_choices(value, "BA_RANGE")


class FeatureIn(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)

    def validate_type(self, value):
        return normalize_choices(value, "FEAT_TYPE")


class ExperienceIn(serializers.Serializer):
    name = serializers.CharField()
    bonus = serializers.IntegerField(required=False, allow_null=True)


class AdversaryCreateIn(serializers.Serializer):
    name = serializers.CharField()

    tier = serializers.CharField(
        allow_null=True, required=False)
    type = serializers.CharField(
        allow_null=True, required=False)
    description = serializers.CharField(
        allow_null=True, required=False)

    difficulty = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    threshold_major = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    threshold_severe = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    hit_point = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    horde_hit_point = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    stress_point = serializers.IntegerField(
        allow_null=True, min_value=0, required=False)
    atk_bonus = serializers.IntegerField(
        allow_null=True, required=False)

    basic_attack = BasicAttackIn(allow_null=True, required=False)
    experiences = ExperienceIn(allow_null=True, required=False, many=True)
    tactics = serializers.ListField(
        child=serializers.CharField(), default=list, required=False)
    features = FeatureIn(allow_null=True, required=False, many=True)

    source = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField(allow_null=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(), default=list, required=False)

    def validate_type(self, value):
        return normalize_choices(value, "ADV_TYPE")

    def validate_tier(self, value):
        return normalize_choices(value, "ADV_TIER")

    def validate_status(self, value):
        return normalize_choices(value, "ADV_STATUS")


class AdversaryPutIn(AdversaryCreateIn):
    pass


class BasicAttackPatchIn(BasicAttackIn):
    # name can be omitted
    name = serializers.CharField(allow_null=True, required=False)


class AdversaryPatchIn(AdversaryCreateIn):
    # name and basic_attack.name can be omitted
    name = serializers.CharField(allow_null=True, required=False)

    basic_attack = BasicAttackPatchIn(allow_null=True, required=False)
