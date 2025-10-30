from rest_framework import serializers

from adversaries.helpers.formatting import format_csv_name, \
    format_csv_experience, format_basic_attack


class AuthorOut(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class DamageOut(serializers.Serializer):
    dice_number = serializers.IntegerField()
    dice_type = serializers.IntegerField()
    bonus = serializers.IntegerField()
    damage_type = serializers.CharField()


class BasicAttackOut(serializers.Serializer):
    name = serializers.CharField()
    range = serializers.CharField()
    damage = serializers.SerializerMethodField()

    def get_damage(self, obj):
        dmg = getattr(obj, "damage", None)
        if dmg is None:
            return None
        return DamageOut(dmg).data


class FeatureOut(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField()


class ExperienceOut(serializers.Serializer):
    name = serializers.CharField(source="experience.name")
    bonus = serializers.IntegerField()


class AdversaryDetailOut(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    tier = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField()

    difficulty = serializers.IntegerField()
    threshold_major = serializers.IntegerField()
    threshold_severe = serializers.IntegerField()
    hit_point = serializers.IntegerField()
    horde_hit_point = serializers.IntegerField()
    stress_point = serializers.IntegerField()
    atk_bonus = serializers.IntegerField()

    basic_attack = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    tactics = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    author = serializers.SerializerMethodField()
    source = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    status = serializers.CharField()
    tags = serializers.SerializerMethodField()

    def get_author(self, obj):
        return self._serialize(AuthorOut, obj.author)

    def get_basic_attack(self, obj):
        ba = getattr(obj, "basic_attack", None)
        return self._serialize(BasicAttackOut, ba)

    def get_features(self, obj):
        return self._serialize_many(
            FeatureOut,
            obj.features.all()
        )

    def get_experiences(self, obj):
        return self._serialize_many(
            ExperienceOut,
            obj.adversary_experiences.all()
        )

    def get_tactics(self, obj):
        return [t.name for t in obj.tactics.all()]

    def get_tags(self, obj):
        return [t.name for t in obj.tags.all()]

    @staticmethod
    def _serialize(ser_cls, instance):
        if instance is None:
            return None
        return ser_cls(instance).data

    @staticmethod
    def _serialize_many(ser_cls, query_selector):
        if query_selector is None:
            return []
        return ser_cls(query_selector, many=True).data


class AdversaryListOut(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    tier = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField()

    difficulty = serializers.IntegerField()
    threshold_major = serializers.IntegerField()
    threshold_severe = serializers.IntegerField()
    hit_point = serializers.IntegerField()
    horde_hit_point = serializers.IntegerField()
    stress_point = serializers.IntegerField()
    atk_bonus = serializers.IntegerField()

    basic_attack = serializers.SerializerMethodField()
    experiences = serializers.SerializerMethodField()
    tactics = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    author = serializers.SerializerMethodField()
    source = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    status = serializers.CharField()
    tags = serializers.SerializerMethodField()

    url = serializers.HyperlinkedIdentityField(
        view_name="adversaries-detail",
        lookup_field="pk",
        lookup_url_kwarg="adversary_id"
    )

    def get_author(self, obj):
        if obj.author:
            return obj.author.username
        return None

    def get_basic_attack(self, obj):
        ba = obj.basic_attack
        dmg = getattr(ba, "damage", None) if ba else None
        if not ba or not dmg:
            return None
        return format_basic_attack(
            name=ba.name,
            rge=ba.range,
            dice_number=dmg.dice_number,
            dice_type=dmg.dice_type,
            bonus=dmg.bonus,
            damage_type=dmg.damage_type
        )

    def get_tactics(self, obj):
        items = list(obj.tactics.all())
        return format_csv_name(items) if items else None

    def get_tags(self, obj):
        items = list(obj.tags.all())
        return format_csv_name(items) if items else None

    def get_experiences(self, obj):
        if obj.adversary_experiences:
            return format_csv_experience(obj.adversary_experiences.all())
        return None

    def get_features(self, obj):
        if obj.features:
            return format_csv_name(obj.features.all())
        return None
