import dataclasses
import datetime
import functools
from enum import Enum, StrEnum
from typing import Any


class SerializationType(StrEnum):
    NAMED_TUPLE = "NAMED_TUPLE"
    ITERABLE = "ITERABLE"
    DICT = "DICT"
    DATACLASS = "DATACLASS"
    DATE = "DATE"
    TIMEDELTA = "TIMEDELTA"
    ENUM = "ENUM"
    UNKNOWN = "UNKNOWN"


@functools.lru_cache(maxsize=500000)
def get_serialization_type(type: Any) -> SerializationType:
    super_classes = set(type.__mro__)

    # check is named tuple
    if tuple in super_classes and hasattr(type, "_fields"):
        return SerializationType.NAMED_TUPLE

    if list in super_classes or set in super_classes or tuple in super_classes:
        return SerializationType.ITERABLE

    if dict in super_classes:
        return SerializationType.DICT

    if dataclasses.is_dataclass(type):
        return SerializationType.DATACLASS

    if Enum in super_classes and str in super_classes:
        return SerializationType.ENUM

    if datetime.date in super_classes:
        return SerializationType.DATE

    if datetime.timedelta in super_classes:
        return SerializationType.TIMEDELTA

    return SerializationType.UNKNOWN
