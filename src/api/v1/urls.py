from django.urls import path

from api.v1.adversaries.views import AdversaryCollectionApi, AdversaryItemApi
from api.v1.lookups.views import ExperienceCollectionApi, ExperienceItemApi, \
    TacticCollectionApi, TacticItemApi, FeatureCollectionApi, FeatureItemApi, \
    TagCollectionApi, TagItemApi
from api.v1.root import RootApi

urlpatterns = [
    path("", RootApi.as_view(), name="api-root"),

    path('adversaries/<int:adversary_id>/', AdversaryItemApi.as_view(),
         name='adversaries-detail'),
    path('adversaries/', AdversaryCollectionApi.as_view(),
         name='adversaries-list'),

    path("lookups/experiences/", ExperienceCollectionApi.as_view(),
         name="experiences-list"),
    path("lookups/experiences/<int:experience_id>/", ExperienceItemApi.as_view(),
         name="experiences-detail"),

    path("lookups/features/", FeatureCollectionApi.as_view(),
         name="features-list"),
    path("lookups/features/<int:feature_id>/", FeatureItemApi.as_view(),
         name="features-detail"),

    path("lookups/tactics/", TacticCollectionApi.as_view(),
         name="tactics-list"),
    path("lookups/tactics/<int:tactic_id>/", TacticItemApi.as_view(),
         name="tactics-detail"),

    path("lookups/tags/", TagCollectionApi.as_view(),
         name="tags-list"),
    path("lookups/tags/<int:tag_id>/", TagItemApi.as_view(),
         name="tags-detail"),
]
