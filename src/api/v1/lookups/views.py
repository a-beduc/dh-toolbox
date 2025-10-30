from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from adversaries.selectors import experience_list, experience_get, \
    tactic_list, tactic_get, tag_list, tag_get, feature_list, feature_get


class ExperienceCollectionApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request):
        experiences = experience_list()
        data = self.OutputSerializer(experiences, many=True).data
        return Response(data)


class ExperienceItemApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request, experience_id):
        experiences = experience_get(pk=experience_id)
        data = self.OutputSerializer(experiences).data
        return Response(data)


class FeatureCollectionApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        type = serializers.CharField()
        description = serializers.CharField()

    def get(self, request):
        features = feature_list()
        data = self.OutputSerializer(features, many=True).data
        return Response(data)


class FeatureItemApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()
        type = serializers.CharField()
        description = serializers.CharField()

    def get(self, request, feature_id):
        features = feature_get(pk=feature_id)
        data = self.OutputSerializer(features).data
        return Response(data)


class TacticCollectionApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request):
        tactics = tactic_list()
        data = self.OutputSerializer(tactics, many=True).data
        return Response(data)


class TacticItemApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request, tactic_id):
        tactic = tactic_get(pk=tactic_id)
        data = self.OutputSerializer(tactic).data
        return Response(data)


class TagCollectionApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request):
        tags = tag_list()
        data = self.OutputSerializer(tags, many=True).data
        return Response(data)


class TagItemApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        name = serializers.CharField()

    def get(self, request, tag_id):
        tag = tag_get(pk=tag_id)
        data = self.OutputSerializer(tag).data
        return Response(data)
