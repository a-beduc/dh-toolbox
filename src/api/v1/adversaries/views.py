from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from adversaries.selectors import adversary_get, adversary_list
from adversaries.services import adversary_create, adversary_update, \
    adversary_partial_update
from api.v1.adversaries.serializers_out import AdversaryDetailOut, \
    AdversaryListOut
from api.v1.adversaries.serializers_in import AdversaryCreateIn, \
    AdversaryPutIn, AdversaryPatchIn
from api.v1.helpers.mappers import to_adversary_dto, to_adversary_patch_dto


class AdversaryItemApi(APIView):
    @staticmethod
    def _get_adv(adversary_id):
        adv = adversary_get(adversary_id)
        if adv is None:
            raise Http404
        return adv

    def get(self, request, adversary_id):
        adv = self._get_adv(adversary_id)
        data = AdversaryDetailOut(adv, context={"request": request}).data
        return Response(data)

    def put(self, request, adversary_id):
        adv = self._get_adv(adversary_id)

        ser = AdversaryPutIn(data=request.data)
        ser.is_valid(raise_exception=True)

        dto = to_adversary_dto(ser.validated_data)
        adv = adversary_update(adv, dto)

        data = AdversaryDetailOut(adv, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, adversary_id):
        adv = self._get_adv(adversary_id)

        ser = AdversaryPatchIn(data=request.data)
        ser.is_valid(raise_exception=True)

        dto = to_adversary_patch_dto(ser.validated_data)
        adv = adversary_partial_update(adv, dto)

        data = AdversaryDetailOut(adv, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)


class AdversaryCollectionApi(APIView):
    def get(self, request):
        adversaries = adversary_list()
        data = AdversaryListOut(adversaries,
                                many=True,
                                context={'request': request}).data
        return Response(data)

    def post(self, request):
        ser = AdversaryCreateIn(data=request.data)
        ser.is_valid(raise_exception=True)

        dto = to_adversary_dto(ser.validated_data)
        adv = adversary_create(dto, author_id=request.user.id)

        data = AdversaryDetailOut(adv, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)
