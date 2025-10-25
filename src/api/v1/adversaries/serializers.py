from rest_framework.exceptions import ValidationError
from rest_framework.fields import ListField, SerializerMethodField
from rest_framework.relations import SlugRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer, IntegerField, \
    CharField

from accounts.models import Account
from adversaries.dtos.dto import DamageDTO, BasicAttackDTO, AdversaryDTO, \
    TacticDTO, TagDTO, ExperienceDTO, FeatureDTO
from adversaries.dtos.dto_patch import DamagePatchDTO, BasicAttackPatchDTO, \
    ExperiencePatchDTO, FeaturePatchDTO, TacticPatchDTO, AdversaryPatchDTO, \
    TagPatchDTO
from adversaries.helpers.formatting import format_basic_attack, \
    format_csv_name, format_csv_experience
from adversaries.helpers.normalizers import normalize_choices
from adversaries.models import Adversary, DamageProfile, \
    BasicAttack, AdversaryExperience, Feature
from adversaries.services import create_adversary, put_adversary, \
    patch_adversary
from api.v1.helpers.sentinel import get_or_unset, present


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


# --- Serializers for writing data --- #
class DamageWriteSerializer(Serializer):
    dice_number = IntegerField(required=False, allow_null=True, min_value=0)
    dice_type = IntegerField(required=False, allow_null=True, min_value=0)
    bonus = IntegerField(required=False, allow_null=True)
    damage_type = CharField(required=False, allow_null=True)

    def validate_damage_type(self, value):
        return normalize_choices(value, "DMG_TYPE")

    @staticmethod
    def to_dto(data):
        return DamageDTO(**data)


class BasicAttackWriteSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
    range = CharField(required=False, allow_null=True)
    damage = DamageWriteSerializer(required=False, allow_null=True)

    def validate_range(self, value):
        return normalize_choices(value, "BA_RANGE")

    @staticmethod
    def to_dto(data):
        dmg = data.get("damage")
        dmg_dto = None
        if dmg:
            dmg_dto = DamageWriteSerializer.to_dto(dmg)
        return BasicAttackDTO(
            name=data["name"],
            range=data.get("range"),
            damage=dmg_dto
        )


class ExperienceWriteSerializer(Serializer):
    name = CharField()
    bonus = IntegerField(required=False, allow_null=True)

    @staticmethod
    def to_dto(data):
        return ExperienceDTO(name=data["name"], bonus=data.get("bonus"))


class FeatureWriteSerializer(Serializer):
    name = CharField()
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)

    def validate_type(self, value):
        return normalize_choices(value, "FEAT_TYPE")

    @staticmethod
    def to_dto(data):
        return FeatureDTO(
            name=data["name"],
            type=data.get("type"),
            description=data.get("description")
        )


class AdversaryWriteSerializer(Serializer):
    name = CharField()
    tier = CharField(allow_null=True, required=False)
    type = CharField(allow_null=True, required=False)
    description = CharField(allow_null=True, required=False)
    difficulty = IntegerField(allow_null=True, min_value=0,
                              write_only=True, required=False)
    threshold_major = IntegerField(allow_null=True,
                                   min_value=0, required=False)
    threshold_severe = IntegerField(allow_null=True,
                                    min_value=0, required=False)
    hit_point = IntegerField(allow_null=True, min_value=0, required=False)
    horde_hit_point = IntegerField(allow_null=True,
                                   min_value=0, required=False)
    stress_point = IntegerField(allow_null=True, min_value=0, required=False)
    atk_bonus = IntegerField(allow_null=True, required=False)
    source = CharField(allow_null=True, required=False)
    status = CharField(allow_null=True, required=False)

    basic_attack = BasicAttackWriteSerializer(allow_null=True, required=False)

    tactics = ListField(child=CharField(), default=list, write_only=True)
    tags = ListField(child=CharField(), default=list, write_only=True)
    experiences = ExperienceWriteSerializer(many=True, required=False,
                                            default=list, write_only=True)
    features = FeatureWriteSerializer(many=True, default=list, write_only=True)

    def to_representation(self, instance):
        """Force a reserialization of instance after post/patch/put"""
        return AdversaryReadSerializer(instance, context=self.context).data

    def validate_type(self, value):
        return normalize_choices(value, "ADV_TYPE")

    def validate_tier(self, value):
        return normalize_choices(value, "ADV_TIER")

    def validate_status(self, value):
        return normalize_choices(value, "ADV_STATUS")

    @staticmethod
    def _build_dto(validated, *, author_id=None):
        ba_dto = None
        if validated.get("basic_attack"):
            ba_dto = (BasicAttackWriteSerializer
                      .to_dto(validated["basic_attack"]))

        experiences = [
            ExperienceWriteSerializer.to_dto(e)
            for e in validated.get("experiences", [])
        ]

        features = [
            FeatureWriteSerializer.to_dto(f)
            for f in validated.get("features", [])
        ]

        tactics = [TacticDTO(name=s) for s in validated.get("tactics", [])]
        tags = [TagDTO(name=s) for s in validated.get("tags", [])]

        return AdversaryDTO(
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
            tactics=tactics,
            tags=tags,
            experiences=experiences,
            features=features,
        )

    def create(self, validated):
        request = self.context.get("request")
        if not request:
            raise ValidationError({"detail": "Missing user in request "
                                             "payload."})
        try:
            author_id = request.user.id
        except AttributeError:
            raise ValidationError({"detail": "Current user has no linked "
                                             "account."})

        dto = self._build_dto(validated, author_id=author_id)
        return create_adversary(dto)

    def update(self, instance, validated):
        dto = self._build_dto(validated)
        return put_adversary(instance, dto)


# --- Serializers for partial update --- #
class DamagePatchSerializer(Serializer):
    dice_number = IntegerField(required=False, allow_null=True, min_value=0)
    dice_type = IntegerField(required=False, allow_null=True, min_value=0)
    bonus = IntegerField(required=False, allow_null=True)
    damage_type = CharField(required=False, allow_null=True)

    def validate_damage_type(self, value):
        return normalize_choices(value, "DMG_TYPE")

    @staticmethod
    def to_dto(data):
        if data is None:
            return None

        return DamagePatchDTO(
            dice_number=get_or_unset(data, "dice_number"),
            dice_type=get_or_unset(data, "dice_type"),
            bonus=get_or_unset(data, "bonus"),
            damage_type=get_or_unset(data, "damage_type"),
        )


class BasicAttackPatchSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
    range = CharField(required=False, allow_null=True)
    damage = DamagePatchSerializer(required=False, allow_null=True)

    def validate_range(self, value):
        return normalize_choices(value, "BA_RANGE")

    @staticmethod
    def to_dto(data):
        if data is None:
            return None

        # return Value or Sentinel

        if present(data, "damage"):
            dmg = DamagePatchSerializer.to_dto(data["damage"])
        else:
            dmg = get_or_unset(data, "damage")

        return BasicAttackPatchDTO(
            name=get_or_unset(data, "name"),
            range=get_or_unset(data, "range"),
            damage=dmg,
        )


class ExperiencePatchSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
    bonus = IntegerField(required=False, allow_null=True)

    @staticmethod
    def to_dto(data):
        return ExperiencePatchDTO(
            name=get_or_unset(data, "name"),
            bonus=get_or_unset(data, "bonus")
        )


class FeaturePatchSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
    type = CharField(required=False, allow_null=True)
    description = CharField(required=False, allow_null=True)

    def validate_type(self, value):
        return normalize_choices(value, "FEAT_TYPE")

    @staticmethod
    def to_dto(data):
        return FeaturePatchDTO(
            name=get_or_unset(data, "name"),
            type=get_or_unset(data, "type"),
            description=get_or_unset(data, "description")
        )


class AdversaryPatchSerializer(Serializer):
    name = CharField(required=False, allow_null=True)
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

    basic_attack = BasicAttackPatchSerializer(required=False, allow_null=True)
    tactics = ListField(child=CharField(), allow_null=True, required=False)
    tags = ListField(child=CharField(), allow_null=True, required=False)
    experiences = ExperiencePatchSerializer(many=True, allow_null=True,
                                            required=False)
    features = FeaturePatchSerializer(many=True, allow_null=True,
                                      required=False)

    def to_representation(self, instance):
        """Force a reserialization of instance after post/patch/put"""
        return AdversaryReadSerializer(instance, context=self.context).data

    def validate_type(self, value):
        return normalize_choices(value, "ADV_TYPE")

    def validate_tier(self, value):
        return normalize_choices(value, "ADV_TIER")

    def validate_status(self, value):
        return normalize_choices(value, "ADV_STATUS")

    def update(self, instance, validated):
        if present(validated, "basic_attack"):
            ba = BasicAttackPatchSerializer.to_dto(validated["basic_attack"])
        else:
            ba = get_or_unset(validated, "basic_attack")

        if present(validated, "tactics"):
            tactics = [TacticPatchDTO(name=n)
                       for n in validated["tactics"]]
        else:
            tactics = get_or_unset(validated, "tactics")

        if present(validated, "tags"):
            tags = [TagPatchDTO(name=n)
                    for n in validated["tags"]]
        else:
            tags = get_or_unset(validated, "tags")

        if present(validated, "experiences"):
            experiences = [ExperiencePatchSerializer.to_dto(e)
                           for e in validated["experiences"]]
        else:
            experiences = get_or_unset(validated, "experiences")

        if present(validated, "features"):
            features = [FeaturePatchSerializer.to_dto(f)
                        for f in validated["features"]]
        else:
            features = get_or_unset(validated, "features")

        dto = AdversaryPatchDTO(
            name=get_or_unset(validated, "name"),
            tier=get_or_unset(validated, "tier"),
            type=get_or_unset(validated, "type"),
            description=get_or_unset(validated, "description"),
            difficulty=get_or_unset(validated, "difficulty"),
            threshold_major=get_or_unset(validated, "threshold_major"),
            threshold_severe=get_or_unset(validated, "threshold_severe"),
            hit_point=get_or_unset(validated, "hit_point"),
            horde_hit_point=get_or_unset(validated, "horde_hit_point"),
            stress_point=get_or_unset(validated, "stress_point"),
            atk_bonus=get_or_unset(validated, "atk_bonus"),
            source=get_or_unset(validated, "source"),
            status=get_or_unset(validated, "status"),
            basic_attack=ba,
            tactics=tactics,
            tags=tags,
            experiences=experiences,
            features=features
        )

        return patch_adversary(instance, dto)
