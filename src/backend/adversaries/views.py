from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class AdversaryViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]


