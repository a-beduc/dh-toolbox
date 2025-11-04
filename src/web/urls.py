from django.urls import path, include


urlpatterns = [
    path("", include("web.accounts.urls"), name="accounts"),
    path("", include("web.core.urls"), name="core"),
]
