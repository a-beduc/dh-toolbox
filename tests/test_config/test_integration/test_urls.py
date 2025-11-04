import pytest
from django.urls import reverse, resolve, Resolver404

import api.v1.lookups.views
import web.accounts.views.auth
import web.core.views


def test_core_home_reverse_and_resolve():
    url = reverse("core:home")
    assert url == "/"

    match = resolve("/")
    assert match.func == web.core.views.home_view


@pytest.mark.parametrize(
    "namespace, path, func",
    [
        ("accounts:login", "/login/",
         web.accounts.views.auth.login_view),
        ("accounts:login-submit", "/login/submit/",
         web.accounts.views.auth.login_submit_view),
        ("accounts:logout", "/logout/",
         web.accounts.views.auth.logout_view),
        ("accounts:register", "/register/",
         web.accounts.views.auth.register_view),
        ("accounts:register-submit", "/register/submit/",
         web.accounts.views.auth.register_submit_view),
    ]
)
def test_accounts_routes_reverse_and_resolve(namespace, path, func):
    url = reverse(namespace)
    assert url == path

    match = resolve(path)
    assert match.func == func


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize(
    "name, list_route, detail_route, pk_kw, list_func, detail_func",
    [
        ("experiences", "experiences-list", "experiences-detail",
         "experience_id",
         api.v1.lookups.views.ExperienceCollectionApi,
         api.v1.lookups.views.ExperienceItemApi),
        ("features", "features-list", "features-detail",
         "feature_id",
         api.v1.lookups.views.FeatureCollectionApi,
         api.v1.lookups.views.FeatureItemApi),
        ("tactics", "tactics-list", "tactics-detail",
         "tactic_id",
         api.v1.lookups.views.TacticCollectionApi,
         api.v1.lookups.views.TacticItemApi),
        ("tags", "tags-list", "tags-detail",
         "tag_id",
         api.v1.lookups.views.TagCollectionApi,
         api.v1.lookups.views.TagItemApi),
    ]
)
def test_api_lookup_routes_reverse_and_resolve(name, list_route, detail_route,
                                               pk_kw, list_func, detail_func):
    """Class based view are transformed in a callable with .as_view().
    To access the class used in the callable need to access
    resolver_match.func.view_class.

    link to explanation :
    https://stackoverflow.com/questions/37631110/
    in-django-how-can-i-get-an-instance-of-the-class-based-view-that-a-
    uri-resolves

    https://stackoverflow.com/questions/31491028/
    django-generic-views-based-as-view-method

    look for as_view(), it stores class in property `view.view_class = cls`
    it returns a wrapper
    https://github.com/django/django/blob/main/django/views/generic/base.py
    """
    list_url = reverse(f"api:v1:{list_route}")
    assert list_url == f"/api/v1/lookups/{name}/"

    list_match = resolve(f"/api/v1/lookups/{name}/")
    # as_view() creates a callable with attributes cf Django source code
    assert callable(list_match.func)
    assert list_match.func.view_class == list_func

    detail_url = reverse(f"api:v1:{detail_route}", kwargs={pk_kw: 1})
    assert detail_url == f"/api/v1/lookups/{name}/1/"

    detail_match = resolve(f"/api/v1/lookups/{name}/1/")
    assert detail_match.func.view_class == detail_func

    # bad pk type
    with pytest.raises(Resolver404):
        resolve(f"/api/v1/lookups/{name}/not_an_int/")
