from adversaries.helpers.sentinel import UNSET


def present(d, key):
    """is key present in dict"""
    return key in d


def get_or_unset(d, key):
    """if key present in dict value otherwise return sentinel"""
    return d[key] if key in d else UNSET
