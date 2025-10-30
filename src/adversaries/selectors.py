from adversaries.models import Adversary, Experience, Tactic, Tag, Feature


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


def experience_get(pk):
    return Experience.objects.get(pk=pk)


def experience_list():
    return Experience.objects.all()


def tactic_get(pk):
    return Tactic.objects.get(pk=pk)


def tactic_list():
    return Tactic.objects.all()


def tag_get(pk):
    return Tag.objects.get(pk=pk)


def tag_list():
    return Tag.objects.all()


def feature_get(pk):
    return Feature.objects.get(pk=pk)


def feature_list():
    return Feature.objects.all()
