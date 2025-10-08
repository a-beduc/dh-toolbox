import pytest
from adversaries.models import Tactic


@pytest.mark.django_db
def test_tactic_create():
    Tactic.objects.bulk_create([
        Tactic(name="Ambush"),
        Tactic(name="Flank")
    ])

    assert Tactic.objects.filter(name="Ambush").exists()

    saved = Tactic.objects.get(name="Ambush")
    assert saved.pk is not None
    assert saved.name == "Ambush"
