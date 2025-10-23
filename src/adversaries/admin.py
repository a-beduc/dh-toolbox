from django.contrib import admin

from adversaries.models import Adversary, BasicAttack, DamageProfile, \
    Experience, Feature, Tactic, AdversaryExperience, Tag


class AdversaryExperienceInline(admin.TabularInline):
    """
    https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
    #working-with-many-to-many-intermediary-models
    """
    model = AdversaryExperience
    extra = 1


@admin.register(Adversary)
class AdversaryAdmin(admin.ModelAdmin):
    inlines = [AdversaryExperienceInline]


@admin.register(BasicAttack)
class BasicAttackAdmin(admin.ModelAdmin):
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


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
