from django.urls import reverse


def test_home_view_renders_template(client):
    url = reverse("core:home")
    resp = client.get(url)
    assert resp.status_code == 200
    assert "core/home.html" in [t.name for t in resp.templates]
