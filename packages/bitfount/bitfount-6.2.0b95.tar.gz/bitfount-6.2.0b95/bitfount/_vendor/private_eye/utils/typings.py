from typing import Any, Tuple, Type, cast


def get_type_args(cls: Type) -> Tuple[Any, ...]:
    """
    Note: This method will be deprecated in Python 3.8
    """
    try:
        generic_bases = cls.__orig_bases__[0]
    except (AttributeError, IndexError):
        return ()
    return cast(Tuple, generic_bases.__args__)
