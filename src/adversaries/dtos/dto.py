from dataclasses import dataclass, field
from typing import Optional, List


@dataclass(frozen=True, slots=True)
class TacticDTO:
    name: str


@dataclass(frozen=True, slots=True)
class DamageDTO:
    dice_number: Optional[int] = None
    dice_type: Optional[int] = None
    bonus: Optional[int] = None
    damage_type: Optional[str] = None


@dataclass(frozen=True, slots=True)
class BasicAttackDTO:
    name: str
    range: Optional[str] = None
    damage: Optional["DamageDTO"] = None


@dataclass(frozen=True, slots=True)
class ExperienceDTO:
    name: str
    bonus: Optional[int] = None


@dataclass(frozen=True, slots=True)
class FeatureDTO:
    name: str
    type: Optional[str] = None
    description: Optional[str] = None


@dataclass(frozen=True, slots=True)
class TagDTO:
    name: str


@dataclass(frozen=True, slots=True)
class AdversaryDTO:
    author_id: int
    name: str
    tier: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    threshold_major: Optional[int] = None
    threshold_severe: Optional[int] = None
    hit_point: Optional[int] = None
    horde_hit_point: Optional[int] = None
    stress_point: Optional[int] = None
    atk_bonus: Optional[int] = None
    source: Optional[str] = None
    status: Optional[str] = None

    basic_attack: Optional["BasicAttackDTO"] = None
    tactics: List["TacticDTO"] = field(default_factory=list)
    experiences: List["ExperienceDTO"] = field(default_factory=list)
    features: List["FeatureDTO"] = field(default_factory=list)
    tags: List["TagDTO"] = field(default_factory=list)

