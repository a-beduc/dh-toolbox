from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField, SerializerMethodField
from rest_framework.relations import SlugRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer, IntegerField, \
    CharField

from accounts.models import Account
from adversaries.dto import DamageDTO, BasicAttackDTO, AdversaryDTO, \
    TacticDTO, AdversaryTagDTO, ExperienceDTO, FeatureDTO
from adversaries.helpers.formatting import format_basic_attack, \
    format_csv_name, format_csv_experience
from adversaries.helpers.normalizers import normalize_choices
from adversaries.models import Experience, Adversary, DamageProfile, \
    BasicAttack, AdversaryExperience, Feature
from adversaries.services import create_adversary


class DamageProfileReadNestedSerializer(ModelSerializer):
    class Meta:
        model = DamageProfile
        fields = ("dice_number", "dice_type", "bonus", "damage_type")


class BasicAttackReadNestedSerializer(ModelSerializer):
    damage = DamageProfileReadNestedSerializer()
    class Meta:
        model = BasicAttack
        fields = ("name", "range", "damage")


class AuthorReadNestedSerializer(ModelSerializer):
    class Meta:
        model = Account
        fields = ("id", "username")


class AdversaryExperienceReadSerializer(ModelSerializer):
    name = CharField(source="experience.name")

    class Meta:
        model = AdversaryExperience
        fields = ("name", "bonus")


class FeatureReadNestedSerializer(ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'name', 'type', 'description')


class AdversaryListSerializer(ModelSerializer):
    author = AuthorReadNestedSerializer()
    basic_attack = SerializerMethodField()
    tactics = SerializerMethodField()
    tags = SerializerMethodField()
    features = SerializerMethodField()
    experiences = SerializerMethodField()
    url = HyperlinkedIdentityField(
        view_name="adversaries-detail",
        lookup_field="pk"
    )

    def get_basic_attack(self, obj):
        if obj.basic_attack:
            return format_basic_attack(
                name=obj.basic_attack.name,
                rge=obj.basic_attack.range,
                dice_number=obj.basic_attack.damage.dice_number,
                dice_type=obj.basic_attack.damage.dice_type,
                bonus=obj.basic_attack.damage.bonus,
                damage_type=obj.basic_attack.damage.damage_type
            )
        return None

    def get_tactics(self, obj):
        if obj.tactics:
            return format_csv_name(obj.tactics.all())
        return None

    def get_tags(self, obj):
        if obj.tags:
            return format_csv_name(obj.tags.all())
        return None

    def get_experiences(self, obj):
        if obj.adversary_experiences:
            return format_csv_experience(obj.adversary_experiences.all())
        return None

    def get_features(self, obj):
        if obj.features:
            return format_csv_name(obj.features.all())
        return None

    class Meta:
        model = Adversary
        fields = (
            "id", "name", "tier", "type", "description", "difficulty",
            "threshold_major", "threshold_severe", "hit_point",
            "horde_hit_point", "stress_point", "atk_bonus", "basic_attack",
            "experiences", "tactics", "features",
            "author", "source", "status", "tags", "url"
        )


class AdversaryReadSerializer(ModelSerializer):
    author = AuthorReadNestedSerializer()
    basic_attack = BasicAttackReadNestedSerializer()

    tactics = SlugRelatedField(many=True, slug_field='name', read_only=True)
    tags = SlugRelatedField(many=True, slug_field='name', read_only=True)
    features = FeatureReadNestedSerializer(many=True, read_only=True)

    experiences = AdversaryExperienceReadSerializer(
        source="adversary_experiences", many=True, read_only=True)

    class Meta:
        model = Adversary
        fields = (
            "id", "name", "tier", "type", "description", "difficulty",
            "threshold_major", "threshold_severe", "hit_point",
            "horde_hit_point", "stress_point", "atk_bonus", "basic_attack",
            "experiences", "tactics", "features",
            "author", "source", "created_at", "updated_at", "status", "tags"
        )


# --- Serializers for input data --- #
class DamageWriteSerializer(Serializer):
    dice_number = IntegerField(required=False, allow_null=True, min_value=0)
    dice_type = IntegerField(required=False, allow_null=True, min_value=0)
    bonus = IntegerField(required=False, allow_null=True)
    damage_type = CharField(required=False, allow_null=True)

    def validate_damage_type(self, value):
        return normalize_choices(value, "DMG_TYPE")


class BasicAttackWriteSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
    range = CharField(required=False, allow_null=True)
    damage = DamageWriteSerializer(required=False, allow_null=True)

    def validate_range(self, value):
        return normalize_choices(value, "BA_RANGE")


class ExperienceWriteSerializer(Serializer):
    name = CharField()
    bonus = IntegerField(required=False, allow_null=True)


class FeatureWriteSerializer(Serializer):
    name = CharField()
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)

    def validate_type(self, value):
        return normalize_choices(value, "FEAT_TYPE")


class AdversaryWriteSerializer(Serializer):
    name = CharField()
    tier = CharField(required=False, allow_null=True)
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)
    difficulty = IntegerField(required=False, allow_null=True, min_value=0,
                              write_only=True)
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

    basic_attack = BasicAttackWriteSerializer(required=False, allow_null=True)

    tactics = ListField(child=CharField(), required=False, default=list, write_only=True)
    tags = ListField(child=CharField(), required=False, default=list, write_only=True)
    experiences = ExperienceWriteSerializer(many=True, required=False,
                                         default=list, write_only=True)
    features = FeatureWriteSerializer(many=True, required=False, default=list, write_only=True)

    def to_representation(self, instance):
        """Force a reserialization of instance after post/patch/put"""
        return AdversaryReadSerializer(instance, context=self.context).data

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
