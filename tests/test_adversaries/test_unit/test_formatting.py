from dataclasses import dataclass

import pytest

from adversaries.helpers.formatting import format_basic_attack, \
    format_csv_name, format_csv_experience


@dataclass
class DummyNameModel():
    name: str


@dataclass
class DummyAdvExpModel():
    experience: DummyNameModel
    bonus: int


@pytest.mark.parametrize(
    "name,rge,dn,dt,bonus,dtp,expected",
    [
        (None, "Close", 1, 6, 2, "PHY", None),
        ("Claws", "Very Close", 1, 12, 0, "MAG",
         "Claws: Very Close | 1d12 MAG"),
        ("Claws", "Very Close", 2, 6, None, "PHY",
         "Claws: Very Close | 2d6 PHY"),
        ("Bite", "Close", 1, 8, 3, "PHY", "Bite: Close | 1d8+3 PHY"),
        ("Tail", "Far", 2, 10, -4, "MAG", "Tail: Far | 2d10-4 MAG"),
        ("Smash", "Close", 0, 0, 7, "PHY", "Smash: Close | 7 PHY"),
        ("Slam", "Close", None, None, -3, "BTH", "Slam: Close | -3 BTH"),
        ("Poke", "Very Far", 0, 0, 0, "PHY", "Poke: Very Far |  PHY"),
    ],
)
def test_format_basic_attack(name, rge, dn, dt, bonus, dtp, expected):
    assert format_basic_attack(name, rge, dn, dt, bonus, dtp) == expected


def test_format_csv_name_joins_names():
    items = [
        DummyNameModel(name="Burrow"),
        DummyNameModel(name="Hide"),
        DummyNameModel(name="Run")
    ]
    assert format_csv_name(items) == "Burrow, Hide, Run"


def test_format_csv_name_empty_list():
    assert format_csv_name([]) is None


def test_format_csv_experience_joins():
    exps = [
        DummyAdvExpModel(experience=DummyNameModel("Drag"), bonus=0),
        DummyAdvExpModel(experience=DummyNameModel("Swimmer"), bonus=-5),
        DummyAdvExpModel(experience=DummyNameModel("Eat ice creams"), bonus=5)
    ]
    assert (format_csv_experience(exps) ==
            "Drag +0, Swimmer -5, Eat ice creams +5")


def test_format_csv_experience_empty_returns_none():
    assert format_csv_experience([]) is None
