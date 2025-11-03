from django.urls import path, include


urlpatterns = [
    path("accounts/", include("web.accounts.urls"), name="accounts"),
    path("", include("web.core.urls")),
]
