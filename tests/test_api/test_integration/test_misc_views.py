import pytest

from django.test import override_settings
from django.urls import resolve
from rest_framework.test import APIClient

from adversaries.models import Experience, Tactic, Feature, Tag


# --- TEST ROOT ENDPOINT --- #
@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_api_root(client):
    res = client.get("/")

    assert res.status_code == 200

    # follow link
    adv_url = res.data["adversaries"]
    res2 = client.get(adv_url)
    assert res2.status_code == 200


# --- TEST LOOKUPS ENDPOINTS --- #
@override_settings(ROOT_URLCONF="api.v1.urls")
def test_experience_detail_url_kwargs():
    match = resolve("/lookups/experiences/13/")
    assert match.kwargs["experience_id"] == 13


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_experience_list_and_detail():
    exp1 = Experience.objects.create(name="Run fast")
    Experience.objects.create(name="Ambusher")

    client = APIClient()

    resp = client.get("/lookups/experiences/")
    assert resp.status_code == 200
    data = resp.json()
    assert {d["name"] for d in data} == {"Ambusher", "Run fast"}

    detail = client.get(f"/lookups/experiences/{exp1.pk}/")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Run fast"


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_tactic_list_and_detail():
    tac1 = Tactic.objects.create(name="Burrow")
    Tactic.objects.create(name="Flank")

    client = APIClient()

    resp = client.get("/lookups/tactics/")
    assert resp.status_code == 200
    assert {d["name"] for d in resp.json()} == {"Burrow", "Flank"}

    detail = client.get(f"/lookups/tactics/{tac1.pk}/")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Burrow"


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_feature_list_and_detail():
    expected = [
        {
            'id': 1,
            'name': 'Relentless',
            'type': 'PAS',
            'description': 'Can be spotlighted 3 times'
        },
        {
            'id': 2,
            'name': 'Wing Push',
            'type': 'ACT',
            'description': 'Knocks targets prone'
        },
    ]

    f1 = Feature.objects.create(
        name="Relentless",
        type="PAS",
        description="Can be spotlighted 3 times",
    )
    Feature.objects.create(
        name="Wing Push",
        type="ACT",
        description="Knocks targets prone",
    )

    client = APIClient()

    resp = client.get("/lookups/features/")
    assert resp.status_code == 200
    data = resp.json()
    assert data == expected

    detail = client.get(f"/lookups/features/{f1.pk}/")
    assert detail.status_code == 200
    d = detail.json()
    assert d == expected[0]


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_tag_list_and_detail():
    expected = [
        {
            "id": 1,
            "name": "Insect"
        },
        {
            "id": 2,
            "name": "Acid"
        }
    ]
    g1 = Tag.objects.create(name="Insect")
    Tag.objects.create(name="Acid")

    client = APIClient()

    resp = client.get("/lookups/tags/")
    assert resp.status_code == 200
    assert resp.json() == expected

    detail = client.get(f"/lookups/tags/{g1.pk}/")
    assert detail.status_code == 200
    assert detail.json() == expected[0]


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_empty_lists_return_200_and_empty_array():
    client = APIClient()
    for endpoint in (
            "/lookups/experiences/",
            "/lookups/tactics/",
            "/lookups/features/",
            "/lookups/tags/",
    ):
        resp = client.get(endpoint)
        assert resp.status_code == 200
        assert resp.json() == []
