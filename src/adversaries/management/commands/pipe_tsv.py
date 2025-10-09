from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


def import_script_from_path(scriptpath):
    spec = spec_from_file_location("script_parser", scriptpath)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Command(BaseCommand):
    help = "Transform tsv input into db entries"
    default_scriptpath = (settings.BASE_DIR / "adversaries" / "scripts" /
                          "tsv_parser.py")

    def add_arguments(self, parser):
        parser.add_argument("tsv_filepath")
        parser.add_argument('-s', '--script_filepath')

    def handle(self, *args, **options):
        filepath = Path(options["tsv_filepath"]).resolve()
        scriptpath = Path(options["script_filepath"]).resolve() \
            if options["script_filepath"] \
            else self.default_scriptpath
        mod = import_script_from_path(scriptpath)
        for adv in mod.parse_tsv(filepath):
            for key, value in adv.items():
                print(f"{key}: {value}")
            print("***")
