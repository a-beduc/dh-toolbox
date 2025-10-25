from json import loads

import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from adversaries.models import Adversary
from api.v1.adversaries.serializers import AdversaryWriteSerializer, \
    AdversaryReadSerializer


@pytest.mark.django_db
def test_adversary_write_serializer_minimal(
        conf_account):
    factory = APIRequestFactory()
    django_request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )
    django_request.user = conf_account

    s = AdversaryWriteSerializer(
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


def test_adversary_write_serializer_missing_request_context():
    factory = APIRequestFactory()
    django_request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )

    s = AdversaryWriteSerializer(
        data=loads(django_request.body),
        context={}
    )
    assert s.is_valid()

    with pytest.raises(ValidationError) as error:
        s.save()

    assert "Missing user" in str(error.value)


# noinspection PyTypeChecker
@pytest.mark.django_db
def test_adversary_write_serializer_invalid_user_object():
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

    s = AdversaryWriteSerializer(
        data={"name": "Goblin"},
        context={"request": request}
    )
    assert s.is_valid()

    with pytest.raises(ValidationError) as err:
        s.save()

    assert "Current user has no linked account." in str(err.value)


@pytest.mark.django_db
def test_adversary_write_serializer_output_matches_read_serializer_output(
        conf_account):
    factory = APIRequestFactory()
    django_request = factory.post(
        "/api/adversaries/",
        {"name": "Goblin"},
        content_type='application/json'
    )
    django_request.user = conf_account

    s = AdversaryWriteSerializer(
        data=loads(django_request.body),
        context={"request": django_request}
    )
    assert s.is_valid()
    obj = s.save()

    # serializer.data call .to_representation()
    post_response = s.data

    g = AdversaryReadSerializer(obj, context={"request": django_request})
    get_response = g.data

    assert post_response == get_response


@pytest.mark.django_db
def test_adversary_write_serializer_basic_attack_with_damage(conf_account):
    factory = APIRequestFactory()
    payload = {
        "name": "Wyvern",
        "basic_attack": {
            "name": "Claws",
            "range": "Very Close",
            "damage": {
                "dice_number": 1,
                "dice_type": 12,
                "bonus": 2,
                "damage_type": "physical",
            },
        },
    }
    django_request = factory.post(
        "/api/adversaries/",
        payload,
        content_type='application/json'
    )
    django_request.user = conf_account

    s = AdversaryWriteSerializer(
        data=loads(django_request.body),
        context={"request": django_request}
    )

    assert s.is_valid()
    obj = s.save()

    assert obj.author_id == conf_account.id
    assert obj.basic_attack is not None
    assert obj.basic_attack.name == "Claws"
    assert obj.basic_attack.range == "VCL"

    dmg = obj.basic_attack.damage
    assert (dmg.dice_number, dmg.dice_type, dmg.bonus) == (1, 12, 2)
    assert dmg.damage_type == "PHY"


@pytest.mark.django_db
def test_adversary_write_serializer_basic_attack_without_damage(conf_account):
    factory = APIRequestFactory()
    payload = {
        "name": "Wyvern",
        "basic_attack": {
            "name": "Claws",
            "range": "Very Close",
        },
    }
    django_request = factory.post(
        "/api/adversaries/",
        payload,
        content_type='application/json'
    )
    django_request.user = conf_account

    s = AdversaryWriteSerializer(
        data=loads(django_request.body),
        context={"request": django_request}
    )

    assert s.is_valid()
    obj = s.save()

    assert obj.author_id == conf_account.id
    assert obj.basic_attack is not None
    assert obj.basic_attack.name == "Claws"
    assert obj.basic_attack.range == "VCL"

    # whole parameter is returned as a null field
    assert obj.basic_attack.damage is None
