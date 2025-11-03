from django.urls import path
from web.core.views import home_view


urlpatterns = [
    path("", home_view, name="home"),
]
