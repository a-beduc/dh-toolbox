from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer, IntegerField, \
    CharField

from accounts.models import Account
from adversaries.dto import DamageDTO, BasicAttackDTO, AdversaryDTO, \
    TacticDTO, AdversaryTagDTO, ExperienceDTO, FeatureDTO
from adversaries.helpers.normalizers import normalize_choices
from adversaries.models import Experience, Adversary, DamageProfile, \
    BasicAttack
from adversaries.services import create_adversary
from api.v1.lookups.serializers import FeatureOutSerializer


class ExperienceOutNestedSerializer(ModelSerializer):
    class Meta:
        model = Experience
        fields = ("name", "bonus")


class DamageProfileOutNestedSerializer(ModelSerializer):
    class Meta:
        model = DamageProfile
        fields = ("dice_number", "dice_type", "bonus", "damage_type")


class BasicAttackOutNestedSerializer(ModelSerializer):
    damage = DamageProfileOutNestedSerializer()
    class Meta:
        model = BasicAttack
        fields = ("name", "range", "damage")


class AuthorOutNestedSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "username")


class AdversaryOutSerializer(ModelSerializer):
    author = AuthorOutNestedSerializer()
    basic_attack = BasicAttackOutNestedSerializer()
    tactics = SlugRelatedField(many=True, slug_field='name')
    tags = SlugRelatedField(many=True, slug_field='name')
    experiences = ExperienceOutNestedSerializer(many=True)
    features = FeatureOutSerializer(many=True)

    class Meta:
        model = Adversary
        fields = (
            "id", "name", "tier", "type", "description", "difficulty",
            "threshold_major", "threshold_severe", "hit_point",
            "horde_hit_point", "stress_point", "atk_bonus",
            "tactics", "experiences", "features",
            "author", "source", "created_at", "updated_at", "status", "tags"
        )


# --- Serializers for input data --- #
class DamageInSerializer(Serializer):
    dice_number = IntegerField(required=False, allow_null=True, min_value=0)
    dice_type = IntegerField(required=False, allow_null=True, min_value=0)
    bonus = IntegerField(required=False, allow_null=True)
    damage_type = CharField(required=False, allow_null=True)

    def validate_damage_type(self, value):
        return normalize_choices(value, "DMG_TYPE")


class BasicAttackInSerializer(Serializer):
    name = CharField()
    range = CharField(required=False, allow_null=True)
    damage = DamageInSerializer(required=False, allow_null=True)

    def validate_range(self, value):
        return normalize_choices(value, "BA_RANGE")


class ExperienceInSerializer(Serializer):
    name = CharField()
    bonus = IntegerField(required=False, allow_null=True)


class FeatureInSerializer(Serializer):
    name = CharField()
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)

    def validate_type(self, value):
        return normalize_choices(value, "FEAT_TYPE")


class AdversaryInSerializer(Serializer):
    name = CharField()
    tier = CharField(required=False, allow_null=True)
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)
    difficulty = IntegerField(required=False, allow_null=True, min_value=0)
    threshold_major = IntegerField(required=False, allow_null=True,
                                   min_value=0)
    threshold_severe = IntegerField(required=False, allow_null=True,
                                    min_value=0)
    hit_point = IntegerField(required=False, allow_null=True, min_value=0)
    horde_hit_point = IntegerField(required=False, allow_null=True,
                                   min_value=0)
    stress_point = IntegerField(required=False, allow_null=True, min_value=0)
    atk_bonus = IntegerField(required=False, allow_null=True)
    source = CharField(required=False, allow_null=True)
    status = CharField(required=False, allow_null=True)

    basic_attack = BasicAttackInSerializer(required=False, allow_null=True)

    tactics = ListField(child=CharField(), required=False, default=list)
    tags = ListField(child=CharField(), required=False, default=list)
    experiences = ExperienceInSerializer(many=True, required=False,
                                         default=list)
    features = FeatureInSerializer(many=True, required=False, default=list)

    def validate_type(self, value):
        return normalize_choices(value, "ADV_TYPE")

    def validate_tier(self, value):
        return normalize_choices(value, "ADV_TIER")

    def validate_status(self, value):
        return normalize_choices(value, "ADV_STATUS")

    def create(self, validated):
        request = self.context.get("request")
        if not request:
            raise ValidationError({"detail": "Missing user in request payload."})
        try:
            author_id = request.user.id
        except AttributeError:
            raise ValidationError({"detail": "Current user has no linked "
                                             "account."})

        ba_dto = None
        if validated.get("basic_attack"):
            ba = validated["basic_attack"]
            dmg_dto = None
            if ba.get("damage"):
                d = ba["damage"]
                dmg_dto = DamageDTO(
                    dice_number=d.get("dice_number"),
                    dice_type=d.get("dice_type"),
                    bonus=d.get("bonus"),
                    damage_type=d.get("damage_type")
                )
            ba_dto = BasicAttackDTO(
                name=ba["name"],
                range=ba.get("range"),
                damage=dmg_dto
            )

        dto = AdversaryDTO(
            author_id=author_id,
            name=validated["name"],
            tier=validated.get("tier"),
            type=validated.get("type"),
            description=validated.get("description"),
            difficulty=validated.get("difficulty"),
            threshold_major=validated.get("threshold_major"),
            threshold_severe=validated.get("threshold_severe"),
            hit_point=validated.get("hit_point"),
            horde_hit_point=validated.get("horde_hit_point"),
            stress_point=validated.get("stress_point"),
            atk_bonus=validated.get("atk_bonus"),
            source=validated.get("source"),
            status=validated.get("status"),
            basic_attack=ba_dto,
            tactics=[TacticDTO(name=s) for s in validated.get("tactics", [])],
            tags=[AdversaryTagDTO(name=s) for s in validated.get("tags", [])],
            experiences=[ExperienceDTO(**e) for e in
                         validated.get("experiences", [])],
            features=[FeatureDTO(**f) for f in validated.get("features", [])],
        )

        return create_adversary(dto)
