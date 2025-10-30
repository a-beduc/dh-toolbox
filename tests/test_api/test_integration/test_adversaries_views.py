import pytest
from django.test import override_settings
from django.urls import resolve
from rest_framework.test import APIClient

from adversaries.models import Adversary
from adversaries.services import adversary_create
from api.v1.helpers.mappers import to_adversary_dto


# --- TEST ADVERSARY ENDPOINTS --- #
@override_settings(ROOT_URLCONF="api.v1.urls")
def test_adversary_detail_url_kwargs():
    match = resolve("/adversaries/13/")
    assert match.kwargs["adversary_id"] == 13


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_list_empty_returns_200_and_empty_array():
    client = APIClient()
    resp = client.get("/adversaries/")
    assert resp.status_code == 200
    assert resp.json() == []


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_detail_404_for_missing():
    client = APIClient()
    resp = client.get("/adversaries/999999/")
    assert resp.status_code == 404


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_list_and_detail_success_via_service_setup(
        big_adversary_payload, conf_account):
    # small validation (usually done before hitting service)
    big_adversary_payload["status"] = "DRA"
    big_adversary_payload["features"][0]["type"] = "PAS"
    big_adversary_payload["features"][1]["type"] = "ACT"

    dto = to_adversary_dto(big_adversary_payload)
    adv = adversary_create(dto, author_id=conf_account.id)

    client = APIClient()
    client.force_authenticate(user=conf_account)
    resp_list = client.get("/adversaries/")
    assert resp_list.status_code == 200
    assert resp_list.json()[0]["name"] == "Acid Burrower"

    resp_detail = client.get(f"/adversaries/{adv.id}/")
    assert resp_detail.status_code == 200
    assert resp_detail.json()["name"] == "Acid Burrower"


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_create_201_and_roundtrip_detail(
        conf_account, big_adversary_payload):
    client = APIClient()
    client.force_authenticate(user=conf_account)

    resp = client.post("/adversaries/", big_adversary_payload, format="json")
    assert resp.status_code == 201, resp.json()
    created = resp.json()
    adv_id = created["id"]

    detail = client.get(f"/adversaries/{adv_id}/")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Acid Burrower"


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_put(conf_account):
    client = APIClient()
    client.force_authenticate(user=conf_account)
    payload = {
        "name": "Fire dragon",
        "tier": "4",
        "type": "SOL"
    }

    resp = client.post("/adversaries/", payload, format="json")
    assert resp.status_code == 201, resp.json()
    assert resp.json()["name"] == "Fire dragon"
    assert resp.json()["tier"] == "4"
    assert resp.json()["type"] == Adversary.Type.SOLO
    created = resp.json()
    adv_id = created["id"]

    put_payload = {
        "name": "Frost dragon",
        "tier": "3",
        "difficulty": "14"
    }
    put_resp = client.put(f"/adversaries/{adv_id}/", put_payload,
                          format="json")
    assert put_resp.status_code == 200, put_resp.json()
    assert put_resp.json()["name"] == "Frost dragon"
    assert put_resp.json()["tier"] == "3"
    # Forgotten type in PUT body result in default value for Adversary.type
    assert put_resp.json().get("type") == Adversary.Type.UNSPECIFIED
    assert put_resp.json()["difficulty"] == 14


@override_settings(ROOT_URLCONF="api.v1.urls")
@pytest.mark.django_db
def test_adversary_patch(conf_account):
    client = APIClient()
    client.force_authenticate(user=conf_account)
    payload = {
        "name": "Fire dragon",
        "tier": "4",
        "type": "SOL"
    }

    resp = client.post("/adversaries/", payload, format="json")
    assert resp.status_code == 201, resp.json()
    assert resp.json()["name"] == "Fire dragon"
    assert resp.json()["tier"] == "4"
    assert resp.json()["type"] == Adversary.Type.SOLO
    created = resp.json()
    adv_id = created["id"]

    patch_payload = {
        "name": "Frost dragon",
        "tier": "3",
        "difficulty": "14"
    }
    patch_resp = client.patch(f"/adversaries/{adv_id}/", patch_payload,
                              format="json")
    assert patch_resp.status_code == 200, patch_resp.json()
    assert patch_resp.json()["name"] == "Frost dragon"
    assert patch_resp.json()["tier"] == "3"
    # Forgotten type in PATCH body didn't modify value
    assert patch_resp.json().get("type") == Adversary.Type.SOLO
    assert patch_resp.json()["difficulty"] == 14
