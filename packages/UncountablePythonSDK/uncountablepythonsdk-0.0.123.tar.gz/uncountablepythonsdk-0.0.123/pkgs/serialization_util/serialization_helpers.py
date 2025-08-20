# warnings -- types here assume that keys to dictionaries are strings
# this is true most of the time, but there are cases where we have integer indexes

import dataclasses
import datetime
import enum
import functools
from collections.abc import Callable, Mapping, Sequence
from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Protocol,
    TypeVar,
    Union,
    overload,
)

from pkgs.argument_parser import snake_to_camel_case
from pkgs.serialization import (
    MISSING_SENTRY,
    OpaqueKey,
    get_serial_class_data,
)

from ._get_type_for_serialization import SerializationType, get_serialization_type
from .dataclasses import iterate_fields

# Inlined types which otherwise would import from types/base.py
JsonScalar = Union[str, float, bool, Decimal, None, datetime.datetime, datetime.date]
if TYPE_CHECKING:
    JsonValue = Union[JsonScalar, Mapping[str, "JsonValue"], Sequence["JsonValue"]]
else:
    JsonValue = Union[JsonScalar, dict[str, Any], list[Any]]

T = TypeVar("T")


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]  # type: ignore[type-arg,unused-ignore]


def identity(x: T) -> T:
    return x


@overload
def key_convert_to_camelcase(o: str) -> str: ...


@overload
def key_convert_to_camelcase(o: int) -> int: ...


def key_convert_to_camelcase(o: Any) -> str | int:
    if isinstance(o, OpaqueKey):
        return o
    if isinstance(o, enum.StrEnum):
        return o.value
    if isinstance(o, str):
        return snake_to_camel_case(o)
    if isinstance(o, int):
        # we allow dictionaries to use integer keys
        return o
    raise ValueError("Unexpected key type", o)


def _convert_dict(d: dict[str, Any]) -> dict[str, JsonValue]:
    return {
        key_convert_to_camelcase(k): serialize_for_api(v)
        for k, v in d.items()
        if v != MISSING_SENTRY
    }


def _serialize_dict(d: dict[str, Any]) -> dict[str, JsonValue]:
    return {k: serialize_for_storage(v) for k, v in d.items() if v != MISSING_SENTRY}


def _serialize_dataclass(d: Any) -> dict[str, JsonValue]:
    return {
        k: serialize_for_storage(v) for k, v in iterate_fields(d) if v != MISSING_SENTRY
    }


def _to_string_value(value: Any) -> str:
    assert isinstance(value, (Decimal, int))
    return str(value)


@dataclasses.dataclass(kw_only=True)
class DataclassConversions:
    key_conversions: dict[str, str]
    value_conversion_functions: dict[str, Callable[[Any], JsonValue]]


@functools.lru_cache(maxsize=10000)
def _get_dataclass_conversion_lookups(dataclass_type: Any) -> DataclassConversions:
    scd = get_serial_class_data(dataclass_type)

    key_conversions: dict[str, str] = {}
    value_conversion_functions: dict[str, Callable[[Any], JsonValue]] = {}

    for field in dataclasses.fields(dataclass_type):
        key = field.name
        if scd.has_unconverted_key(key):
            key_conversions[key] = key
        else:
            key_conversions[key] = key_convert_to_camelcase(key)

        if scd.has_to_string_value(key):
            value_conversion_functions[key] = _to_string_value
        elif scd.has_unconverted_value(key):
            value_conversion_functions[key] = serialize_for_storage
        else:
            value_conversion_functions[key] = serialize_for_api

    return DataclassConversions(
        key_conversions=key_conversions,
        value_conversion_functions=value_conversion_functions,
    )


def _convert_dataclass(d: Any) -> dict[str, JsonValue]:
    conversions = _get_dataclass_conversion_lookups(type(d))  # type: ignore[arg-type]
    return {
        conversions.key_conversions[k]: (
            conversions.value_conversion_functions[k](v) if v is not None else None
        )
        for k, v in iterate_fields(d)
        if v != MISSING_SENTRY
    }


_SERIALIZATION_FUNCS_STANDARD = {
    SerializationType.ENUM: lambda x: str(x.value),
    SerializationType.DATE: lambda x: x.isoformat(),
    SerializationType.TIMEDELTA: lambda x: x.total_seconds(),
    SerializationType.UNKNOWN: identity,
}

_CONVERSION_SERIALIZATION_FUNCS: dict[SerializationType, Callable[[Any], JsonValue]] = {
    **_SERIALIZATION_FUNCS_STANDARD,
    SerializationType.NAMED_TUPLE: lambda x: _convert_dict(x._asdict()),
    SerializationType.ITERABLE: lambda x: [serialize_for_api(v) for v in x],
    SerializationType.DICT: _convert_dict,
    SerializationType.DATACLASS: _convert_dataclass,
}


@overload
def serialize_for_api(obj: None) -> None: ...


@overload
def serialize_for_api(obj: dict[str, Any]) -> dict[str, JsonValue]: ...


@overload
def serialize_for_api(obj: Dataclass) -> dict[str, JsonValue]: ...


@overload
def serialize_for_api(obj: Any) -> JsonValue: ...


def serialize_for_api(obj: Any) -> JsonValue:
    """
    Serialize to a parsed-JSON format suitably encoded for API output.

    Use the CachedParser.parse_api to parse this data.
    """
    serialization_type = get_serialization_type(type(obj))  # type: ignore
    if (
        serialization_type == SerializationType.UNKNOWN
    ):  # performance optimization to not do function lookup
        return obj  # type: ignore
    r = _CONVERSION_SERIALIZATION_FUNCS[serialization_type](obj)
    return r


_SERIALIZATION_FUNCS_DICT: dict[
    SerializationType, Callable[[Any], dict[str, JsonValue]]
] = {
    SerializationType.DICT: _serialize_dict,
    SerializationType.DATACLASS: _serialize_dataclass,
}


_SERIALIZATION_FUNCS: dict[SerializationType, Callable[[Any], JsonValue]] = {
    **_SERIALIZATION_FUNCS_STANDARD,
    **_SERIALIZATION_FUNCS_DICT,
    SerializationType.NAMED_TUPLE: lambda x: _serialize_dict(x._asdict()),
    SerializationType.ITERABLE: lambda x: [serialize_for_storage(v) for v in x],
}


def serialize_for_storage(obj: Any) -> JsonValue:
    """
    Convert a value into the pseudo-JSON form for
    storage in the DB, file, or other non-API use.

    Use the CachedParser.parse_storage to parse this data.
    """
    serialization_type = get_serialization_type(type(obj))  # type: ignore
    if (
        serialization_type == SerializationType.UNKNOWN
    ):  # performance optimization to not do function lookup
        return obj  # type: ignore
    return _SERIALIZATION_FUNCS[serialization_type](obj)


def serialize_for_storage_dict(obj: dict | Dataclass) -> dict[str, JsonValue]:  # type: ignore[type-arg]
    """
    Same as serialize for storage but guarantees outer object is a dictionary
    """
    serialization_type = get_serialization_type(type(obj))
    return _SERIALIZATION_FUNCS_DICT[serialization_type](obj)
