import pytest


@pytest.fixture
def big_adversary_payload():
    return {
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
