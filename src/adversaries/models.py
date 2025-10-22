from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

from accounts.models import Account


class Tactic(models.Model):
    """Value object"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_tactic_value_object"
            )
        ]


class Tag(models.Model):
    """Value object"""
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_tag_value_object"
            )
        ]


class Experience(models.Model):
    """Value object
    source: https://stackoverflow.com/questions/59596176/when-we-should-use-db-index-true-in-django#59596256
    """
    name = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_experience_value_object"
            )
        ]


class DamageType(models.TextChoices):
    """Out of class because might be used by DamageProfile and Feature"""
    PHYSICAL = "PHY", "PHYSICAL"
    MAGICAL = "MAG", "MAGICAL"
    BOTH = "BTH", "BOTH"


class DamageProfile(models.Model):
    """Value object"""
    dice_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0)],
        default=0,
        help_text="0 dice means flat damage"
    )
    dice_type = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
    )
    bonus = models.SmallIntegerField(default=0)
    damage_type = models.CharField(
        max_length=3,
        choices=DamageType.choices,
        default=DamageType.PHYSICAL,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="dp_valid_shape",
                condition=(
                    (Q(dice_number=0) & Q(dice_type=0) & Q(bonus__gte=0)) |
                    (Q(dice_number__gte=1) & Q(dice_type__gte=2))
                ),
            ),
            models.UniqueConstraint(
                name="damage_profile_value_object",
                fields=("dice_number", "dice_type", "bonus", "damage_type"),
            )
        ]


class BasicAttack(models.Model):
    """Value object"""
    class Range(models.TextChoices):
        MELEE = "MEL", "MELEE"
        VERY_CLOSE = "VCL", "VERY CLOSE"
        CLOSE = "CLO", "CLOSE"
        FAR = "FAR", "FAR"
        VERY_FAR = "VFA", "VERY FAR"

    name = models.CharField(max_length=100)
    range = models.CharField(
        max_length=3,
        choices=Range.choices,
        default=Range.MELEE
    )
    damage = models.ForeignKey(
        to=DamageProfile,
        on_delete=models.PROTECT,
        related_name="basic_attack",
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="basic_attack_value_object",
                fields=("name", "range", "damage"),
            )
        ]


class Feature(models.Model):
    """Entity"""
    class Type(models.TextChoices):
        PASSIVE = "PAS", "PASSIVE"
        ACTION = "ACT", "ACTION"
        REACTION = "REA", "REACTION"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=Type.choices)
    description = models.TextField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("name", "type", "description"),
                name="feature_entity"
            )
        ]
    # finish later the decomposition of features


class Adversary(models.Model):
    """Entity / Aggregate

    Temporary notes, to avoid IntegrityError that may appear when
    creating an adversary using entities (exp, feature, basic_attack)
    that already exist, use 'get_or_create' or a try/except in the
    service layer to fetch existing entities before adding new rows."""
    class Type(models.TextChoices):
        BRUISER = "BRU", "BRUISER"
        HORDE = "HOR", "HORDE"
        LEADER = "LEA", "LEADER"
        MINION = "MIN", "MINION"
        RANGED = "RAN", "RANGED"
        SKULK = "SKU", "SKULK"
        SOCIAL = "SOC", "SOCIAL"
        SOLO = "SOL", "SOLO"
        STANDARD = "STA", "STANDARD"
        SUPPORT = "SUP", "SUPPORT"

    class Tier(models.IntegerChoices):
        ONE = 1, "I"
        TWO = 2, "II"
        THREE = 3, "III"
        FOUR = 4, "IV"

    class Status(models.TextChoices):
        DRAFT = "DRA", "DRAFT"
        PUBLISHED = "PUB", "PUBLISHED"

    name = models.CharField(max_length=120, blank=False)
    tier = models.PositiveSmallIntegerField(
        choices=Tier.choices,
        default=Tier.ONE
    )
    type = models.CharField(
        max_length=3,
        choices=Type.choices,
        default=Type.STANDARD
    )
    description = models.TextField(null=True)

    tactics = models.ManyToManyField(Tactic, null=True)

    difficulty = models.PositiveSmallIntegerField(null=True)
    threshold_major = models.PositiveSmallIntegerField(null=True)
    threshold_severe = models.PositiveSmallIntegerField(null=True)
    hit_point = models.PositiveSmallIntegerField(null=True)
    horde_hit_point = models.PositiveSmallIntegerField(null=True)
    stress_point = models.PositiveSmallIntegerField(null=True)

    atk_bonus = models.SmallIntegerField(null=True)
    basic_attack = models.ForeignKey(to=BasicAttack, on_delete=models.PROTECT,
                                     null=True)
    experiences = models.ManyToManyField(Experience,
                                         through="AdversaryExperience",
                                         related_name="adversaries")
    features = models.ManyToManyField(Feature)

    # metadata
    author = models.ForeignKey(to=Account, on_delete=models.PROTECT)
    source = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=3, choices=Status.choices,
                              default=Status.DRAFT, db_index=True)
    tags = models.ManyToManyField(Tag, null=True)

    class Meta:
        verbose_name_plural = 'Adversaries'
        constraints = [
            models.UniqueConstraint(
                fields=("author", "name"),
                name="adversary_entity",
            ),
            models.CheckConstraint(
                name="adversary_name_not_empty",
                condition=~Q(name="")
            )
        ]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["type", "tier"]),
            models.Index(fields=["status"])
        ]

    def add_experience(self, experience, bonus=0):
        AdversaryExperience.objects.create(
            adversary=self,
            experience=experience,
            bonus=bonus
        )


class AdversaryExperience(models.Model):
    """M2M relationship manager"""
    adversary = models.ForeignKey(Adversary, on_delete=models.CASCADE,
                                  related_name="adversary_experiences")
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE,
                                   related_name="adversary_experiences")
    bonus = models.SmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["adversary", "experience"],
                name="unique_adversary_experience"
            )
        ]
