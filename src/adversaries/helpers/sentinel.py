class _UnsetFlag:
    """Sentinel class"""
    __slots__ = ()

    def __bool__(self):
        return False


UNSET = _UnsetFlag()


def is_unset(value):
    return value is UNSET
