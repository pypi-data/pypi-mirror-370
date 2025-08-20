import inspect
import typing
from enum import Enum


def is_string_enum_class(object_type: type[typing.Any]) -> bool:
    return (
        inspect.isclass(object_type)
        and issubclass(object_type, Enum)
        and issubclass(object_type, str)
    )
