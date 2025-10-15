from json import loads

import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from adversaries.models import Adversary
from adversaries.serializers import AdversaryInSerializer


@pytest.mark.django_db
def test_adversary_in_serializer_minimal(
        conf_account):
    factory = APIRequestFactory()
    django_request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )
    django_request.user = conf_account

    s = AdversaryInSerializer(
        data=loads(django_request.body),
        context={"request": django_request}
    )
    assert s.is_valid()

    # call the Serializer.create() (and other methods)
    adversary = s.save()
    assert adversary.author_id == conf_account.id

    # verify if adversary is in the DB
    saved_adversary = Adversary.objects.all()[0]
    assert saved_adversary.name == "Goblin"
    assert saved_adversary.author == conf_account


def test_adversary_in_serializer_missing_request_context():
    factory = APIRequestFactory()
    django_request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )

    s = AdversaryInSerializer(
        data=loads(django_request.body),
        context={}
    )
    assert s.is_valid()

    with pytest.raises(ValidationError) as error:
        s.save()

    assert "Missing user" in str(error.value)


# noinspection PyTypeChecker
@pytest.mark.django_db
def test_adversary_in_serializer_invalid_user_object():
    class FakeUser:
        """Dummy class"""
        pass

    factory = APIRequestFactory()
    request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )
    request.user = FakeUser()

    s = AdversaryInSerializer(
        data={"name": "Goblin"},
        context={"request": request}
    )
    assert s.is_valid()

    with pytest.raises(ValidationError) as err:
        s.save()

    assert "Current user has no linked account." in str(err.value)
