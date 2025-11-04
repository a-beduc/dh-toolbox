from django.urls import include, path

from web.accounts.views.auth import login_view, login_submit_view, \
    logout_view, register_view, register_submit_view

app_name = "accounts"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("login/submit/", login_submit_view, name="login-submit"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("register/submit/", register_submit_view, name="register-submit"),
]
