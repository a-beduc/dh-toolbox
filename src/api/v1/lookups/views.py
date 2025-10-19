from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from adversaries.models import Experience, Tactic, Feature, Tag
from api.v1.lookups.serializers import ExperienceOutSerializer, \
    TacticOutSerializer, FeatureOutSerializer, TagOutSerializer


class ExperienceViewSet(GenericViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceOutSerializer

    def list(self, request, *args, **kwargs):
        names = (
            Experience.objects
            .values_list("name", flat=True)
            .order_by("name")
            .distinct()
        )
        return Response([{"name": n} for n in names])


class TacticViewSet(GenericViewSet):
    queryset = Tactic.objects.all()
    serializer_class = TacticOutSerializer

    def list(self, request, *args, **kwargs):
        names = (
            Tactic.objects
            .values_list("name", flat=True)
            .order_by("name")
        )
        return Response([{"name": n} for n in names])


class FeatureViewSet(GenericViewSet):
    queryset = Feature.objects.all()
    serializer_class = FeatureOutSerializer

    def list(self, request, *args, **kwargs):
        features = (
            Feature.objects
            .values("name", "type", "description")
            .order_by("name")
        )
        return Response(features)


class TagViewSet(GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagOutSerializer

    def list(self, request, *args, **kwargs):
        names = (
            Tag.objects
            .values_list("name", flat=True)
            .order_by("name")
        )
        return Response([{"name": n} for n in names])
