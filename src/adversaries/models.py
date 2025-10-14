from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q

from accounts.models import Account


class Tactic(models.Model):
    name = models.CharField(max_length=100, unique=True)


class DamageType(models.TextChoices):
    PHYSICAL = "PHY", "Physical"
    MAGICAL = "MAG", "Magical"
    BOTH = "BTH", "Both"


class DamageProfile(models.Model):
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
                name="damage_profile_entity",
                fields=("dice_number", "dice_type", "bonus", "damage_type"),
            )
        ]


class BasicAttack(models.Model):
    class Range(models.TextChoices):
        MELEE = "MELEE", "melee"
        VERY_CLOSE = "VCLOSE", "very close"
        CLOSE = "CLOSE", "close"
        FAR = "FAR", "far"
        VERY_FAR = "VFAR", "very far"

    name = models.CharField(max_length=100)
    range = models.CharField(
        max_length=6,
        choices=Range.choices,
        default=Range.MELEE
    )
    damage = models.ForeignKey(
        to=DamageProfile,
        on_delete=models.PROTECT,
        related_name="basic_attack"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="basic_attack_entity",
                fields=("name", "range", "damage"),
            )
        ]


class Experience(models.Model):
    name = models.CharField(max_length=100)
    bonus = models.SmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name="experience_entity",
                fields=("name", "bonus"),
            )
        ]


class Feature(models.Model):
    class Type(models.TextChoices):
        PASSIVE = "PAS", "passive"
        ACTION = "ACT", "action"
        REACTION = "REA", "reaction"

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=Type.choices)
    description = models.TextField(blank=True, null=True)
    # finish later the decomposition of features


class AdversaryTag(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Adversary(models.Model):
    """Temporary notes, to avoid IntegrityError that may appear when
    creating an adversary using entities (exp, feature, basic_attack)
    that already exist, use 'get_or_create' or a try/except in the
    service layer to fetch existing entities before adding new rows."""
    class Type(models.TextChoices):
        BRUISER = "BRU", "bruiser"
        HORDE = "HOR", "horde"
        LEADER = "LEA", "leader"
        MINION = "MIN", "minion"
        RANGED = "RAN", "ranged"
        SKULK = "SKU", "skulk"
        SOCIAL = "SOC", "social"
        SOLO = "SOL", "solo"
        STANDARD = "STA", "standard"
        SUPPORT = "SUP", "support"

    class Tier(models.IntegerChoices):
        ONE = 1, "I"
        TWO = 2, "II"
        THREE = 3, "III"
        FOUR = 4, "IV"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "draft"
        PUBLISHED = "PUBLISHED", "published"

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
    description = models.TextField(blank=True, null=True)

    tactics = models.ManyToManyField(Tactic, blank=True)

    difficulty = models.PositiveSmallIntegerField(blank=True, null=True)
    threshold_major = models.PositiveSmallIntegerField(blank=True, null=True)
    threshold_severe = models.PositiveSmallIntegerField(blank=True, null=True)
    hit_point = models.PositiveSmallIntegerField(blank=True, null=True)
    horde_hit_point = models.PositiveSmallIntegerField(blank=True, null=True)
    stress_point = models.PositiveSmallIntegerField(blank=True, null=True)

    atk_bonus = models.SmallIntegerField(blank=True, null=True)
    basic_attack = models.ForeignKey(to=BasicAttack, on_delete=models.PROTECT,
                                     blank=True, null=True)
    experiences = models.ManyToManyField(Experience, blank=True)
    features = models.ManyToManyField(Feature, blank=True)

    # metadata
    author = models.ForeignKey(to=Account, on_delete=models.PROTECT)
    source = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=Status.choices,
                              default=Status.DRAFT, db_index=True)
    tags = models.ManyToManyField(AdversaryTag, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("author", "name"),
                name="unique_author_name",
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

    def publish(self):
        self.status = self.Status.PUBLISHED
        self.save(update_fields=["status", "updated_at"])

    def unpublish(self):
        self.status = self.Status.DRAFT
        self.save(update_fields=["status", "updated_at"])
        