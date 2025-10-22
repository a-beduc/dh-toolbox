import pytest
from django.db import IntegrityError, transaction

from adversaries.dto import TagDTO, TacticDTO, FeatureDTO, ExperienceDTO
from adversaries.models import Tag, Tactic, Feature, Experience, \
    AdversaryExperience
from adversaries.services import _sync_m2m_by_name, _sync_features, \
    _sync_experiences


# --- _sync_m2m_by_name --- #
@pytest.mark.django_db
def test_sync_m2m_by_name_tags_creates_and_links(conf_adv):
    dtos = [TagDTO(name="fire"), TagDTO(name="desert")]
    _sync_m2m_by_name(conf_adv.tags, Tag, dtos)

    assert Tag.objects.count() == 2
    assert (set(conf_adv.tags.values_list("name", flat=True)) ==
            {"fire", "desert"})
    list_tag = list(Tag.objects.all())
    assert list_tag[0].id, list_tag[0].name == (1, "fire")
    assert list_tag[1].id, list_tag[1].name == (2, "desert")


@pytest.mark.django_db
def test_sync_m2m_by_name_tags_does_not_replace_existing(conf_adv):
    dtos = [TagDTO(name="fire"), TagDTO(name="desert")]
    _sync_m2m_by_name(conf_adv.tags, Tag, dtos)
    _sync_m2m_by_name(conf_adv.tags, Tag, dtos)

    assert Tag.objects.count() == 2
    assert (set(conf_adv.tags.values_list("name", flat=True)) ==
            {"fire", "desert"})
    list_tag = list(Tag.objects.all())
    assert list_tag[0].id, list_tag[0].name == (1, "fire")
    assert list_tag[1].id, list_tag[1].name == (2, "desert")


@pytest.mark.django_db
def test_sync_m2m_by_name_tags_clears_empty(conf_adv):
    _sync_m2m_by_name(conf_adv.tags, Tag, [TagDTO(name="Temp")])
    assert conf_adv.tags.exists()

    _sync_m2m_by_name(conf_adv.tags, Tag, [])
    assert not conf_adv.tags.exists()


@pytest.mark.django_db
def test_sync_m2m_by_name_tags_conflicts_raises(conf_adv):
    Tag.objects.create(name="sneak")

    with pytest.raises(IntegrityError):
        _sync_m2m_by_name(conf_adv.tags, Tag, [TagDTO(name="SNEAK")])


@pytest.mark.django_db
def test_sync_m2m_by_name_tags_update_delete(conf_adv):
    dtos = [TagDTO(name="fire"), TagDTO(name="desert")]
    _sync_m2m_by_name(conf_adv.tags, Tag, dtos)

    assert Tag.objects.count() == 2
    assert (set(conf_adv.tags.values_list("name", flat=True)) ==
            {"fire", "desert"})
    list_tag = list(Tag.objects.all())
    assert list_tag[0].id, list_tag[0].name == (1, "fire")
    assert list_tag[1].id, list_tag[1].name == (2, "desert")

    dtos = [TagDTO(name="earth"), TagDTO(name="desert")]
    _sync_m2m_by_name(conf_adv.tags, Tag, dtos)

    # does not delete unused tag (for now).
    assert Tag.objects.count() == 3
    assert (set(conf_adv.tags.values_list("name", flat=True)) ==
            {"earth", "desert"})
    list_tag = list(Tag.objects.all())
    assert list_tag[0].id, list_tag[0].name == (2, "desert")
    assert list_tag[1].id, list_tag[1].name == (3, "earth")


@pytest.mark.django_db
def test_sync_m2m_by_name_tactics_works(conf_adv):
    assert Tactic.objects.count() == 0
    assert conf_adv.tactics.count() == 0

    dtos = [TacticDTO(name="Flank"), TacticDTO(name="Ambush")]
    _sync_m2m_by_name(conf_adv.tactics, Tactic, dtos)

    assert (set(conf_adv.tactics.values_list("name", flat=True)) ==
            {"Flank", "Ambush"})
    assert Tactic.objects.count() == 2
    assert conf_adv.tactics.count() == 2


# --- _sync_features --- #
@pytest.mark.django_db
def test_sync_features_creates_and_links(conf_adv):
    assert Feature.objects.count() == 0
    assert conf_adv.features.count() == 0

    dtos = [
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
        FeatureDTO(name="Spit Acid", type="ACT", description="Cone attack"),
    ]
    _sync_features(conf_adv.features, dtos)

    assert Feature.objects.count() == 2
    assert conf_adv.features.count() == 2

    feature_in_db = Feature.objects.values_list("name", "type", "description")
    expected_feature_in_db = {("Relentless", "PAS", "Act twice"),
                              ("Spit Acid", "ACT", "Cone attack")}
    assert set(feature_in_db) == expected_feature_in_db


@pytest.mark.django_db
def test_sync_features_does_not_replace_existing(conf_adv):
    assert Feature.objects.count() == 0
    assert conf_adv.features.count() == 0

    dtos = [
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
        FeatureDTO(name="Spit Acid", type="ACT", description="Cone attack"),
    ]

    _sync_features(conf_adv.features, dtos)
    assert Feature.objects.count() == 2
    assert conf_adv.features.count() == 2

    _sync_features(conf_adv.features, dtos)
    assert Feature.objects.count() == 2
    assert conf_adv.features.count() == 2

    list_features = list(Feature.objects.all())
    assert list_features[0].id, list_features[0].name == (1, "Relentless")
    assert list_features[1].id, list_features[1].name == (2, "Spit Acid")


@pytest.mark.django_db
def test_sync_features_duplicate_raises(conf_adv):
    dtos = [
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
    ]

    with pytest.raises(IntegrityError):
        # add savepoint for rollback (without can't do assert after error)
        with transaction.atomic():
            _sync_features(conf_adv.features, dtos)

    assert conf_adv.features.count() == 0
    assert Feature.objects.count() == 0


@pytest.mark.django_db
def test_sync_feature_only_desc_diff(conf_adv):
    assert conf_adv.features.count() == 0
    assert Feature.objects.count() == 0

    dtos = [
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
        FeatureDTO(name="Relentless", type="PAS", description="Act thrice"),
    ]
    _sync_features(conf_adv.features, dtos)

    assert conf_adv.features.count() == 2
    assert Feature.objects.count() == 2


@pytest.mark.django_db
def test_sync_feature_update_delete(conf_adv):
    assert Feature.objects.count() == 0
    assert conf_adv.features.count() == 0

    dtos = [
        FeatureDTO(name="Relentless", type="PAS", description="Act twice"),
        FeatureDTO(name="Spit Acid", type="ACT", description="Cone attack"),
    ]

    _sync_features(conf_adv.features, dtos)
    assert Feature.objects.count() == 2
    assert conf_adv.features.count() == 2

    dtos = [
        FeatureDTO(name="Updated", type="ACT", description="Whatever"),
        FeatureDTO(name="Spit Acid", type="ACT", description="Cone attack"),
    ]

    _sync_features(conf_adv.features, dtos)
    assert Feature.objects.count() == 3
    assert conf_adv.features.count() == 2

    list_features = list(Feature.objects.all())
    assert list_features[0].id, list_features[0].name == (1, "Relentless")
    assert list_features[1].id, list_features[1].name == (2, "Spit Acid")
    assert list_features[2].id, list_features[2].name == (3, "Updated")


# --- _sync_experiences --- #
@pytest.mark.django_db
def test_sync_experiences_creates_and_links(conf_adv):
    assert Experience.objects.count() == 0
    assert conf_adv.experiences.count() == 0

    dtos = [
        ExperienceDTO(name="Burrow", bonus=2),
        ExperienceDTO(name="Flank", bonus=3)
    ]
    _sync_experiences(conf_adv, dtos)

    assert Experience.objects.count() == 2
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 2
    assert conf_adv.experiences.count() == 2


@pytest.mark.django_db
def test_sync_experiences_updates_deletes(conf_adv):
    assert Experience.objects.count() == 0
    assert conf_adv.experiences.count() == 0

    dtos = [
        ExperienceDTO(name="Burrow", bonus=2),
        ExperienceDTO(name="Flank", bonus=3)
    ]
    _sync_experiences(conf_adv, dtos)

    assert Experience.objects.count() == 2
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 2
    assert conf_adv.experiences.count() == 2

    # update bonus, does not create new M2M rel but update existing
    dtos = [
        ExperienceDTO(name="Burrow", bonus=3),
        ExperienceDTO(name="Flank", bonus=3)
    ]
    _sync_experiences(conf_adv, dtos)
    assert Experience.objects.count() == 2
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 2
    assert conf_adv.experiences.count() == 2

    # update experience, create new M2M rel and remove link from Adversary
    dtos = [
        ExperienceDTO(name="Burrow", bonus=3),
        ExperienceDTO(name="Face", bonus=1)
    ]
    _sync_experiences(conf_adv, dtos)
    assert Experience.objects.count() == 3
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 2
    assert conf_adv.experiences.count() == 2

@pytest.mark.django_db
def test_sync_experiences_empty_list_clear_links_only(conf_adv):
    _sync_experiences(conf_adv, [ExperienceDTO(name="Burrow", bonus=1)])
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 1

    _sync_experiences(conf_adv, [])
    assert AdversaryExperience.objects.filter(adversary=conf_adv).count() == 0

    assert Experience.objects.filter(name="Burrow").exists()
