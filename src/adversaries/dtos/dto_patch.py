from dataclasses import dataclass, field
from typing import Optional, List

from adversaries.helpers.sentinel import UNSET


@dataclass(frozen=True, slots=True)
class TacticPatchDTO:
    name: str = UNSET


@dataclass(frozen=True, slots=True)
class DamagePatchDTO:
    dice_number: Optional[int] = UNSET
    dice_type: Optional[int] = UNSET
    bonus: Optional[int] = UNSET
    damage_type: Optional[str] = UNSET


@dataclass(frozen=True, slots=True)
class BasicAttackPatchDTO:
    name: str = UNSET
    range: Optional[str] = UNSET
    damage: Optional["DamagePatchDTO"] = UNSET


@dataclass(frozen=True, slots=True)
class ExperiencePatchDTO:
    name: str = UNSET
    bonus: Optional[int] = UNSET


@dataclass(frozen=True, slots=True)
class FeaturePatchDTO:
    name: str = UNSET
    type: Optional[str] = UNSET
    description: Optional[str] = UNSET


@dataclass(frozen=True, slots=True)
class TagPatchDTO:
    name: str = UNSET


@dataclass(frozen=True, slots=True)
class AdversaryPatchDTO:
    author_id: int = UNSET
    name: str = UNSET
    tier: Optional[int] = UNSET
    type: Optional[str] = UNSET
    description: Optional[str] = UNSET
    difficulty: Optional[int] = UNSET
    threshold_major: Optional[int] = UNSET
    threshold_severe: Optional[int] = UNSET
    hit_point: Optional[int] = UNSET
    horde_hit_point: Optional[int] = UNSET
    stress_point: Optional[int] = UNSET
    atk_bonus: Optional[int] = UNSET
    source: Optional[str] = UNSET
    status: Optional[str] = UNSET

    basic_attack: Optional["BasicAttackPatchDTO"] = UNSET
    tactics: List["TacticPatchDTO"] = field(default=UNSET)
    experiences: List["ExperiencePatchDTO"] = field(default=UNSET)
    features: List["FeaturePatchDTO"] = field(default=UNSET)
    tags: List["TagPatchDTO"] = field(default=UNSET)
