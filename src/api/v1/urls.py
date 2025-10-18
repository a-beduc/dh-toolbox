from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.lookups.views import ExperienceViewSet

router = DefaultRouter()
router.register(r"lookups/experiences", ExperienceViewSet,
                basename="lookup-experiences")


urlpatterns = [
    path("", include(router.urls))
]
