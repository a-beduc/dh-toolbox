from rest_framework.serializers import ModelSerializer

from adversaries.models import Experience, Tactic, Tag, Feature


class ExperienceReadSerializer(ModelSerializer):
    class Meta:
        model = Experience
        fields = ("id", "name")


class TacticReadSerializer(ModelSerializer):
    class Meta:
        model = Tactic
        fields = ("id", "name")


class FeatureReadSerializer(ModelSerializer):
    class Meta:
        model = Feature
        fields = ('id', 'name', 'type', 'description')


class TagReadSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
