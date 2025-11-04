import pytest
from django.core.exceptions import ValidationError

from accounts.services import create_account


@pytest.mark.django_db
def test_create_account_ok():
    username = "username_01"
    password1 = "Password_01"
    password2 = "Password_01"
    email = "valid@mail.com"

    account = create_account(username, password1, password2, email)

    assert account.id == 1
    assert account.username == "username_01"
    assert account.email == "valid@mail.com"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "label, password",
    [
        ("short", "a"),
        ("common", "chocolate"),
        ("numeric", "147369258"),
        ("similar_username", "username_01"),
        ("similar_mail", "valid@mail.com"),
    ]
)
def test_create_account_password_weak(label, password):
    username = "username_01"
    email = "valid@mail.com"

    with pytest.raises(ValidationError):
        create_account(username, password, password, email)


def test_create_account_password_mismatch():
    username = "username_01"
    password1 = "Password01"
    password2 = "Password02"
    email = "valid@mail.com"
    with pytest.raises(ValidationError, match="password do not match"):
        create_account(username, password1, password2, email)
