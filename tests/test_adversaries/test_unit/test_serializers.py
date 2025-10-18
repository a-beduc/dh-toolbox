from rest_framework.exceptions import ErrorDetail

from adversaries.models import DamageType, BasicAttack, Feature
from api.v1.adversaries.serializers import DamageInSerializer, \
    BasicAttackInSerializer, ExperienceInSerializer, FeatureInSerializer, \
    AdversaryInSerializer


# --- INPUT SERIALIZER TESTS : DamageInSerializer --- #
def test_damage_in_serializer_accepts_all_none():
    s = DamageInSerializer(data={
        "dice_number": None,
        "dice_type": None,
        "bonus": None,
        "damage_type": None,
    })
    assert s.is_valid(), s.errors
    assert s.validated_data["dice_number"] is None
    assert s.validated_data["damage_type"] is None


def test_damage_in_serializer_valid_type():
    for damage_type in [c[0] for c in DamageType.choices]:
        s = DamageInSerializer(data={"damage_type": damage_type})
        assert s.is_valid()
        assert s.validated_data["damage_type"] == damage_type


def test_damage_in_serializer_invalid_type():
    s = DamageInSerializer(data={"damage_type": "BAD"})
    assert not s.is_valid()
    assert s.errors["damage_type"] == [
        ErrorDetail(string="Invalid value 'BAD'. Try one of "
                           "['PHY', 'PHYSICAL', "
                           "'MAG', 'MAGICAL', "
                           "'BTH', 'BOTH', 'PHY/MAG'].",
                    code='invalid')
    ]


# --- INPUT SERIALIZER TESTS : BasicAttackInSerializer --- #
def test_basic_attack_in_serializer_minimal_requires_name():
    s = BasicAttackInSerializer(data={"name": "Slash"})
    assert s.is_valid()
    vd = s.validated_data
    assert vd["name"] == "Slash"
    assert "range" not in vd.keys()
    assert "damage" not in vd.keys()


def test_basic_attack_in_serializer_allows_null_range_and_damage():
    s = BasicAttackInSerializer(data={
        "name": "Slash",
        "range": None,
        "damage": None,
    })
    assert s.is_valid()
    vd = s.validated_data
    assert vd["name"] == "Slash"
    assert vd["range"] is None
    assert vd["damage"] is None


def test_basic_attack_in_serializer_valid_range():
    for range_ba in [c[0] for c in BasicAttack.Range.choices]:
        s = BasicAttackInSerializer(data={"name": "Hit", "range": range_ba})
        assert s.is_valid()
        assert s.validated_data["range"] == range_ba


def test_basic_attack_in_serializer_invalid_range():
    s = BasicAttackInSerializer(data={"name": "Hit", "range": "UNKNOWN"})
    assert not s.is_valid()
    assert s.errors['range'] == [
        ErrorDetail(string="Invalid value 'UNKNOWN'. Try one of "
                           "['MEL', 'MELEE', "
                           "'CLO', 'CLOSE', "
                           "'FAR', "
                           "'VCL', 'VERY_CLOSE', 'V_CLOSE', 'VCLOSE', "
                           "'VFA', 'VERY_FAR', 'V_FAR', 'VFAR'].",
                    code='invalid')
    ]


# --- INPUT SERIALIZER TESTS : ExperienceInSerializer --- #
def test_experience_in_serializer_minimal():
    s = ExperienceInSerializer(data={"name": "Resolve"})
    assert s.is_valid()
    vd = s.validated_data
    assert vd["name"] == "Resolve"


# --- INPUT SERIALIZER TESTS : FeatureInSerializer --- #
def test_feature_in_serializer_minimal():
    s = FeatureInSerializer(data={"name": "Scorched Earth"})
    assert s.is_valid()
    vd = s.validated_data
    assert "type" not in vd
    assert "description" not in vd


def test_feature_in_serializer_valid_type():
    for type_f in [c[0] for c in Feature.Type.choices]:
        s = FeatureInSerializer(data={"name": "Scorched Earth",
                                      "type": type_f})
        assert s.is_valid()
        assert s.validated_data["type"] == type_f


def test_feature_in_serializer_invalid_type():
    s = FeatureInSerializer(data={"name": "Invalid", "type": "Invalid"})
    assert not s.is_valid()
    assert s.errors["type"] == [
        ErrorDetail(string="Invalid value 'Invalid'. Try one of "
                           "['PAS', 'PASSIVE', "
                           "'ACT', 'ACTION', "
                           "'REA', 'REACTION'].",
                    code='invalid')
    ]


# --- INPUT SERIALIZER TESTS : AdversaryInSerializer --- #
def test_adversary_in_serializer_minimal():
    s = AdversaryInSerializer(data={"name": "Acid Burrower"})
    assert s.is_valid()
    vd = s.validated_data
    assert vd["name"] == "Acid Burrower"
    assert vd["tactics"] == []
    assert vd["tags"] == []
    assert vd["experiences"] == []
    assert vd["features"] == []


def test_adversary_in_serializer_complete():
    payload = {
        "name": "Acid Burrower",
        "tier": "1",
        "type": "SOL",
        "description": "A horse-sized insect with digging claws and acidic "
                       "blood.",
        "difficulty": "14",
        "threshold_major": "8",
        "threshold_severe": 15,
        "hit_point": "8",
        "horde_hit_point": None,
        "stress_point": 3,
        "atk_bonus": "+3",
        "source": "Darrington Press",
        "status": "DRAFT",
        "basic_attack": {
            "name": "Claws",
            "range": "Very Close",
            "damage": {
                "dice_number": "1",
                "dice_type": "12",
                "bonus": "2",
                "damage_type": "physical"
            }
        },
        "tactics": [
            "Burrow",
            "drag away",
            "feed",
            "reposition"
        ],
        "tags": [
            "underworld",
            "cavern",
            "desert"
        ],
        "experiences": [
            {
                "name": "Tremorsense",
                "bonus": "-2"
            },
            {
                "name": "Second Exp",
                "bonus": "+2"
            }
        ],
        "features": [
            {
                "name": "Relentless (3)",
                "type": "Passive",
                "description": "The Burrower can be spotlighted up to three "
                               "times per GM turn. Spend Fear as usual to "
                               "spotlight them."
            },
            {
                "name": "Earth Eruption",
                "type": "Action",
                "description": "Mark a Stress to have the Burrower burst out "
                               "of the ground. All creatures within Very "
                               "Close range must succeed on an Agility "
                               "Reaction Roll or be knocked over, making them "
                               "Vulnerable until they next act."
            }
        ]
    }
    s = AdversaryInSerializer(data=payload)
    assert s.is_valid(), s.errors
    vd = s.validated_data

    assert vd["name"] == "Acid Burrower"
    assert vd["tier"] == 1
    assert vd["type"] == "SOL"
    assert vd["description"].startswith("A horse-sized insect")
    assert vd["difficulty"] == 14
    assert vd["threshold_major"] == 8
    assert vd["threshold_severe"] == 15
    assert vd["hit_point"] == 8
    assert vd["horde_hit_point"] is None
    assert vd["stress_point"] == 3
    assert vd["atk_bonus"] == 3
    assert vd["source"] == "Darrington Press"
    assert vd["status"] == "DRA"

    ba = vd["basic_attack"]
    assert ba["name"] == "Claws"
    assert ba["range"] == "VCL"

    assert vd["tactics"] == ["Burrow", "drag away", "feed", "reposition"]
    assert vd["tags"] == ["underworld", "cavern", "desert"]

    exps = vd["experiences"]
    assert [e["name"] for e in exps] == ["Tremorsense", "Second Exp"]
    assert [e["bonus"] for e in exps] == [-2, 2]

    feats = vd["features"]
    assert [f["name"] for f in feats] == ["Relentless (3)", "Earth Eruption"]
    assert [f["type"] for f in feats] == ["PAS", "ACT"]
    assert all(isinstance(f.get("description"), str) for f in feats)


def test_adversary_in_serializer_unknown_field_is_ignored():
    s = AdversaryInSerializer(data={"name": "Goblin", "unknown": 1})
    assert s.is_valid()


def test_adversary_in_serializer_invalid_type():
    s = AdversaryInSerializer(data={"name": "Goblin", "type": "BAD TYPE"})
    assert not s.is_valid()
    assert "type" in s.errors.keys()


def test_adversary_in_serializer_invalid_tier():
    s = AdversaryInSerializer(data={"name": "Goblin", "tier": 5})
    assert not s.is_valid()
    assert "tier" in s.errors.keys()


def test_adversary_in_serializer_invalid_status():
    s = AdversaryInSerializer(data={"name": "Goblin", "status": "BAD STATUS"})
    assert not s.is_valid()
    assert "status" in s.errors.keys()
