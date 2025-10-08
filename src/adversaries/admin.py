from django.contrib import admin

from adversaries.models import Adversary, BasicAttack, DamageProfile, \
    Experience, Feature, Tactic


@admin.register(Adversary)
class AdversaryAdmin(admin.ModelAdmin):
    pass


@admin.register(BasicAttack)
class BasicAttack(admin.ModelAdmin):
    pass


@admin.register(DamageProfile)
class DamageProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    pass


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    pass


@admin.register(Tactic)
class TacticAdmin(admin.ModelAdmin):
    pass
