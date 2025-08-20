from typing import Callable, List, Optional, TypeVar

S = TypeVar("S")
T = TypeVar("T")


def get_optional(optional: Optional[T]) -> T:
    if optional is None:
        raise ValueError("Attempt to get optional containing None")
    return optional


def map_optional(val: Optional[S], f: Callable[[S], T]) -> Optional[T]:
    if val is None:
        return None
    return f(val)


def optional_to_list(val: Optional[T]) -> List[T]:
    if val is None:
        return []
    return [val]


def convert_or_default(value: S, func: Callable[[S], T], default_value: Optional[T]) -> Optional[T]:
    try:
        return func(value)
    except ValueError:
        return default_value


def get_attr_if_present(optional: Optional[S], attrib: str) -> Optional[T]:
    if optional is not None:
        return getattr(optional, attrib)  # type: ignore
    return None
