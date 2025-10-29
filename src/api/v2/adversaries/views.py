from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from adversaries.selectors import adversary_get, adversary_list
from adversaries.services import adversary_create
from api.v2.adversaries.serializers_out import AdversaryDetailOut, \
    AdversaryListOut
from api.v2.adversaries.serializers_in import AdversaryCreateIn, \
    AdversaryPutIn, AdversaryPatchIn
from api.v2.helpers.mappers import to_adversary_dto


class AdversaryDetailApi(APIView):
    serializer = AdversaryDetailOut

    def get(self, request, adversary_id):
        adv = adversary_get(adversary_id)
        if adv is None:
            raise Http404
        data = self.serializer(adv, context={"request": request}).data
        return Response(data)


class AdversaryListApi(APIView):
    serializer = AdversaryListOut

    def get(self, request):
        adversaries = adversary_list()
        data = self.serializer(adversaries,
                               many=True,
                               context={'request': request}).data
        return Response(data)
