import logging
import os
from typing import Iterable, TypeVar, Type, cast, Any
from enum import Enum

T = TypeVar("T")

logger = logging.getLogger("serato-tools")

SERATO_DIR_NAME = "_Serato_"
SERATO_DIR = os.path.join(os.path.expanduser("~"), "Music", SERATO_DIR_NAME)


def get_key_from_value(value: T, dict: dict[str, T]) -> str:
    for key, v in dict.items():
        if v == value:
            return key
    raise ValueError(f"no key for value {value}")


def parse_cli_keys_and_values(args: list[str]):
    pairs: dict[str, str | int] = {}
    key = None
    for arg in args:
        if arg.startswith("--"):
            key = arg.lstrip("-")
            # pairs[key] = True  # default to True if no value follows
        elif key:
            pairs[key] = arg
            key = None
    return pairs


def get_enum_key_from_value(value: str | bytes | int, enum_class: Type[Enum]):
    for member in enum_class:
        if member.value == value:
            return member.name
    raise ValueError(f"no key for value {value}")


def get_enum_key(enum_class: Type[Enum], key_name: str) -> str | None:
    try:
        member = enum_class[key_name]
        return member.name
    except KeyError:
        return None


def to_array(x: T | Iterable[T]) -> Iterable[T]:
    if isinstance(x, (str, bytes)):
        return cast(list[T], [x])
    if isinstance(x, Iterable):
        return x
    return [x]


class DataTypeError(Exception):
    def __init__(self, value: Any, expected_type: type | Iterable[type], field: str | None):
        super().__init__(
            f"value must be {' or '.join(e.__name__ for e in to_array(expected_type))} when field is {field} (type: {type(value).__name__}) (value: {str(value)})"
        )


class DeeplyNestedStructError(Exception):
    def __init__(self):
        super().__init__("unexpected type, deeply nested list. if this occurs, need to implement code for it.")
