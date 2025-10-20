from rest_framework.viewsets import ModelViewSet

from adversaries.models import Adversary
from api.v1.adversaries.serializers import AdversaryReadSerializer, \
    AdversaryWriteSerializer, AdversaryListSerializer


class AdversaryViewSet(ModelViewSet):
    queryset = Adversary.objects.all()
    serializer_class = AdversaryWriteSerializer

    action_serializer_classes = {
        "create": AdversaryWriteSerializer,
        "update": AdversaryWriteSerializer,
        "retrieve": AdversaryReadSerializer,
        "list": AdversaryListSerializer,
        "partial_update": AdversaryWriteSerializer,
    }

    def get_serializer_class(self):
        try:
            return self.action_serializer_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()

    def get_queryset(self):
        return (
            Adversary.objects
            .select_related("author", "basic_attack__damage")
            .prefetch_related("tactics", "tags", "features",
                              "adversary_experiences__experience")
        )
