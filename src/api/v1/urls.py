from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.v1.adversaries.views import AdversaryViewSet
from api.v1.lookups.views import ExperienceViewSet, TacticViewSet, \
    FeatureViewSet, TagViewSet


router = DefaultRouter()
router.register(r"lookups/experiences", ExperienceViewSet,
                basename="lookup-experiences")
router.register(r"lookups/tactics", TacticViewSet,
                basename="lookup-tactics")
router.register(r"lookups/features", FeatureViewSet,
                basename="lookup-features")
router.register(r"lookups/tags", TagViewSet,
                basename="lookup-tags")
router.register(r"adversaries", AdversaryViewSet,
                basename="adversaries")


urlpatterns = [
    path("", include(router.urls))
]
