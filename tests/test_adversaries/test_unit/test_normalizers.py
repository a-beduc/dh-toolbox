import pytest
from rest_framework.exceptions import ValidationError

from adversaries.helpers.normalizers import _norm_key, normalize_choices


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("phy", "PHY"),
        ("  Physical  ", "PHYSICAL"),
        ("very-close", "VERY_CLOSE"),
        ("Very Close", "VERY_CLOSE"),
        ("v_fAr", "V_FAR"),
        ("", ""),
        (None, ""),
        (123, "123"),
    ],
)
def test__norm_key_basic(raw, expected):
    assert _norm_key(raw) == expected


# --- normalize_choices: ALLOW_NULL --- #
def test_normalize_choices_allows_null_when_flag_true():
    assert normalize_choices(None, "DMG_TYPE") is None


def test_normalize_choices_refuses_null_when_flag_false():
    with pytest.raises(ValidationError) as error:
        normalize_choices(None, "DMG_TYPE", allow_null=False)
    assert "cannot be empty" in str(error.value)


# --- normalize_choices: VALID MAPS --- #
@pytest.mark.parametrize(
    "value, expected",
    [
        ("phy", "PHY"),
        ("PHYSICAL", "PHY"),
        ("magical", "MAG"),
        ("BTH", "BTH"),
        ("phy/mag", "BTH"),
    ],
)
def test_normalize_choices_damage_type(value, expected):
    assert normalize_choices(value, "DMG_TYPE") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("melee", "MEL"),
        ("MEL", "MEL"),
        ("Close", "CLO"),
        ("far", "FAR"),
        ("Very Close", "VCL"),
        ("v_close", "VCL"),
        ("vclose", "VCL"),
        ("very-far", "VFA"),
        ("V_FAR", "VFA"),
        ("vfar", "VFA"),
    ],
)
def test_normalize_choices_basic_attack_range(value, expected):
    assert normalize_choices(value, "BA_RANGE") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("passive", "PAS"),
        ("PAS", "PAS"),
        ("action", "ACT"),
        ("REACTION", "REA"),
    ],
)
def test_normalize_choices_feature_type(value, expected):
    assert normalize_choices(value, "FEAT_TYPE") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("bruiser", "BRU"),
        ("RAN", "RAN"),
        ("support", "SUP"),
        ("Skulk", "SKU"),
        ("solo", "SOL"),
        ("STANDARD", "STA"),
    ],
)
def test_normalize_choices_adversary_type(value, expected):
    assert normalize_choices(value, "ADV_TYPE") == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        (1, 1),
        ("1", 1),
        ("one", 1),
        ("I", 1),
        (4, 4),
        ("FOUR", 4),
        ("IV", 4),
    ],
)
def test_normalize_choices_adversary_tier(value, expected):
    assert normalize_choices(value, "ADV_TIER") == expected
    assert isinstance(normalize_choices(value, "ADV_TIER"), int)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("draft", "DRA"),
        ("DRA", "DRA"),
        ("published", "PUB"),
        ("PUB", "PUB"),
    ],
)
def test_normalize_choices_adversary_status(value, expected):
    assert normalize_choices(value, "ADV_STATUS") == expected


# --- normalize_choices: INVALID MAPS --- #
@pytest.mark.parametrize(
    "table_name, bad_value",
    [
        ("DMG_TYPE", "LASER"),
        ("BA_RANGE", "POINT_BLANK"),
        ("FEAT_TYPE", "CHANNEL"),
        ("ADV_TYPE", "BOSS"),
        ("ADV_TIER", "FIVE"),
        ("ADV_STATUS", "ARCHIVED"),
    ],
)
def test_normalize_choices_invalid_value_raises(table_name, bad_value):
    with pytest.raises(ValidationError) as exc:
        normalize_choices(bad_value, table_name)
    msg = str(exc.value)
    assert "Invalid value" in msg


def test_normalize_choices_unknown_table_raises_key_error():
    with pytest.raises(KeyError):
        normalize_choices("anything", "NOT_A_TABLE")
