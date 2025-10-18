from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from adversaries.models import Experience
from adversaries.serializers.read import ExperienceOutSerializer


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
