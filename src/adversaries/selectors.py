from adversaries.models import Adversary


def adversary_get(pk):
    return (
        Adversary.objects
        .select_related("author", "basic_attack__damage")
        .prefetch_related(
            "tactics",
            "tags", "features",
            "adversary_experiences__experience"
        )
        .filter(pk=pk)
        .first()
    )


def adversary_list():
    return (
        Adversary.objects
        .select_related("author", "basic_attack__damage")
        .prefetch_related(
            "tactics",
            "tags",
            "features",
            "adversary_experiences__experience",
        )
        .all()
    )
