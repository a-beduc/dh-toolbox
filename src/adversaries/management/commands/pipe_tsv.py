from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from adversaries.models import Tactic, DamageProfile, BasicAttack, \
    Experience, Feature, Adversary, DamageType


def import_script_from_path(scriptpath):
    spec = spec_from_file_location("script_parser", scriptpath)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Command(BaseCommand):
    help = "Transform tsv input into db entries"
    default_scriptpath = (settings.BASE_DIR / "adversaries" / "scripts" /
                          "tsv_parser.py")

    RANGE_MAP = {
        "close": BasicAttack.Range.CLOSE,
        "far": BasicAttack.Range.FAR,
        "melee": BasicAttack.Range.MELEE,
        "very close": BasicAttack.Range.VERY_CLOSE,
        "very far": BasicAttack.Range.VERY_FAR,
    }

    FEATURE_TYPE_MAP = {
        "PAS": Feature.Type.PASSIVE,
        "ACT": Feature.Type.ACTION,
        "REA": Feature.Type.REACTION,
    }

    def add_arguments(self, parser):
        parser.add_argument("tsv_filepath")
        parser.add_argument('-s', '--script_filepath')

    @transaction.atomic
    def handle(self, *args, **options):
        filepath = Path(options["tsv_filepath"]).resolve()
        scriptpath = Path(options["script_filepath"]).resolve() \
            if options["script_filepath"] else self.default_scriptpath

        mod = import_script_from_path(scriptpath)
        adversaries = mod.parse_tsv(filepath)

        for data in adversaries:
            tactics = []
            for t_name in data["tactics"]:
                tac, _ = Tactic.objects.get_or_create(name=t_name)
                tactics.append(tac)

            dmg = data["basic_attack"]["damage"]
            dp, _ = DamageProfile.objects.get_or_create(
                dice_number=dmg["dice_number"],
                dice_type=dmg["dice_type"],
                bonus=dmg["bonus"],
                damage_type=DamageType(dmg["damage_type"]),
            )

            ba_range = self.RANGE_MAP.get(
                data["basic_attack"]["range"].lower(),
                BasicAttack.Range.MELEE,
            )
            basic_attack, _ = BasicAttack.objects.get_or_create(
                name=data["basic_attack"]["name"],
                range=ba_range,
                damage=dp,
            )

            experiences = []
            for exp in data["experiences"]:
                exp_obj, _ = Experience.objects.get_or_create(
                    name=exp["name"], bonus=exp["bonus"]
                )
                experiences.append(exp_obj)

            features = []
            for feat in data["features"]:
                ftype = self.FEATURE_TYPE_MAP[feat["type"].upper()]
                feat_obj, created = Feature.objects.get_or_create(
                    name=feat["name"],
                    type=ftype,
                    defaults={"description": feat.get("description", "")},
                )
                desc = feat.get("description")
                if not created and desc and feat_obj.description != desc:
                    feat_obj.description = desc
                    feat_obj.save(update_fields=["description"])
                features.append(feat_obj)

            adversary = Adversary.objects.create(
                name=data["name"],
                tier=data["tier"],
                type=Adversary.Type(data["type"].upper()),
                description=data["description"],
                difficulty=data["difficulty"],
                threshold_major=data["threshold_major"],
                threshold_severe=data["threshold_severe"],
                hit_point=data["hit_point"],
                horde_hit_point=data["horde_hit_point"],
                stress_point=data["stress_point"],
                atk_bonus=data["atk_bonus"],
                basic_attack=basic_attack,
                source="official",
            )

            adversary.tactics.add(*tactics)
            adversary.experiences.add(*experiences)
            adversary.features.add(*features)
