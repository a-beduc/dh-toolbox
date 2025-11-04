from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from accounts.models import Account


def create_account(username, password1, password2, email):
    if password1 != password2:
        raise ValidationError("password do not match")

    class_user = get_user_model()
    temp_user = class_user(username=username, email=email)

    validate_password(password1, user=temp_user)

    account = Account.objects.create_user(
        username=username,
        password=password1,
        email=email
    )
    return account
