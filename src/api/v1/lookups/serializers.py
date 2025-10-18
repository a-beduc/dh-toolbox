from rest_framework.serializers import ModelSerializer

from adversaries.models import Experience, Tactic, Tag, Feature


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
