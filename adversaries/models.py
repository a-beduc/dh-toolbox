from django.db import models


class Tactic(models.Model):
    tactic = models.CharField(max_length=100)


class DamageType(models.TextChoices):
    PHYSICAL = "PHY", "Physical"
    MAGICAL = "MAG", "Magical"
    BOTH = "BOTH", "Both"


class Weapon(models.Model):
    class Range(models.TextChoices):
        MELEE = "MELEE", "melee"
        VERY_CLOSE = "VCLOSE", "very close"
        CLOSE = "CLOSE", "close"
        FAR = "FAR", "far"
        VERY_FAR = "VFAR", "very far"
        OUT_OF_RANGE = "OOR", "out of range"

    name = models.CharField(max_length=100)
    range = models.TextField(choices=Range.choices, default=Range.MELEE)
    dice_formula = models.CharField(max_length=30, blank=True, null=True)
    dice_bonus = models.IntegerField(blank=True, null=True)
    damage_type = models.CharField(choices=DamageType.choices, blank=True)


class Experience(models.Model):
    name = models.CharField(max_length=100)


class Feature(models.Model):
    class Type(models.TextChoices):
        PASSIVE = "PAS", "passive"
        ACTION = "ACT", "action"
        REACTION = "REA", "reaction"

    name = models.CharField(max_length=100)
    type = models.CharField(choices=Type.choices)
    description = models.TextField(blank=True, null=True)
    # finish later the decomposition of features


class Adversary(models.Model):
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

    name = models.CharField(max_length=100)
    tier = models.IntegerField(choices=Tier.choices, default=Tier.ONE)
    type = models.TextField(choices=Type.choices, default=Type.STANDARD,
                            blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tactic = models.ManyToManyField(Tactic, blank=True)
    difficulty = models.IntegerField(blank=True, null=True)
    threshold_major = models.IntegerField(blank=True, null=True)
    threshold_severe = models.IntegerField(blank=True, null=True)
    hit_point = models.IntegerField(blank=True, null=True)
    stress_point = models.IntegerField(blank=True, null=True)
    atk = models.IntegerField(blank=True, null=True)
    weapon = models.ForeignKey(to=Weapon, on_delete=models.CASCADE)
    experience = models.ManyToManyField(Experience, blank=True)
    feature = models.ManyToManyField(Feature, blank=True)
