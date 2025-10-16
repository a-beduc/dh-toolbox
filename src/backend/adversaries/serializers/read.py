from rest_framework.serializers import ModelSerializer, CharField

from accounts.models import Account
from adversaries.models import Experience, Tactic, Tag, Feature, Adversary, \
    DamageProfile, BasicAttack


# --- Stand Alone Resources (with endpoints) --- #
class ExperienceOutSerializer(ModelSerializer):
    class Meta:
        model = Experience
        fields = ("name",)


class TacticOutSerializer(ModelSerializer):
    class Meta:
        model = Tactic
        fields = ("name",)


class FeatureOutSerializer(ModelSerializer):
    class Meta:
        model = Feature
        fields = ('name', 'type', 'description')


class TagOutSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


# --- Nested Resources (No dedicated endpoints) --- #
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
    tactics = TacticOutSerializer(many=True)
    tags = TagOutSerializer(many=True)
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
