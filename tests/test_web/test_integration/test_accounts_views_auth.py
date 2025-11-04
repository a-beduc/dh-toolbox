import pytest
from django.urls import reverse

from accounts.models import Account
from accounts.services import create_account


# --- login view --- #
def test_login_view_get_returns_form_template(client):
    url = reverse("accounts:login")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "accounts/login.html" in [t.name for t in resp.templates]
    assert "form" in resp.context_data


def test_login_submit_view_invalid_form_return_400(client):
    url = reverse("accounts:login-submit")
    resp = client.post(url, {"username": ""})
    assert resp.status_code == 400
    assert "accounts/login.html" in [t.name for t in resp.templates]


@pytest.mark.django_db
def test_login_submit_view_wrong_credential_return_401(client, fast_auth):
    url = reverse("accounts:login-submit")
    resp = client.post(url, {"username": "nobody", "password": "wrong"})
    assert resp.status_code == 401
    assert "accounts/login.html" in [t.name for t in resp.templates]


@pytest.mark.django_db
def test_login_submit_view_valid_redirects_home(client, fast_auth):
    create_account(
        username="test_user",
        password1="Password_01",
        password2="Password_01",
        email="dummymail@mail.co"
    )
    url = reverse("accounts:login-submit")
    resp = client.post(url, {"username": "test_user", "password": "Password_01"})
    assert resp.status_code == 302
    assert resp.url == reverse("core:home")


# --- logout view ---#
@pytest.mark.django_db
def test_logout_view_redirect_login(client, fast_auth):
    create_account(
        username="test_user",
        password1="Password_01",
        password2="Password_01",
        email="dummymail@mail.co"
    )
    client.login(username="test_user", password="Password_01")
    url = reverse("accounts:logout")
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.url == reverse("accounts:login")


@pytest.mark.django_db
def test_logout_view_not_logged_in_redirect_login(client, fast_auth):
    url = reverse("accounts:logout")
    resp = client.get(url)
    assert resp.status_code == 302
    assert resp.url == reverse("accounts:login")


# --- register view ---#
def test_register_view_get_returns_form_template(client):
    url = reverse("accounts:register")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "accounts/register.html" in [t.name for t in resp.templates]
    assert "form" in resp.context_data


def test_register_submit_view_invalid_form_return_400(client):
    url = reverse("accounts:register-submit")
    resp = client.post(url, {"username": ""})
    assert resp.status_code == 400
    assert "accounts/register.html" in [t.name for t in resp.templates]


@pytest.mark.django_db
def test_register_submit_valid_form_create_and_redirects(client):
    accounts = Account.objects.all()
    assert list(accounts) == []

    url = reverse("accounts:register-submit")
    data = {
        "username": "test_user",
        "password1": "Password_01",
        "password2": "Password_01",
        "email": "dummymail@mail.co"
    }
    resp = client.post(url, data)
    assert resp.status_code == 302
    assert resp.url == reverse("accounts:login")

    account = Account.objects.get(username="test_user")
    accounts = Account.objects.all()
    assert list(accounts) == [account]
