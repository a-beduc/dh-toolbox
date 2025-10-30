from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class RootApi(APIView):
    def get(self, request):
        return Response({
            "adversaries": reverse("adversaries-list", request=request),
            "experiences": reverse("experiences-list", request=request),
            "features": reverse("features-list", request=request),
            "tactics": reverse("tactics-list", request=request),
            "tags": reverse("tags-list", request=request),
        })
