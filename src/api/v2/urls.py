from django.urls import path, include

from api.v2.adversaries.views import AdversaryDetailApi, AdversaryListApi


adversary_patterns = [
    path('<int:adversary_id>/', AdversaryDetailApi.as_view(), name='detail'),
    path('', AdversaryListApi.as_view(), name='list')
]

urlpatterns = [
    path('adversaries/', include((adversary_patterns, 'adversaries')))
]
