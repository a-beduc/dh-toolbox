from rest_framework.viewsets import ReadOnlyModelViewSet

from adversaries.models import Experience, Tactic, Feature, Tag
from api.v1.lookups.serializers import ExperienceReadSerializer, \
    TacticReadSerializer, FeatureReadSerializer, TagReadSerializer


class ExperienceViewSet(ReadOnlyModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceReadSerializer


class TacticViewSet(ReadOnlyModelViewSet):
    queryset = Tactic.objects.all()
    serializer_class = TacticReadSerializer


class FeatureViewSet(ReadOnlyModelViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureReadSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagReadSerializer
